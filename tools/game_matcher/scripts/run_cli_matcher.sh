#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="${ROOT_DIR}/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Missing virtual environment Python at ${VENV_PYTHON}" >&2
  echo "Run ./scripts/setup_cli_env.sh first." >&2
  exit 1
fi

exec "$VENV_PYTHON" "${ROOT_DIR}/cli/game_matcher_cli.py" "$@"