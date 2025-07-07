from __future__ import annotations

import os
from typing import List, Tuple

import openai

from reflection.reflection_engine import generate_reflection
from utils.json_utils import parse_json_safe

from memory.intention_graph import IntentionGraph
from metabo_rules import METABO_RULES
from reasoning.entropy_analyzer import entropy_of_graph


class CycleManager:
    """Manages Metabo cycles including graph updates and reflections."""

    def __init__(self, api_key: str | None = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_key = key
        self.client = openai.OpenAI(api_key=key) if key else None
        self.graph = IntentionGraph()
        self.cycle = 0
        self.logs: List[str] = []

    def _extract_triplets(self, text: str) -> List[Tuple[str, str, str]]:
        """Use OpenAI to extract triples from text."""
        if not self.client:
            words = text.split()
            if len(words) >= 3:
                return [(words[0], words[1], " ".join(words[2:]))]
            return []

        prompt = (
            "Extrahiere (Subjekt, Relation, Objekt)-Tripel aus folgendem Text. "
            "Antworte im JSON-Listenformat: [[\"subj\", \"rel\", \"obj\"], ...]."
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": METABO_RULES},
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
        )
        content = response.choices[0].message.content
        data = parse_json_safe(content)
        if isinstance(data, list):
            return [(t[0], t[1], t[2]) for t in data]
        return []

    def _reflect(self, triplets: List[Tuple[str, str, str]], emotion: float) -> dict:
        """Use the reflection engine to analyse triplets and emotion."""
        content = f"Triples: {triplets}\nEmotion: {emotion:.3f}"
        return generate_reflection(content, api_key=self.api_key)

    def run_cycle(self, text: str) -> str:
        """Run a single Metabo cycle with the provided text."""
        self.cycle += 1
        before = entropy_of_graph(self.graph.snapshot())
        triplets = self._extract_triplets(text)
        if triplets:
            self.graph.add_triplets(triplets)
        after = entropy_of_graph(self.graph.snapshot())
        emotion = after - before
        reflection = self._reflect(triplets, emotion)
        log_entry = (
            f"Cycle{self.cycle}: ent_b={before:.3f} ent_a={after:.3f} "
            f"emotion={emotion:.3f}"
        )
        self.logs.append(log_entry)
        self.graph.save_graph()
        return (
            f"[Cycle {self.cycle}] Entropy before: {before:.3f}, "
            f"after: {after:.3f}, Emotion: {emotion:+.3f}\n"
            f"Reflection: {reflection['reflection']}\n"
            f"Begründung: {reflection.get('explanation', '')}\n"
            f"[Logging] {log_entry}"
        )
