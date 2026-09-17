"""Local, self-hosted embeddings (sentence-transformers, 384-dim).

No external API and no per-token cost — this is the "RAG in your own infra,
not a third-party SaaS" pitch. Model loads once, lazily, on first use.
"""
from functools import lru_cache

from .config import settings


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embed_model)


def embed(texts: list[str]) -> list[list[float]]:
    """Return normalized embeddings (unit vectors) so cosine distance is a
    clean similarity measure in pgvector."""
    vectors = _model().encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]
