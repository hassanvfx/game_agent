#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game_matcher_v2.builder import DEFAULT_APP_JSON_PATH, build_artifacts  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build or refresh deterministic game_matcher_v2 artifacts from app.json."
    )
    parser.add_argument(
        "--app-json",
        type=Path,
        default=DEFAULT_APP_JSON_PATH,
        help="Optional override path to the source app.json. Defaults to games/published/public/app.json.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a rebuild even if artifact metadata matches the current source.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_artifacts(app_json=args.app_json, force=args.force)
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 1

    payload = {
        "source_path": str(result.source_path),
        "artifacts_dir": str(result.artifacts_dir),
        "metadata_path": str(result.metadata_path),
        "game_count": result.game_count,
        "source_md5": result.source_md5,
        "rebuilt": result.rebuilt,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())