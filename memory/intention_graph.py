
import os
from pathlib import Path
from typing import List, Tuple

import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class IntentionGraph:
    """Graph storing intention triples and goal transitions with persistence."""

    def __init__(self, filepath: str = "data/graph.gml", goal_path: str | None = None):
        """Load existing graphs or create new ones.

        Parameters
        ----------
        filepath:
            Path to the knowledge graph file used for triplets.
        goal_path:
            Path to the directed goal graph. Defaults to ``memory/intent_graph.gml``.
        """

        self.filepath = filepath
        self.goal_path = Path(goal_path or "memory/intent_graph.gml")
        self.load_graph()
        self._load_goal_graph()

    def load_graph(self):
        """Load the graph from ``self.filepath`` if it exists."""
        if os.path.exists(self.filepath):
            try:
                self.graph = nx.read_gml(self.filepath)
                if not isinstance(self.graph, nx.MultiDiGraph):
                    self.graph = nx.MultiDiGraph(self.graph)
                print(f"[Graph] Lade bestehenden Graph aus {self.filepath}")
            except Exception as exc:
                print(f"[Graph] Fehler beim Laden, erstelle neuen Graph: {exc}")
                self.graph = nx.MultiDiGraph()
        else:
            print("[Graph] Erzeuge neuen, leeren Graph")
            self.graph = nx.MultiDiGraph()

    def save_graph(self):
        """Write the current graph to ``self.filepath`` in GML format."""
        try:
            nx.write_gml(self.graph, self.filepath)
            print(f"[Graph] gespeichert nach {self.filepath}")
        except Exception as exc:
            print(f"[Graph] Fehler beim Speichern: {exc}")

    def _load_goal_graph(self) -> None:
        """Load the directed goal graph from ``self.goal_path`` if available."""
        if self.goal_path.exists():
            try:
                self.goal_graph = nx.read_gml(self.goal_path)
                if not isinstance(self.goal_graph, nx.DiGraph):
                    self.goal_graph = nx.DiGraph(self.goal_graph)
                print(f"[GoalGraph] Lade bestehenden Graph aus {self.goal_path}")
            except Exception as exc:  # pragma: no cover - log for debugging
                print(f"[GoalGraph] Fehler beim Laden, erstelle neuen Graph: {exc}")
                self.goal_graph = nx.DiGraph()
        else:
            self.goal_graph = nx.DiGraph()

    def _save_goal_graph(self) -> None:
        """Persist the goal graph to disk."""
        try:
            nx.write_gml(self.goal_graph, self.goal_path)
        except Exception as exc:  # pragma: no cover - log for debugging
            print(f"[GoalGraph] Fehler beim Speichern: {exc}")


    def add_triplets(self, triplets: List[Tuple[str, str, str]]):
        """Add a list of (subject, relation, object) triples to the graph."""
        for subj, rel, obj in triplets:
            self.graph.add_node(subj)
            self.graph.add_node(obj)
            self.graph.add_edge(subj, obj, relation=rel)

    def snapshot(self) -> nx.MultiDiGraph:
        """Return a copy of the current graph."""
        return self.graph.copy()

    # ------------------------------------------------------------------
    # Goal transition management

    def add_goal_transition(self, previous_goal: str, new_goal: str) -> None:
        """Add a directed edge from ``previous_goal`` to ``new_goal``.

        Nodes are created if they do not yet exist. Duplicate edges are
        ignored. The goal graph is persisted after modification.
        """

        self.goal_graph.add_node(previous_goal)
        self.goal_graph.add_node(new_goal)
        if not self.goal_graph.has_edge(previous_goal, new_goal):
            self.goal_graph.add_edge(previous_goal, new_goal)
            self._save_goal_graph()

    def get_goal_path(self) -> List[str]:
        """Return a list representing the current goal path."""

        if len(self.goal_graph) == 0:
            return []
        try:
            return list(nx.topological_sort(self.goal_graph))
        except nx.NetworkXUnfeasible:
            start = next(iter(self.goal_graph.nodes()))
            return list(nx.dfs_preorder_nodes(self.goal_graph, start))

    def visualize_graph(self, output_path: str = "memory/intent_graph.png") -> None:
        """Create a simple PNG visualization of the goal graph."""

        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(self.goal_graph)
        nx.draw(self.goal_graph, pos, with_labels=True, arrows=True, node_color="lightblue")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()


def expand_target_neighborhood(
    G: nx.Graph,
    target_node: str,
    embeddings: dict,
    entropies: dict,
    top_k: int = 5,
) -> List[str]:
    """Return the ``top_k`` nodes most relevant to ``target_node``.

    Relevance is measured as cosine similarity multiplied by the node's
    entropy value.
    """

    if target_node not in embeddings:
        raise ValueError(f"Embedding for target node '{target_node}' not found")

    target_vec = embeddings[target_node].reshape(1, -1)

    scores = {}
    for node in G.nodes():
        if node == target_node:
            continue
        vec = embeddings.get(node)
        entropy = entropies.get(node)
        if vec is None or entropy is None:
            continue

        sim = cosine_similarity(target_vec, vec.reshape(1, -1))[0, 0]
        scores[node] = sim * entropy

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, _ in ranked[:top_k]]


