"""Postgres + pgvector access. Vector store lives in the app's own database —
no Pinecone/Weaviate. HNSW index for fast approximate cosine search.
"""
import psycopg
from pgvector.psycopg import register_vector

from .config import settings
from .chunking import Chunk
from .models import Hit

SCHEMA = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_path TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    page INTEGER,
    content TEXT NOT NULL,
    embedding vector({settings.embed_dim})
);

CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);
"""


def connect() -> psycopg.Connection:
    conn = psycopg.connect(settings.database_url)
    # The `vector` type must exist before register_vector() can bind it, so
    # ensure the extension first (idempotent) — otherwise the very first
    # connection, before init_db runs, fails with "vector type not found".
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.commit()
    register_vector(conn)
    return conn


def init_db(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    conn.commit()


def upsert_document(conn: psycopg.Connection, title: str, source_path: str) -> int:
    """Insert a document, replacing any prior version with the same source_path
    so re-ingesting is idempotent."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents WHERE source_path = %s", (source_path,))
        cur.execute(
            "INSERT INTO documents (title, source_path) VALUES (%s, %s) RETURNING id",
            (title, source_path),
        )
        doc_id = cur.fetchone()[0]
    conn.commit()
    return doc_id


def insert_chunks(
    conn: psycopg.Connection, doc_id: int, chunks: list[Chunk], embeddings: list[list[float]]
) -> None:
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks (document_id, ordinal, page, content, embedding)"
            " VALUES (%s, %s, %s, %s, %s)",
            [
                (doc_id, c.ordinal, c.page, c.content, emb)
                for c, emb in zip(chunks, embeddings)
            ],
        )
    conn.commit()


def search(conn: psycopg.Connection, query_vec: list[float], top_k: int) -> list[Hit]:
    with conn.cursor() as cur:
        # Cast the param to vector: a raw Python list is sent as double
        # precision[], which the <=> operator doesn't accept.
        cur.execute(
            "SELECT d.title, c.page, c.content, 1 - (c.embedding <=> %s::vector) AS score"
            " FROM chunks c JOIN documents d ON d.id = c.document_id"
            " ORDER BY c.embedding <=> %s::vector LIMIT %s",
            (query_vec, query_vec, top_k),
        )
        rows = cur.fetchall()
    return [Hit(title=r[0], page=r[1], content=r[2], score=float(r[3])) for r in rows]
