"""Request/response models for the API."""
from pydantic import BaseModel


class Citation(BaseModel):
    title: str
    page: int | None = None
    snippet: str
    score: float


class AskRequest(BaseModel):
    question: str


class Answer(BaseModel):
    text: str
    citations: list[Citation] = []
    grounded: bool  # False when the guard refused (answer not from the corpus)
    model: str | None = None  # which Claude model answered, None when the guard refused
