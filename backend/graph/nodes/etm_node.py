"""ETM node — Experience-Triggered Memory.

Matches workspace events (terminal errors, file saves, etc.) to teaching
concepts. When a match is found, provides contextual information to help
the Socratic and Persona nodes tailor their response.

Uses REASONING_MODEL to extract concepts from workspace events.
"""
import json
import logging
from graph.state import PMEState
from services.llm_service import llm_service

logger = logging.getLogger(__name__)

ETM_SYSTEM_PROMPT = """You are an Experience-Triggered Memory (ETM) engine. Analyze the workspace event (error message, code snippet, etc.) and identify the core programming/technical concept the student is encountering.

Return ONLY a valid JSON object with these keys:
- "concept": a short snake_case concept key (e.g., "null_safety", "async_await", "recursion_base_case")
- "context": a 1-2 sentence explanation of what the event reveals about the student's current challenge
- "matched": boolean, true if a clear teaching concept was identified

Example response:
{"concept": "null_safety", "context": "The error shows accessing a property on undefined, indicating the data hasn't loaded when the component renders.", "matched": true}"""


async def etm_node(state: PMEState) -> dict:
    """Experience-Triggered Memory — matches workspace events to concepts.

    If no workspace event, passes through without LLM call.
    If event present, uses REASONING_MODEL to extract concept.
    """
    # No workspace event → pass-through
    if not state.get("workspace_event"):
        return {
            "etm_context": None,
            "etm_matched": False,
        }

    event = state["workspace_event"]

    # Build event description
    event_type = event.get("type", "unknown")
    content = event.get("content", "")
    file_name = event.get("file", "unknown")
    language = event.get("language", "unknown")

    analysis_prompt = f"""Workspace event:
Type: {event_type}
File: {file_name}
Language: {language}
Content:
{content}

Student's message about this: {state['user_message']}

Identify the core concept and provide context."""

    try:
        response = await llm_service.chat(
            message=analysis_prompt,
            system=ETM_SYSTEM_PROMPT,
            use_reasoning=True,
        )

        parsed = _parse_etm_response(response)
        if parsed["matched"]:
            # Build a contextual string combining concept and explanation
            context = f"[{parsed['concept']}] {parsed['context']}"
            return {
                "etm_context": context,
                "etm_matched": True,
            }
        else:
            return {
                "etm_context": None,
                "etm_matched": False,
            }

    except Exception as e:
        logger.warning(f"ETM analysis failed: {e}")
        return {
            "etm_context": None,
            "etm_matched": False,
        }


def _parse_etm_response(response: str) -> dict:
    """Parse the LLM's JSON ETM response, with fallback defaults."""
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
        return {
            "concept": str(data.get("concept", "unknown")),
            "context": str(data.get("context", "")),
            "matched": bool(data.get("matched", False)),
        }

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"Failed to parse ETM response: {e}")
        return {"concept": "unknown", "context": "", "matched": False}
