#!/bin/bash
# PME Setup Script — Run once after cloning
set -e

echo "=== PME Setup ==="

# Backend
echo "Setting up backend..."
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx
echo "Installing Playwright browsers..."
playwright install chromium --with-deps 2>/dev/null || true
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
