#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import subprocess
import time

TARGETS = [
    "run_v4_rick_morty_raw_one_game_model55_20260509T073323Z",
    "run_v4_rick_morty_raw_one_game_model55_20260509T073337Z",
]


def list_matches() -> list[dict[str, str]]:
    output = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True)
    matches: list[dict[str, str]] = []
    own_pid = os.getpid()
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        pid_text, _, command = stripped.partition(" ")
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if pid == own_pid:
            continue
        if any(target in command for target in TARGETS):
            matches.append({"pid": str(pid), "command": command})
    return matches


def kill_matches(matches: list[dict[str, str]], sig: signal.Signals) -> list[int]:
    killed: list[int] = []
    for match in matches:
        pid = int(match["pid"])
        try:
            os.kill(pid, sig)
            killed.append(pid)
        except ProcessLookupError:
            pass
    return killed


def main() -> None:
    initial = list_matches()
    sigterm_pids = kill_matches(initial, signal.SIGTERM)
    time.sleep(2)
    after_term = list_matches()
    sigkill_pids = kill_matches(after_term, signal.SIGKILL)
    time.sleep(1)
    survivors = list_matches()

    print(json.dumps({
        "targets": TARGETS,
        "initial_matches": initial,
        "sigterm_pids": sigterm_pids,
        "sigkill_pids": sigkill_pids,
        "survivors": survivors,
        "success": not survivors,
    }, indent=2))


if __name__ == "__main__":
    main()