from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from memory.metabo_graph import MetaboGraph
from reasoning.graph_entropy_scorer import calculate_entropy as score_graph
from reasoning.emotion import interpret_emotion


class MemoryManager:
    """Handle graph updates and store reflections and emotions."""

    def __init__(
        self,
        emotion_log: str = "data/emotions.jsonl",
        reflection_path: str = "data/last_reflection.txt",
        entropy_path: str = "data/last_entropy.txt",
        meta_path: str = "data/metabograph.gml",
    ) -> None:
        self.metabo_graph = MetaboGraph(meta_path)
        self.graph = self.metabo_graph
        self.emotion_log = Path(emotion_log)
        self.emotion_log.parent.mkdir(parents=True, exist_ok=True)
        self.reflection_path = Path(reflection_path)
        self.reflection_path.parent.mkdir(parents=True, exist_ok=True)
        self.entropy_path = Path(entropy_path)
        self.entropy_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Triplet handling

    def store_triplets(self, triplets: List[dict]) -> tuple[float, float]:
        """Add ``triplets`` to the MetaboGraph and return entropy values."""
        before = self.metabo_graph.calculate_entropy()
        if triplets:
            from parsing import triplet_pipeline
            triplet_pipeline.add_triplets_to_graph(triplets, mg=self.metabo_graph)
        after = self.metabo_graph.calculate_entropy()
        return before, after

    def add_metabo_insight_to_graph(
        self,
        user_input: str,
        triplets: List[Tuple[str, str, str]] | None = None,
        goal: str | None = None,
        reflection: str | None = None,
        emotion: dict | None = None,
    ) -> None:
        """Insert all insights of one cycle into the :class:`MetaboGraph`."""



        inp_node = f"eingabe:{user_input}"
        self.metabo_graph.graph.add_node(inp_node, typ="eingabe", text=user_input)

        if goal:
            goal_node = f"ziel:{goal}"
            self.metabo_graph.graph.add_node(goal_node, typ="ziel", text=goal)
            self.metabo_graph.graph.add_edge(
                inp_node,
                goal_node,
                relation="fuehrt_zu",
                typ="relation",
            )

        target_node = goal_node if goal else inp_node

        if reflection:
            ref_node = f"reflexion:{datetime.utcnow().isoformat(timespec='seconds')}"
            self.metabo_graph.graph.add_node(ref_node, typ="reflexion", text=reflection)
            self.metabo_graph.graph.add_edge(
                ref_node,
                target_node,
                relation="reflektiert_zu",
                typ="relation",
            )
            if emotion:
                self.metabo_graph.graph.nodes[ref_node]["meta"] = json.dumps(emotion)
        elif emotion:
            self.metabo_graph.graph.nodes[inp_node]["meta"] = json.dumps(emotion)

        try:
            self.metabo_graph.save()
        except Exception:
            pass

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
        return score_graph(self.metabo_graph.snapshot())

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

