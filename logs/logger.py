"""Structured cycle logging for MetaboMind."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


class MetaboLogger:
    """Append JSON lines with cycle information to a log file."""

    def __init__(self, filepath: str = "logs/metabo_log.jsonl") -> None:
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def log_cycle(
        self,
        *,
        input_text: str,
        reflection: str,
        triplets: List[Tuple[str, str, str]],
        ent_before: float,
        ent_after: float,
        emotion: str,
        intensity: str,
    ) -> None:
        """Write one cycle entry in JSON Lines format."""
        delta = ent_after - ent_before
        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "input_text": input_text,
            "reflection": reflection,
            "triplets": [list(t) for t in triplets],
            "entropy_before": ent_before,
            "entropy_after": ent_after,
            "delta": delta,
            "emotion": emotion,
            "intensity": intensity,
        }
        with self.filepath.open("a", encoding="utf-8", newline="\n") as fh:
            json.dump(record, fh, ensure_ascii=False)
            fh.write("\n")

