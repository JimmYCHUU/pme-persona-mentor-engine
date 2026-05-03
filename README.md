# Persona Mentor Engine (PME)

A private, local-first AI workspace that clones the intellectual DNA of any real-world expert and places that mentor beside you as you learn and work.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.com/) installed and running
- Models: `ollama pull llama3.2:3b && ollama pull nomic-embed-text`

### Manual Setup

```bash
# Backend
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker-compose up --build
```

Open http://localhost:5173 — the frontend will connect to the backend at http://localhost:8000.

## Architecture

- **Backend**: FastAPI + LangGraph orchestrator + LlamaIndex RAG
- **Frontend**: React + Vite + TypeScript + Zustand
- **LLM**: Ollama (local only, no cloud APIs)
- **Design**: Cinematic Editorial (Playfair Display, warm gold, glassmorphism)

## License

Private — Single User System
