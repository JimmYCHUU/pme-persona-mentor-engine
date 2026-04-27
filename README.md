# Persona Mentor Engine (PME)

## Quick Start (Docker)
1. `cd pme`
2. `cp backend/.env.example backend/.env`
3. `docker-compose up --build`

## Manual Setup
- Run [scripts/setup.sh](scripts/setup.sh)
- Start services with [scripts/start.sh](scripts/start.sh)

## Required Local Models
PME requires local Ollama models:
- `llama3.2:3b` (chat)
- `nomic-embed-text` (embeddings)

`scripts/setup.sh` pulls both models automatically when `ollama` is installed.
You can verify with:
- `ollama list`

## First Run
On first launch you should see the opening ritual, then the workspace shell with persona setup and chat.

## How Mastery Tracking Works
Each chat turn emits a mastery event. Background tasks update concept score, status, and certificate eligibility in local SQLite/JSON.

## How the Ethical Time Machine Works
During fingerprint ingestion, evolution notes are stored per persona. When a concept is mentioned later, ETM injects context before Socratic reasoning.

## Architecture
Pipeline order: memory → etm → socratic → persona → guardian → END.
Mastery and certification run as FastAPI background tasks.
