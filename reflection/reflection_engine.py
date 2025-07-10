import os
from typing import Dict, List, Tuple

from llm_client import get_client

from control.metabo_rules import METABO_RULES


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
        "explanation": "",  # kept for backwards compatibility
        "triplets": [],
    }
