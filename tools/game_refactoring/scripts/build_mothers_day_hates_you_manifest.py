import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_JSON = Path("/Users/hassan/Downloads/tag-and-fix-annotation-state-2.json")
RAW_ROOT = Path("/Volumes/backup/game_maker/catalogs/raw")
OUTPUT_PATH = ROOT / "fixtures" / "mothers_day_hates_you_raw_catalog_107_manifest.json"


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


def build_manifest(gamezones: list[str], created_at: str) -> dict:
    return {
        "manifest_version": "1.0.0",
        "run_label": "raw-catalog-mothers-day-hates-you-107-game-batch",
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
    manifest = build_manifest(gamezones, created_at)
    OUTPUT_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"[ok] wrote {OUTPUT_PATH}")
    print(f"[summary] prepared manifest for {len(gamezones)} games")


if __name__ == "__main__":
    main()