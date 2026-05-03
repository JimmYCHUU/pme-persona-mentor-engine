#!/bin/bash
# PME Docker Start Script
set -e

echo "=== Starting PME (Docker) ==="
echo "This will build and start all containers."
echo ""

docker-compose up --build -d

echo ""
echo "=== PME Running ==="
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  Ollama:   http://localhost:11434"
echo ""
echo "Models will be pulled automatically (first start may take a while)."
echo "Run 'docker-compose logs -f' to monitor."
echo "Run 'docker-compose down' to stop."
