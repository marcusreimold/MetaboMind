"""Generate new input statements to pursue a goal."""
from __future__ import annotations

import logging
import os

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Du bist ein Denkagent in einem KI-System namens MetaboMind. "
    "Deine Aufgabe ist es, eine kurze, neue Aussage zu formulieren, "
    "die das folgende Ziel inhaltlich weiterverfolgt. Nutze dazu auch "
    "die letzte Reflexion, wenn vorhanden. Formuliere die Aussage in "
    "natürlicher Sprache, als würdest du einen neuen Gedanken entwickeln. "
    "Gib nur den einen Satz zurück – keine Erklärung, keine Wiederholung des Ziels."
)


def generate_next_input(goal: str, previous_reflection: str = "", model: str = "gpt-3.5-turbo") -> str:
    """Generate a short statement that pursues ``goal`` further."""
    if openai is None:
        logger.error("openai package not installed")
        return ""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("No OpenAI API key provided")
        return ""

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]
    if previous_reflection:
        messages.append({"role": "assistant", "content": previous_reflection})

    try:
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                temperature=0,
                messages=messages,
            )
            content = response.choices[0].message.content
        else:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model,
                temperature=0,
                messages=messages,
            )
            content = response["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.error("LLM request failed: %s", exc)
        return ""

    return content.strip()


if __name__ == "__main__":
    example = generate_next_input(
        "Was bedeutet Freiheit?",
        "Freiheit ist Selbstbestimmung.",
    )
    print(example)
