import os
import json
import logging
from typing import Dict, List, Tuple, Optional

from llm_client import get_client
from goals import goal_manager
from memory_manager import get_memory_manager

from control.metabo_rules import METABO_RULES


logger = logging.getLogger(__name__)


def run_llm_task(prompt: str, api_key: str | None = None) -> str:
    """Execute a simple LLM chat completion and return the text."""
    client = get_client(api_key or os.getenv("OPENAI_API_KEY"))
    if client is None:
        return ""

    messages = [{"role": "user", "content": prompt}]

    try:
        if hasattr(client, "chat"):
            resp = client.chat.completions.create(model="gpt-4o", temperature=0, messages=messages)
            return resp.choices[0].message.content.strip()
        resp = client.ChatCompletion.create(model="gpt-4o", temperature=0, messages=messages)
        return resp["choices"][0]["message"]["content"].strip()
    except Exception:  # pragma: no cover - network errors
        return ""


def detect_goal_shift(user_input: str, current_goal: str, api_key: str | None = None) -> tuple[bool, Optional[str]]:
    """Return ``(change_goal, new_goal)`` based on ``user_input`` and ``current_goal``."""
    client = get_client(api_key or os.getenv("OPENAI_API_KEY"))
    if client is None:
        return False, None

    system = (
        "Du bist ein Zielerkennungsmodul. Prüfe, ob der Nutzer ein neues Thema vorschlägt. "
        "Vergleiche es mit dem aktuellen Ziel und gib ein JSON-Objekt zurück."
    )
    user = f"Aktuelles Ziel: {current_goal}\nEingabe: {user_input}"

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
                model="gpt-4o",
                temperature=0,
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
                model="gpt-4o",
                temperature=0,
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

    changed, proposed = detect_goal_shift(last_user_input, goal, api_key)
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
            f"Reflektiere kurz den Zielwechsel von '{goal}' zu '{proposed}'.",
            api_key=api_key,
        )
        goal = proposed

    facts = "; ".join([f"{s} {p} {o}" for s, p, o in triplets or []])

    system_prompt = (
        METABO_RULES
        + (
            "\nDu bist ein Denkagent im KI-System MetaboMind. "
            "Beziehe dich direkt auf die Nutzereingabe und verfolge dabei das Ziel. "
            "Nutze die Tripel aus dem Ged\u00e4chtnis und die letzte Reflexion, um den Gedanken weiterzuentwickeln. "
            "Antworte der Nutzerin oder dem Nutzer in genau einem klaren Satz ohne Floskeln."
        )
    )

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
            model="gpt-4o",
            temperature=0,
            messages=messages,
        )
        content = response.choices[0].message.content
    else:
        response = client.ChatCompletion.create(
            model="gpt-4o",
            temperature=0,
            messages=messages,
        )
        content = response["choices"][0]["message"]["content"]

    return {
        "reflection": content.strip(),
        "explanation": goal_update_msg,
        "triplets": [],
    }
