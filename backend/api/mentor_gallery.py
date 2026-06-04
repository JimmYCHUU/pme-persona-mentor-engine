"""
Pre-built mentor gallery API.
Serves mentor profiles, categories, and handles mentor activation.
"""
import json
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks

router = APIRouter()
MENTOR_BASE = Path("./data/mentors")

CATEGORY_META = {
    "cybersecurity": {"label": "Cybersecurity",      "emoji": "🛡️"},
    "business":      {"label": "Business",           "emoji": "💼"},
    "programming":   {"label": "Programming",        "emoji": "💻"},
    "ai_ml":         {"label": "AI & Machine Learning","emoji": "🤖"},
    "finance":       {"label": "Finance",            "emoji": "📈"},
    "design":        {"label": "Design",             "emoji": "🎨"},
    "fitness":       {"label": "Fitness",            "emoji": "🏋️"},
    "psychology":    {"label": "Psychology",         "emoji": "🧠"},
}


@router.get("/categories")
async def get_categories():
    categories = []
    for cat_id, meta in CATEGORY_META.items():
        cat_dir = MENTOR_BASE / cat_id
        count = len([d for d in cat_dir.iterdir() if d.is_dir()]) if cat_dir.exists() else 0
        categories.append({
            "id": cat_id,
            "label": meta["label"],
            "emoji": meta["emoji"],
            "mentor_count": count,
        })
    return {"success": True, "data": categories, "error": None}


@router.get("/{category}")
async def get_category_mentors(category: str):
    cat_dir = MENTOR_BASE / category
    if not cat_dir.exists():
        return {"success": False, "data": None, "error": "Category not found"}
    mentors = []
    for mentor_dir in sorted(cat_dir.iterdir()):
        profile_path = mentor_dir / "profile.json"
        if profile_path.exists():
            mentors.append(json.loads(profile_path.read_text()))
    return {"success": True, "data": mentors, "error": None}


@router.post("/{category}/{mentor_id}/activate")
async def activate_mentor(
    category: str,
    mentor_id: str,
    background_tasks: BackgroundTasks,
):
    mentor_dir = MENTOR_BASE / category / mentor_id
    if not mentor_dir.exists():
        return {"success": False, "data": None, "error": "Mentor not found"}

    profile      = json.loads((mentor_dir / "profile.json").read_text())
    system_prompt = (mentor_dir / "system_prompt.txt").read_text()

    from services.persona_service import PersonaService
    persona = await PersonaService.create_prebuilt(
        mentor_id=mentor_id,
        profile=profile,
        system_prompt=system_prompt,
    )

    knowledge_dir = mentor_dir / "knowledge"
    if knowledge_dir.exists():
        background_tasks.add_task(_embed_knowledge, mentor_id, knowledge_dir)

    return {
        "success": True,
        "data": {
            "persona_id": persona["id"],
            "mentor_name": profile["display_name"],
            "status": "activated",
        },
        "error": None,
    }


async def _embed_knowledge(mentor_id: str, knowledge_dir: Path) -> None:
    """Embed mentor knowledge files into ChromaDB in background."""
    import chromadb
    from core.config import settings
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    try:
        collection = client.get_or_create_collection(f"vault_{mentor_id}")
    except Exception:
        return

    for json_file in knowledge_dir.glob("*.json"):
        try:
            data  = json.loads(json_file.read_text())
            items = (
                data.get("quotes", []) +
                data.get("explanations", []) +
                data.get("methodology", [])
            )
            for i, item in enumerate(items):
                text   = item.get("quote") or item.get("explanation") or str(item)
                doc_id = f"{mentor_id}_{json_file.stem}_{i}"
                existing = collection.get(ids=[doc_id])
                if existing["ids"]:
                    continue
                collection.add(
                    documents=[text],
                    ids=[doc_id],
                    metadatas=[{
                        "mentor_id": mentor_id,
                        "topic": item.get("topic", "general"),
                        "source": json_file.name,
                        "why": item.get("why_they_said_it", ""),
                        "authority": 100,
                    }],
                )
        except Exception:
            continue
