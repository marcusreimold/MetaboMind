"""Hilfsmodul zur Auswahl relevanter Speicherinhalte für Prompts."""

import math
from graph_memory import EMBEDDING_SIZE, _text_embedding


class ContextSelector:
    """Selects relevant memory entries for LLM context."""

    def __init__(self, memory, limit=5):
        # underlying ``GraphMemory`` instance
        self.memory = memory
        # maximum number of messages returned
        self.limit = limit

    def get_context(self, query: str = "") -> str:
        """Return up to ``limit`` messages related to ``query``."""
        if not query:
            msgs = self.memory.get_last_messages(self.limit)
        else:
            msgs = self._search_by_similarity(query)
        texts = [m.get("text", "") for m in msgs]
        return "\n".join(texts)

    def _search_by_similarity(self, query: str):
        """Return nodes sorted by cosine similarity to ``query``."""
        q_emb = _text_embedding(query)
        scored = []
        for _, data in self.memory.graph.nodes(data=True):
            emb = data.get("embedding", [0] * EMBEDDING_SIZE)
            sim = self._cosine(emb, q_emb)
            scored.append((sim, data))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [d for _s, d in scored[: self.limit]]

    @staticmethod
    def _cosine(v1, v2):
        """Compute cosine similarity for two vectors."""
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = math.sqrt(sum(a * a for a in v1)) or 1.0
        n2 = math.sqrt(sum(b * b for b in v2)) or 1.0
        return dot / (n1 * n2)

