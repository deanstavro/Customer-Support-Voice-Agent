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

from agent.context import recall

load_dotenv()


class SupportAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful customer support agent. "
            "Be concise, warm, and accurate."
        )

    async def on_user_turn_completed(self, turn_ctx, new_message) -> None:
        if ctx := await recall(new_message.text_content or ""):
            turn_ctx.add_message(role="system", content=ctx)


async def entrypoint(ctx: agents.JobContext) -> None:
    await ctx.connect()

    session = AgentSession(
        stt=openai.STT(),                       # Whisper
        llm=openai.LLM(model="gpt-4o"),         # componentized (exposes text turn)
        tts=openai.TTS(),
        # VAD is bundled into AgentSession by default (local Silero).
        turn_detection=inference.TurnDetector(),  # LiveKit inference gateway
    )

    await session.start(room=ctx.room, agent=SupportAgent())
    await session.generate_reply(instructions="Greet the customer and offer help.")

    # SEAM 2 — decision write.
    # Persist the interaction (decision, reasoning, response) to Neo4j as
    # connected nodes so the reasoning is traceable and editable.


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
