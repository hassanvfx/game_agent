import os
import subprocess


def run_cline_check() -> dict:
    command = os.getenv("CLINE_CHECK_COMMAND", "cline --help")
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"Cline CLI check failed with code {completed.returncode}: {completed.stderr.strip()}"
        )

    return {
        "tool": "cline",
        "status": "success",
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip()[:2000],
        "stderr": completed.stderr.strip()[:1000],
    }