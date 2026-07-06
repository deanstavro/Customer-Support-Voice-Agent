"""Tests for agent configuration."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from agent.config import RecallConfig, load_config


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith(
            (
                "AGENT_",
                "LLM_",
                "TTS_",
                "STT_",
                "TURN_",
                "RECALL_",
                "NEO4J_VECTOR",
            )
        ):
            monkeypatch.delenv(key, raising=False)


def test_load_config_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=test\n", encoding="utf-8")

    config = load_config(env_file=env_file)

    assert "customer support agent" in config.instructions.lower()
    assert config.greeting == "Greet the customer and offer help."
    assert config.llm_model == "gpt-4o"
    assert config.tts_voice is None
    assert config.tts_model is None
    assert config.stt_model is None
    assert config.turn_detection == "livekit"
    assert config.recall == RecallConfig()


def test_load_config_env_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "AGENT_INSTRUCTIONS=Custom system prompt",
                "AGENT_GREETING=Say hello",
                "LLM_MODEL=gpt-4.1-mini",
                "TTS_VOICE=nova",
                "TTS_MODEL=tts-1-hd",
                "STT_MODEL=whisper-1",
                "TURN_DETECTION=none",
                "RECALL_ENABLED=false",
                "RECALL_TOP_K=5",
                "RECALL_GRAPH_HOPS=2",
                "RECALL_MIN_WORDS=6",
                "RECALL_TOPIC_OVERLAP=0.4",
                "NEO4J_VECTOR_INDEX=docs_index",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(env_file=env_file)

    assert config.instructions == "Custom system prompt"
    assert config.greeting == "Say hello"
    assert config.llm_model == "gpt-4.1-mini"
    assert config.tts_voice == "nova"
    assert config.tts_model == "tts-1-hd"
    assert config.stt_model == "whisper-1"
    assert config.turn_detection == "none"
    assert config.recall.enabled is False
    assert config.recall.top_k == 5
    assert config.recall.graph_hops == 2
    assert config.recall.min_words == 6
    assert config.recall.topic_overlap == 0.4
    assert config.recall.vector_index == "docs_index"


def test_load_config_prompt_file_override(tmp_path: Path) -> None:
    prompt_file = tmp_path / "system.txt"
    prompt_file.write_text("Prompt from file\n", encoding="utf-8")

    env_file = tmp_path / ".env"
    env_file.write_text(f"AGENT_INSTRUCTIONS_FILE={prompt_file}\n", encoding="utf-8")

    config = load_config(env_file=env_file)

    assert config.instructions == "Prompt from file"


def test_load_config_invalid_recall_top_k(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("RECALL_TOP_K=0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="RECALL_TOP_K"):
        load_config(env_file=env_file)


def test_load_config_invalid_turn_detection(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("TURN_DETECTION=vad\n", encoding="utf-8")

    with pytest.raises(ValueError, match="TURN_DETECTION"):
        load_config(env_file=env_file)
