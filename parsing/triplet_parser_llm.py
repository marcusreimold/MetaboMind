"""LLM-based extraction of semantic triples from German text."""
from __future__ import annotations

import json
import ast
import os
import logging
from typing import List, Tuple

from utils.llm_client import get_client
from cfg.config import PROMPTS, MODELS, TEMPERATURES

# System prompt instructing the model

_SYSTEM_PROMPT = PROMPTS['triplet_parser_system']
logger = logging.getLogger(__name__)


def _parse_unquoted(text: str) -> List[Tuple[str, str, str]] | None:
    """Attempt to parse a list of triples without quoted strings."""
    import re

    txt = text.strip()
    if not (txt.startswith("[") and txt.endswith("]")):
        return None
    inner = txt[1:-1].strip()
    # split triples separated by brackets, parentheses, commas or newlines
    segments = re.split(r"\]\s*,\s*\[|\]\s*\n\s*\[|\)\s*,\s*\(|\],\s*\(|\),\s*\[", inner)
    triples: List[Tuple[str, str, str]] = []
    for seg in segments:
        seg = seg.strip().strip("[]()")
        if not seg:
            continue
        parts = [p.strip(" '\"") for p in seg.split(',')]
        if len(parts) != 3:
            return None
        triples.append(tuple(parts))
    return triples


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
            if match:
                snippet = match.group(0)
                for parser in (json.loads, ast.literal_eval):
                    try:
                        data = parser(snippet)
                        break
                    except Exception:
                        data = None
                if data is None:
                    data = _parse_unquoted(snippet)
            else:
                data = _parse_unquoted(text)
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


def extract_triplets_via_llm(
    text: str,
    model: str = MODELS['chat'],
    *,
    mode_hint: str | None = None,
) -> List[Tuple[str, str, str]]:
    """Extract semantic triples from ``text`` using an OpenAI chat model."""
    client = get_client(os.getenv("OPENAI_API_KEY"))
    if client is None:
        logger.error("No OpenAI API key provided or client unavailable")
        return []

    messages = []
    if mode_hint:
        messages.append({"role": "system", "content": mode_hint})
    messages.extend(
        [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
    )

    try:
        if hasattr(client, "chat"):
            response = client.chat.completions.create(
                model=model,
                temperature=TEMPERATURES['chat'],
                messages=messages,
            )
        else:
            response = client.ChatCompletion.create(
                model=model,
                temperature=TEMPERATURES['chat'],
                messages=messages,
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
