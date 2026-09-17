"""Query-time retrieval: embed the question, pull the nearest chunks."""
import psycopg

from .db import search
from .embeddings import embed_one
from .models import Hit


def retrieve(conn: psycopg.Connection, question: str, top_k: int) -> list[Hit]:
    return search(conn, embed_one(question), top_k)
