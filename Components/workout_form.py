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


def _normalize_initial_data(
    initial_data: pd.DataFrame | None,
    exercises: list[str],
) -> list[dict]:
    if initial_data is None or initial_data.empty:
        return [
            {
                "exercise": exercises[0] if exercises else "",
                "set_number": 1,
                "weight_kg": 0.0,
                "reps": 0,
                "rir": 0.0,
            }
        ]

    rows = []
    for _, row in initial_data.iterrows():
        rows.append(
            {
                "exercise": str(row.get("exercise", "")),
                "set_number": int(row.get("set_number", len(rows) + 1)),
                "weight_kg": float(row.get("weight_kg", 0.0) or 0.0),
                "reps": int(row.get("reps", 0) or 0),
                "rir": 0.0 if pd.isna(row.get("rir")) else float(row.get("rir")),
            }
        )
    return rows


def _mobile_editor(
    key: str,
    initial_data: pd.DataFrame | None,
    exercises: list[str],
) -> pd.DataFrame:
    state_key = f"{key}_rows"

    if state_key not in st.session_state:
        st.session_state[state_key] = _normalize_initial_data(initial_data, exercises)

    rows = st.session_state[state_key]
    output_rows = []

    for idx, row in enumerate(rows):
        st.markdown(f"#### Set {idx + 1}")

        exercise_index = (
            exercises.index(row["exercise"])
            if row.get("exercise") in exercises
            else 0
        )

        exercise = st.selectbox(
            "Exercise",
            exercises,
            index=exercise_index,
            key=f"{key}_exercise_{idx}",
        )

        weight_col, reps_col = st.columns([1.35, 0.65], gap="small")

        with weight_col:
            weight = st.number_input(
                "Weight (kg)",
                min_value=0.0,
                step=0.5,
                value=float(row.get("weight_kg", 0.0)),
                format="%.1f",
                key=f"{key}_weight_{idx}",
            )

        with reps_col:
            reps = st.number_input(
                "Reps",
                min_value=0,
                step=1,
                value=int(row.get("reps", 0)),
                key=f"{key}_reps_{idx}",
            )

        rir = st.number_input(
            "RIR",
            min_value=0.0,
            max_value=10.0,
            step=0.5,
            value=float(row.get("rir", 0.0)),
            format="%.1f",
            key=f"{key}_rir_{idx}",
        )

        output_rows.append(
            {
                "exercise": exercise,
                "set_number": idx + 1,
                "weight_kg": weight,
                "reps": reps,
                "rir": rir,
            }
        )

        st.divider()

    st.session_state[state_key] = output_rows

    add_col, remove_col = st.columns(2, gap="small")

    with add_col:
        if st.button(
            "＋ Add set",
            key=f"{key}_add_set",
            use_container_width=True,
        ):
            prev = output_rows[-1]
            st.session_state[state_key].append(
                {
                    "exercise": prev["exercise"],
                    "set_number": len(output_rows) + 1,
                    "weight_kg": prev["weight_kg"],
                    "reps": 0,
                    "rir": prev["rir"],
                }
            )
            st.rerun()

    with remove_col:
        if st.button(
            "− Remove",
            key=f"{key}_remove_set",
            use_container_width=True,
            disabled=len(output_rows) <= 1,
        ):
            st.session_state[state_key] = output_rows[:-1]
            st.rerun()

    return pd.DataFrame(output_rows)


def _desktop_editor(
    key: str,
    initial_data: pd.DataFrame | None,
    exercises: list[str],
) -> pd.DataFrame:
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


def workout_editor(
    key: str = "workout_editor",
    initial_data: pd.DataFrame | None = None,
) -> pd.DataFrame:
    exercises = load_exercises()
    mobile = bool(st.session_state.get("is_mobile", False))

    if mobile:
        return _mobile_editor(key, initial_data, exercises)

    return _desktop_editor(key, initial_data, exercises)
