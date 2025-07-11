from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)


class YinYangOrchestrator:
    """Manage Yin/Yang mode switching based on context metrics."""

    def __init__(self, heartbeat: int | None = None) -> None:
        self._mode = "yang"
        self._override: str | None = None
        self._deltas: List[float] = []
        self._heartbeat = heartbeat or 0
        self._next_beat = (
            datetime.utcnow() + timedelta(seconds=self._heartbeat)
            if self._heartbeat
            else None
        )

    # ------------------------------------------------------------------
    # Mode helpers
    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        """Manually overwrite the current mode."""
        if mode.lower() in {"yin", "yang"}:
            self._mode = mode.lower()
            self._override = self._mode
            logger.info("Mode manually set to %s", self._mode)

    def decide_mode(self, context_metrics: Dict[str, float], user_input: str) -> str:
        """Return 'yin' or 'yang' according to entropy trend and hints."""
        if self._override:
            return self._override

        delta = context_metrics.get("entropy_delta", 0.0)
        self._deltas.append(delta)
        if len(self._deltas) > 5:
            self._deltas.pop(0)
        trend = sum(self._deltas) / len(self._deltas)

        text = user_input.lower()

        if "/takt" in text or "denk" in text or "reflekt" in text:
            self._mode = "yin"
        elif "aktion" in text or "mach" in text or "tu was" in text:
            self._mode = "yang"
        else:
            if trend > 0.1:
                self._mode = "yin"
            elif trend < -0.1:
                self._mode = "yang"

        if self._heartbeat and self._next_beat and datetime.utcnow() >= self._next_beat:
            self._next_beat = datetime.utcnow() + timedelta(seconds=self._heartbeat)
            self._mode = "yin" if self._mode == "yang" else "yang"
            logger.info("Heartbeat toggled mode to %s", self._mode)

        return self._mode


# Shared orchestrator ---------------------------------------------------
_ORCHESTRATOR = YinYangOrchestrator()

def decide_mode(context_metrics: Dict[str, float], user_input: str) -> str:
    return _ORCHESTRATOR.decide_mode(context_metrics, user_input)

def current_mode() -> str:
    return _ORCHESTRATOR.mode

def set_mode(mode: str) -> None:
    _ORCHESTRATOR.set_mode(mode)
