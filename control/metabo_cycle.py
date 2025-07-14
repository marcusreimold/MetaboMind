from __future__ import annotations

import logging
from typing import Dict

from goals.goal_manager import GoalManager
from goals.goal_updater import propose_goal, check_goal_shift
from memory.memory_manager import get_memory_manager
from memory.context_selector import load_context
from parsing.triplet_parser_llm import extract_triplets_via_llm
from memory.recall_context import recall_context
from reflection.reflection_engine import generate_reflection
from logs.logger import MetaboLogger
from reasoning.emotion import interpret_emotion
from reasoning.entropy_analyzer import entropy_of_graph
from goals.subgoal_planner import decompose_goal
from goals.subgoal_executor import execute_first_subgoal
from control.yin_yang_controller import decide_mode, current_mode
from control.mode_decider import decide_yin_yang_mode
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


def is_new_topic(user_input: str, current_goal: str) -> bool:
    """Return True if ``user_input`` appears unrelated to ``current_goal``."""
    if not user_input or not current_goal:
        return False
    prefix = user_input.lower().strip()[:25]
    return prefix not in current_goal.lower()


def run_metabo_cycle(user_input: str) -> Dict[str, object]:
    """Execute one MetaboMind cycle and return a structured result."""
    goal_mgr = GoalManager()
    memory = get_memory_manager()
    log = MetaboLogger()

    try:
        path = memory.graph.get_goal_path()
        sub_done = max(len(path) - 1, 0)
    except Exception:
        sub_done = 0

    mode = current_mode()


    goal = goal_mgr.get_goal()
    last_reflection = goal_mgr.load_reflection()

    proposed = propose_goal(user_input)
    new_goal = None
    if not proposed and is_new_topic(user_input, goal):
        proposed = user_input.strip()

    if proposed and check_goal_shift(goal, proposed):
        if goal:
            memory.graph.add_goal_transition(goal, proposed)
        else:
            memory.graph.goal_graph.add_node(proposed)
            memory.graph._save_goal_graph()
        goal_mgr.set_goal(proposed)
        new_goal = proposed
        logger.info("Neues Ziel erkannt: %s -> %s", goal, proposed)
        goal = proposed

    try:
        subgoals = decompose_goal(goal, last_reflection)
    except Exception as exc:
        logger.warning("subgoal planning failed: %s", exc)
        subgoals = [goal]
    goal = execute_first_subgoal(goal, subgoals)

    graph_snapshot = memory.graph.snapshot()
    entropy_before = entropy_of_graph(graph_snapshot)

    try:
        context_nodes = load_context(memory.graph.graph, goal)
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
                last_user_input=user_input,
                goal=goal,
                last_reflection=last_reflection,
                triplets=fact_triplets,
            )
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
                memory.graph.add_triplets(triplets)
            except Exception as exc:
                logger.warning("graph update failed: %s", exc)

        entropy_after = entropy_of_graph(memory.graph.snapshot())
        emotion = interpret_emotion(entropy_before, entropy_after)
    else:
        reflection_text = last_reflection
        triplets = []
        entropy_after = entropy_before
        emotion = interpret_emotion(entropy_before, entropy_after)

    metrics = {"entropy_delta": emotion["delta"], "emotion": emotion["emotion"]}
    mode = decide_mode(metrics, user_input, sub_done)
    llm_result = decide_yin_yang_mode(user_input, metrics)
    if llm_result and llm_result.get("mode") in {"yin", "yang"}:
        mode = llm_result["mode"]
        logger.info("LLM decided mode: %s (%s)", mode, llm_result.get("rationale", ""))
    logger.info(
        "MetaboMind mode: %s (Δ%.2f → %s)", mode, emotion["delta"], emotion["emotion"]
    )



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
    try:
        memory.store_last_entropy(entropy_after)
    except Exception as exc:
        logger.warning("storing entropy failed: %s", exc)

    try:
        memory.add_metabo_insight_to_graph(
            user_input=user_input,
            triplets=triplets,
            goal=new_goal,
            reflection=reflection_text,
            emotion={"emotion": emotion["emotion"], "delta": emotion["delta"]},
        )
    except Exception as exc:
        logger.warning("metabograph update failed: %s", exc)

    return {
        "goal": goal,
        "input": user_input,
        "subgoals": subgoals,
        "context": context_nodes,
        "reflection": reflection_text,
        "triplets": triplets,
        "entropy_before": entropy_before,
        "entropy_after": entropy_after,
        "emotion": emotion["emotion"],
        "delta": emotion["delta"],
        "mode": mode,
    }
