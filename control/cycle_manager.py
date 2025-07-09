from __future__ import annotations

import os
from typing import List, Tuple

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None

from logs.logger import MetaboLogger
from reasoning.emotion import interpret_emotion

from parsing.triplet_parser_llm import extract_triplets_via_llm

from reflection.reflection_engine import generate_reflection

from memory.intention_graph import IntentionGraph
from control.metabo_rules import METABO_RULES
from reasoning.entropy_analyzer import entropy_of_graph


class CycleManager:
    """Manages Metabo cycles including graph updates and reflections."""

    def __init__(self, api_key: str | None = None, logger: MetaboLogger | None = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_key = key
        if key and openai is not None:
            if hasattr(openai, "OpenAI"):
                self.client = openai.OpenAI(api_key=key)
            else:
                openai.api_key = key
                self.client = openai
        else:
            self.client = None
        self.graph = IntentionGraph()
        self.cycle = 0
        self.logger = logger
        self.logs: List[str] = []

    def _extract_triplets(self, text: str) -> List[Tuple[str, str, str]]:
        """Naive fallback extraction of triples when no API key is available."""
        words = text.split()
        if len(words) >= 3:
            return [(words[0], words[1], " ".join(words[2:]))]
        return []

    def _reflect(
        self,
        user_input: str,
        triplets: List[Tuple[str, str, str]],
        emotion: float,
    ) -> dict:
        """Use the reflection engine to analyse triplets and emotion."""
        return generate_reflection(
            last_user_input=user_input,
            goal="",
            last_reflection="",
            triplets=triplets,
            api_key=self.api_key,
        )

    def run_cycle(self, text: str) -> dict:
        """Run a single Metabo cycle with the provided text and return results."""
        self.cycle += 1
        before = entropy_of_graph(self.graph.snapshot())
        if self.api_key and self.client is not None:
            triplets = extract_triplets_via_llm(text)
        else:
            triplets = self._extract_triplets(text)
        if triplets:
            self.graph.add_triplets(triplets)
        after = entropy_of_graph(self.graph.snapshot())
        emo = interpret_emotion(before, after)
        reflection = self._reflect(text, triplets, emo["delta"])
        log_entry = (
            f"Cycle{self.cycle}: ent_b={before:.3f} ent_a={after:.3f} "
            f"emotion={emo['delta']:.3f}"
        )
        self.logs.append(log_entry)
        self.graph.save_graph()

        if self.logger:
            self.logger.log_cycle(
                input_text=text,
                reflection=reflection["reflection"],
                triplets=triplets,
                ent_before=before,
                ent_after=after,
                emotion=emo["emotion"],
                intensity=emo["intensity"],
            )

        return {
            "cycle": self.cycle,
            "entropy_before": before,
            "entropy_after": after,
            "delta": emo["delta"],
            "emotion": emo["emotion"],
            "intensity": emo["intensity"],
            "reflection": reflection["reflection"],
            "explanation": reflection.get("explanation", ""),
            "triplets": triplets,
            "log_entry": log_entry,
        }
