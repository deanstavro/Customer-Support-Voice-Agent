# Customer Support Voice Agent

A framework for building customer-support voice agents that are high-fidelity, low-latency, and inexpensive to run.

## What makes it different
Most voice agents are stateless - each call starts from scratch. This framework gives the agent a **persistent, connected memory graph**. On every customer interaction it records what decision it made, why it made that decision, and what it told the customer, all as connected nodes in Neo4j.

The payoff: both long-term knowledge and the agent's reasoning history live in one queryable graph. You can inspect why the agent said what it said, edit its knowledge directly, and steer it toward better decisions over time.

## How it works
1. **Configure** — set your docs URL, Neo4j keys, LiveKit keys, and model keys in `.env` (OpenAI supported today).
2. **Ingest** — the agent ingests your docs into a Neo4j knowledge graph, building a connected representation of everything your documents cover.
3. **Customize** — set your agent's prompt and voice.
4. **Run** — try out your agent, and edit its knowledge directly in Neo4j.
5. **Learn** — every interaction is stored as a context graph (decision, reasoning, and response), so you can review and guide the agent's decision-making.

## How to run [TO BE EDITED]
1. Clone the repo locally
2. Install dependencies and run locally

## Roadmap
- Configurable voice models
- Connect to realtime customer data for more intelligent decisions
- Let the agent A/B test decisions
- Support for more models, voices, and hosting options
