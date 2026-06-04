"""FastAPI entry point for the PME backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import init_db
from core.config import settings
from api import chat, persona, session, ingest, workspace, mastery, mentor_gallery
import logging

logging.basicConfig(level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    # Import all models so Base.metadata knows about them
    import models.session  # noqa: F401
    import models.mastery  # noqa: F401
    await init_db()
    yield


app = FastAPI(title='PME API', version='1.0.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(chat.router, prefix='/chat', tags=['chat'])
app.include_router(persona.router, prefix='/persona', tags=['persona'])
app.include_router(session.router, prefix='/session', tags=['session'])
app.include_router(ingest.router, prefix='/ingest', tags=['ingest'])
app.include_router(workspace.router, prefix='/workspace', tags=['workspace'])
app.include_router(mastery.router, prefix='/mastery', tags=['mastery'])
app.include_router(mentor_gallery.router, prefix='/mentors', tags=['mentors'])


@app.get('/health')
async def health_check():
    """Returns LLM provider status. Used by StatusBar."""
    from services.llm_service import llm_service
    from core.config import settings
    status = await llm_service.check_health()
    return {
        'success': True,
        'data': {
            'openrouter_online': status['openrouter'],
            'ollama_online': status['ollama'],
            'primary_provider': status['primary'],
            'persona_model': settings.PERSONA_MODEL,
            'reasoning_model': settings.REASONING_MODEL,
        },
        'error': None,
    }
