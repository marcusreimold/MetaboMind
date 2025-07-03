import networkx as nx
from datetime import datetime
from collections import Counter
import math


class KnowledgeGraph:
    """Graph-backed semantic and episodic memory store."""

    def __init__(self):
        self.semantic_graph = nx.MultiDiGraph()
        self.episodic_memory = []

    # Semantic memory methods
    def add_semantic_fact(self, subject: str, relation: str, obj: str) -> None:
        """Store a fact in the semantic graph."""
        self.semantic_graph.add_edge(subject, obj, relation=relation)

    def query_semantic(self, text: str) -> str:
        """Retrieve semantic triples containing the text."""
        results = []
        for u, v, data in self.semantic_graph.edges(data=True):
            rel = data.get("relation", "")
            if any(text.lower() in part.lower() for part in (u, v, rel)):
                results.append(f"{u} -{rel}-> {v}")
        if not results:
            return "[KG Semantic] No relevant info."
        return "[KG Semantic] " + "; ".join(results)

    # Episodic memory methods
    def add_episode(self, event: str) -> None:
        """Store an event with a timestamp."""
        self.episodic_memory.append({
            "time": datetime.utcnow().isoformat(timespec="seconds"),
            "event": event,
        })

    def query_episodic(self, text: str) -> str:
        """Retrieve episodic memories containing the text."""
        results = [
            f"{e['time']}: {e['event']}"
            for e in self.episodic_memory
            if text.lower() in e["event"].lower()
        ]
        if not results:
            return "[KG Episodic] No relevant info."
        return "[KG Episodic] " + "; ".join(results)

    def query(self, text: str) -> str:
        """Return combined semantic and episodic search results."""
        semantic = self.query_semantic(text)
        episodic = self.query_episodic(text)
        return f"{semantic}\n{episodic}"

    # Entropy metrics
    def semantic_entropy(self) -> float:
        """Return Shannon entropy of semantic graph degree distribution."""
        degrees = [self.semantic_graph.degree(n) for n in self.semantic_graph.nodes]
        total = sum(degrees)
        if total == 0:
            return 0.0
        counts = Counter(degrees)
        return -sum((c / total) * math.log2(c / total) for c in counts.values())

    def episodic_entropy(self) -> float:
        """Return entropy over user/agent event types in episodic memory."""
        labels = [
            "user" if e["event"].startswith("user:") else "agent"
            for e in self.episodic_memory
        ]
        total = len(labels)
        if total == 0:
            return 0.0
        counts = Counter(labels)
        return -sum((c / total) * math.log2(c / total) for c in counts.values())

    def graph_entropies(self) -> dict:
        """Return both semantic and episodic entropy metrics."""
        return {
            "semantic_entropy": self.semantic_entropy(),
            "episodic_entropy": self.episodic_entropy(),
        }
