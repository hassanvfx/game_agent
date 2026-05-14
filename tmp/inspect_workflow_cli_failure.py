import subprocess
from pathlib import Path

ROOT = Path("tools/game_refactoring").resolve()

command = [
    "python3",
    str(ROOT / "scripts" / "creative_refactor_cli.py"),
    "--json",
    "start-batch",
    "--manifest",
    str(ROOT / "runs" / "_workflow_manifests" / "creative_remix_v4__game_refactoring_two_random_kawaii_manifest.json"),
    "--pipeline",
    "v2",
    "--model",
    "gpt-5.4",
    "--agent-timeout",
    "3600",
    "--max-concurrency",
    "2",
    "--poll-seconds",
    "5.0",
    "--stale-heartbeat-seconds",
    "900",
    "--source-mode",
    "copy",
    "--remix-prompt",
    "Kawaii Style",
]

completed = subprocess.run(command, capture_output=True, text=True, cwd=str(ROOT))

print("RETURN_CODE=", completed.returncode)
print("--- STDOUT ---")
print(completed.stdout)
print("--- STDERR ---")
print(completed.stderr)