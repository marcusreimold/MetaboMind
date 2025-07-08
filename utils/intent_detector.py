from __future__ import annotations

"""Very simple heuristic intent detection for user input."""


def classify(text: str) -> str:
    """Return an intent label for ``text``.

    Labels: 'recall', 'frage', 'ziel', 'aktion', 'text'.
    """
    if not text:
        return "text"
    lower = text.lower()
    if lower.startswith("/ziel") or " ziel" in lower:
        return "ziel"
    if "?" in lower:
        return "frage"
    if any(key in lower for key in ["erinn", "zeige", "was weisst", "was weiß", "erzaehl nochmal"]):
        return "recall"
    if any(key in lower for key in ["aktion", "mach", "tu", "starte"]):
        return "aktion"
    return "text"
