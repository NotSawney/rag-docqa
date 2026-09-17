"""Claude generation, grounded on retrieved chunks.

Cost criterion (shown in the README): Haiku 4.5 answers the bulk cheaply
($1/$5 per Mtok); long/complex questions escalate to Sonnet 5 ($2/$10).
Embeddings are local, so only this generation step is billed.
"""
from functools import lru_cache

from anthropic import Anthropic

from .config import settings
from .models import Hit

SYSTEM = (
    "Sos un asistente que responde SOLO con la información de los fragmentos de contexto "
    "numerados que se te dan. Citá las fuentes usando sus números entre corchetes, por "
    "ejemplo [1] o [2]. Si el contexto no alcanza para responder, decí explícitamente que "
    "no está en los documentos; no inventes. Respondé en el idioma de la pregunta."
)


@lru_cache(maxsize=1)
def _client() -> Anthropic:
    if settings.anthropic_api_key:
        return Anthropic(api_key=settings.anthropic_api_key)
    return Anthropic()  # falls back to ANTHROPIC_API_KEY / ant profile


def choose_model(question: str) -> str:
    if len(question) >= settings.escalation_char_threshold:
        return settings.escalation_model
    return settings.answer_model


def _build_prompt(question: str, hits: list[Hit]) -> str:
    blocks = []
    for i, h in enumerate(hits, start=1):
        loc = f"{h.title}, p. {h.page}" if h.page else h.title
        blocks.append(f"[{i}] ({loc})\n{h.content}")
    context = "\n\n".join(blocks)
    return f"Contexto:\n{context}\n\nPregunta: {question}"


def _answer_anthropic(prompt: str, question: str) -> tuple[str, str]:
    model = choose_model(question)
    resp = _client().messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    return text, model


def _answer_ollama(prompt: str) -> tuple[str, str]:
    """Local generation via Ollama's chat API — free, offline, same grounded
    prompt. Used for e2e testing without spending the Claude key."""
    import httpx

    resp = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        json={
            "model": settings.ollama_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"], settings.ollama_model


def answer(question: str, hits: list[Hit]) -> tuple[str, str]:
    """Return (answer_text, model_used)."""
    prompt = _build_prompt(question, hits)
    if settings.llm_provider == "ollama":
        return _answer_ollama(prompt)
    return _answer_anthropic(prompt, question)
