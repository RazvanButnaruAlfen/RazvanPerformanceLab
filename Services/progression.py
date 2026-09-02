from __future__ import annotations

import pandas as pd


def next_target_message(df: pd.DataFrame, exercise: str, rep_min: int = 6, rep_max: int = 10) -> str:
    """
    Simple double-progression suggestion:
    - If every set at the top working weight reaches rep_max, suggest a small load increase.
    - Otherwise suggest adding reps while staying in the target range.
    """
    if df.empty:
        return "No previous data yet. Log your first session."

    ex = df[df["exercise"] == exercise].copy()
    if ex.empty:
        return "No previous data yet for this exercise."

    ex["workout_date"] = pd.to_datetime(ex["workout_date"])
    latest_date = ex["workout_date"].max()
    latest = ex[ex["workout_date"] == latest_date].copy()

    top_weight = latest["weight_kg"].max()
    top_sets = latest[latest["weight_kg"] == top_weight]
    reps = top_sets["reps"].tolist()

    if reps and all(r >= rep_max for r in reps):
        return (
            f"All top-weight sets reached {rep_max}+ reps at {top_weight:g} kg. "
            "Consider a small load increase next session."
        )

    if any(r < rep_min for r in reps):
        return (
            f"At {top_weight:g} kg, at least one top set fell below {rep_min} reps. "
            "Keep the load or reduce slightly and rebuild reps."
        )

    return (
        f"Keep {top_weight:g} kg as the main load and try to add reps "
        f"until your working sets approach {rep_max} reps."
    )
