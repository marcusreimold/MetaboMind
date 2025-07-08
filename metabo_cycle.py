from __future__ import annotations

import logging
from typing import Dict

from goal_manager import GoalManager
from graph_manager import GraphManager
from context_selector import load_context
from triplet_parser_llm import extract_triplets_via_llm
from reflection.reflection_engine import generate_reflection
from logs.logger import MetaboLogger
from reasoning.emotion import interpret_emotion
from reasoning.entropy_analyzer import entropy_of_graph

logger = logging.getLogger(__name__)


def run_metabo_cycle(user_input: str) -> Dict[str, object]:
    """Execute one MetaboMind cycle and return a structured result."""
    goal_mgr = GoalManager()
    graph_mgr = GraphManager()
    log = MetaboLogger()

    goal = goal_mgr.get_goal()
    last_reflection = goal_mgr.load_reflection()

    graph_snapshot = graph_mgr.snapshot()
    entropy_before = entropy_of_graph(graph_snapshot)

    try:
        context_nodes = load_context(graph_mgr.graph, goal)
    except Exception as exc:
        logger.warning("context selection failed: %s", exc)
        context_nodes = []

    prompt = (
        f"Ziel: {goal}\n"\
        f"Eingabe: {user_input}\n"\
        f"Kontext: {', '.join(context_nodes)}\n"\
        f"Letzte Reflexion: {last_reflection}"
    )

    try:
        reflection_data = generate_reflection(prompt)
        reflection_text = reflection_data.get("reflection", "")
    except Exception as exc:
        logger.warning("reflection generation failed: %s", exc)
        reflection_text = ""
        reflection_data = {"reflection": "", "triplets": [], "explanation": ""}

    try:
        triplets = extract_triplets_via_llm(reflection_text)
    except Exception as exc:
        logger.warning("triplet extraction failed: %s", exc)
        triplets = []

    if triplets:
        try:
            graph_mgr.add_triplets(triplets)
        except Exception as exc:
            logger.warning("graph update failed: %s", exc)

    entropy_after = entropy_of_graph(graph_mgr.snapshot())
    emotion = interpret_emotion(entropy_before, entropy_after)

    try:
        graph_mgr.save()
    except Exception as exc:
        logger.warning("graph save failed: %s", exc)

    try:
        log.log_cycle(
            input_text=user_input,
            reflection=reflection_text,
            triplets=triplets,
            ent_before=entropy_before,
            ent_after=entropy_after,
            emotion=emotion["emotion"],
            intensity=emotion["intensity"],
        )
    except Exception as exc:
        logger.warning("logging failed: %s", exc)

    goal_mgr.save_reflection(reflection_text)

    return {
        "goal": goal,
        "input": user_input,
        "context": context_nodes,
        "reflection": reflection_text,
        "triplets": triplets,
        "entropy_before": entropy_before,
        "entropy_after": entropy_after,
        "emotion": emotion["emotion"],
        "delta": emotion["delta"],
    }
