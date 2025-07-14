"""LLM-driven selection of Yin or Yang mode."""
from __future__ import annotations

import json
import logging
import os
from typing import Dict, Optional

from utils.llm_client import get_client
from cfg.config import PROMPTS, MODELS, TEMPERATURES

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = PROMPTS['mode_decider_system']


def decide_yin_yang_mode(
    user_input: str,
    metrics: Dict[str, float],
    api_key: str | None = None,
    *,
    mode_hint: str | None = None,
) -> Optional[Dict[str, str]]:
    """Return an LLM decision for Yin or Yang.

    Parameters
    ----------
    user_input : str
        Last text from the user.
    metrics : Dict[str, float]
        Current metrics like ``emotion`` and ``entropy_delta``.
    api_key : str | None, optional
        API key if not provided via ``OPENAI_API_KEY``.

    Returns
    -------
    Optional[Dict[str, str]]
        Dictionary with ``mode`` and optional ``rationale`` or ``None`` if the
        client is unavailable.
    """
    client = get_client(api_key or os.getenv("OPENAI_API_KEY"))
    if client is None:
        return None

    content = f"Eingabe: {user_input}\nMetriken: {json.dumps(metrics)}"
    messages = []
    if mode_hint:
        messages.append({"role": "system", "content": mode_hint})
    messages.extend(
        [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ]
    )
    functions = [
        {
            "name": "decide_yin_yang_mode",
            "description": "Wähle den Modus yin oder yang",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["yin", "yang"]},
                    "rationale": {"type": "string"},
                },
                "required": ["mode"],
            },
        }
    ]

    try:
        if hasattr(client, "chat"):
            resp = client.chat.completions.create(
                model=MODELS['chat'],
                temperature=TEMPERATURES['chat'],
                messages=messages,
                functions=functions,
                function_call={"name": "decide_yin_yang_mode"},
            )
            choice = resp.choices[0]
            if choice.finish_reason == "function_call":
                fc = choice.message.function_call
                if fc and fc.name == "decide_yin_yang_mode":
                    data = json.loads(fc.arguments)
                    return {
                        "mode": data.get("mode", "yin"),
                        "rationale": data.get("rationale", ""),
                    }
        else:
            resp = client.ChatCompletion.create(
                model=MODELS['chat'],
                temperature=TEMPERATURES['chat'],
                messages=messages,
                functions=functions,
                function_call={"name": "decide_yin_yang_mode"},
            )
            choice = resp["choices"][0]
            if choice.get("finish_reason") == "function_call":
                fc = choice["message"]["function_call"]
                if fc["name"] == "decide_yin_yang_mode":
                    data = json.loads(fc["arguments"])
                    return {
                        "mode": data.get("mode", "yin"),
                        "rationale": data.get("rationale", ""),
                    }
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("mode_decider failed: %s", exc)
    return None
