from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


def load_exercises() -> list[str]:
    path = Path("Data/exercises.json")
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["name"] for item in data]


def workout_editor(key: str = "workout_editor") -> pd.DataFrame:
    exercises = load_exercises()

    starter = pd.DataFrame(
        [
            {
                "exercise": exercises[0] if exercises else "",
                "set_number": 1,
                "weight_kg": 0.0,
                "reps": 0,
                "rir": None,
            }
        ]
    )

    return st.data_editor(
        starter,
        num_rows="dynamic",
        use_container_width=True,
        key=key,
        column_config={
            "exercise": st.column_config.SelectboxColumn(
                "Exercise",
                options=exercises,
                required=True,
            ),
            "set_number": st.column_config.NumberColumn(
                "Set", min_value=1, step=1, required=True
            ),
            "weight_kg": st.column_config.NumberColumn(
                "Weight (kg)", min_value=0.0, step=0.5, format="%.1f", required=True
            ),
            "reps": st.column_config.NumberColumn(
                "Reps", min_value=0, step=1, required=True
            ),
            "rir": st.column_config.NumberColumn(
                "RIR", min_value=0.0, max_value=10.0, step=0.5, format="%.1f"
            ),
        },
    )
