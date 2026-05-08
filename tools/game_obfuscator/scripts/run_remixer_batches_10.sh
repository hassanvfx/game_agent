#!/bin/zsh
set -euo pipefail

GAME_OBFUSCATOR_ROOT="/Volumes/Elements/game_obfuscator"
MANIFEST_DIR="$GAME_OBFUSCATOR_ROOT/manifests/remixer_export_top1000_batches_10"
CLI_SCRIPT="$GAME_OBFUSCATOR_ROOT/scripts/game_obfuscator_cli.py"
POLL_SECONDS="${POLL_SECONDS:-30}"
START_BATCH="${START_BATCH:-1}"
END_BATCH="${END_BATCH:-80}"

if [[ ! -d "$MANIFEST_DIR" ]]; then
  echo "Manifest directory not found: $MANIFEST_DIR" >&2
  exit 1
fi

if [[ ! -f "$CLI_SCRIPT" ]]; then
  echo "CLI script not found: $CLI_SCRIPT" >&2
  exit 1
fi

echo "Running remixer obfuscation batches sequentially"
echo "Manifest dir: $MANIFEST_DIR"
echo "Batch range: $(printf "%03d" "$START_BATCH") -> $(printf "%03d" "$END_BATCH")"
echo "Poll interval: ${POLL_SECONDS}s"
echo

for batch_num in $(seq "$START_BATCH" "$END_BATCH"); do
  batch_name=$(printf "batch_%03d.json" "$batch_num")
  manifest_path="$MANIFEST_DIR/$batch_name"

  if [[ ! -f "$manifest_path" ]]; then
    echo "Skipping missing manifest: $manifest_path" >&2
    continue
  fi

  echo "============================================================"
  echo "Starting $batch_name"
  echo "Manifest: $manifest_path"

  start_json=$(cd "$GAME_OBFUSCATOR_ROOT" && python3 "$CLI_SCRIPT" start --manifest "manifests/remixer_export_top1000_batches_10/$batch_name")
  echo "$start_json"

  run_id=$(printf '%s\n' "$start_json" | python3 -c 'import sys, json; print(json.load(sys.stdin)["run_id"])')
  if [[ -z "$run_id" ]]; then
    echo "Failed to extract run_id for $batch_name" >&2
    exit 1
  fi

  echo "Polling run_id=$run_id"
  while true; do
    status_json=$(cd "$GAME_OBFUSCATOR_ROOT" && python3 "$CLI_SCRIPT" status --run-id "$run_id")
    echo "$status_json"

    completed=$(printf '%s\n' "$status_json" | python3 -c 'import sys, json; print(str(json.load(sys.stdin).get("completed", False)).lower())')
    run_status=$(printf '%s\n' "$status_json" | python3 -c 'import sys, json; print(json.load(sys.stdin).get("status", ""))')

    if [[ "$completed" == "true" ]]; then
      echo "Batch $batch_name completed with status=$run_status"
      break
    fi

    sleep "$POLL_SECONDS"
  done

  echo "Resolved outputs for $batch_name"
  cd "$GAME_OBFUSCATOR_ROOT" && python3 "$CLI_SCRIPT" output-path --run-id "$run_id" --include-games
  echo
done

echo "All requested batches processed."