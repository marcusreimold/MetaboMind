"""Abstraktion der OpenAI API für Textgenerierung."""

import openai
import os

class LLMInterface:
    """Wrapper for OpenAI ChatCompletion API."""

    def __init__(self, api_key: str | None = None):
        """Initialise API key from argument or environment."""
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY", "")
        openai.api_key = api_key

    def generate(self, messages, functions=None):
        """Send message list to the ChatCompletion API.

        If ``functions`` is provided, the API may return a function call which
        is returned as a dict::
            {"function_call": {"name": str, "arguments": str}}
        Otherwise the assistant message text is returned.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                functions=functions,
                function_call="auto" if functions else None,
            )
            choice = response.choices[0]
            if choice.finish_reason == "function_call":
                call = choice.message.function_call
                return {"function_call": {"name": call.name, "arguments": call.arguments}}
            # plain assistant message text
            return choice.message.content
        except Exception as exc:
            return f"Fehler bei LLM-Anfrage: {exc}"
