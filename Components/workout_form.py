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
                "rir": None,
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
                "rir": None if pd.isna(row.get("rir")) else float(row.get("rir")),
            }
        )
    return rows


def workout_editor(
    key: str = "workout_editor",
    initial_data: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Mobile-friendly set entry.

    Instead of a wide data_editor table, each set is rendered as a compact card:
    Exercise
    Weight | Reps | RIR
    Add/remove buttons

    Returns the same DataFrame structure as the old editor, so the rest of the app
    can keep using it without database changes.
    """
    exercises = load_exercises()
    state_key = f"{key}_rows"

    if state_key not in st.session_state:
        st.session_state[state_key] = _normalize_initial_data(initial_data, exercises)

    rows = st.session_state[state_key]

    st.markdown(
        """
        <style>
        .rpl-set-card {
            border: 1px solid #30343b;
            border-radius: 10px;
            padding: 0.55rem 0.7rem 0.3rem 0.7rem;
            margin-bottom: 0.55rem;
            background: #101318;
        }

        .rpl-set-title {
            font-size: 0.82rem;
            font-weight: 700;
            color: #aeb2b9;
            margin-bottom: 0.15rem;
            letter-spacing: 0.02em;
        }

        @media (max-width: 768px) {
            .rpl-set-card {
                padding: 0.5rem 0.55rem 0.2rem 0.55rem;
            }

            .st-key-rpl_set_controls div[data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
                gap: 0.35rem !important;
            }

            .st-key-rpl_set_controls div[data-testid="column"] {
                min-width: 0 !important;
                width: auto !important;
                flex: 1 1 0 !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    output_rows = []

    for idx, row in enumerate(rows):
        st.markdown(
            f'<div class="rpl-set-title">SET {idx + 1}</div>',
            unsafe_allow_html=True,
        )

        exercise = st.selectbox(
            "Exercise",
            exercises,
            index=exercises.index(row["exercise"]) if row["exercise"] in exercises else 0,
            key=f"{key}_exercise_{idx}",
            label_visibility="collapsed",
        )

        with st.container(key="rpl_set_controls"):
            weight_col, reps_col, rir_col = st.columns([1.2, 1, 1])

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

            with rir_col:
                rir_default = row.get("rir")
                rir = st.number_input(
                    "RIR",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.5,
                    value=float(rir_default) if rir_default is not None else 0.0,
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

        st.markdown('<div style="height:0.15rem;"></div>', unsafe_allow_html=True)

    # Keep current input values before changing row count.
    st.session_state[state_key] = output_rows

    add_col, remove_col = st.columns(2)

    with add_col:
        if st.button(
            "＋ Add set",
            use_container_width=True,
            key=f"{key}_add_set",
        ):
            previous = output_rows[-1] if output_rows else {
                "exercise": exercises[0] if exercises else "",
                "weight_kg": 0.0,
                "reps": 0,
                "rir": 0.0,
            }

            st.session_state[state_key].append(
                {
                    "exercise": previous["exercise"],
                    "set_number": len(output_rows) + 1,
                    "weight_kg": previous["weight_kg"],
                    "reps": 0,
                    "rir": previous["rir"],
                }
            )
            st.rerun()

    with remove_col:
        if st.button(
            "− Remove last set",
            use_container_width=True,
            disabled=len(output_rows) <= 1,
            key=f"{key}_remove_set",
        ):
            st.session_state[state_key] = output_rows[:-1]
            st.rerun()

    return pd.DataFrame(output_rows)
