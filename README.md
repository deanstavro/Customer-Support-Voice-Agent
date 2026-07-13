# KG for Voice Agents

## What makes it different
Most voice agents are stateless. Every conversation starts from scratch. This framework gives the agent a persistent memory graph backed by Neo4j.

The memory graph consists of two connected layers:
* Long-term knowledge: Your documentation and business knowledge are modeled as a knowledge graph. This enables high-fidelity retrieval of business context, supports GraphRAG, and allows the agent to use structured tools and skills.
* Reasoning memory: Every customer interaction records the decision the agent made, why it made that decision, and what it ultimately told the customer. Those decisions become connected, queryable nodes in the graph.

Over time, the reasoning memory becomes a dataset for improving the agent. For example, you can compare how different policies, prompts, or workflows affect CSAT, resolution rates, or other business metrics.

The payoff: Both the agent's long-term knowledge and its reasoning history live in a single connected graph. Every answer is traceable - you can inspect why the agent responded the way it did, edit its knowledge directly, and continuously improve future decisions based on historical outcomes.

## How it works
1. **Configure** — set your docs URL, Neo4j keys, LiveKit keys, and model keys in `.env` (OpenAI supported today).
2. **Ingest** — the agent ingests your docs into a Neo4j knowledge graph, building a connected representation of everything your documents cover. Alternatively, if you have your graph with embeddings in Neo4j, simply connect to that instance in your environment variables.
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

V1 (Current Version)
Talk to your docs
GraphRAG
Voice

v2
Remember conversations
Store decisions
Explain why answers were given

v3
Learn from thousands of conversations
Identify successful resolutions
Recommend better responses
Detect outdated documentation
Suggest documentation improvements

v4
Multiple agents sharing organizational memory
Customer support, sales, onboarding, success
Shared enterprise ontology
Shared reasoning memory
