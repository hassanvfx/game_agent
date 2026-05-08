import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_JSON = Path("/Users/hassan/Downloads/tag-and-fix-annotation-state-2.json")
RAW_ROOT = Path("/Volumes/backup/game_maker/catalogs/raw")
FIXTURES_DIR = ROOT / "fixtures"

PROMPTS = [
    ("harry potter", "harry_potter"),
    ("rick and morty", "rick_and_morty"),
    ("flappy bird", "flappy_bird"),
    ("harry potter with angrybrids mehcnics in 3d", "harry_potter_angrybrids_3d"),
]


def load_selected_gamezones() -> list[str]:
    with SOURCE_JSON.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    game_notes = data["collections"]["favorites"]["gameNotes"]
    return sorted(game_notes.keys())


def ensure_all_present(gamezones: list[str]) -> None:
    missing = [gamezone for gamezone in gamezones if not (RAW_ROOT / gamezone).exists()]
    if missing:
        raise SystemExit(
            f"Missing {len(missing)} selected game directories under {RAW_ROOT}: "
            + ", ".join(missing[:10])
        )


def build_manifest(prompt_slug: str, gamezones: list[str], created_at: str) -> dict:
    return {
        "manifest_version": "1.0.0",
        "run_label": f"raw-catalog-{prompt_slug}-107-game-batch",
        "created_at": created_at,
        "games": [
            {
                "game_id": gamezone.removeprefix("gamezone-"),
                "source_path": str(RAW_ROOT / gamezone),
                "display_name": gamezone,
            }
            for gamezone in gamezones
        ],
        "source_manifest_path": str(SOURCE_JSON),
    }


def main() -> None:
    gamezones = load_selected_gamezones()
    ensure_all_present(gamezones)

    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    generated_paths: list[Path] = []

    for prompt_text, prompt_slug in PROMPTS:
        manifest = build_manifest(prompt_slug, gamezones, created_at)
        output_path = FIXTURES_DIR / f"{prompt_slug}_raw_catalog_107_manifest.json"
        output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        generated_paths.append(output_path)
        print(f"[ok] {prompt_text} -> {output_path}")

    print(f"[summary] generated {len(generated_paths)} manifests for {len(gamezones)} games")


if __name__ == "__main__":
    main()