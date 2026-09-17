"""Lightweight shared types (no DB/model imports, so guard tests stay pure)."""
from dataclasses import dataclass


@dataclass
class Hit:
    title: str
    page: int | None
    content: str
    score: float  # cosine similarity in [0, 1]; higher = closer
