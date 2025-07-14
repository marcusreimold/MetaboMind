from __future__ import annotations

from typing import Dict

from control.metabo_engine import metabo_tick


def run_metabotakt(api_key: str | None = None) -> Dict[str, object]:
    """Execute a MetaboTakt via the unified engine."""
    return metabo_tick(api_key=api_key)
