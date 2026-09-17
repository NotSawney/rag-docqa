"""Split source text into overlapping chunks that keep their source metadata.

Pure functions (no DB, no model) so they stay cheap to unit-test.
"""
from dataclasses import dataclass


@dataclass
class Chunk:
    title: str
    page: int | None
    ordinal: int
    content: str


def chunk_text(
    text: str,
    title: str,
    *,
    page: int | None = None,
    chunk_words: int = 180,
    overlap_words: int = 40,
    start_ordinal: int = 0,
) -> list[Chunk]:
    """Word-window chunker with overlap. Overlap keeps context across chunk
    boundaries so an answer split across two chunks is still retrievable."""
    if overlap_words >= chunk_words:
        raise ValueError("overlap_words must be smaller than chunk_words")

    words = text.split()
    if not words:
        return []

    step = chunk_words - overlap_words
    chunks: list[Chunk] = []
    ordinal = start_ordinal
    for start in range(0, len(words), step):
        window = words[start : start + chunk_words]
        if not window:
            break
        chunks.append(Chunk(title=title, page=page, ordinal=ordinal, content=" ".join(window)))
        ordinal += 1
        if start + chunk_words >= len(words):
            break  # last window already reached the end
    return chunks
