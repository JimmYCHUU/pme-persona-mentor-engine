#!/bin/bash
# PME Start Script — Launches backend and frontend
set -e

echo "=== Starting PME ==="

# Check Ollama
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "⚠ Ollama is not running. Please start Ollama first."
  echo "  Run: ollama serve"
  exit 1
fi

# Start backend
echo "Starting backend..."
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== PME Running ==="
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop."

# Handle shutdown
trap 'echo "Stopping..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' SIGINT SIGTERM
wait
