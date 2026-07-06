"""Tests for recall routing heuristics."""

from agent.config import RecallConfig
from agent.context import router


def test_should_search_skips_greeting() -> None:
    recall = RecallConfig(min_words=4)
    assert router.should_search("hello", recall=recall) is False
    assert router.should_search("thanks", recall=recall) is False


def test_should_search_requires_substantive_turn() -> None:
    recall = RecallConfig(min_words=4)
    assert router.should_search("how do refunds work", recall=recall) is True
    assert router.should_search("one two three", recall=recall) is False


def test_topic_shifted_detects_marker() -> None:
    recall = RecallConfig()
    assert router.topic_shifted(
        "actually I have a different question",
        "refund policy for shoes",
        recall=recall,
    )
