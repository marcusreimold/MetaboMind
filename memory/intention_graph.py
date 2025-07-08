
import os
from typing import List, Tuple

import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class IntentionGraph:
    """Graph storing intention triples with persistent GML saving."""

    def __init__(self, filepath: str = "memory/graph.gml"):
        """Load existing graph from ``filepath`` or create a new one."""
        self.filepath = filepath
        self.load_graph()

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


    def add_triplets(self, triplets: List[Tuple[str, str, str]]):
        """Add a list of (subject, relation, object) triples to the graph."""
        for subj, rel, obj in triplets:
            self.graph.add_node(subj)
            self.graph.add_node(obj)
            self.graph.add_edge(subj, obj, relation=rel)

    def snapshot(self) -> nx.MultiDiGraph:
        """Return a copy of the current graph."""
        return self.graph.copy()


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

