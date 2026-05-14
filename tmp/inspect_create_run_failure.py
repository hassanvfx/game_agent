import subprocess
from pathlib import Path

ROOT = Path("tools/game_refactoring").resolve()

command = [
    "python3",
    str(ROOT / "scripts" / "create_run.py"),
    "--manifest",
    str(ROOT / "runs" / "_workflow_manifests" / "creative_remix_v4__game_refactoring_two_random_kawaii_manifest.json"),
    "--source-mode",
    "copy",
]

completed = subprocess.run(command, capture_output=True, text=True, cwd=str(ROOT))

print("RETURN_CODE=", completed.returncode)
print("--- STDOUT ---")
print(completed.stdout)
print("--- STDERR ---")
print(completed.stderr)