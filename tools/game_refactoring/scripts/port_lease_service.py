#!/usr/bin/env python3
from __future__ import annotations

import errno
import json
import os
import socket
import tempfile
import time
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PORT_BASE = 43100
DEFAULT_POOL_SIZE = 1000
DEFAULT_LEASE_TTL_SECONDS = 3 * 60 * 60


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as handle:
        handle.write(json.dumps(payload, indent=2) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def process_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def can_bind_localhost(port: int) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError as exc:
            if exc.errno in {errno.EADDRINUSE, errno.EACCES}:
                return False
            raise
    return True


@dataclass(frozen=True)
class PortLease:
    port: int
    owner_pid: int
    owner_label: str
    lease_id: str
    acquired_at: str
    expires_at: str
    state_path: Path

    @property
    def localhost_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/"


def default_port_state_path(root: Path) -> Path:
    return root / "runs" / "_shared" / "port_leases.json"


def shared_port_state_path_for_run_dir(run_dir: Path) -> Path:
    run_dir = run_dir.resolve()
    run_state_path = run_dir / "run_state.json"
    if run_state_path.exists():
        try:
            run_state = load_json(run_state_path)
        except json.JSONDecodeError:
            run_state = {}
        runs_root_value = run_state.get("runs_root")
        if isinstance(runs_root_value, str) and runs_root_value.strip():
            return Path(runs_root_value).resolve() / "_shared" / "port_leases.json"
    return run_dir.parent.resolve() / "_shared" / "port_leases.json"


def build_initial_state(port_base: int, pool_size: int, lease_ttl_seconds: int) -> dict[str, Any]:
    created_at = utc_now()
    ports = [port_base + offset for offset in range(pool_size)]
    return {
        "version": 1,
        "created_at": created_at,
        "updated_at": created_at,
        "port_base": port_base,
        "pool_size": pool_size,
        "lease_ttl_seconds": lease_ttl_seconds,
        "ports": ports,
        "leases": {},
        "history": [
            {
                "at": created_at,
                "action": "initialize_pool",
                "detail": f"Initialized shared lease pool with ports {ports[0]}-{ports[-1]} ({pool_size} ports).",
            }
        ],
    }


def load_or_initialize_state(
    state_path: Path,
    *,
    port_base: int = DEFAULT_PORT_BASE,
    pool_size: int = DEFAULT_POOL_SIZE,
    lease_ttl_seconds: int = DEFAULT_LEASE_TTL_SECONDS,
) -> dict[str, Any]:
    if state_path.exists():
        state = load_json(state_path)
        state.setdefault("version", 1)
        state.setdefault("port_base", port_base)
        state.setdefault("pool_size", pool_size)
        state.setdefault("lease_ttl_seconds", lease_ttl_seconds)
        state.setdefault("ports", [state["port_base"] + offset for offset in range(state["pool_size"])])
        state.setdefault("leases", {})
        state.setdefault("history", [])
        return state

    state = build_initial_state(port_base=port_base, pool_size=pool_size, lease_ttl_seconds=lease_ttl_seconds)
    atomic_write_json(state_path, state)
    return state


def _append_history(state: dict[str, Any], *, action: str, detail: str) -> None:
    state.setdefault("history", []).append(
        {
            "at": utc_now(),
            "action": action,
            "detail": detail,
        }
    )
    max_history = 200
    if len(state["history"]) > max_history:
        state["history"] = state["history"][-max_history:]


def passive_evict_stale_leases(state: dict[str, Any]) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    ttl_seconds = int(state.get("lease_ttl_seconds", DEFAULT_LEASE_TTL_SECONDS))
    leases = state.setdefault("leases", {})
    evicted: list[dict[str, Any]] = []

    for port_key, lease in list(leases.items()):
        if not isinstance(lease, dict):
            evicted.append({"port": int(port_key), "reason": "invalid_lease_payload"})
            leases.pop(port_key, None)
            continue

        owner_pid = int(lease.get("owner_pid") or 0)
        expires_at = parse_utc(lease.get("expires_at"))
        pid_alive = process_exists(owner_pid)
        expired = expires_at is not None and now >= expires_at

        if not pid_alive:
            evicted.append({"port": int(port_key), "reason": "dead_pid"})
            leases.pop(port_key, None)
            continue

        if expired:
            evicted.append({"port": int(port_key), "reason": "ttl_expired"})
            leases.pop(port_key, None)
            continue

        if not can_bind_localhost(int(port_key)):
            continue

        lease_updated_at = parse_utc(lease.get("updated_at")) or parse_utc(lease.get("acquired_at"))
        if lease_updated_at is None and ttl_seconds > 0:
            evicted.append({"port": int(port_key), "reason": "missing_timestamp"})
            leases.pop(port_key, None)

    for entry in evicted:
        _append_history(
            state,
            action="evict_lease",
            detail=f"Released port {entry['port']} during passive eviction ({entry['reason']}).",
        )

    if evicted:
        state["updated_at"] = utc_now()
    return evicted


def acquire_port_lease(
    state_path: Path,
    *,
    owner_pid: int,
    owner_label: str,
    port_base: int = DEFAULT_PORT_BASE,
    pool_size: int = DEFAULT_POOL_SIZE,
    lease_ttl_seconds: int = DEFAULT_LEASE_TTL_SECONDS,
) -> PortLease:
    if owner_pid <= 0:
        raise ValueError("owner_pid must be a positive integer")

    state = load_or_initialize_state(
        state_path,
        port_base=port_base,
        pool_size=pool_size,
        lease_ttl_seconds=lease_ttl_seconds,
    )
    passive_evict_stale_leases(state)

    ports = state.get("ports", [])
    leases = state.setdefault("leases", {})
    available_ports = [int(port) for port in ports if str(port) not in leases]

    selected_port: int | None = None
    for port in available_ports:
        if can_bind_localhost(port):
            selected_port = port
            break

    if selected_port is None:
        raise RuntimeError(
            f"No available leased localhost ports remain in pool {ports[0] if ports else 'UNKNOWN'}-"
            f"{ports[-1] if ports else 'UNKNOWN'}."
        )

    acquired_at = utc_now()
    expires_at_dt = datetime.now(timezone.utc).timestamp() + int(state.get("lease_ttl_seconds", lease_ttl_seconds))
    expires_at = datetime.fromtimestamp(expires_at_dt, tz=timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )
    lease_id = f"{owner_pid}:{selected_port}:{int(time.time())}"
    lease_payload = {
        "port": selected_port,
        "owner_pid": owner_pid,
        "owner_label": owner_label,
        "lease_id": lease_id,
        "acquired_at": acquired_at,
        "updated_at": acquired_at,
        "expires_at": expires_at,
    }
    leases[str(selected_port)] = lease_payload
    _append_history(
        state,
        action="acquire_lease",
        detail=f"Leased port {selected_port} to pid={owner_pid} owner={owner_label}.",
    )
    state["updated_at"] = acquired_at
    atomic_write_json(state_path, state)

    return PortLease(
        port=selected_port,
        owner_pid=owner_pid,
        owner_label=owner_label,
        lease_id=lease_id,
        acquired_at=acquired_at,
        expires_at=expires_at,
        state_path=state_path,
    )


def refresh_port_lease(state_path: Path, *, port: int, owner_pid: int) -> bool:
    state = load_or_initialize_state(state_path)
    lease = state.setdefault("leases", {}).get(str(port))
    if not isinstance(lease, dict):
        return False
    if int(lease.get("owner_pid") or 0) != owner_pid:
        return False

    now = utc_now()
    ttl_seconds = int(state.get("lease_ttl_seconds", DEFAULT_LEASE_TTL_SECONDS))
    lease["updated_at"] = now
    expires_at_dt = datetime.now(timezone.utc).timestamp() + ttl_seconds
    lease["expires_at"] = datetime.fromtimestamp(expires_at_dt, tz=timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )
    state["updated_at"] = now
    atomic_write_json(state_path, state)
    return True


def release_port_lease(state_path: Path, *, port: int, owner_pid: int | None = None) -> bool:
    state = load_or_initialize_state(state_path)
    leases = state.setdefault("leases", {})
    lease = leases.get(str(port))
    if not isinstance(lease, dict):
        return False
    if owner_pid is not None and int(lease.get("owner_pid") or 0) != owner_pid:
        return False

    leases.pop(str(port), None)
    now = utc_now()
    _append_history(
        state,
        action="release_lease",
        detail=f"Released port {port} owner_pid={lease.get('owner_pid')} owner={lease.get('owner_label')}.",
    )
    state["updated_at"] = now
    atomic_write_json(state_path, state)
    return True