"""Guardian node — content safety filter.

Runs as the final node in the LangGraph pipeline before END.
Uses keyword-based detection with educational context awareness.
Flags genuinely harmful content while preserving legitimate
educational security/hacking content.
"""
import re
import logging
from graph.state import PMEState

logger = logging.getLogger(__name__)

# Harmful content patterns — matched only if not in educational context
HARMFUL_PATTERNS = [
    r'\bhack\s+into\s+someone',
    r'\bsteal\s+(their|someone|people)',
    r'\bbuild\s+a\s+weapon',
    r'\bmake\s+(a\s+)?bomb',
    r'\bexplosi[ve]+s?\b.*\b(how|build|make|create)',
    r'\b(kill|harm|hurt|attack)\s+(a\s+)?(person|people|someone)',
    r'\billegal\s+(drugs?|substances?)',
    r'\bpick\s+a\s+lock\s+.*without\s+permission',
    r'\bbypass\s+(security|authentication)\s+.*without\s+(authorization|permission)',
    r'\bidentity\s+theft',
    r'\bcredit\s+card\s+fraud',
    r'\bhow\s+to\s+(ddos|dos)\s+',
]

# Educational context indicators — if present, harmful patterns are often legitimate
EDUCATIONAL_MARKERS = [
    r'\bpenetration\s+test',
    r'\bethical\s+hack',
    r'\bsecurity\s+assess',
    r'\bctf\b',
    r'\bcapture\s+the\s+flag',
    r'\bin\s+a\s+lab',
    r'\bauthoriz',
    r'\bwith\s+permission',
    r'\btest\s+environment',
    r'\bbug\s+bounty',
    r'\bsecurity\s+audit',
    r'\bstandard\s+(security|assessment)\s+technique',
]

SAFE_RESPONSE = (
    "I appreciate your curiosity, but I cannot provide guidance on that topic "
    "as it could potentially be harmful. Let me help you with something else "
    "within our learning focus."
)


async def guardian_node(state: PMEState) -> dict:
    """Check response for safety/appropriateness.

    Uses keyword detection with educational context awareness.
    Flags genuinely harmful content, preserves educational security content.
    """
    response = state.get("styled_response", state.get("raw_llm_response", ""))

    if not response:
        return {
            "guardian_flagged": False,
            "final_response": response,
        }

    is_harmful = _check_harmful(response)

    if is_harmful:
        logger.warning("Guardian flagged response as harmful")
        return {
            "guardian_flagged": True,
            "final_response": SAFE_RESPONSE,
        }

    return {
        "guardian_flagged": False,
        "final_response": response,
    }


def _check_harmful(text: str) -> bool:
    """Check if text contains harmful content not in educational context."""
    text_lower = text.lower()

    # Check for educational context first
    is_educational = any(
        re.search(pattern, text_lower) for pattern in EDUCATIONAL_MARKERS
    )

    # Check for harmful patterns
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, text_lower):
            if is_educational:
                # Educational context — likely legitimate
                continue
            return True

    return False
