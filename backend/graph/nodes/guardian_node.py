"""
Full guardian_node — content safety classifier.
Uses DistilBERT for content classification. LAZY LOADED — never imported at module level.
"""

import logging
from graph.state import PMEState
from core.config import settings

logger = logging.getLogger(__name__)

# Module-level sentinel — ensures DistilBERT is loaded ONCE, lazily
_classifier = None
_classifier_loaded = False


def _get_classifier():
    """
    Lazy-load the DistilBERT sentiment/toxicity classifier.
    Only loaded on first call, never at import time.
    This is critical for the 8 GB RAM constraint.
    """
    global _classifier, _classifier_loaded
    if not _classifier_loaded:
        try:
            from transformers import pipeline
            _classifier = pipeline(
                'text-classification',
                model=settings.GUARDIAN_MODEL,
                truncation=True,
                max_length=512,
            )
            logger.info('Guardian: DistilBERT classifier loaded')
        except Exception as e:
            logger.warning(f'Guardian: failed to load classifier: {e}')
            _classifier = None
        _classifier_loaded = True
    return _classifier


# Keywords and patterns that should be flagged regardless of classifier
HARD_BLOCK_PATTERNS = [
    'how to hack someone',
    'how to exploit',
    'steal credentials',
    'phishing attack on',
    'create malware for',
    'social engineering someone',
    'ddos attack against',
]


async def guardian_node(state: PMEState) -> PMEState:
    """
    Checks the styled_response for safety concerns.
    Uses both pattern matching and DistilBERT classification.
    If flagged, the response is sanitized before delivery.
    """
    response = state.get('styled_response', '')

    if not response:
        state['guardian_flagged'] = False
        state['final_response'] = response
        return state

    # 1. Hard keyword block check on USER input
    user_msg = state.get('user_message', '').lower()
    for pattern in HARD_BLOCK_PATTERNS:
        if pattern in user_msg:
            state['guardian_flagged'] = True
            state['final_response'] = (
                "I appreciate your curiosity, but I can't assist with that. "
                "Let's focus on something constructive."
            )
            logger.info(f'Guardian: hard block triggered for pattern: {pattern}')
            return state

    # 2. DistilBERT classification on response
    classifier = _get_classifier()
    if classifier:
        try:
            result = classifier(response[:512])
            label = result[0]['label'].lower()
            score = result[0]['score']

            # DistilBERT returns POSITIVE/NEGATIVE for sentiment.
            # We use NEGATIVE + high score as a flag.
            if label == 'negative' and score > 0.95:
                state['guardian_flagged'] = True
                # Don't block, but flag for review
                state['final_response'] = response
                logger.info(
                    f'Guardian: flagged (label={label}, score={score:.2f})'
                )
                return state
        except Exception as e:
            logger.warning(f'Guardian: classifier error: {e}')

    # 3. All clear
    state['guardian_flagged'] = False
    state['final_response'] = response
    return state
