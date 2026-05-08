#!/usr/bin/env python3
from __future__ import annotations

import os
import signal
import subprocess
from dataclasses import asdict, dataclass
from typing import Iterable

DEFAULT_PATTERN_GROUPS: tuple[str, ...] = (
    "creative_refactor_cli.py",
    "run_parallel_batch.py",
    "run_single_game.py",
    "debug_creative_refactor.py",
)

OPTIONAL_PATTERN_GROUPS: tuple[str, ...] = ("cline",)


@dataclass
class ProcessMatch:
    pid: int
    command: str
    matched_patterns: list[str]


def _pgrep_output(patterns: Iterable[str]) -> str:
    non_empty = [pattern for pattern in patterns if pattern]
    if not non_empty:
        return ""
    regex = "|".join(non_empty)
    completed = subprocess.run(
        ["pgrep", "-af", regex],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode not in {0, 1}:
        stderr = completed.stderr.strip()
        raise RuntimeError(f"pgrep failed: {stderr or completed.returncode}")
    return completed.stdout.strip()


def list_matching_processes(*, include_cline: bool = False, exclude_pid: int | None = None) -> list[ProcessMatch]:
    patterns = list(DEFAULT_PATTERN_GROUPS)
    if include_cline:
        patterns.extend(OPTIONAL_PATTERN_GROUPS)

    output = _pgrep_output(patterns)
    results: list[ProcessMatch] = []
    if not output:
        return results

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split(maxsplit=1)
        if not parts:
            continue
        try:
            pid = int(parts[0])
        except ValueError:
            continue
        if exclude_pid is not None and pid == exclude_pid:
            continue
        command = parts[1] if len(parts) > 1 else ""
        matched = [pattern for pattern in patterns if pattern in command]
        if not matched:
            continue
        results.append(ProcessMatch(pid=pid, command=command, matched_patterns=matched))
    return results


def signal_processes(
    matches: list[ProcessMatch],
    *,
    force: bool = False,
) -> dict[str, object]:
    if not matches:
        return {
            "signal": "SIGKILL" if force else "SIGTERM",
            "terminated_pids": [],
            "errors": [],
        }

    sig = signal.SIGKILL if force else signal.SIGTERM
    terminated_pids: list[int] = []
    errors: list[dict[str, object]] = []

    for match in matches:
        try:
            os.kill(match.pid, sig)
            terminated_pids.append(match.pid)
        except ProcessLookupError:
            errors.append(
                {
                    "pid": match.pid,
                    "error": "process_not_found",
                }
            )
        except PermissionError:
            errors.append(
                {
                    "pid": match.pid,
                    "error": "permission_denied",
                }
            )

    return {
        "signal": "SIGKILL" if force else "SIGTERM",
        "terminated_pids": terminated_pids,
        "errors": errors,
    }


def build_kill_all_payload(
    *,
    include_cline: bool,
    dry_run: bool,
    force: bool,
    exclude_pid: int | None = None,
) -> dict[str, object]:
    before_matches = list_matching_processes(include_cline=include_cline, exclude_pid=exclude_pid)
    payload: dict[str, object] = {
        "mode": "kill-all",
        "include_cline": include_cline,
        "dry_run": dry_run,
        "force": force,
        "matched_processes": [asdict(match) for match in before_matches],
        "matched_count": len(before_matches),
    }

    if dry_run:
        payload["signal"] = None
        payload["terminated_pids"] = []
        payload["survivors"] = [asdict(match) for match in before_matches]
        payload["success"] = True
        return payload

    signal_result = signal_processes(before_matches, force=force)
    survivors = list_matching_processes(include_cline=include_cline, exclude_pid=exclude_pid)

    payload["signal"] = signal_result["signal"]
    payload["terminated_pids"] = signal_result["terminated_pids"]
    payload["errors"] = signal_result["errors"]
    payload["survivors"] = [asdict(match) for match in survivors]
    payload["survivor_count"] = len(survivors)
    payload["success"] = len(survivors) == 0
    return payload


def render_kill_all_human(payload: dict[str, object]) -> str:
    lines = [
        "Kill-All Operation",
        "==================",
        f"include_cline: {payload['include_cline']}",
        f"dry_run: {payload['dry_run']}",
        f"force: {payload['force']}",
        f"matched_count: {payload['matched_count']}",
    ]

    matched = payload.get("matched_processes", [])
    if matched:
        lines.extend(["", "Matched processes", "-----------------"])
        for item in matched:
            lines.append(f"{item['pid']} | {item['command']}")
    else:
        lines.extend(["", "Matched processes", "-----------------", "none"])

    if not payload["dry_run"]:
        lines.extend(
            [
                "",
                f"signal: {payload['signal']}",
                f"terminated_pids: {payload.get('terminated_pids', [])}",
                f"survivor_count: {payload.get('survivor_count', 0)}",
            ]
        )
        survivors = payload.get("survivors", [])
        if survivors:
            lines.extend(["", "Survivors", "---------"])
            for item in survivors:
                lines.append(f"{item['pid']} | {item['command']}")
        else:
            lines.extend(["", "Survivors", "---------", "none"])
    return "\n".join(lines)