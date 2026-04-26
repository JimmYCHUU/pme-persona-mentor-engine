#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIDS=()

cleanup() {
  for p in "${PIDS[@]:-}"; do
    kill "$p" >/dev/null 2>&1 || true
  done
}
trap cleanup INT TERM EXIT

if ! curl -sSf http://localhost:11434/api/tags >/dev/null 2>&1; then
  ollama serve >/tmp/pme_ollama.log 2>&1 &
  PIDS+=("$!")
  sleep 2
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/backend/.venv/bin/activate"
cd "$ROOT_DIR/backend"
uvicorn main:app --reload >/tmp/pme_backend.log 2>&1 &
PIDS+=("$!")

cd "$ROOT_DIR/frontend"
npm run dev >/tmp/pme_frontend.log 2>&1 &
PIDS+=("$!")

wait
