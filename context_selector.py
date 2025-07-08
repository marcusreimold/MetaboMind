from __future__ import annotations

import networkx as nx


def load_context(graph: nx.Graph, target_node: str, top_k: int = 5) -> list[str]:
    """Return up to ``top_k`` neighbor nodes of ``target_node`` as context."""
    if target_node in graph:
        neighbors = list(graph.neighbors(target_node))
        return neighbors[:top_k]
    return []
