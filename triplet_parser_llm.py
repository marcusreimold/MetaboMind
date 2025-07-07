"""LLM-based extraction of semantic triples from German text."""
from __future__ import annotations

import json
import ast
import os
import logging
from typing import List, Tuple

import openai

# System prompt instructing the model
_SYSTEM_PROMPT = (
    "Extrahiere aus folgendem deutschen Text alle bedeutungsvollen Aussagen als "
    "Tripel (Subjekt, Prädikat, Objekt). Gib nur eine Liste von Tripeln im "
    "Format [(Subjekt, Prädikat, Objekt)] zurück. Kein Kommentar, keine "
    "Erklärungen."
)

logger = logging.getLogger(__name__)


def _parse_response(content: str) -> List[Tuple[str, str, str]] | None:
    """Parse a raw string from the LLM into a list of triples."""
    text = content.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1])

    # Try JSON first, then Python literal evaluation
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(text)
        except Exception:
            import re

            match = re.search(r"\[.*\]", text, re.S)
            if not match:
                return None
            snippet = match.group(0)
            for parser in (json.loads, ast.literal_eval):
                try:
                    data = parser(snippet)
                    break
                except Exception:
                    data = None
            if data is None:
                return None

    if isinstance(data, list):
        triples: List[Tuple[str, str, str]] = []
        for item in data:
            if (
                isinstance(item, (list, tuple))
                and len(item) == 3
            ):
                triples.append(
                    (str(item[0]).strip(), str(item[1]).strip(), str(item[2]).strip())
                )
        return triples
    return None


def extract_triplets_via_llm(text: str, model: str = "gpt-3.5-turbo") -> List[Tuple[str, str, str]]:
    """Extract semantic triples from ``text`` using an OpenAI chat model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("No OpenAI API key provided")
        return []

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        )
    except Exception as exc:
        logger.error("LLM request failed: %s", exc)
        return []

    try:
        content = response.choices[0].message.content
    except Exception:
        # Fallback for older client versions
        content = response["choices"][0]["message"]["content"]
    triples = _parse_response(content)
    if triples is None:
        logger.error("Parsing failed. Text: %r Response: %r", text, content)
        return []
    return triples


if __name__ == "__main__":
    example = "Freiheit ist wie ein Schmetterling – je mehr du sie jagst, desto weiter fliegt sie."
    print(extract_triplets_via_llm(example))
