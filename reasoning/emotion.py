"""Interpret entropy change as emotional feedback."""
from __future__ import annotations


def interpret_emotion(ent_before: float, ent_after: float) -> dict:
    """Return an emotion assessment based on entropy difference.

    Parameters
    ----------
    ent_before : float
        Entropy value before the cycle.
    ent_after : float
        Entropy value after the cycle.

    Returns
    -------
    dict
        Dictionary containing the delta, qualitative emotion and intensity.
    """
    delta = ent_after - ent_before

    # Determine emotion polarity
    if delta <= -0.05:
        emotion = "positive"
    elif delta >= 0.05:
        emotion = "negative"
    else:
        emotion = "neutral"

    # Determine intensity based on absolute delta
    abs_delta = abs(delta)
    if abs_delta < 0.05:
        intensity = "low"
    elif abs_delta <= 0.15:
        intensity = "medium"
    else:
        intensity = "high"

    return {"delta": delta, "emotion": emotion, "intensity": intensity}


if __name__ == "__main__":
    # Simple manual test
    example = interpret_emotion(0.82, 0.45)
    print(example)
