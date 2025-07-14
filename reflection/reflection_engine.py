import os
import json
import logging
from typing import Dict, List, Tuple, Optional

from datetime import datetime

from utils.llm_client import get_client
from goals import goal_manager
from memory.memory_manager import get_memory_manager
from memory.graph_manager import get_graph_manager, GraphManager
from parsing import triplet_extractor
from cfg.config import PROMPTS, MODELS, TEMPERATURES


logger = logging.getLogger(__name__)


def run_llm_task(prompt: str, api_key: str | None = None) -> str:
    """Execute a simple LLM chat completion and return the text."""
    client = get_client(api_key or os.getenv("OPENAI_API_KEY"))
    if client is None:
        return ""

    messages = [{"role": "user", "content": prompt}]

    try:
        if hasattr(client, "chat"):
            resp = client.chat.completions.create(
                model=MODELS['chat'],
                temperature=TEMPERATURES['chat'],
                messages=messages,
            )
            return resp.choices[0].message.content.strip()
        resp = client.ChatCompletion.create(
            model=MODELS['chat'],
            temperature=TEMPERATURES['chat'],
            messages=messages,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception:  # pragma: no cover - network errors
        return ""


def detect_goal_shift(
    user_input: str,
    current_goal: str,
    api_key: str | None = None,
    previous_user_inputs: list[str] | None = None,
    last_system_output: str = "",
) -> tuple[bool, Optional[str]]:
    """Return ``(change_goal, new_goal)`` based on conversation context."""
    client = get_client(api_key or os.getenv("OPENAI_API_KEY"))
    if client is None:
        return False, None

    previous_user_inputs = previous_user_inputs or []

    system = PROMPTS['goal_detector_system']

    parts = [f"Aktuelles Ziel: {current_goal}"]
    if previous_user_inputs:
        recent = ' | '.join(previous_user_inputs[-2:])
        parts.append(f"Vorherige Nutzereingaben: {recent}")
    if last_system_output.strip():
        parts.append(f"Letzte Systemantwort: {last_system_output.strip()}")
    parts.append(f"Eingabe: {user_input}")
    user = "\n".join(parts)

    functions = [
        {
            "name": "goal_decision",
            "description": "Entscheidet, ob ein neues Ziel vorgeschlagen wird",
            "parameters": {
                "type": "object",
                "properties": {
                    "change_goal": {"type": "boolean"},
                    "new_goal": {"type": "string"},
                },
                "required": ["change_goal"],
            },
        }
    ]

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    try:
        if hasattr(client, "chat"):
            resp = client.chat.completions.create(
                model=MODELS['chat'],
                temperature=TEMPERATURES['chat'],
                messages=messages,
                functions=functions,
                function_call="auto",
            )
            choice = resp.choices[0]
            if choice.finish_reason == "function_call":
                fc = choice.message.function_call
                if fc and fc.name == "goal_decision":
                    data = json.loads(fc.arguments)
                    return data.get("change_goal", False), data.get("new_goal")
        else:
            resp = client.ChatCompletion.create(
                model=MODELS['chat'],
                temperature=TEMPERATURES['chat'],
                messages=messages,
                functions=functions,
                function_call="auto",
            )
            choice = resp["choices"][0]
            if choice.get("finish_reason") == "function_call":
                fc = choice["message"]["function_call"]
                if fc["name"] == "goal_decision":
                    data = json.loads(fc["arguments"])
                    return data.get("change_goal", False), data.get("new_goal")
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("goal detection failed: %s", exc)

    return False, None

def generate_reflection(
    last_user_input: str,
    goal: str,
    last_reflection: str,
    triplets: List[Tuple[str, str, str]] | None = None,
    api_key: str | None = None,
    previous_user_inputs: list[str] | None = None,
    last_system_output: str = "",
) -> Dict[str, object]:
    """Generate a short reflection addressing the user input and goal."""

    client = get_client(api_key or os.getenv("OPENAI_API_KEY"))
    if client is None:
        return {
            "reflection": last_user_input,
            "explanation": "Kein OpenAI API-Schl\u00fcssel vorhanden; Eingabe unver\u00e4ndert.",
            "triplets": [],
        }

    if not goal.strip():
        goal = f"Erkundung: {last_user_input.strip()[:40]}"

    changed, proposed = detect_goal_shift(
        last_user_input,
        goal,
        api_key=api_key,
        previous_user_inputs=previous_user_inputs,
        last_system_output=last_system_output,
    )
    goal_update_msg = ""
    memory = get_memory_manager()
    if changed and proposed and proposed.strip() and proposed != goal:
        logger.info("Neues Ziel erkannt: %s -> %s", goal, proposed)
        if goal:
            memory.graph.add_goal_transition(goal, proposed)
        else:
            memory.graph.goal_graph.add_node(proposed)
            memory.graph._save_goal_graph()
        goal_manager.set_goal(proposed)
        goal_update_msg = run_llm_task(
            PROMPTS['goal_shift_reflection'].format(old=goal, new=proposed),
            api_key=api_key,
        )
        goal = proposed

    facts = "; ".join([f"{s} {p} {o}" for s, p, o in triplets or []])

    system_prompt = PROMPTS['reflection_system']

    user_content = f"Ziel: {goal}\nEingabe: {last_user_input}"
    if last_reflection.strip():
        user_content += f"\nLetzte Reflexion: {last_reflection.strip()}"
    if facts:
        user_content += f"\nTripel: {facts}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    if hasattr(client, "chat"):
        response = client.chat.completions.create(
            model=MODELS['chat'],
            temperature=TEMPERATURES['chat'],
            messages=messages,
        )
        content = response.choices[0].message.content
    else:
        response = client.ChatCompletion.create(
            model=MODELS['chat'],
            temperature=TEMPERATURES['chat'],
            messages=messages,
        )
        content = response["choices"][0]["message"]["content"]

    return {
        "reflection": content.strip(),
        "explanation": goal_update_msg,
        "triplets": [],
    }


def store_reflection_triplets(
    reflection: str,
    goal: str,
    emotion: dict | None = None,
    manager: GraphManager | None = None,
) -> List[Tuple[str, str, str]]:
    """Extract triplets from ``reflection`` and persist them via ``GraphManager``.

    Parameters
    ----------
    reflection:
        The textual reflection returned by the LLM.
    goal:
        Currently active goal used to connect the reflection node.
    emotion:
        Optional emotion metadata to store with the reflection node.
    manager:
        Optional preconfigured :class:`GraphManager` instance.

    Returns
    -------
    List[Tuple[str, str, str]]
        Triplets extracted from the reflection.
    """

    manager = manager or get_graph_manager()
    triples = triplet_extractor.extract(reflection)
    if not triples:
        return []

    manager.add_triplets(triples, source="reflection")

    ref_node = f"reflexion:{datetime.utcnow().isoformat(timespec='seconds')}"
    manager.graph.add_node(ref_node, typ="reflexion", text=reflection)

    if goal:
        goal_node = f"ziel:{goal}"
        manager.graph.add_node(goal_node, typ="ziel", text=goal)
        manager.graph.add_edge(ref_node, goal_node, relation="reflektiert_zu", typ="relation")

    if emotion:
        manager.graph.nodes[ref_node]["meta"] = json.dumps(emotion)

    manager.save_graph()
    return triples
