#!/bin/bash
# PME Setup Script — Run once after cloning
set -e

echo "=== PME Setup ==="

# Backend
echo "Setting up backend..."
cd backend

# Auto-detect Python
PYTHON=""
for cmd in python3.12 python3.11 python3 python; do
  if command -v "$cmd" &>/dev/null; then
    PYTHON="$cmd"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "❌ No Python 3 found. Please install Python 3.11+."
  exit 1
fi

echo "Using $PYTHON ($($PYTHON --version))"
$PYTHON -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx
echo "Installing Playwright browsers (optional, skipping if fails)..."
playwright install chromium 2>/dev/null || echo "  Skipped Playwright — run 'sudo playwright install --with-deps chromium' later if needed"
cp .env.example .env
cd ..

# Frontend
echo "Setting up frontend..."
cd frontend
npm install
cd ..

# Data directories
echo "Creating data directories..."
mkdir -p backend/data/{chroma,sessions,uploads,personas,mastery_certs}

# Ollama models
echo "Pulling Ollama models..."
ollama pull llama3.2:3b 2>/dev/null || echo "Warning: Could not pull llama3.2:3b. Is Ollama running?"
ollama pull nomic-embed-text 2>/dev/null || echo "Warning: Could not pull nomic-embed-text."

echo ""
echo "=== Setup complete! ==="
echo "Run ./scripts/start.sh to start the application."
