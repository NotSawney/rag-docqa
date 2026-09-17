"""Retrieval guard: refuse instead of hallucinating when the corpus doesn't
cover the question. Pure function — no DB, no LLM — so a low-confidence question
is answered "I don't know" WITHOUT spending a Claude call.
"""
from .models import Hit

REFUSAL = (
    "No encontré esa información en los documentos provistos, así que no puedo "
    "responder con certeza. Reformulá la pregunta o agregá el documento relevante."
)


def is_grounded(hits: list[Hit], threshold: float) -> bool:
    """True only if at least one retrieved chunk clears the similarity threshold."""
    return bool(hits) and max(h.score for h in hits) >= threshold
