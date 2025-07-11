from __future__ import annotations

from typing import List, Dict
import networkx as nx

from memory.memory_manager import get_memory_manager
from goal_manager import get_active_goal


def _edges_to_dicts(edges: List[tuple]) -> List[Dict[str, str]]:
    """Convert edges with data to list of triple dictionaries."""
    out: List[Dict[str, str]] = []
    for subj, obj, data in edges:
        rel = ""
        if isinstance(data, dict):
            rel = str(data.get("relation", ""))
        out.append({"subject": subj, "predicate": rel, "object": obj})
    return out


def recall_context(limit: int = 10, scope: str = "global") -> List[Dict[str, str]]:
    """Return up to ``limit`` facts from the IntentionGraph.

    Parameters
    ----------
    limit:
        Maximum number of triples to return.
    scope:
        "goal" focuses on edges connected to the current active goal. Any other
        value returns a global selection of edges ordered by node degree.
    """

    G: nx.MultiDiGraph = get_memory_manager().graph.graph

    edges: List[tuple] = []
    if scope == "goal":
        target = get_active_goal()
        if target and target in G:
            edges.extend(G.out_edges(target, data=True))
            edges.extend(G.in_edges(target, data=True))

    if not edges:
        # Fallback to global view sorted by node degree
        ranked_nodes = sorted(G.degree(), key=lambda x: x[1], reverse=True)
        for node, _ in ranked_nodes:
            for _, neighbor, data in G.edges(node, data=True):
                edges.append((node, neighbor, data))
                if len(edges) >= limit:
                    break
            if len(edges) >= limit:
                break

    return _edges_to_dicts(edges[:limit])
