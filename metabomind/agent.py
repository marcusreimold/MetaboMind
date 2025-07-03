from typing import Optional

from .llm_interface import LLMInterface
from .knowledge_graph import KnowledgeGraph


class MetaboAgent:
    """Simple agent to demonstrate the MetaboMind rules."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.entropy = 0.0
        self.history = []
        kg = KnowledgeGraph()
        # Seed the graph with a simple semantic fact about the agent
        kg.add_semantic_fact("MetaboMind", "is", "a prototype agent")
        self.kg = kg
        self.llm = LLMInterface(model=model, api_key=api_key, kg=kg)

    def _update_entropy(self, delta: float):
        """Update the entropy and interpret as emotional state."""
        self.entropy += delta
        if delta < 0:
            state = 'positive'
        elif delta > 0:
            state = 'negative'
        else:
            state = 'neutral'
        return state

    def process_input(self, message: str) -> str:
        """Process user input according to MetaboMind rules."""
        self.history.append(message)
        # Store the interaction in episodic memory
        self.kg.add_episode(f"user: {message}")
        # Always involve the language model so it can apply the Metabo rules
        reply = self.llm.complete(message)
        self.kg.add_episode(f"agent: {reply}")

        if message.strip().lower() == 'takt':
            # The user requests only the system status
            self._update_entropy(-0.05)
            return self.system_status()

        self._update_entropy(-0.1)
        return reply

    def system_status(self) -> str:
        """Return current status of the agent."""
        return f"Entropy: {self.entropy:.2f}, History length: {len(self.history)}"
