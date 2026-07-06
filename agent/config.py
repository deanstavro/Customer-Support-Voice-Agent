"""Agent configuration loaded from environment variables and prompt files."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_PACKAGE_DIR = Path(__file__).resolve().parent
_DEFAULT_SYSTEM_PROMPT = _PACKAGE_DIR / "prompts" / "system.txt"
_DEFAULT_GREETING_PROMPT = _PACKAGE_DIR / "prompts" / "greeting.txt"

_BUILTIN_SYSTEM = (
    "You are a helpful customer support agent. "
    "Be concise, warm, and accurate."
)
_BUILTIN_GREETING = "Greet the customer and offer help."


@dataclass(frozen=True)
class RecallConfig:
    enabled: bool = True
    top_k: int = 3
    graph_hops: int = 4
    min_words: int = 4
    topic_overlap: float = 0.25
    vector_index: str = "chunk_embeddings"


@dataclass(frozen=True)
class AgentConfig:
    instructions: str
    greeting: str
    llm_model: str
    tts_voice: str | None
    tts_model: str | None
    stt_model: str | None
    turn_detection: str
    recall: RecallConfig


def _read_text_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Prompt file is empty: {path}")
    return text


def _resolve_prompt(
    *,
    env_file_key: str,
    default_file: Path,
    builtin: str,
) -> str:
    file_path = os.environ.get(env_file_key)
    if file_path:
        return _read_text_file(Path(file_path).expanduser())

    if default_file.is_file():
        return _read_text_file(default_file)

    return builtin


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false, got {raw!r}")


def _env_int(name: str, default: int, *, minimum: int = 1) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value}")
    return value


def _env_float(name: str, default: float, *, minimum: float = 0.0, maximum: float = 1.0) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = float(raw.strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be a number, got {raw!r}") from exc
    if value < minimum or value > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}, got {value}")
    return value


def _env_optional_str(name: str) -> str | None:
    raw = os.environ.get(name)
    if raw is None:
        return None
    value = raw.strip()
    return value or None


def load_config(*, env_file: str | Path | None = None) -> AgentConfig:
    """Load agent configuration from the environment and default prompt files."""
    if env_file is not None:
        load_dotenv(env_file)
    else:
        load_dotenv()

    turn_detection = os.environ.get("TURN_DETECTION", "livekit").strip().lower()
    if turn_detection not in {"livekit", "none"}:
        raise ValueError(
            f"TURN_DETECTION must be 'livekit' or 'none', got {turn_detection!r}"
        )

    recall = RecallConfig(
        enabled=_env_bool("RECALL_ENABLED", True),
        top_k=_env_int("RECALL_TOP_K", 3),
        graph_hops=_env_int("RECALL_GRAPH_HOPS", 4),
        min_words=_env_int("RECALL_MIN_WORDS", 4),
        topic_overlap=_env_float("RECALL_TOPIC_OVERLAP", 0.25),
        vector_index=os.environ.get("NEO4J_VECTOR_INDEX", "chunk_embeddings").strip()
        or "chunk_embeddings",
    )

    return AgentConfig(
        instructions=_resolve_prompt(
            env_file_key="AGENT_INSTRUCTIONS_FILE",
            default_file=_DEFAULT_SYSTEM_PROMPT,
            builtin=_BUILTIN_SYSTEM,
        ),
        greeting=_resolve_prompt(
            env_file_key="AGENT_GREETING_FILE",
            default_file=_DEFAULT_GREETING_PROMPT,
            builtin=_BUILTIN_GREETING,
        ),
        llm_model=os.environ.get("LLM_MODEL", "gpt-4o").strip() or "gpt-4o",
        tts_voice=_env_optional_str("TTS_VOICE"),
        tts_model=_env_optional_str("TTS_MODEL"),
        stt_model=_env_optional_str("STT_MODEL"),
        turn_detection=turn_detection,
        recall=recall,
    )
