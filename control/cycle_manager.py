from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

from goals import goal_engine
from memory.memory_manager import get_memory_manager

from logs.logger import MetaboLogger

from utils.graph_utils import process_triples

from reflection.reflection_engine import generate_reflection, run_llm_task
from control.yin_yang_controller import mode_hint
from cfg.config import PROMPTS


class CycleManager:
    """Manages Metabo cycles including graph updates and reflections."""

    def __init__(self, api_key: str | None = None, logger: MetaboLogger | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.memory = get_memory_manager()
        self.cycle = 0
        self.logger = logger
        self.logs: List[str] = []
        self.current_goal = goal_engine.get_current_goal()


    def _extract_triplets(self, text: str) -> List[dict]:
        """Naive fallback extraction of triples when no API key is available."""
        words = text.split()
        if len(words) >= 3:
            return [
                {
                    "subject": words[0],
                    "predicate": words[1],
                    "object": " ".join(words[2:]),
                    "source": "user_input",
                    "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
                }
            ]
        return []

    def _reflect(
        self,
        user_input: str,
        triplets: List[Tuple[str, str, str]],
    ) -> dict:
        """Use the reflection engine to analyse triplets and emotion."""
        return generate_reflection(
            last_user_input=user_input,
            goal=self.current_goal,
            last_reflection=self.memory.load_reflection(),
            triplets=triplets,
            api_key=self.api_key,
            mode_hint=mode_hint(),
        )

    def run_cycle(self, text: str) -> dict:
        """Run a single Metabo cycle with the provided text and return results."""
        self.cycle += 1

        triplets = []
        if self.api_key:
            before = self.memory.metabo_graph.calculate_entropy()
            tuple_triplets = process_triples(text, source="user_input")
            triplets = tuple_triplets
            after = self.memory.metabo_graph.calculate_entropy()
        else:
            triplets = self._extract_triplets(text)
            tuple_triplets = [
                (t["subject"], t["predicate"], t["object"]) for t in triplets
            ]
            before, after = self.memory.store_triplets(triplets)
        emo = self.memory.save_emotion(before, after)

        new_goal = goal_engine.update_goal(
            user_input=text,
            last_reflection=self.memory.load_reflection(),
            triplets=tuple_triplets,
            mode_hint=mode_hint(),
        )

        goal_message = ""
        goal_reflection = ""
        if new_goal != self.current_goal:
            if self.current_goal:
                self.memory.graph.add_goal_transition(self.current_goal, new_goal)
            else:
                self.memory.graph.goal_graph.add_node(new_goal)
                self.memory.graph._save_goal_graph()
            goal_reflection = run_llm_task(
                PROMPTS['goal_shift_reflection'].format(
                    old=self.current_goal, new=new_goal
                ),
                api_key=self.api_key,
                mode_hint=mode_hint(),
            )
            if goal_reflection:
                self.memory.store_reflection(goal_reflection)
            self.current_goal = new_goal
            goal_message = f"Neues Ziel erkannt: {self.current_goal}"

        reflection = self._reflect(text, tuple_triplets)
        self.memory.store_reflection(reflection.get("reflection", ""))

        log_entry = (
            f"Cycle{self.cycle}: ent_b={before:.3f} ent_a={after:.3f} "
            f"emotion={emo['delta']:.3f}"
        )
        self.logs.append(log_entry)

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
            "goal": self.current_goal,
            "goal_update": goal_message,
            "goal_reflection": goal_reflection,
        }
