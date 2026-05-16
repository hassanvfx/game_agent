#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Rebuilding game matcher reverse index..."
python3 scripts/build_gameplay_reverse_index.py

echo "Exporting all queries..."
python3 scripts/export_all_queries.py

echo "Done."
