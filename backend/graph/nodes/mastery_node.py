"""Mastery node — runs as BackgroundTask only (ARCH-2). Never in the graph.

Extracts concepts from the conversation and records mastery events.
Uses REASONING_MODEL to identify concepts discussed in the exchange.
"""
import json
import logging
from graph.state import PMEState
from services.llm_service import llm_service
from services.mastery_service import MasteryService

logger = logging.getLogger(__name__)

MASTERY_SYSTEM_PROMPT = """You are a concept extraction engine. Analyze the mentor-student exchange and identify teaching concepts that were discussed.

Return ONLY a valid JSON object with this key:
- "concepts": array of objects, each with:
  - "key": snake_case concept identifier (e.g., "recursion", "null_safety", "async_await")
  - "label": human-readable label (e.g., "Recursion", "Null Safety")
  - "outcome": either "success" (student demonstrated understanding) or "failure" (student showed misconception or didn't understand)

If no clear teaching concepts were discussed, return: {"concepts": []}

Example:
{"concepts": [{"key": "recursion", "label": "Recursion", "outcome": "success"}]}"""


async def mastery_node(state: PMEState) -> dict:
    """Extract concepts from conversation and record mastery events.

    Called as a BackgroundTask after response delivery (ARCH-2).
    Uses deviation_score to influence outcome assessment.
    """
    final_response = state.get("final_response", "")
    if not final_response or len(final_response) < 20:
        return {"mastery_event": None}

    user_message = state.get("user_message", "")
    deviation = state.get("deviation_score", 0.0)

    analysis_prompt = f"""Student's message: {user_message}

Mentor's response: {final_response}

Deviation score: {deviation} (0=correct understanding, 1=complete misconception)

Extract the teaching concepts from this exchange."""

    try:
        response = await llm_service.chat(
            message=analysis_prompt,
            system=MASTERY_SYSTEM_PROMPT,
            use_reasoning=True,
        )

        parsed = _parse_concepts(response)
        concepts = parsed.get("concepts", [])

        if not concepts:
            return {"mastery_event": None}

        # Override outcomes based on deviation score
        if deviation >= 0.65:  # settings.DEVIATION_THRESHOLD
            for c in concepts:
                c["outcome"] = "failure"

        # Record mastery events
        svc = MasteryService()
        persona_id = state.get("persona_id", "")

        for concept in concepts:
            try:
                await svc.record_encounter(
                    persona_id=persona_id,
                    concept_key=concept["key"],
                    concept_label=concept["label"],
                )
                if concept["outcome"] == "success":
                    await svc.record_success(persona_id, concept["key"])
                elif concept["outcome"] == "failure":
                    await svc.record_failure(persona_id, concept["key"])
            except Exception as e:
                logger.warning(f"Failed to record mastery for {concept['key']}: {e}")

        return {
            "mastery_event": {
                "persona_id": persona_id,
                "concepts": concepts,
            }
        }

    except Exception as e:
        logger.warning(f"Mastery concept extraction failed: {e}")
        return {"mastery_event": None}


def _parse_concepts(response: str) -> dict:
    """Parse the LLM's JSON concept response."""
    try:
        text = response.strip()
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    text = part
                    break

        data = json.loads(text)
        concepts = data.get("concepts", [])
        # Validate each concept
        valid = []
        for c in concepts:
            if isinstance(c, dict) and "key" in c:
                valid.append({
                    "key": str(c["key"]),
                    "label": str(c.get("label", c["key"])),
                    "outcome": str(c.get("outcome", "encounter")),
                })
        return {"concepts": valid}

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"Failed to parse mastery concepts: {e}")
        return {"concepts": []}


async def process_mastery_event(event: dict) -> None:
    """Process a mastery event as a BackgroundTask.

    Called from chat.py and workspace.py after response delivery.
    Records encounters, successes, and failures via MasteryService.
    """
    if not event:
        return

    svc = MasteryService()
    try:
        await svc.record_event(event)
    except Exception as e:
        logger.warning(f"Background mastery event processing failed: {e}")

