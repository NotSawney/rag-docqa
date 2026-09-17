"""Ingest a folder of .md / .pdf docs into the vector store.

Run as a script:  python -m app.ingest scripts/seed_docs
"""
import sys
from pathlib import Path

import psycopg

from .chunking import Chunk, chunk_text
from .config import settings
from .db import connect, init_db, insert_chunks, upsert_document
from .embeddings import embed


def _chunks_for_file(path: Path) -> list[Chunk]:
    title = path.stem.replace("_", " ").replace("-", " ").strip().title()
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        chunks: list[Chunk] = []
        ordinal = 0
        for page_num, page in enumerate(PdfReader(str(path)).pages, start=1):
            page_chunks = chunk_text(
                page.extract_text() or "",
                title,
                page=page_num,
                chunk_words=settings.chunk_words,
                overlap_words=settings.chunk_overlap_words,
                start_ordinal=ordinal,
            )
            chunks.extend(page_chunks)
            ordinal += len(page_chunks)
        return chunks
    # markdown / plain text: no page numbers
    return chunk_text(
        path.read_text(encoding="utf-8"),
        title,
        chunk_words=settings.chunk_words,
        overlap_words=settings.chunk_overlap_words,
    )


def ingest_path(conn: psycopg.Connection, folder: str) -> int:
    total = 0
    for path in sorted(Path(folder).glob("**/*")):
        if path.suffix.lower() not in {".md", ".txt", ".pdf"}:
            continue
        chunks = _chunks_for_file(path)
        if not chunks:
            continue
        doc_id = upsert_document(conn, chunks[0].title, str(path))
        insert_chunks(conn, doc_id, chunks, embed([c.content for c in chunks]))
        total += len(chunks)
        print(f"  ingested {path.name}: {len(chunks)} chunks")
    return total


def main() -> None:
    folder = sys.argv[1] if len(sys.argv) > 1 else "scripts/seed_docs"
    conn = connect()
    init_db(conn)
    print(f"Ingesting {folder} ...")
    total = ingest_path(conn, folder)
    print(f"Done. {total} chunks stored.")
    conn.close()


if __name__ == "__main__":
    main()
