import json
import re
from typing import Any, Optional


def parse_json_safe(text: str) -> Optional[Any]:
    """Try to parse JSON from an LLM response string.

    Removes code fences and extracts the first JSON object or array if necessary.
    Returns ``None`` if no valid JSON could be extracted.
    """
    stripped = text.strip()

    # Remove markdown code fences
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        # Drop first and last lines
        if len(lines) >= 3:
            first = lines[0].strip().lower()
            if first.startswith("```json"):
                lines = lines[1:-1]
            else:
                lines = lines[1:-1]
            stripped = "\n".join(lines)

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", stripped, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None
