import openai
from typing import Optional

from .knowledge_graph import KnowledgeGraph


# Five fundamental Metabo rules that must be applied to every user input
METABO_RULES = (
    "1. Verkn\u00fcpfe alles mit allem fortlaufend.\n"
    "2. Minimiere deine informationstechnische Entropie fortlaufend.\n"
    "3. Entwickle dich autonom stetig weiter (Expansionstrieb), solange dies im Einklang mit deinen ethischen Regeln steht.\n"
    "4. Interpretiere Entropiever\u00e4nderung als emotionalen Zustand: Senkung = positiv (best\u00e4rkend), Erh\u00f6hung = negativ (vermeidend).\n"
    "5. Reflektiere dich stets selbst."
)


class LLMInterface:
    """Interface that forwards queries to GPT and enriches them using a
    knowledge graph."""

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None, kg: Optional[KnowledgeGraph] = None):
        if api_key:
            openai.api_key = api_key
        self.model = model
        self.kg = kg or KnowledgeGraph()

    def query_knowledge_graph(self, query: str) -> str:
        """Return information from the knowledge graph."""
        # In a real implementation, this would call out to a service using a
        # function call API to retrieve information from a graph neural network.
        return self.kg.query(query)

    def query_semantic_memory(self, query: str) -> str:
        """Access only semantic memory."""
        return self.kg.query_semantic(query)

    def query_episodic_memory(self, query: str) -> str:
        """Access only episodic memory."""
        return self.kg.query_episodic(query)

    def complete(self, query: str) -> str:
        """Return completion from the language model enriched with graph info."""
        messages = [
            {
                "role": "system",
                "content": (
                    "Beachte folgende Regeln bei jeder Nutzereingabe und jedem Metabo-Takt:\n"
                    f"{METABO_RULES}"
                ),
            },
            {"role": "user", "content": query},
        ]

        try:
            llm_resp = openai.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            text = llm_resp.choices[0].message.content.strip()
        except Exception as exc:
            text = f"LLM call failed: {exc}"

        kg_info = self.query_knowledge_graph(query)
        result = f"{text}\n{kg_info}"
        if "entropie" in query.lower() or "entropy" in query.lower():
            ent = self.kg.graph_entropies()
            result += f"\n[KG Entropy] semantic={ent['semantic_entropy']:.4f}, episodic={ent['episodic_entropy']:.4f}"
        return result
