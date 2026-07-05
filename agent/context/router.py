"""Decide when a user turn should trigger knowledge-graph retrieval."""

from __future__ import annotations

import re

_SKIP_PATTERNS = re.compile(
    r"^(thanks|thank you|thx|ok|okay|yes|no|yep|nope|got it|sure|hello|hi|hey|bye|goodbye)\.?!?$",
    re.I,
)

_TOPIC_SHIFT_MARKERS = (
    "actually",
    "different question",
    "another question",
    "what about",
    "instead",
    "switch to",
    "new issue",
)

_MIN_SUBSTANTIVE_WORDS = 4


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}


def should_search(query: str) -> bool:
    """Return False for greetings and short acknowledgments."""
    text = (query or "").strip()
    if not text:
        return False
    if _SKIP_PATTERNS.match(text):
        return False
    if len(text.split()) < _MIN_SUBSTANTIVE_WORDS:
        return False
    return True


def topic_shifted(current: str, previous: str, *, overlap_threshold: float = 0.25) -> bool:
    """Return True when the user has likely moved to a new subject."""
    cur = (current or "").strip().lower()
    if any(marker in cur for marker in _TOPIC_SHIFT_MARKERS):
        return True

    cur_words, prev_words = _words(current), _words(previous)
    if not cur_words or not prev_words:
        return True

    overlap = len(cur_words & prev_words) / len(cur_words | prev_words)
    return overlap < overlap_threshold
