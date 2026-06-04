# Persona Mentor Engine (PME)

> **An AI-powered mentoring platform** that creates personalised learning experiences through 40+ pre-built mentor personas, a 5-level Socratic ladder, experience-triggered memory, and proof-of-mastery certification.

[![Tests](https://img.shields.io/badge/tests-73%20passing-brightgreen)](./backend/tests)
[![Python](https://img.shields.io/badge/python-3.12-blue)](./backend)
[![React](https://img.shields.io/badge/react-19-blue)](./frontend)
[![TypeScript](https://img.shields.io/badge/typescript-5.6-blue)](./frontend)

---

## Architecture

```
┌─────────────┐    ┌──────────────────────────────────────────────────────────────┐
│  React 19   │    │  FastAPI Backend                                             │
│  Vite       │◄──►│  ┌─────────────────────────────────────────────────────────┐  │
│  Zustand    │    │  │  LangGraph Pipeline (ARCH-3)                            │  │
│  globals.css│    │  │  memory → etm → socratic → persona → guardian → END     │  │
│             │    │  └─────────────────────────────────────────────────────────┘  │
│             │    │  BackgroundTasks: mastery_node → cert_node                    │
│             │    │  LLMService: OpenRouter → Fallback Chain → Ollama            │
│             │    │  ChromaDB: vault + fingerprint collections                   │
│             │    │  SQLite: mastery_ledger + mastery_certificates               │
└─────────────┘    └──────────────────────────────────────────────────────────────┘
```

### Non-Negotiable Rules
- **ARCH-1**: `socratic_node` (WHAT) and `persona_node` (HOW) always separate
- **ARCH-2**: `mastery_node` and `cert_node` run ONLY as BackgroundTasks
- **ARCH-3**: Pipeline order fixed: `memory → etm → socratic → persona → guardian → END`
- **ARCH-4**: All LLM calls through `LLMService` singleton only
- **ARCH-5**: Every endpoint returns `{"success": bool, "data": any, "error": str | null}`

## Features

### 🎓 40 Pre-Built Mentor Personas
8 categories × 5 mentors each: Cybersecurity, Business, Programming, AI/ML, Finance, Design, Fitness, Psychology. Each with unique voice, teaching style, and embedded knowledge base.

### 🧠 5-Level Socratic Ladder
| Level | Behavior |
|-------|----------|
| 0 | Neutral — provide information |
| 1 | Gentle probing — "What do you think?" |
| 2 | Guided discovery — "What if we changed X?" |
| 3 | Challenge — "Can you explain WHY?" |
| 4 | Corrective — "Let's reconsider..." |

### ⚡ Experience-Triggered Memory (ETM)
VS Code extension sends workspace events (terminal errors, file saves). ETM extracts teaching concepts and connects mentoring to the student's real code.

### 📊 Mastery Tracking
Concepts encountered → attempted → struggling or mastered. Configurable score thresholds. Proof-of-mastery certificates generated when thresholds are met.

### 🛡️ Content Guardian
Regex-based safety filter with educational context awareness. Blocks harmful content while preserving legitimate security education (pentesting, CTF, etc.).

### 🔄 Rate Limit Mitigation
SHA256-keyed response cache (24h TTL) + 3-tier fallback chain: OpenRouter primary → free model fallback → local Ollama.

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- (Optional) Ollama for local LLM fallback

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your OpenRouter API key
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # → http://localhost:5173
```

### Tests
```bash
cd backend
python -m pytest tests/ -v  # → 73 passing
```

## Directory Structure
```
pme/
├── backend/
│   ├── api/           # FastAPI routers (chat, persona, session, mastery, gallery, workspace)
│   ├── core/          # Config, database, utils
│   ├── graph/         # LangGraph pipeline
│   │   ├── nodes/     # memory, etm, socratic, persona, guardian, mastery, cert
│   │   ├── state.py   # PMEState TypedDict
│   │   └── orchestrator.py
│   ├── models/        # SQLAlchemy models + Pydantic schemas
│   ├── rag/           # vault.py, fingerprint.py, retriever.py
│   ├── services/      # llm_service, persona_service, session_service, mastery_service
│   ├── data/mentors/  # 40 mentor profiles (8 categories × 5)
│   └── tests/         # 73 tests
├── frontend/
│   ├── src/
│   │   ├── api/       # Axios client
│   │   ├── components/ # React components (gallery, chat, layout, session, mastery)
│   │   ├── hooks/     # useChat, useMastery, useSession
│   │   ├── store/     # Zustand stores
│   │   ├── styles/    # globals.css design system
│   │   └── pages/     # SessionPage, DashboardPage, MentorsPage, SettingsPage
│   └── package.json
└── vscode-extension/  # VS Code extension for workspace events
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | (required) |
| `PERSONA_MODEL` | Primary LLM for mentor voice | `nvidia/llama-3.3-nemotron-super-49b-v1:free` |
| `REASONING_MODEL` | LLM for Socratic assessment | `nvidia/llama-3.3-nemotron-super-49b-v1:free` |
| `FALLBACK_MODEL_1` | First fallback model | `meta-llama/llama-3.3-70b-instruct:free` |
| `FALLBACK_MODEL_2` | Second fallback model | `mistralai/mistral-7b-instruct:free` |
| `OLLAMA_BASE_URL` | Local Ollama URL | `http://localhost:11434` |
| `DEVIATION_THRESHOLD` | Score for misconception detection | `0.65` |
| `MASTERY_CERT_THRESHOLD` | Score needed for certification | `0.8` |

## License

MIT
