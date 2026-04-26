#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command_exists() { command -v "$1" >/dev/null 2>&1; }

if ! command_exists python3; then
  echo "python3 is required"
  exit 1
fi

if ! command_exists node; then
  echo "node is required (v20+)"
fi

if ! command_exists ollama; then
  echo "ollama is not installed"
fi

mkdir -p "$ROOT_DIR/backend/data"/{chroma,sessions,uploads,personas,mastery_certs}

if [[ ! -d "$ROOT_DIR/backend/.venv" ]]; then
  python3 -m venv "$ROOT_DIR/backend/.venv"
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/backend/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/backend/requirements.txt"

cp -n "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env" || true

cd "$ROOT_DIR/frontend"
npm install
