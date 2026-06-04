"""PMEState — the single state dict flowing through the LangGraph pipeline."""
from typing import TypedDict, Optional, Literal


class PMEState(TypedDict):
    session_id:        str
    persona_id:        str
    user_message:      str
    workspace_event:   Optional[dict]
    session_snapshot:  Optional[dict]
    is_returning_user: bool
    mastery_summary:   Optional[dict]
    etm_context:       Optional[str]
    etm_matched:       bool
    deviation_score:   float
    socratic_level:    int          # 0–4
    vault_citation:    Optional[str]
    mastery_event:     Optional[dict]
    raw_llm_response:  str
    styled_response:   str
    guardian_flagged:  bool
    final_response:    str
    mode:              Literal["deep_dive", "friend_mode"]
