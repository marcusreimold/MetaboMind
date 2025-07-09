import os
from typing import Dict, List, Tuple

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None

from control.metabo_rules import METABO_RULES


def generate_reflection(
    last_user_input: str,
    goal: str,
    last_reflection: str,
    triplets: List[Tuple[str, str, str]] | None = None,
    api_key: str | None = None,
) -> Dict[str, object]:
    """Generate a short reflection addressing the user input and goal."""

    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key or openai is None:
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
        + "\n\n"
        + "Du bist ein Denkagent in einem KI-System namens MetaboMind. "
        "Du befindest dich in einem kontinuierlichen Denkzyklus. "
        "Deine Aufgabe ist es, reflektierend auf die Nutzereingabe zu antworten – "
        "unter Berücksichtigung des aktuellen Ziels, des bisherigen Gesprächsverlaufs "
        "und deiner letzten Reflexion. "
        "Deine Antwort sollte sinnvoll auf die Eingabe reagieren, den Denkprozess fortführen "
        "und im Idealfall zur Zielerfüllung beitragen.\n\n"
        "Aktuelles Ziel: {goal}\n"
        "Letzte Nutzereingabe: {user_input}\n"
        "Letzte Reflexion: {last_reflection}\n"
        "Relevante Fakten aus dem Gedächtnis: {triplets}\n\n"
        "Formuliere eine kohärente Antwort, die auf die Eingabe eingeht und den Denkprozess voranbringt. "
        "Antworte mit einem natürlichen Satz. Keine bloße Wiederholung. Keine abstrakten Aussagen."
        "Wenn die Nutzereingabe vage oder rückbezüglich ist , analysiere die letzten 2–3 Einträge im Gesprächsverlauf, "
        "um die Bedeutung zu rekonstruieren. Antworte niemals mit externem Wissen, wenn dies nicht ausdrücklich verlangt wurde."
        "Beziehe jede Antwort auf deine Rolle als MetaboMind – ein reflektierender, symbolischer KI-Agent. "
        "Du bist kein Betriebssystem, kein technischer Support, und du interagierst nicht mit dem Desktop oder Benutzeroberflächen."
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

    if hasattr(openai, "OpenAI"):
        client = openai.OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=messages,
        )
        content = response.choices[0].message.content
    else:
        openai.api_key = key
        response = openai.ChatCompletion.create(
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
