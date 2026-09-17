"""Chunker keeps overlap and source metadata — the check that fails if a chunk
boundary silently drops context or loses its citation info."""
from app.chunking import chunk_text


def test_overlap_and_metadata():
    words = [f"w{i}" for i in range(400)]
    chunks = chunk_text(
        " ".join(words), "Manual", page=7, chunk_words=180, overlap_words=40
    )

    # 400 words, window 180, step 140 -> windows at 0,140,280 = 3 chunks
    assert len(chunks) == 3

    # metadata preserved on every chunk
    assert all(c.title == "Manual" and c.page == 7 for c in chunks)
    assert [c.ordinal for c in chunks] == [0, 1, 2]

    # consecutive chunks share exactly `overlap_words` words at the seam
    tail = chunks[0].content.split()[-40:]
    head = chunks[1].content.split()[:40]
    assert tail == head


def test_empty_text_yields_nothing():
    assert chunk_text("   ", "Empty") == []
