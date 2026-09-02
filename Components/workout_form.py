from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from Services.database import get_user_exercises


def load_default_exercises() -> list[str]:
    path = Path("Data/exercises.json")
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return [item["name"] for item in data]


def load_exercises() -> list[str]:
    default_exercises = load_default_exercises()
    custom_exercises = get_user_exercises()

    combined = []
    seen = set()

    for name in default_exercises + custom_exercises:
        key = name.casefold()
        if key not in seen:
            seen.add(key)
            combined.append(name)

    return sorted(combined, key=str.casefold)


def workout_editor(
    key: str = "workout_editor",
    initial_data: pd.DataFrame | None = None,
) -> pd.DataFrame:
    exercises = load_exercises()

    if initial_data is None:
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
    else:
        starter = initial_data.copy()

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
                width="large",
            ),
            "set_number": st.column_config.NumberColumn(
                "Set",
                min_value=1,
                step=1,
                required=True,
                width="small",
            ),
            "weight_kg": st.column_config.NumberColumn(
                "Weight (kg)",
                min_value=0.0,
                step=0.5,
                format="%.1f",
                required=True,
                width="small",
            ),
            "reps": st.column_config.NumberColumn(
                "Reps",
                min_value=0,
                step=1,
                required=True,
                width="small",
            ),
            "rir": st.column_config.NumberColumn(
                "RIR",
                min_value=0.0,
                max_value=10.0,
                step=0.5,
                format="%.1f",
                width="small",
            ),
        },
    )
