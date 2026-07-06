"""Neo4j knowledge-graph retrieval."""

from __future__ import annotations

import asyncio
import logging
import os

import neo4j
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.retrievers import VectorCypherRetriever

from agent.config import RecallConfig

logger = logging.getLogger(__name__)

_retrievers: dict[tuple[str, int], VectorCypherRetriever] = {}


def _retrieval_query(graph_hops: int) -> str:
    return f"""
RETURN node.text AS text,
       node.source AS source,
       score,
       collect {{
         MATCH (node)-[*1..{graph_hops}]-(related)
         WHERE related <> node
         RETURN DISTINCT
           labels(related)[0] AS type,
           coalesce(related.name, related.title, left(related.text, 200)) AS label
       }} AS related
"""


def _neo4j_configured() -> bool:
    return bool(os.environ.get("NEO4J_URI") and os.environ.get("NEO4J_PASSWORD"))


def _get_retriever(recall: RecallConfig) -> VectorCypherRetriever:
    cache_key = (recall.vector_index, recall.graph_hops)
    retriever = _retrievers.get(cache_key)
    if retriever is None:
        retriever = VectorCypherRetriever(
            driver=neo4j.GraphDatabase.driver(
                os.environ["NEO4J_URI"],
                auth=(
                    os.environ.get("NEO4J_USERNAME", "neo4j"),
                    os.environ["NEO4J_PASSWORD"],
                ),
            ),
            index_name=recall.vector_index,
            embedder=OpenAIEmbeddings(),
            retrieval_query=_retrieval_query(recall.graph_hops),
        )
        _retrievers[cache_key] = retriever
    return retriever


def _format_hits(records: list) -> str | None:
    if not records:
        return None

    lines: list[str] = []
    for r in records:
        line = f"- ({r['source']}) {r['text']}"
        related = [x for x in (r.get("related") or []) if x.get("label")]
        if related:
            related_str = "; ".join(f"{x['type']}: {x['label']}" for x in related[:10])
            line += f"\n  Related: {related_str}"
        lines.append(line)
    return "Relevant knowledge:\n" + "\n".join(lines)


async def fetch_kg_context(query: str, *, recall: RecallConfig) -> str | None:
    """Query Neo4j and return formatted context. Used by RecallSession."""
    text = (query or "").strip()
    if not text or not recall.enabled or not _neo4j_configured():
        return None

    try:
        hits = await asyncio.to_thread(
            _get_retriever(recall).search,
            query_text=text,
            top_k=recall.top_k,
        )
    except Exception:
        logger.exception("knowledge graph recall failed")
        return None

    return _format_hits(hits.records)


async def recall(query: str, *, recall: RecallConfig) -> str | None:
    """Stateless recall — always hits Neo4j. Prefer RecallSession in production."""
    return await fetch_kg_context(query, recall=recall)
