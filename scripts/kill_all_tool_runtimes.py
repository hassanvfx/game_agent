#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TOOL_KILL_COMMANDS: tuple[tuple[str, list[str]], ...] = (
    (
        "game_refactoring",
        [sys.executable, str(ROOT / "tools" / "game_refactoring" / "scripts" / "creative_refactor_cli.py"), "--json", "kill-all", "--include-cline"],
    ),
    (
        "game_remix_editor",
        [sys.executable, str(ROOT / "tools" / "game_remix_editor" / "scripts" / "creative_refactor_cli.py"), "--json", "kill-all", "--include-cline"],
    ),
)

FALLBACK_PATTERNS: tuple[str, ...] = (
    "creative_refactor_cli.py",
    "run_operator_pipeline_batch.py",
    "run_parallel_batch.py",
    "run_single_game.py",
    "run_operator_pipeline_game.py",
    "game_workflow.py",
    "spec_adaptor.py",
    "cline",
)

RUN_ID_PATTERNS: tuple[str, ...] = (
    "/Volumes/backup/output/remixed",
    "run_game_remixer_",
)


@dataclass
class ProcessMatch:
    pid: int
    command: str
    matched_patterns: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Robust kill-all helper that fans out across tool-local kill commands and direct process matching."
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview matches without sending signals.")
    parser.add_argument("--force", action="store_true", help="Use SIGKILL instead of SIGTERM.")
    parser.add_argument(
        "--run-id",
        action="append",
        default=[],
        help="Optional run id to match directly. Can be passed multiple times.",
    )
    parser.add_argument(
        "--run-dir",
        action="append",
        default=[],
        help="Optional run directory path to match directly. Can be passed multiple times.",
    )
    parser.add_argument(
        "--include-default-run-patterns",
        action="store_true",
        help="Also match generic run-root patterns like /Volumes/backup/output/remixed and run_game_remixer_.",
    )
    return parser.parse_args()


def run_tool_command(name: str, command: list[str], dry_run: bool, force: bool) -> dict[str, Any]:
    adjusted = command[:]
    if dry_run:
        adjusted.append("--dry-run")
    if force:
        adjusted.append("--force")

    completed = subprocess.run(adjusted, capture_output=True, text=True, check=False)
    payload: dict[str, Any] = {
        "tool": name,
        "command": adjusted,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "parsed": None,
    }
    if completed.stdout.strip():
        try:
            payload["parsed"] = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload["parsed"] = None
    return payload


def _pgrep_output(patterns: list[str]) -> str:
    if not patterns:
        return ""
    regex = "|".join(patterns)
    completed = subprocess.run(
        ["pgrep", "-af", regex],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode not in {0, 1}:
        raise RuntimeError(completed.stderr.strip() or f"pgrep failed with {completed.returncode}")
    return completed.stdout.strip()


def list_matching_processes(patterns: list[str], exclude_pid: int | None) -> list[ProcessMatch]:
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
        matched = [pattern for pattern in patterns if pattern and pattern in command]
        if not matched:
            continue
        results.append(ProcessMatch(pid=pid, command=command, matched_patterns=matched))
    return results


def signal_processes(matches: list[ProcessMatch], force: bool) -> dict[str, Any]:
    sig = signal.SIGKILL if force else signal.SIGTERM
    terminated: list[int] = []
    errors: list[dict[str, Any]] = []
    for match in matches:
        try:
            os.kill(match.pid, sig)
            terminated.append(match.pid)
        except ProcessLookupError:
            errors.append({"pid": match.pid, "error": "process_not_found"})
        except PermissionError:
            errors.append({"pid": match.pid, "error": "permission_denied"})
    if not force and terminated:
        time.sleep(1.0)
    return {
        "signal": "SIGKILL" if force else "SIGTERM",
        "terminated_pids": terminated,
        "errors": errors,
    }


def build_patterns(args: argparse.Namespace) -> list[str]:
    patterns = list(FALLBACK_PATTERNS)
    for run_id in args.run_id:
        if run_id and run_id not in patterns:
            patterns.append(run_id)
    for run_dir in args.run_dir:
        if run_dir and run_dir not in patterns:
            patterns.append(run_dir)
    if args.include_default_run_patterns:
        for pattern in RUN_ID_PATTERNS:
            if pattern not in patterns:
                patterns.append(pattern)
    return patterns


def main() -> None:
    args = parse_args()

    tool_results = [run_tool_command(name, command, args.dry_run, args.force) for name, command in TOOL_KILL_COMMANDS]

    patterns = build_patterns(args)
    matches = list_matching_processes(patterns, exclude_pid=os.getpid())

    payload: dict[str, Any] = {
        "mode": "kill-all-tool-runtimes",
        "dry_run": args.dry_run,
        "force": args.force,
        "tool_results": tool_results,
        "fallback_patterns": patterns,
        "fallback_matches": [asdict(match) for match in matches],
        "fallback_match_count": len(matches),
    }

    if args.dry_run:
        payload["signal"] = None
        payload["terminated_pids"] = []
        payload["survivors"] = [asdict(match) for match in matches]
        payload["success"] = True
        print(json.dumps(payload, indent=2))
        return

    signal_result = signal_processes(matches, args.force)
    survivors = list_matching_processes(patterns, exclude_pid=os.getpid())
    payload["signal"] = signal_result["signal"]
    payload["terminated_pids"] = signal_result["terminated_pids"]
    payload["errors"] = signal_result["errors"]
    payload["survivors"] = [asdict(match) for match in survivors]
    payload["survivor_count"] = len(survivors)
    payload["success"] = len(survivors) == 0
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()