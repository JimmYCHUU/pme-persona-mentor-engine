"""
Full cert_node — generates Proof of Mastery certificates.
Runs as a FastAPI BackgroundTask, NOT in the LangGraph pipeline.
"""

import json
import os
import logging
from core.config import settings
from core.database import AsyncSessionLocal
from core.utils import generate_id, now_iso
from models.mastery import MasteryCertificate, MasteryLedger
from services.ollama_service import ollama_service
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def generate_certificate(persona_id: str, concept_key: str) -> dict | None:
    """
    Generate a Proof of Mastery certificate for a concept.
    Called when mastery_node detects should_certify=True.

    Returns the cert data dict, or None on failure.
    """
    async with AsyncSessionLocal() as db:
        # Get mastery ledger entry
        result = await db.execute(
            select(MasteryLedger).where(
                MasteryLedger.persona_id == persona_id,
                MasteryLedger.concept_key == concept_key,
            )
        )
        entry = result.scalar_one_or_none()
        if not entry:
            logger.warning(f'cert_node: no ledger entry for {concept_key}')
            return None

        # Check not already certified
        cert_check = await db.execute(
            select(MasteryCertificate).where(
                MasteryCertificate.persona_id == persona_id,
                MasteryCertificate.concept_key == concept_key,
            )
        )
        if cert_check.scalar_one_or_none():
            logger.info(f'cert_node: {concept_key} already certified')
            return None

    # Generate mentor statement via LLM
    mentor_statement = await _generate_mentor_statement(
        persona_id, concept_key, entry
    )

    evidence = {
        'sessions_tested': len(json.loads(entry.sessions_tested or '[]')),
        'success_count': entry.success_count,
        'failure_count': entry.failure_count,
        'mastery_score': entry.mastery_score,
    }

    cert_id = generate_id()
    issued_at = now_iso()

    # Save to SQLite
    async with AsyncSessionLocal() as db:
        cert = MasteryCertificate(
            cert_id=cert_id,
            persona_id=persona_id,
            concept_key=concept_key,
            concept_label=entry.concept_label,
            issued_at=issued_at,
            mentor_statement=mentor_statement,
            evidence_summary=json.dumps(evidence),
            cert_json_path='',
            delivered=0,
        )
        db.add(cert)
        await db.commit()

    # Save as JSON file for export
    cert_data = {
        'cert_id': cert_id,
        'persona_id': persona_id,
        'concept_key': concept_key,
        'concept_label': entry.concept_label,
        'issued_at': issued_at,
        'mentor_statement': mentor_statement,
        'evidence_summary': evidence,
    }

    cert_dir = os.path.join(settings.MASTERY_CERT_DIR, persona_id)
    os.makedirs(cert_dir, exist_ok=True)
    cert_json_path = os.path.join(cert_dir, f'{cert_id}.json')
    with open(cert_json_path, 'w') as f:
        json.dump(cert_data, f, indent=2)

    # Update the cert_json_path
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MasteryCertificate).where(
                MasteryCertificate.cert_id == cert_id,
            )
        )
        c = result.scalar_one()
        c.cert_json_path = cert_json_path
        await db.commit()

    logger.info(f'cert_node: certificate issued for {concept_key} ({cert_id})')
    return cert_data


async def _generate_mentor_statement(persona_id: str, concept_key: str,
                                      entry: MasteryLedger) -> str:
    """Generate a personalized mentor statement for the certificate."""
    from services.persona_service import PersonaService

    profile = await PersonaService.load(persona_id)
    mentor_name = profile['name'] if profile else 'Your Mentor'

    prompt = (
        f'You are {mentor_name}. '
        f'Write a 2-3 sentence "Proof of Mastery" statement for your student '
        f'who has mastered "{concept_key.replace("_", " ")}". '
        f'They succeeded {entry.success_count} times across '
        f'{len(json.loads(entry.sessions_tested or "[]"))} sessions. '
        f'Speak in your authentic voice. Be proud but keep it real. '
        f'Do not use phrases like "I am pleased to certify".'
    )

    try:
        statement = await ollama_service.chat(
            model=settings.OLLAMA_MODEL,
            system=f'You are {mentor_name}. Write a brief mastery certification statement.',
            message=prompt,
        )
        return statement.strip()
    except Exception as e:
        logger.error(f'cert_node: LLM statement generation failed: {e}')
        return (f'{mentor_name} has determined that you have demonstrated '
                f'mastery of {concept_key.replace("_", " ")}.')
