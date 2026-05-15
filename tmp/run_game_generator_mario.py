import subprocess
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
tool_root = repo_root / "tools" / "game_generator"

completed = subprocess.run(
    ["python3", "scripts/run_pipeline.py", "mario bros"],
    cwd=tool_root,
    capture_output=True,
    text=True,
)

print("EXIT_CODE:", completed.returncode)
if completed.stdout:
    print("STDOUT:")
    print(completed.stdout)
if completed.stderr:
    print("STDERR:")
    print(completed.stderr)