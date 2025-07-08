from __future__ import annotations

from memory.intention_graph import IntentionGraph


class GraphManager:
    """Lightweight wrapper for ``IntentionGraph`` access."""

    def __init__(self, filepath: str = "data/graph.gml") -> None:
        self.intention_graph = IntentionGraph(filepath)

    def snapshot(self):
        return self.intention_graph.snapshot()

    def add_triplets(self, triplets) -> None:
        self.intention_graph.add_triplets(triplets)

    def save(self) -> None:
        self.intention_graph.save_graph()

    @property
    def graph(self):
        return self.intention_graph.graph
