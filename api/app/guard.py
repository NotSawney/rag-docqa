"""Retrieval guard: refuse instead of hallucinating when the corpus doesn't
cover the question. Pure function — no DB, no LLM — so a low-confidence question
is answered "I don't know" WITHOUT spending a Claude call.
"""
from .models import Hit

REFUSAL = (
    "I couldn't find that in the provided documents, so I can't answer with "
    "confidence. Try rephrasing, or add the relevant document to the corpus."
)


def is_grounded(hits: list[Hit], threshold: float) -> bool:
    """True only if at least one retrieved chunk clears the similarity threshold."""
    return bool(hits) and max(h.score for h in hits) >= threshold
