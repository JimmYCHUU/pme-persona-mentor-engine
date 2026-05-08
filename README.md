# Persona Mentor Engine (PME)

> *Train with the version of your mentor who already learned from all their mistakes.*

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-FF6B35?logo=langchain&logoColor=white)](https://langchain.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Free%20Tier-6B46C1?logo=openai&logoColor=white)](https://openrouter.ai)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

---

## What Is PME?

PME is a **private, local-first AI workspace** that clones the intellectual DNA of any real-world expert and places them beside you as you learn.

It is not a chatbot. It is not a course platform. It is a **Digital Twin Mentorship environment** — a persistent workspace where your chosen mentor watches you work, challenges you Socratically, tracks your mastery across sessions, and issues in-character certifications when you genuinely understand something.

**The Ethical Time Machine advantage:** Every competitor gives you a frozen snapshot of the mentor at their most famous moment. PME gives you the version that already learned from their own mistakes — with all the original wisdom *plus* the knowledge of what they got wrong, what has since changed, and what they'd tell their past self.

---

## ✨ Core Features

### 🧠 Bimodal Intelligence
The system separates **SOUL** (how the mentor speaks) from **BRAIN** (what they know). Public fingerprints from social media and YouTube build the persona. Your private vault — paid courses, PDFs, personal notes — is the highest-authority knowledge source. Vault data always overrides public data.

### ⚡ Socratic Interruption Engine
The mentor never just gives you the answer. It monitors your workspace via a VS Code extension and escalates through four intervention levels:

| Level | Name | Behaviour |
|-------|------|-----------|
| 0 | Listening | Silent observation |
| 1 | Nudge | One probing question, no answer |
| 2 | Hint | Points to a specific vault source |
| 3 | Critique | Explains the consequence of your approach |
| 4 | Reveal | Direct answer — only after 3 failures |

### 📈 Cross-Session Mastery Tracking
Every exchange is tracked. Each concept moves through four states:
`encountered → attempted → struggling → mastered`. The Socratic engine adapts its starting level based on your history with each concept.

### 🏆 Proof of Mastery Certificates
When you genuinely master a concept across multiple sessions, the mentor issues an in-character certification — not a quiz score, but the mentor saying in their own voice: *"I would trust you to do this unsupervised."*

### 🕰️ The Ethical Time Machine
During ingestion, the system extracts evolution events — paradigm shifts, deprecated practices, statements of regret. The mentor proactively frames these as their own growth: *"I used to say X. I was wrong. Here is why."* No frozen snapshots. No outdated advice.

### 🤖 Dual-Model Routing
Two LLM models, two jobs. The persona model (DeepSeek V3 / Nemotron) handles all mentor voice and style transfers. The reasoning model (DeepSeek R1 / Nemotron) handles Socratic scoring and concept extraction. Runs via OpenRouter with local Ollama fallback.

---

## 🏗️ Architecture

```
pme/
├── backend/                    ← FastAPI + Python 3.12
│   ├── graph/
│   │   ├── orchestrator.py     ← LangGraph pipeline
│   │   └── nodes/
│   │       ├── memory_node.py  ← Session + mastery loading
│   │       ├── etm_node.py     ← Ethical Time Machine
│   │       ├── socratic_node.py← Deviation detection + ladder
│   │       ├── persona_node.py ← Style-transfer LLM call
│   │       └── guardian_node.py← Shadow safety classifier
│   ├── rag/
│   │   ├── vault.py            ← Private vault ingestion
│   │   ├── fingerprint.py      ← Public fingerprint scraping
│   │   └── retriever.py        ← Dual-collection RAG retriever
│   ├── services/
│   │   ├── llm_service.py      ← OpenRouter + Ollama fallback
│   │   ├── mastery_service.py  ← Mastery scoring engine
│   │   └── session_service.py  ← Session snapshot manager
│   └── data/
│       ├── chroma/             ← ChromaDB vector store (gitignored)
│       ├── sessions/           ← Session JSON snapshots (gitignored)
│       └── personas/           ← Persona profiles + evolution_db (gitignored)
│
├── frontend/                   ← React 18 + TypeScript + Vite
│   └── src/
│       ├── components/
│       │   ├── session/        ← OpeningRitual, ResumeModal
│       │   ├── chat/           ← ChatPane, Message, SocraticBadge
│       │   ├── mastery/        ← MasteryMap, CertModal
│       │   └── persona/        ← PersonaBuilder wizard
│       └── store/              ← Zustand state management
│
├── vscode-extension/           ← Workspace monitor
└── scripts/                    ← setup.sh, start.sh, start-docker.sh
```

**Pipeline (every chat message):**
```
memory → etm → socratic → persona → guardian → response
                   ↓
         mastery_node (BackgroundTask)
                   ↓
          cert_node (if mastery conditions met)
```

---

## 🐳 Quick Start (Docker)

```bash
# 1. Clone
git clone https://github.com/JimmYCHUU/pme-personal-mentorship-engine.git
cd pme-personal-mentorship-engine/pme

# 2. Add your OpenRouter key (get one free at openrouter.ai/settings/keys)
cp backend/.env.example backend/.env
# Edit backend/.env and set OPENROUTER_API_KEY=sk-or-v1-...

# 3. Start everything
./scripts/start-docker.sh
```

Open **http://localhost:5173** — the opening ritual will guide you from there.

---

## 🛠️ Manual Setup

```bash
# One-time setup (installs Python venv, npm deps, pulls Ollama models)
./scripts/setup.sh

# Start backend + frontend
./scripts/start.sh
```

> **Requires**: Python 3.11+, Node 18+, and either [Ollama](https://ollama.com) (for local inference fallback) or an [OpenRouter](https://openrouter.ai) API key.

---

## 🔌 Service Map

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React workspace UI |
| Backend API | http://localhost:8000 | FastAPI REST |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health | http://localhost:8000/health | LLM provider status |

---

## ⚙️ Environment Variables

```bash
cp backend/.env.example backend/.env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | *(required)* | Your OpenRouter key |
| `PERSONA_MODEL` | `nvidia/nemotron-3-super-120b-a12b:free` | Mentor voice model |
| `REASONING_MODEL` | `nvidia/nemotron-3-super-120b-a12b:free` | Socratic reasoning model |
| `OLLAMA_FALLBACK_MODEL` | `llama3.2:3b` | Local fallback if OpenRouter is down |
| `DEVIATION_THRESHOLD` | `0.65` | Socratic trigger sensitivity (0–1) |
| `MASTERY_CERT_THRESHOLD` | `0.8` | Score required for certification |
| `MASTERY_CERT_MIN_SESSIONS` | `3` | Sessions required before cert eligible |
| `IDLE_TRIGGER_SECONDS` | `300` | Idle time before mentor checks in |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph 0.1+ |
| RAG Pipeline | LlamaIndex 0.10+ |
| LLM Provider | OpenRouter (DeepSeek V3 / Nemotron) |
| LLM Fallback | Ollama (local, llama3.2:3b) |
| Vector DB | ChromaDB (local) |
| Backend | FastAPI + Python 3.12 |
| Transcription | OpenAI Whisper (local) |
| Scraping | Playwright + yt-dlp |
| Safety | DistilBERT (local, lazy-loaded) |
| Frontend | React 18 + TypeScript + Vite |
| State | Zustand |
| Database | SQLite + aiosqlite |
| Containers | Docker Compose |

---

## About

PME is a private, local-first Digital Twin Mentorship workspace.
All rights reserved.

© 2026 — Built with the Persona Mentor Engine
