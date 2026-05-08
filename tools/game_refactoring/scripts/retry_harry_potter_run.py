import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
command = [
    "python3",
    str(root / "scripts" / "game_workflow.py"),
    "--json",
    "--id",
    "creative_remix_v3",
    "--games-manifest-source",
    str(root / "fixtures" / "harry_potter_two_game_manifest.json"),
    "--remix-prompt",
    "harry potter",
    "--max-concurrency",
    "1",
]

completed = subprocess.run(command, check=True, capture_output=True, text=True, cwd=root)
print(completed.stdout.strip())