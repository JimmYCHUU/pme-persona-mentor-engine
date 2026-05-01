# PME Project Intelligence
# This file is read automatically by AI coding agents at session start.

## Project
Persona Mentor Engine — local-first AI mentor workspace.
SRS: docs/PME_SRS_Final.docx
SDD: docs/PME_SDD_Final.docx

## Architecture Rules — NON-NEGOTIABLE
- socratic_node + persona_node: ALWAYS separate LangGraph nodes
- mastery_node + cert_node: FastAPI BackgroundTasks ONLY. Never in graph.
- Graph order: memory → etm → socratic → persona → guardian → END
- All LLM calls: OllamaService only. No direct httpx to Ollama.
- All FastAPI endpoints: return {success, data, error} envelope.
- ChromaDB: vault_{persona_id} and fingerprint_{persona_id} namespacing.
- Zero external inference APIs. Ollama local only.

## Coding Standards
- TDD: test before code for ALL backend modules
- DRY: shared Python logic → core/utils.py
- YAGNI: only build what SRS REQ/NFR explicitly requires
- Type hints: ALL Python functions require complete type annotations
- Docstrings: all public functions and classes require docstrings
- Async: all FastAPI endpoints and LangGraph nodes must be async

## Memory Constraints (8 GB RAM machine)
- Model: llama3.2:3b only
- Whisper: base or small only
- DistilBERT guardian: lazy-loaded only (not at import time)
- ChromaDB: persistent local client only (not in-memory)

## Context7 — Required Before Every Library
Resolve each library in Context7 before implementing files that import it.
See SDD Section 0 for the full resolution table.
