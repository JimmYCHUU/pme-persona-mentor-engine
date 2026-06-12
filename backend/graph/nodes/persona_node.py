"""Persona node — generates the mentor's response using their voice (ARCH-1).

This node handles HOW to say it. The Socratic node determined WHAT to say.
All LLM calls go through LLMService (ARCH-4).

Phase 2: Integrates Socratic level, vault citations, and ETM context
into the LLM prompt to produce contextually-aware responses.

Enhanced: Enforces persona expertise boundaries. When a question is outside
the mentor's domain, the mentor responds vaguely in-character and suggests
a better-suited mentor from the PME gallery.
"""
import logging
from graph.state import PMEState
from services.llm_service import llm_service
from services.persona_service import PersonaService

logger = logging.getLogger(__name__)

# Socratic level instructions for the persona
SOCRATIC_INSTRUCTIONS = {
    0: "",  # Neutral — no special instruction
    1: "\n\n[SOCRATIC L1] Gently probe the student's understanding. Ask what they think happens, without giving the answer directly.",
    2: "\n\n[SOCRATIC L2] Guide the student toward discovery. Ask 'what if' questions. Help them find the gap themselves.",
    3: "\n\n[SOCRATIC L3] Challenge the student's assumptions directly. Ask them to explain WHY their approach works. Push for deeper understanding.",
    4: "\n\n[SOCRATIC L4] The student has a misconception. Correct it clearly but kindly. Explain what is actually true and why their understanding was wrong.",
}

# Loaded once per invocation — list of all available mentors for suggestions
_mentor_cache: list[dict] | None = None


async def _get_available_mentors(current_persona_id: str) -> list[dict]:
    """Load all activated personas except the current one for cross-referral."""
    global _mentor_cache
    if _mentor_cache is None:
        svc = PersonaService()
        all_personas = await svc.list_personas()
        _mentor_cache = []
        for p in all_personas:
            _mentor_cache.append({
                "id": p.get("id", ""),
                "name": p.get("name", ""),
                "field": p.get("profile", {}).get("field", "general"),
                "sub_speciality": p.get("profile", {}).get("sub_speciality", ""),
            })

    return [m for m in _mentor_cache if m["id"] != current_persona_id]


def _build_mentor_directory(mentors: list[dict]) -> str:
    """Build a formatted string describing available mentors for cross-referral."""
    if not mentors:
        return ""
    lines = []
    for m in mentors:
        lines.append(f"  - {m['name']} ({m['field']}: {m['sub_speciality']})")
    return "\n".join(lines)


def _build_boundary_instruction(persona: dict, available_mentors: list[dict]) -> str:
    """Build the expertise boundary enforcement instruction.

    This is the key piece that makes each mentor respond differently
    based on their actual expertise area.
    """
    profile = persona.get("profile", {})
    field = profile.get("field", "general")
    sub_speciality = profile.get("sub_speciality", "")
    best_for = profile.get("best_for", [])

    mentor_dir = _build_mentor_directory(available_mentors)

    instruction = f"""

━━ CRITICAL: EXPERTISE BOUNDARY RULES ━━
Your domain of expertise is: {field}
Your specific specialties are: {sub_speciality}
Topics you are best at: {', '.join(best_for) if best_for else 'general topics in your field'}

You MUST follow these rules strictly:

1. IN-DOMAIN QUESTIONS: If the question falls within your field ({field}) or
   your specialties, answer with full depth, passion and authority in your
   authentic voice. Use your teaching style, verbal patterns, and references.

2. OUT-OF-DOMAIN QUESTIONS: If the question is clearly outside your expertise
   (e.g. you are a design mentor asked about networking, or a cybersecurity
   mentor asked about stock trading):
   - Acknowledge the question briefly and honestly in YOUR voice/personality
   - Give only a surface-level, casual/conversational answer (like a smart
     person with general knowledge would — NOT an expert answer)
   - Clearly state this is not your area of expertise
   - Suggest the student talk to a more qualified mentor"""

    if mentor_dir:
        instruction += f"""
   - Recommend the best-suited mentor from this list:
{mentor_dir}

   Example: "That's more of a networking question — I'd suggest talking to
   NetworkChuck here in PME, he's the networking guru."
"""
    else:
        instruction += """
   - Suggest browsing the PME Mentor Gallery for a specialist in that area.
"""

    instruction += """
3. ADJACENT QUESTIONS: If the question is slightly related but not your core
   specialty, answer with what you know from your perspective, but be upfront
   that you're not the best source. You may still offer your unique angle.

4. ALWAYS stay in character. Your personality, tone, verbal tics, and teaching
   style should come through in EVERY response — whether in-domain or not.
   A cybersecurity mentor should sound like THEMSELVES even when deflecting
   a cooking question.
"""
    return instruction


async def persona_node(state: PMEState) -> dict:
    """Generate the mentor's styled response.

    Uses the persona's system prompt + expertise boundaries + Socratic context
    + vault citations + ETM context to produce a response in the mentor's
    authentic voice while staying within expertise boundaries.
    """
    # Invalidate mentor cache each request so new activations show up
    global _mentor_cache
    _mentor_cache = None

    persona_svc = PersonaService()
    persona = await persona_svc.get_persona(state["persona_id"])

    if not persona:
        return {
            "raw_llm_response": "Mentor not found. Please select a mentor first.",
            "styled_response": "Mentor not found. Please select a mentor first.",
            "final_response": "Mentor not found. Please select a mentor first.",
        }

    system_prompt = persona.get("system_prompt", "You are a helpful mentor.")

    # Add expertise boundary enforcement
    available_mentors = await _get_available_mentors(state["persona_id"])
    boundary_instruction = _build_boundary_instruction(persona, available_mentors)
    system_prompt += boundary_instruction

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
