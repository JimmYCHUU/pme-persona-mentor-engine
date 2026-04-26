"""Background certificate generation node."""

from __future__ import annotations

import json
import logging
import os
import uuid

from core.config import settings
from core.database import AsyncSessionLocal
from core.utils import ensure_dir, utcnow_iso, write_json
from models.mastery import MasteryCertificate
from services.ollama_service import ollama_service
from services.persona_service import PersonaService


logger = logging.getLogger(__name__)


async def cert_node(persona_id: str, concept_key: str, concept_label: str, ledger_entry) -> None:
    """Generate and store proof-of-mastery certificate artifacts."""

    try:
        profile = await PersonaService.load(persona_id)
        prompt = (
            f"You are {profile.get('name', 'Mentor')}. A student has genuinely mastered '{concept_label}'. "
            f"Reference the evidence: tested in {ledger_entry.encounter_count} encounters and succeeded {ledger_entry.success_count} times. "
            "Write 3-5 sentences in-character that confirm trust for independent work."
        )
        cert_text = await ollama_service.chat(
            model=settings.OLLAMA_MODEL,
            system=f"You are {profile.get('name', 'Mentor')}.",
            message=prompt,
        )

        evidence = {
            "sessions_tested": len(json.loads(ledger_entry.sessions_tested or "[]")),
            "success_count": ledger_entry.success_count,
            "failure_count": ledger_entry.failure_count,
            "mastery_score": ledger_entry.mastery_score,
        }
        cert_id = str(uuid.uuid4())
        issued_at = utcnow_iso()
        cert_dir = ensure_dir(os.path.join(settings.MASTERY_CERT_DIR, persona_id))
        cert_path = cert_dir / f"{concept_key}.json"
        cert_data = {
            "cert_id": cert_id,
            "persona_id": persona_id,
            "concept_key": concept_key,
            "concept_label": concept_label,
            "issued_at": issued_at,
            "mentor_statement": cert_text,
            "evidence_summary": evidence,
        }
        write_json(cert_path, cert_data)

        async with AsyncSessionLocal() as db:
            db.add(
                MasteryCertificate(
                    cert_id=cert_id,
                    persona_id=persona_id,
                    concept_key=concept_key,
                    concept_label=concept_label,
                    issued_at=issued_at,
                    mentor_statement=cert_text,
                    evidence_summary=json.dumps(evidence),
                    cert_json_path=str(cert_path),
                    delivered=0,
                )
            )
            await db.commit()
    except Exception as exc:
        logger.error("cert_node failed: %s", exc, exc_info=True)
