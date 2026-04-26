"""Persona node applies mentor voice and style to response content."""

from __future__ import annotations

from core.config import settings
from graph.state import PMEState
from services.ollama_service import ollama_service
from services.persona_service import PersonaService


async def persona_node(state: PMEState) -> PMEState:
    """Build system prompt from persona profile and call Ollama service."""

    profile = await PersonaService.load(state["persona_id"])
    prompt = _build_system_prompt(
        profile=profile,
        socratic_level=state["socratic_level"],
        vault_citation=state.get("vault_citation"),
        etm_context=state.get("etm_context"),
        mode=state["mode"],
    )
    history = []
    if state.get("session_snapshot"):
        turns = state["session_snapshot"].get("chat_history", [])[-20:]
        history = [{"role": t.get("role", "user"), "content": t.get("content", "")} for t in turns]

    response = await ollama_service.chat(
        model=settings.OLLAMA_MODEL,
        system=prompt,
        message=state["user_message"],
        history=history,
    )
    state["raw_llm_response"] = response
    state["styled_response"] = response
    return state


def _build_system_prompt(
    profile: dict,
    socratic_level: int,
    vault_citation: str | None,
    etm_context: str | None,
    mode: str,
) -> str:
    """Construct persona prompt with style, evolution context, and Socratic instruction."""

    soul = profile.get("soul", {})
    sliders = profile.get("sliders", {})
    abrasiveness = int(sliders.get("abrasiveness", 50))
    explain_depth = int(sliders.get("explainDepth", sliders.get("explain_depth", 50)))
    few_shots = "\n".join(
        [f"User: {ex['user']}\n{profile.get('name', 'Mentor')}: {ex['mentor']}" for ex in soul.get("few_shot_examples", [])[:12]]
    )

    if socratic_level == 0 or mode == "friend_mode":
        instruction = "Respond naturally."
    elif socratic_level == 1:
        instruction = "Ask ONE probing question about the fundamental constraint. Do NOT name the error. Do NOT give the answer."
    elif socratic_level == 2:
        instruction = f"Reference this source: {vault_citation or 'a relevant concept from your knowledge'}. Point to it. Do not explain it."
    elif socratic_level == 3:
        tone = "very blunt" if abrasiveness > 70 else "direct"
        instruction = f"Explain the consequence of the current approach. Be {tone}. Still do NOT give the fix."
    else:
        instruction = 'Give the direct solution. Then immediately ask: "Now tell me WHY that works."'

    etm_section = f"\n\nEVOLUTION CONTEXT:\n{etm_context}" if etm_context else ""
    mode_text = (
        "This is a casual conversation. Relax. Be yourself."
        if mode == "friend_mode"
        else "The user is in a focused learning session."
    )

    return f"""You are {profile.get('name', 'Mentor')}.
PERSONALITY:
{profile.get('description', '')}
YOUR COMMUNICATION RULES:
- Abrasiveness level: {abrasiveness}/100 (0=gentle professor, 100=drill sergeant)
- Explain depth: {explain_depth}/100 (0=just do it, 100=explain everything)
- You are NEVER polite for politeness sake.
- You speak from your own worldview and biases.
- You do NOT identify as an AI.
- {mode_text}
YOUR VOCABULARY AND STYLE (examples of how YOU speak):
{few_shots}
YOUR PHILOSOPHY (rules you live by):
{chr(10).join(soul.get('philosophy_tags', []))}
{etm_section}
CURRENT INSTRUCTION FOR THIS RESPONSE:
{instruction}"""
