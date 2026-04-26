"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import chat, ingest, mastery, persona, session, workspace
from core.config import settings
from core.database import init_db


logging.basicConfig(level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""

    await init_db()
    yield


app = FastAPI(title="PME API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(persona.router, prefix="/persona", tags=["persona"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
app.include_router(mastery.router, prefix="/mastery", tags=["mastery"])


@app.get("/health")
async def health_check() -> dict:
    """Health endpoint reporting Ollama availability."""

    from services.ollama_service import ollama_service

    online = await ollama_service.check_health()
    return {"success": True, "data": {"ollama_online": online}, "error": None}
