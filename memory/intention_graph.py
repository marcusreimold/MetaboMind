import networkx as nx
from typing import List, Tuple

class IntentionGraph:
    """Graph storing intention triples."""

    def __init__(self):
        # using directed multigraph to allow multiple relations between nodes
        self.graph = nx.MultiDiGraph()

    def add_triplets(self, triplets: List[Tuple[str, str, str]]):
        """Add a list of (subject, relation, object) triples to the graph."""
        for subj, rel, obj in triplets:
            self.graph.add_node(subj)
            self.graph.add_node(obj)
            self.graph.add_edge(subj, obj, relation=rel)

    def snapshot(self) -> nx.MultiDiGraph:
        """Return a copy of the current graph."""
        return self.graph.copy()
