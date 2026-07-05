"""Minimal Neo4j knowledge-graph recall for the voice agent."""

from __future__ import annotations

import asyncio
import logging
import os

import neo4j
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.retrievers import VectorCypherRetriever

logger = logging.getLogger(__name__)

_retriever: VectorCypherRetriever | None = None

GRAPH_HOPS = 4

RETRIEVAL_QUERY = f"""
RETURN node.text AS text,
       node.source AS source,
       score,
       collect {{
         MATCH (node)-[*1..{GRAPH_HOPS}]-(related)
         WHERE related <> node
         RETURN DISTINCT
           labels(related)[0] AS type,
           coalesce(related.name, related.title, left(related.text, 200)) AS label
       }} AS related
"""


def _neo4j_configured() -> bool:
    return bool(os.environ.get("NEO4J_URI") and os.environ.get("NEO4J_PASSWORD"))


def _get_retriever() -> VectorCypherRetriever:
    global _retriever
    if _retriever is None:
        _retriever = VectorCypherRetriever(
            driver=neo4j.GraphDatabase.driver(
                os.environ["NEO4J_URI"],
                auth=(
                    os.environ.get("NEO4J_USERNAME", "neo4j"),
                    os.environ["NEO4J_PASSWORD"],
                ),
            ),
            index_name=os.environ.get("NEO4J_VECTOR_INDEX", "chunk_embeddings"),
            embedder=OpenAIEmbeddings(),
            retrieval_query=RETRIEVAL_QUERY,
        )
    return _retriever


async def recall(query: str, *, top_k: int = 3) -> str | None:
    """Search the knowledge graph and return context for the LLM, or None."""
    text = (query or "").strip()
    if not text or not _neo4j_configured():
        return None

    try:
        hits = await asyncio.to_thread(
            _get_retriever().search, query_text=text, top_k=top_k
        )
    except Exception:
        logger.exception("knowledge graph recall failed")
        return None

    if not hits.records:
        return None

    lines: list[str] = []
    for r in hits.records:
        line = f"- ({r['source']}) {r['text']}"
        related = [x for x in (r.get("related") or []) if x.get("label")]
        if related:
            related_str = "; ".join(f"{x['type']}: {x['label']}" for x in related[:10])
            line += f"\n  Related: {related_str}"
        lines.append(line)
    return "Relevant knowledge:\n" + "\n".join(lines)
