"""Per-call recall state: when to query Neo4j vs reuse cached context."""

from __future__ import annotations

from dataclasses import dataclass, field

from . import router
from .recall import fetch_kg_context


@dataclass
class RecallSession:
    """Tracks one voice session's knowledge recall decisions."""

    session_id: str
    cached_context: str | None = None
    last_query: str | None = None
    _recall_count: int = field(default=0, repr=False)

    def _needs_fresh_recall(self, query: str) -> bool:
        if self.cached_context is None or self.last_query is None:
            return True
        return router.topic_shifted(query, self.last_query)

    async def recall_for_turn(self, query: str) -> str | None:
        """Return KG context to inject, or None to skip injection for this turn."""
        text = (query or "").strip()
        if not text or not router.should_search(text):
            return None

        if self._needs_fresh_recall(text):
            context = await fetch_kg_context(text)
            if context:
                self.cached_context = context
                self.last_query = text
                self._recall_count += 1
            return context

        return self.cached_context
