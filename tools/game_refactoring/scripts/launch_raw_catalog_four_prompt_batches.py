import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME_WORKFLOW = ROOT / "scripts" / "game_workflow.py"

BATCHES = [
    ("harry potter", ROOT / "fixtures" / "harry_potter_raw_catalog_107_manifest.json"),
    ("rick and morty", ROOT / "fixtures" / "rick_and_morty_raw_catalog_107_manifest.json"),
    ("flappy bird", ROOT / "fixtures" / "flappy_bird_raw_catalog_107_manifest.json"),
    (
        "harry potter with angrybrids mehcnics in 3d",
        ROOT / "fixtures" / "harry_potter_angrybrids_3d_raw_catalog_107_manifest.json",
    ),
]


def main() -> None:
    for prompt, manifest_path in BATCHES:
        command = [
            "python3",
            str(GAME_WORKFLOW),
            "--json",
            "--id",
            "creative_remix_v3",
            "--games-manifest-source",
            str(manifest_path),
            "--remix-prompt",
            prompt,
            "--max-concurrency",
            "1",
        ]
        print(f"[launch] prompt={prompt}")
        completed = subprocess.run(command, check=True, capture_output=True, text=True, cwd=ROOT)
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        if stdout:
            print(stdout)
        if stderr:
            print("[stderr]")
            print(stderr)
        print("[done]")
        print("-" * 80)


if __name__ == "__main__":
    main()