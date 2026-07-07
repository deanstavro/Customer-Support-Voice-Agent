"""Minimal LiveKit voice-agent baseline.

Componentized STT -> LLM -> TTS pipeline (all OpenAI), NOT the realtime
speech-to-speech model. The pipeline is deliberate: it exposes the text turn,
which is where the memory graph plugs in. Two seams are stubbed below:

  1. Recall  -> `SupportAgent.on_user_turn_completed`: inject knowledge-graph
     context into the chat before the LLM answers.
  2. Write   -> after `generate_reply`: persist decision / reasoning / response
     as connected nodes.

Run it:
  uv run python -m agent.main console   # local terminal voice loop
  uv run python -m agent.main dev       # connect to a LiveKit room
"""
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, inference
from livekit.plugins import openai

from agent.config import AgentConfig, load_config

load_dotenv()
from agent.context import RecallSession


class SupportAgent(Agent):
    def __init__(self, *, config: AgentConfig, session_id: str) -> None:
        super().__init__(instructions=config.instructions)
        self._recall_session = RecallSession(
            session_id=session_id,
            recall=config.recall,
        )

    async def on_user_turn_completed(self, turn_ctx, new_message) -> None:
        if ctx := await self._recall_session.recall_for_turn(
            new_message.text_content or ""
        ):
            turn_ctx.add_message(role="system", content=ctx)


def _build_openai_stt(config: AgentConfig):
    if config.stt_model:
        return openai.STT(model=config.stt_model)
    return openai.STT()


def _build_openai_llm(config: AgentConfig):
    return openai.LLM(model=config.llm_model)


def _build_openai_tts(config: AgentConfig):
    kwargs: dict[str, str] = {}
    if config.tts_model:
        kwargs["model"] = config.tts_model
    if config.tts_voice:
        kwargs["voice"] = config.tts_voice
    return openai.TTS(**kwargs) if kwargs else openai.TTS()


async def entrypoint(ctx: agents.JobContext) -> None:
    config = load_config()
    await ctx.connect()

    session_kwargs: dict = {
        "stt": _build_openai_stt(config),
        "llm": _build_openai_llm(config),
        "tts": _build_openai_tts(config),
    }
    if config.turn_detection == "livekit":
        session_kwargs["turn_detection"] = inference.TurnDetector()

    session = AgentSession(**session_kwargs)

    await session.start(
        room=ctx.room,
        agent=SupportAgent(config=config, session_id=ctx.room.name),
    )
    await session.generate_reply(instructions=config.greeting)

    # SEAM 2 — decision write.
    # Persist the interaction (decision, reasoning, response) to Neo4j as
    # connected nodes so the reasoning is traceable and editable.


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
