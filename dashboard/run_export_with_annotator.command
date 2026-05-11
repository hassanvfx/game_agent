#!/bin/bash
set -euo pipefail

ROOT_DIR="/Volumes/Elements/games_top_gameplays"
cd "$ROOT_DIR"

LIMIT=""
LAUNCH="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      LIMIT="${2:-}"
      shift 2
      ;;
    --launch)
      LAUNCH="1"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--limit N] [--launch]"
      exit 1
      ;;
  esac
done

LABEL="annotator-coordinated"
if [[ -n "$LIMIT" ]]; then
  LABEL="${LABEL}-${LIMIT}"
fi

RUN_CMD=(python3 outputs/build_tag_and_fix_public_export.py --label "$LABEL")
if [[ -n "$LIMIT" ]]; then
  RUN_CMD+=(--limit "$LIMIT")
fi

"${RUN_CMD[@]}"

LATEST_RUN="$(find tag_and_fix_1k_export/runs -maxdepth 1 -type d -name "*--${LABEL}*" | sort | tail -n 1)"
if [[ -z "$LATEST_RUN" ]]; then
  echo "Could not find latest run for label: $LABEL"
  exit 1
fi

python3 outputs/build_tag_and_fix_app_json.py --run-dir "$LATEST_RUN"

PUBLIC_DIR="$LATEST_RUN/public"

zsh publish_annotator_to_public.command "$PUBLIC_DIR"

echo "Run ready at: $LATEST_RUN"
echo "Public folder: $PUBLIC_DIR"

if [[ "$LAUNCH" == "1" ]]; then
  bash "$PUBLIC_DIR/launch_annotator.command"
fi