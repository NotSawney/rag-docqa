"""FastAPI app: ingest docs, ask grounded questions."""
from contextlib import contextmanager

from fastapi import FastAPI

from .config import settings
from .db import connect, init_db
from .guard import REFUSAL, is_grounded
from .ingest import ingest_path
from .llm import answer
from .retrieval import retrieve
from .schemas import Answer, AskRequest, Citation

app = FastAPI(title="RAG Document Q&A", version="0.1.0")


@contextmanager
def _db():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest")
def ingest(folder: str = "scripts/seed_docs") -> dict:
    with _db() as conn:
        init_db(conn)
        total = ingest_path(conn, folder)
    return {"folder": folder, "chunks": total}


@app.post("/ask", response_model=Answer)
def ask(req: AskRequest) -> Answer:
    with _db() as conn:
        hits = retrieve(conn, req.question, settings.top_k)

    if not is_grounded(hits, settings.score_threshold):
        # Guard refuses without spending a Claude call.
        return Answer(text=REFUSAL, citations=[], grounded=False, model=None)

    text, model = answer(req.question, hits)
    citations = [
        Citation(title=h.title, page=h.page, snippet=h.content[:200], score=round(h.score, 3))
        for h in hits
        if h.score >= settings.score_threshold
    ]
    return Answer(text=text, citations=citations, grounded=True, model=model)
