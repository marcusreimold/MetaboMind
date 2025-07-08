"""Score subgoals by estimated feasibility."""
from __future__ import annotations

from typing import Dict, List


def score_subgoals(subgoals: List[str]) -> Dict[str, float]:
    """Return a feasibility score between 0 and 1 for each subgoal."""
    scores: Dict[str, float] = {}
    for sg in subgoals:
        length = len(sg)
        if length <= 10:
            score = 0.7
        elif length <= 40:
            score = 1.0
        elif length <= 80:
            score = 0.8
        else:
            score = 0.5
        scores[sg] = round(min(max(score, 0.0), 1.0), 2)
    return scores
