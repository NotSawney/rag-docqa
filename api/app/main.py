"""FastAPI app: ingest docs, ask grounded questions."""
from contextlib import contextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import connect, init_db
from .guard import REFUSAL, is_grounded
from .ingest import ingest_path
from .llm import answer
from .retrieval import retrieve
from .schemas import Answer, AskRequest, Citation

app = FastAPI(title="RAG Document Q&A", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    # Cite only above-threshold hits, and feed the LLM the same set, so the
    # `[n]` it emits maps 1:1 onto citations[n-1] for the UI to highlight.
    relevant = [h for h in hits if h.score >= settings.score_threshold]
    text, model = answer(req.question, relevant)
    citations = [
        Citation(title=h.title, page=h.page, snippet=h.content[:200], score=round(h.score, 3))
        for h in relevant
    ]
    return Answer(text=text, citations=citations, grounded=True, model=model)
