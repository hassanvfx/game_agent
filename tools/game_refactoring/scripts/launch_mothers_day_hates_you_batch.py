import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME_WORKFLOW = ROOT / "scripts" / "game_workflow.py"
MANIFEST_PATH = ROOT / "fixtures" / "mothers_day_hates_you_raw_catalog_107_manifest.json"
PROMPT = "mothers day, but your mom hates you"


def main() -> None:
    command = [
        "python3",
        str(GAME_WORKFLOW),
        "--json",
        "--id",
        "creative_remix_v3",
        "--games-manifest-source",
        str(MANIFEST_PATH),
        "--remix-prompt",
        PROMPT,
        "--max-concurrency",
        "1",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True, cwd=ROOT)
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stdout:
        print(stdout)
    if stderr:
        print("[stderr]")
        print(stderr)


if __name__ == "__main__":
    main()