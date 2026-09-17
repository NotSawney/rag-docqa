"""Guard gates the LLM: a question the corpus doesn't cover must be refused
BEFORE any Claude call. is_grounded() is that gate (see main.ask), and it's a
pure function so this check needs no DB and no API key."""
from app.guard import REFUSAL, is_grounded
from app.models import Hit


def _hit(score: float) -> Hit:
    return Hit(title="Manual", page=1, content="...", score=score)


def test_refuses_when_no_hits():
    assert is_grounded([], threshold=0.35) is False


def test_refuses_when_all_below_threshold():
    assert is_grounded([_hit(0.10), _hit(0.20)], threshold=0.35) is False


def test_grounded_when_one_clears_threshold():
    assert is_grounded([_hit(0.10), _hit(0.42)], threshold=0.35) is True


def test_refusal_message_is_nonempty():
    assert REFUSAL.strip()
