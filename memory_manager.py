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
        graph_path: str = "data/graph.gml",
        emotion_log: str = "data/emotions.jsonl",
        reflection_path: str = "memory/last_reflection.txt",
    ) -> None:
        self.graph = IntentionGraph(graph_path)
        self.emotion_log = Path(emotion_log)
        self.emotion_log.parent.mkdir(parents=True, exist_ok=True)
        self.reflection_path = Path(reflection_path)
        self.reflection_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Triplet handling

    def store_triplets(self, triplets: List[Tuple[str, str, str]]) -> tuple[float, float]:
        """Add ``triplets`` to the intention graph and return entropy values."""
        before = entropy_of_graph(self.graph.snapshot())
        if triplets:
            self.graph.add_triplets(triplets)
            self.graph.save_graph()
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
