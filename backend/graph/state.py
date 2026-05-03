"""PMEState — the shared LangGraph state that flows through every node."""

from typing import TypedDict, Optional, Literal


class PMEState(TypedDict):
    """Single state object flowing through all LangGraph nodes."""

    # ── Identity ──────────────────────────────────────────
    session_id: str
    persona_id: str

    # ── Input ─────────────────────────────────────────────
    user_message: str
    workspace_event: Optional[dict]

    # ── memory_node outputs ────────────────────────────────
    session_snapshot: Optional[dict]
    is_returning_user: bool
    mastery_summary: Optional[dict]

    # ── etm_node outputs ───────────────────────────────────
    etm_context: Optional[str]
    etm_matched: bool

    # ── socratic_node outputs ──────────────────────────────
    deviation_score: float
    socratic_level: int  # 0-4
    vault_citation: Optional[str]
    mastery_event: Optional[dict]

    # ── persona_node outputs ───────────────────────────────
    raw_llm_response: str
    styled_response: str

    # ── guardian_node outputs ──────────────────────────────
    guardian_flagged: bool
    final_response: str

    # ── Mode ──────────────────────────────────────────────
    mode: Literal['deep_dive', 'friend_mode']
