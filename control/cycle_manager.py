from __future__ import annotations

import json
import os
from typing import List, Tuple

import openai

from memory.intention_graph import IntentionGraph
from reasoning.entropy_analyzer import entropy_of_graph


class CycleManager:
    """Manages Metabo cycles including graph updates and reflections."""

    def __init__(self, api_key: str | None = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
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
            "Antworte im JSON-Listenformat: [[\"subj\", \"rel\", \"obj\"], ...].\n" + text
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
        try:
            triplets = json.loads(content)
            return [(t[0], t[1], t[2]) for t in triplets]
        except Exception:
            return []

    def _reflect(self, triplets: List[Tuple[str, str, str]], emotion: float) -> str:
        """Ask the model to reflect on new triples and emotion change."""
        prompt = (
            "Formuliere basierend auf den neuen Tripeln und der Emotion (Entropie-Änderung) "
            "eine kurze Reflexion, wie der Wissensgraph verbessert werden kann."\
        )
        content = (
            f"Triples: {triplets}\nEmotion: {emotion:.3f}"
        )
        if not self.client:
            return "No reflection available without OpenAI API key."

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        )
        return response.choices[0].message.content.strip()

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
        return (
            f"[Cycle {self.cycle}] Entropy before: {before:.3f}, "
            f"after: {after:.3f}, Emotion: {emotion:+.3f}\n"
            f"Reflection: {reflection}\n[Logging] {log_entry}"
        )
