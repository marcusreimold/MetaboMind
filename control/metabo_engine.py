from __future__ import annotations

import logging
from typing import Dict, Literal

from goals.goal_manager import GoalManager
from goals.goal_updater import propose_goal, check_goal_shift
from memory.memory_manager import get_memory_manager
from memory.context_selector import load_context
from utils.graph_utils import process_triples
from memory.recall_context import recall_context
from reflection.reflection_engine import generate_reflection, run_llm_task
from logs.logger import MetaboLogger
from reasoning.emotion import interpret_emotion
from reasoning.entropy_analyzer import entropy_of_graph
from goals.subgoal_planner import decompose_goal
from goals.subgoal_executor import execute_first_subgoal
from control.yin_yang_controller import (
    decide_mode,
    current_mode,
    mode_hint,
)
from control.mode_decider import decide_yin_yang_mode
from goals import goal_engine
from cfg.config import PROMPTS

logger = logging.getLogger(__name__)


def is_new_topic(user_input: str, current_goal: str) -> bool:
    """Return True if ``user_input`` appears unrelated to ``current_goal``."""
    if not user_input or not current_goal:
        return False
    prefix = user_input.lower().strip()[:25]
    return prefix not in current_goal.lower()


def run_metabo_cycle(source: str, source_type: Literal["user", "system"] = "user") -> Dict[str, object]:
    """Execute one MetaboMind cycle for ``source`` and return a structured result."""
    goal_mgr = GoalManager()
    memory = get_memory_manager()
    log = MetaboLogger()

    try:
        path = memory.metabo_graph.get_goal_path()
        sub_done = max(len(path) - 1, 0)
    except Exception:
        sub_done = 0

    mode = current_mode()
    mode_instruction = mode_hint()

    goal = goal_mgr.get_goal()
    last_reflection = goal_mgr.load_reflection()

    proposed = propose_goal(source, mode_hint=mode_instruction)
    new_goal = None
    if not proposed and is_new_topic(source, goal):
        proposed = source.strip()

    if proposed and check_goal_shift(goal, proposed):
        if goal:
            memory.metabo_graph.add_goal_transition(goal, proposed)
        else:
            memory.metabo_graph.goal_graph.add_node(proposed)
            memory.metabo_graph._save_goal_graph()
        goal_mgr.set_goal(proposed)
        new_goal = proposed
        logger.info("Neues Ziel erkannt: %s -> %s", goal, proposed)
        goal = proposed

    try:
        subgoals = decompose_goal(goal, last_reflection, mode_hint=mode_instruction)
    except Exception as exc:
        logger.warning("subgoal planning failed: %s", exc)
        subgoals = [goal]
    goal = execute_first_subgoal(goal, subgoals)

    graph_snapshot = memory.metabo_graph.snapshot()
    entropy_before = entropy_of_graph(graph_snapshot)

    try:
        context_nodes = load_context(memory.metabo_graph.graph, goal)
    except Exception as exc:
        logger.warning("context selection failed: %s", exc)
        context_nodes = []

    if mode == "yang":
        try:
            mem_facts = recall_context(scope="goal", limit=5)
            fact_triplets = [
                (d["subject"], d["predicate"], d["object"]) for d in mem_facts
            ]
        except Exception as exc:
            logger.warning("context recall failed: %s", exc)
            fact_triplets = []

        try:
            reflection_data = generate_reflection(
                last_user_input=source,
                goal=goal,
                last_reflection=last_reflection,
                triplets=fact_triplets,
                mode_hint=mode_instruction,
            )
            reflection_text = reflection_data.get("reflection", "")
        except Exception as exc:
            logger.warning("reflection generation failed: %s", exc)
            reflection_text = ""
            reflection_data = {"reflection": "", "triplets": [], "explanation": ""}

        try:
            tuple_triplets = process_triples(reflection_text, source="reflection")
        except Exception as exc:
            logger.warning("triplet processing failed: %s", exc)
            tuple_triplets = []
        triplets = tuple_triplets

        entropy_after = entropy_of_graph(memory.metabo_graph.snapshot())
        emotion = interpret_emotion(entropy_before, entropy_after)
    else:
        reflection_text = last_reflection
        triplets = []
        entropy_after = entropy_before
        emotion = interpret_emotion(entropy_before, entropy_after)

    metrics = {"entropy_delta": emotion["delta"], "emotion": emotion["emotion"]}
    mode = decide_mode(metrics, source, sub_done)
    llm_result = decide_yin_yang_mode(source, metrics)
    if llm_result and llm_result.get("mode") in {"yin", "yang"}:
        mode = llm_result["mode"]
        logger.info("LLM decided mode: %s (%s)", mode, llm_result.get("rationale", ""))
    logger.info(
        "MetaboMind mode: %s (Δ%.2f → %s)", mode, emotion["delta"], emotion["emotion"]
    )

    try:
        log.log_cycle(
            input_text=source,
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
    try:
        memory.store_last_entropy(entropy_after)
    except Exception as exc:
        logger.warning("storing entropy failed: %s", exc)

    try:
        memory.add_metabo_insight_to_graph(
            user_input=source,
            triplets=tuple_triplets,
            goal=new_goal,
            reflection=reflection_text,
            emotion={"emotion": emotion["emotion"], "delta": emotion["delta"]},
        )
    except Exception as exc:
        logger.warning("metabograph update failed: %s", exc)

    return {
        "goal": goal,
        "input": source,
        "subgoals": subgoals,
        "context": context_nodes,
        "reflection": reflection_text,
        "triplets": triplets,
        "entropy_before": entropy_before,
        "entropy_after": entropy_after,
        "emotion": emotion["emotion"],
        "delta": emotion["delta"],
        "mode": mode,
        "source_type": source_type,
    }


def handle_user_input(text: str) -> Dict[str, object]:
    """Convenience wrapper to process user input."""
    return run_metabo_cycle(text, source_type="user")


def metabo_tick(api_key: str | None = None) -> Dict[str, object]:
    """Run a system-driven Metabo cycle based on internal reflection."""
    memory = get_memory_manager()
    current_goal = goal_engine.get_current_goal()

    last_entropy = memory.load_last_entropy()
    current_entropy = memory.calculate_entropy()
    prompt = PROMPTS['takt_reflection'].format(goal=current_goal, delta=current_entropy - last_entropy)
    base_reflection = run_llm_task(
        prompt,
        api_key=api_key,
        mode_hint=mode_hint(),
    )

    result = run_metabo_cycle(base_reflection, source_type="system")

    new_entropy = memory.calculate_entropy()
    delta = new_entropy - current_entropy
    memory.store_last_entropy(new_entropy)
    emotion = memory.map_entropy_to_emotion(delta)

    goal_update = ""
    if result["goal"] != current_goal:
        goal_update = f"Neues Ziel erkannt: {result['goal']}"

    result.update({
        "delta": delta,
        "emotion": emotion["emotion"],
        "intensity": emotion["intensity"],
        "goal_update": goal_update,
        "base_reflection": base_reflection,
    })
    return result
