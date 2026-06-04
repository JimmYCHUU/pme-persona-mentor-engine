"""Persona node — generates the mentor's response using their voice (ARCH-1).

This node handles HOW to say it. The Socratic node determined WHAT to say.
All LLM calls go through LLMService (ARCH-4).

Phase 2: Integrates Socratic level, vault citations, and ETM context
into the LLM prompt to produce contextually-aware responses.
"""
from graph.state import PMEState
from services.llm_service import llm_service
from services.persona_service import PersonaService

# Socratic level instructions for the persona
SOCRATIC_INSTRUCTIONS = {
    0: "",  # Neutral — no special instruction
    1: "\n\n[SOCRATIC L1] Gently probe the student's understanding. Ask what they think happens, without giving the answer directly.",
    2: "\n\n[SOCRATIC L2] Guide the student toward discovery. Ask 'what if' questions. Help them find the gap themselves.",
    3: "\n\n[SOCRATIC L3] Challenge the student's assumptions directly. Ask them to explain WHY their approach works. Push for deeper understanding.",
    4: "\n\n[SOCRATIC L4] The student has a misconception. Correct it clearly but kindly. Explain what is actually true and why their understanding was wrong.",
}


async def persona_node(state: PMEState) -> dict:
    """Generate the mentor's styled response.

    Uses the persona's system prompt + Socratic context + vault citations
    + ETM context to produce a response in the mentor's authentic voice.
    """
    persona_svc = PersonaService()
    persona = await persona_svc.get_persona(state["persona_id"])

    if not persona:
        return {
            "raw_llm_response": "Mentor not found. Please select a mentor first.",
            "styled_response": "Mentor not found. Please select a mentor first.",
            "final_response": "Mentor not found. Please select a mentor first.",
        }

    system_prompt = persona.get("system_prompt", "You are a helpful mentor.")

    # Add Socratic level instruction
    level = state.get("socratic_level", 0)
    socratic_instruction = SOCRATIC_INSTRUCTIONS.get(level, "")
    if socratic_instruction:
        system_prompt += socratic_instruction

    # Add vault citation context
    vault_citation = state.get("vault_citation")
    if vault_citation:
        system_prompt += f"\n\n[REFERENCE] The student's own materials contain this relevant passage: {vault_citation}\nWeave this reference naturally into your response when appropriate."

    # Add ETM context
    etm_context = state.get("etm_context")
    if etm_context:
        system_prompt += f"\n\n[WORKSPACE CONTEXT] The student is working on something related to: {etm_context}\nConnect your teaching to this specific context."

    # Build history from session snapshot
    history = []
    if state.get("session_snapshot"):
        history = state["session_snapshot"].get("history", [])

    response = await llm_service.chat(
        message=state["user_message"],
        system=system_prompt,
        history=history,
    )

    return {
        "raw_llm_response": response,
        "styled_response": response,
        "final_response": response,
    }
