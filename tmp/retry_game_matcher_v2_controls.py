from pathlib import Path
import subprocess

repo_root = Path(__file__).resolve().parents[1]
cli_path = repo_root / "tools" / "game_matcher_v2" / "cli" / "match_prompt.py"
prompts = [
    "flappy bird",
    "mario bros",
    "angry birds",
]

for prompt in prompts:
    print("=" * 80)
    print(f"PROMPT: {prompt}")
    print("=" * 80)
    completed = subprocess.run(
        ["python3", str(cli_path), prompt],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
    )
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print("--- STDERR ---")
        print(completed.stderr.rstrip())
    print(f"EXIT CODE: {completed.returncode}")
    print()