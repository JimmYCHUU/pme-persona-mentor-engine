"""Socratic node — determines WHAT to say and WHEN (ARCH-1).

Separated from persona_node which handles HOW to say it.
Full 5-level Socratic ladder implementation.

Levels:
  0 — Neutral / informational (friend mode always maps here)
  1 — Gentle probing ("What do you think happens here?")
  2 — Guided discovery ("What if we changed X?")
  3 — Challenge ("Can you explain WHY that works?")
  4 — Corrective ("Let's reconsider this part…")

Uses REASONING_MODEL to assess user's understanding.
Retrieves vault citations for grounding.
"""
import json
import logging
from graph.state import PMEState
from services.llm_service import llm_service
from rag.retriever import retriever

logger = logging.getLogger(__name__)

SOCRATIC_SYSTEM_PROMPT = """You are a Socratic assessment engine. Analyze the student's message and conversation history to determine their understanding level.

Return ONLY a valid JSON object with these keys:
- "level": integer 0-4 representing Socratic intensity
  0 = Student shows good understanding, just provide information
  1 = Student seems unsure, gently probe their understanding
  2 = Student has partial understanding, guide them to discover gaps
  3 = Student has significant gaps, challenge their assumptions
  4 = Student has a clear misconception that needs correction
- "deviation_score": float 0.0-1.0 measuring how far the student's understanding deviates from correct
  0.0 = No deviation, understanding is accurate
  0.5 = Moderate gaps or partial misunderstanding
  1.0 = Completely wrong understanding
- "reasoning": brief explanation of your assessment

Example response:
{"level": 2, "deviation_score": 0.35, "reasoning": "Student understands the basic concept but confuses X with Y"}"""


async def socratic_node(state: PMEState) -> dict:
    """Determine Socratic level (0-4), deviation score, and vault citation.

    In friend_mode, always returns level 0 (no probing).
    Otherwise, uses REASONING_MODEL to assess understanding.
    """
    # Friend mode = no Socratic probing
    if state.get("mode") == "friend_mode":
        citation = await _get_citation(state)
        return {
            "socratic_level": 0,
            "deviation_score": 0.0,
            "vault_citation": citation,
        }

    # Get vault citation for grounding
    citation = await _get_citation(state)

    # Build context from conversation history
    history_context = ""
    if state.get("session_snapshot"):
        history = state["session_snapshot"].get("history", [])
        if history:
            recent = history[-6:]  # Last 3 exchanges
            history_context = "\n".join(
                f"{t['role'].upper()}: {t['content']}" for t in recent
            )

    # ETM context if available
    etm_info = ""
    if state.get("etm_context"):
        etm_info = f"\n\nWorkspace context: {state['etm_context']}"

    assessment_prompt = f"""Conversation history:
{history_context}

Current student message: {state['user_message']}{etm_info}

Assess the student's understanding level and respond with the JSON object."""

    try:
        response = await llm_service.chat(
            message=assessment_prompt,
            system=SOCRATIC_SYSTEM_PROMPT,
            use_reasoning=True,
        )

        parsed = _parse_assessment(response)
        return {
            "socratic_level": parsed["level"],
            "deviation_score": parsed["deviation_score"],
            "vault_citation": citation,
        }

    except Exception as e:
        logger.warning(f"Socratic assessment failed: {e}")
        return {
            "socratic_level": 0,
            "deviation_score": 0.0,
            "vault_citation": citation,
        }


async def _get_citation(state: PMEState) -> str | None:
    """Retrieve vault citation for the user's message."""
    try:
        return await retriever.get_citation(
            state["user_message"], state["persona_id"]
        )
    except Exception as e:
        logger.debug(f"Vault citation retrieval failed: {e}")
        return None


def _parse_assessment(response: str) -> dict:
    """Parse the LLM's JSON assessment, with fallback defaults."""
    try:
        # Try to extract JSON from the response
        # Handle case where LLM wraps JSON in markdown code blocks
        text = response.strip()
        if "```" in text:
            # Extract content between code fences
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    text = part
                    break

        data = json.loads(text)
        level = max(0, min(4, int(data.get("level", 0))))
        deviation = max(0.0, min(1.0, float(data.get("deviation_score", 0.0))))
        return {"level": level, "deviation_score": deviation}

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"Failed to parse Socratic assessment: {e}")
        return {"level": 0, "deviation_score": 0.0}
