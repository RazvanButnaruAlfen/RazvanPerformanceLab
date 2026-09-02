from __future__ import annotations

import pandas as pd


def estimated_1rm(weight_kg: float, reps: int) -> float:
    """Epley estimated 1RM."""
    if reps <= 0:
        return 0.0
    if reps == 1:
        return float(weight_kg)
    return float(weight_kg) * (1 + reps / 30.0)


def add_set_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    out = df.copy()
    out["volume_kg"] = out["weight_kg"] * out["reps"]
    out["estimated_1rm"] = out.apply(
        lambda r: estimated_1rm(r["weight_kg"], int(r["reps"])), axis=1
    )
    return out


def exercise_summary(df: pd.DataFrame, exercise: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    data = add_set_metrics(df)
    data = data[data["exercise"] == exercise].copy()
    if data.empty:
        return data

    data["workout_date"] = pd.to_datetime(data["workout_date"])
    summary = (
        data.groupby(["workout_id", "workout_date"], as_index=False)
        .agg(
            top_weight_kg=("weight_kg", "max"),
            best_e1rm=("estimated_1rm", "max"),
            total_reps=("reps", "sum"),
            total_volume_kg=("volume_kg", "sum"),
        )
        .sort_values("workout_date")
    )
    return summary
