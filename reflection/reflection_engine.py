import os
from typing import Dict, List, Tuple

from utils.json_utils import parse_json_safe

try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    openai = None

from metabo_rules import METABO_RULES


def generate_reflection(text: str, api_key: str | None = None) -> Dict[str, object]:
    """Generate a reflection over the given text.

    Parameters
    ----------
    text: str
        Input statement or generated output of the LLM.
    api_key: str | None
        Optional API key for OpenAI. If omitted and no ``OPENAI_API_KEY``
        environment variable exists, a simple offline reflection is returned.

    Returns
    -------
    dict
        Dictionary with keys ``reflection`` (improved text), ``explanation``
        describing the improvement and optional ``triplets`` listing semantic
        triples as ``(subject, predicate, object)`` tuples.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key or openai is None:
        return {
            "reflection": text,
            "explanation": "Kein OpenAI API-Schlüssel vorhanden; Eingabe unverändert.",
            "triplets": [],
        }

    system_prompt = (
        METABO_RULES
        + (
            "\nDu bist ein Denkagent in einem KI-System namens MetaboMind. "
            "Deine Aufgabe ist es, auf eine Nutzereingabe im Kontext eines Ziels "
            "zu antworten. Sprich dabei direkt zum Nutzer – nicht über die Eingabe. "
            "Formuliere eine neue Aussage, die dem Ziel näherkommt. Nutze dein "
            "vorhandenes Wissen und die letzte Reflexion, wenn sie dir hilft. "
            "Antworte in einem einzigen natürlichen Satz. Keine Meta-Analyse, "
            "keine Wiederholung des Ziels."
        )
    )

    if hasattr(openai, "OpenAI"):
        client = openai.OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        content = response.choices[0].message.content
    else:
        openai.api_key = key
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        content = response["choices"][0]["message"]["content"]
    data = parse_json_safe(content)
    if isinstance(data, dict):
        if "triplets" in data and isinstance(data["triplets"], list):
            data["triplets"] = [tuple(t) for t in data["triplets"]]
        return data
    return {
        "reflection": content.strip(),
        "explanation": "Antwort nicht im JSON-Format parsbar.",
        "triplets": [],
    }
