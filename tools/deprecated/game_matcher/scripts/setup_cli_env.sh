#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

python3 -m venv "$VENV_DIR"

"$VENV_DIR/bin/python" -m pip install --upgrade pip

if [ ! -f "${ROOT_DIR}/.env" ]; then
  cp "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
  echo "Created ${ROOT_DIR}/.env from .env.example"
else
  echo ".env already exists at ${ROOT_DIR}/.env"
fi

echo "Virtual environment ready at ${VENV_DIR}"
echo "Activate it with: source ${VENV_DIR}/bin/activate"
echo "Then edit ${ROOT_DIR}/.env and set OPENAI_API_KEY"