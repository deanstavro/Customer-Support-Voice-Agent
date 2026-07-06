# Enterprise Memory for Voice Agents

## What makes it different
Most voice agents are stateless - each call starts from scratch. This framework gives the agent a **persistent, connected memory graph. The memory graph includes the agent's long-term knowledge (your docs modeled as a knowledge graph), and it's reasoning memory (context graph), connected**:
* Long term memory is stored as a knowledge graph. This allows us return high fidelity context cheaply, and leverages tools, skills and GraphRAG.
* On every customer interaction it records what decision it made, why it made that decision, and what it told the customer, all as connected nodes in Neo4j.

In the future, our reasoning memory will allow us to A/B test new underlying policies in achieving better CSAT/satisfaction metrics.

The payoff: Knowledge Graph for long term memory will yield better fidelity (compared to vectors). And both long-term knowledge and the agent's reasoning history live in one queryable graph that is now traceable. You can inspect why the agent said what it said, edit its knowledge directly, and steer it toward better decisions over time.

## How it works
1. **Configure** — set your docs URL, Neo4j keys, LiveKit keys, and model keys in `.env` (OpenAI supported today).
2. **Ingest** — the agent ingests your docs into a Neo4j knowledge graph, building a connected representation of everything your documents cover.
3. **Customize** — set your agent's prompt and voice.
4. **Run** — try out your agent, and edit its knowledge directly in Neo4j.
5. **Learn** — every interaction is stored as a context graph (decision, reasoning, and response), so you can review and guide the agent's decision-making.

## How to run

### Prerequisites
- [uv](https://docs.astral.sh/uv/) (Python package manager) — `brew install uv` or see the uv docs
- A [LiveKit Cloud](https://cloud.livekit.io) project (for `LIVEKIT_URL`, API key, and secret)
- An [OpenAI API key](https://platform.openai.com/api-keys) (used for STT, LLM, and TTS)
- A [Neo4j](https://neo4j.com/cloud/aura/) instance (for the memory graph)

### Steps
1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-org>/Customer-Support-Voice-Agent.git
   cd Customer-Support-Voice-Agent
   ```

2. **Install dependencies** (uv creates the virtualenv and installs from the lockfile)
   ```bash
   uv sync
   ```

3. **Configure your keys** — copy the example env file and fill in your values
   ```bash
   cp .env.example .env
   # then edit .env with your LiveKit, OpenAI, and Neo4j credentials
   ```

4. **Run the agent**
   ```bash
   uv run python -m agent.main console   # local terminal voice loop (uses your mic)
   uv run python -m agent.main dev       # connect to a LiveKit room
   ```

## How to configure

Copy `.env.example` to `.env` and set your credentials. Agent behavior is configured via environment variables and optional prompt files.

### Agent prompt

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_INSTRUCTIONS_FILE` | `agent/prompts/system.txt` | Path to system prompt file |
| `AGENT_GREETING_FILE` | `agent/prompts/greeting.txt` | Path to greeting instruction file |

Resolution order: env file path → default prompt file → built-in fallback.

### Agent characteristics

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | `gpt-4o` | OpenAI chat model |
| `TTS_VOICE` | OpenAI default | e.g. `alloy`, `nova`, `shimmer` |
| `TTS_MODEL` | plugin default | OpenAI TTS model |
| `STT_MODEL` | plugin default | OpenAI Whisper model |
| `TURN_DETECTION` | `livekit` | `livekit` or `none` |

### Long-term memory / recall

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | — | Neo4j connection URI |
| `NEO4J_USERNAME` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | — | Neo4j password |
| `NEO4J_VECTOR_INDEX` | `chunk_embeddings` | Vector index name |
| `RECALL_ENABLED` | `true` | Inject KG context on substantive turns |
| `RECALL_TOP_K` | `3` | Chunks retrieved per query |
| `RECALL_GRAPH_HOPS` | `4` | Related-node traversal depth |
| `RECALL_MIN_WORDS` | `4` | Min words before recall triggers |
| `RECALL_TOPIC_OVERLAP` | `0.25` | Topic-shift threshold (0–1) |

## Roadmap
- Configurable voice models
- Connect to realtime customer data for more intelligent decisions (pull in CustomerContext)
- Let the agent A/B test decisions
- Support for more models, voices, and hosting options
