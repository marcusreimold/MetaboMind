from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from textblob import TextBlob

logger = logging.getLogger(__name__)


class YinYangOrchestrator:
    """Manage Yin/Yang mode switching based on context metrics."""

    def __init__(self, heartbeat: int | None = None) -> None:
        self._mode = "yang"
        self._override: str | None = None
        self._deltas: List[float] = []
        self._history: List[str] = []
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

    def decide_mode(
        self,
        context_metrics: Dict[str, float],
        user_input: str,
        subgoal_count: int = 0,
    ) -> str:
        """Return ``'yin'`` or ``'yang'`` based on multiple indicators."""

        if self._override:
            return self._override

        delta = context_metrics.get("entropy_delta", 0.0)
        self._deltas.append(delta)
        if len(self._deltas) > 5:
            self._deltas.pop(0)
        trend = sum(self._deltas) / len(self._deltas)
        emotion = context_metrics.get("emotion", "")

        text = user_input.lower()

        # ----------------------------------
        # indicator collection
        yin_votes = 0

        # negative or uncertain sentiment
        try:
            polarity = TextBlob(text).sentiment.polarity
        except Exception:  # pragma: no cover - sentiment failed
            polarity = 0.0
        if polarity < -0.1:
            yin_votes += 1

        # explicit emotion metric
        if isinstance(emotion, str) and emotion.lower() in {"negative", "unsicher"}:
            yin_votes += 1

        # sentiment already captures vague expressions; explicit regex no longer used

        # entropy trend
        if trend > 0.1:
            yin_votes += 1

        # negative or very small delta
        if delta < 0 or abs(delta) < 0.01:
            yin_votes += 1

        # few completed subgoals
        if subgoal_count < 2:
            yin_votes += 1

        # cumulative yin tendency
        if len(self._history) >= 3 and len(set(self._history[-3:])) == 1:
            yin_votes += 1

        # ----------------------------------
        if "/takt" in text or "denk" in text or "reflekt" in text:
            mode = "yin"
        elif "aktion" in text or "mach" in text or "tu was" in text:
            mode = "yang"
        else:
            mode = "yin" if yin_votes > 2 else "yang"

        if self._heartbeat and self._next_beat and datetime.utcnow() >= self._next_beat:
            self._next_beat = datetime.utcnow() + timedelta(seconds=self._heartbeat)
            mode = "yin" if mode == "yang" else "yang"
            logger.info("Heartbeat toggled mode to %s", mode)

        print(
            f"[Modus-Entscheidung] Grund: emotion={emotion}, delta={delta:.2f} → {mode.upper()}"
        )

        self._mode = mode
        self._history.append(mode)
        if len(self._history) > 5:
            self._history.pop(0)

        return self._mode


# Shared orchestrator ---------------------------------------------------
_ORCHESTRATOR = YinYangOrchestrator()

def decide_mode(
    context_metrics: Dict[str, float], user_input: str, subgoal_count: int = 0
) -> str:
    return _ORCHESTRATOR.decide_mode(context_metrics, user_input, subgoal_count)

def current_mode() -> str:
    return _ORCHESTRATOR.mode

def set_mode(mode: str) -> None:
    _ORCHESTRATOR.set_mode(mode)
