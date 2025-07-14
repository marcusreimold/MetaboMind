"""Compatibility wrappers for the legacy module name."""
from __future__ import annotations

from typing import Dict, Literal

from .metabo_engine import run_metabo_cycle, handle_user_input, metabo_tick

__all__ = ["run_metabo_cycle", "handle_user_input", "metabo_tick"]
