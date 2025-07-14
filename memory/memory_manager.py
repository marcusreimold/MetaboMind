from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from memory.intention_graph import IntentionGraph
from reasoning.entropy_analyzer import entropy_of_graph
from reasoning.emotion import interpret_emotion


class MemoryManager:
    """Handle graph updates and store reflections and emotions."""

    def __init__(
        self,
        graph_path: str = "data/metabograph.gml",
        emotion_log: str = "data/emotions.jsonl",
        reflection_path: str = "memory/last_reflection.txt",
        entropy_path: str = "memory/last_entropy.txt",
    ) -> None:
        self.graph = IntentionGraph(graph_path)
        self.emotion_log = Path(emotion_log)
        self.emotion_log.parent.mkdir(parents=True, exist_ok=True)
        self.reflection_path = Path(reflection_path)
        self.reflection_path.parent.mkdir(parents=True, exist_ok=True)
        self.entropy_path = Path(entropy_path)
        self.entropy_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Triplet handling

    def store_triplets(self, triplets: List[Tuple[str, str, str]]) -> tuple[float, float]:
        """Add ``triplets`` to the intention graph and return entropy values."""
        before = entropy_of_graph(self.graph.snapshot())
        if triplets:
            self.graph.add_triplets(triplets)
        after = entropy_of_graph(self.graph.snapshot())
        return before, after

    # ------------------------------------------------------------------
    # Reflection persistence

    def store_reflection(self, reflection: str) -> None:
        """Persist the latest reflection text."""
        self.reflection_path.write_text(reflection, encoding="utf-8")

    def load_reflection(self) -> str:
        """Return the last saved reflection."""
        try:
            return self.reflection_path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            return ""

    # ------------------------------------------------------------------
    # Emotion logging

    def save_emotion(self, ent_before: float, ent_after: float) -> dict:
        """Interpret and store the emotion derived from entropy change."""
        emo = interpret_emotion(ent_before, ent_after)
        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "entropy_before": ent_before,
            "entropy_after": ent_after,
            **emo,
        }
        with self.emotion_log.open("a", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False)
            fh.write("\n")
        return emo

    # ------------------------------------------------------------------
    # Entropy helpers

    def calculate_entropy(self) -> float:
        """Return the entropy of the current knowledge graph."""
        return entropy_of_graph(self.graph.snapshot())

    def load_last_entropy(self) -> float:
        """Return the previously stored entropy value."""
        try:
            return float(self.entropy_path.read_text())
        except (FileNotFoundError, ValueError):
            return 0.0

    def store_last_entropy(self, value: float) -> None:
        """Persist the latest entropy value for future deltas."""
        self.entropy_path.write_text(str(value))

    def map_entropy_to_emotion(self, delta: float) -> dict:
        """Map an entropy delta to an emotion assessment."""
        if delta <= -0.05:
            emotion = "positive"
        elif delta >= 0.05:
            emotion = "negative"
        else:
            emotion = "neutral"

        abs_delta = abs(delta)
        if abs_delta < 0.05:
            intensity = "low"
        elif abs_delta <= 0.15:
            intensity = "medium"
        else:
            intensity = "high"

        return {"delta": delta, "emotion": emotion, "intensity": intensity}

# ------------------------------------------------------------------
# Global memory instance handling

_default_manager: MemoryManager | None = None


def get_memory_manager() -> MemoryManager:
    """Return a shared :class:`MemoryManager` instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = MemoryManager()
    return _default_manager

