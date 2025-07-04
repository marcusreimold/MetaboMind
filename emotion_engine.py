"""Einfache Interpretation von Entropieänderungen als Emotionen."""


class EmotionEngine:
    """Interprets entropy change as emotional state."""
    def __init__(self, memory):
        # reference to graph memory for entropy calculation
        self.memory = memory
        self.last_entropy = self.memory.entropy()
        self.last_change = 0.0

    def evaluate(self) -> str:
        """Return a German description of the emotional state."""
        current = self.memory.entropy()
        # difference of current entropy to previous tick
        self.last_change = current - self.last_entropy
        self.last_entropy = current
        # map entropy change to coarse sentiment
        if self.last_change < -0.05:
            return "sehr positiv"
        if self.last_change < 0:
            return "positiv"
        if self.last_change > 0.05:
            return "sehr negativ"
        if self.last_change > 0:
            return "negativ"
        return "neutral"

    def intensity(self) -> float:
        """Return absolute normalized entropy change."""
        scale = max(self.last_entropy, 1.0)
        # normalise change by entropy magnitude for a 0-1 scale
        return abs(self.last_change) / scale
