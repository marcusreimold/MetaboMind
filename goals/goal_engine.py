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


def generate_next_input(
    goal: str,
    previous_reflection: str = "",
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
) -> str:
    """Generate a short statement that pursues ``goal`` further."""
    if openai is None:
        raise ImportError("openai package not installed")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")

    reflection = previous_reflection.strip()[:300] if previous_reflection else ""
    content = f"Ziel: {goal}"
    if reflection:
        content += f"\nLetzte Reflexion: {reflection}"

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]

    try:
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=messages,
            )
            text = response.choices[0].message.content
        else:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model,
                temperature=temperature,
                messages=messages,
            )
            text = response["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.error("LLM request failed: %s", exc)
        text = ""

    if not text or not text.strip():
        return "Verantwortung ist der Preis der Freiheit."
    return text.strip()


if __name__ == "__main__":
    example = generate_next_input(
        "Was bedeutet Freiheit?",
        "Freiheit ist Selbstbestimmung.",
    )
    print(example)
