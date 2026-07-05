"""Context / memory layer.

This package will hold the Neo4j-backed memory graph:
  - long-term knowledge (docs modeled as a knowledge graph)
  - reasoning memory (per-interaction decision / reasoning / response nodes)

Kept empty for now. The agent wires its recall/write seams to functions
defined here (see agent/main.py: on_user_turn_completed and the post-reply
write in the entrypoint).
"""
