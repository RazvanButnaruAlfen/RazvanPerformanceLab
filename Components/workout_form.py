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


def _blank_set(
    weight_kg: float = 0.0,
    reps: int = 0,
    rir: float | None = 0.0,
) -> dict:
    return {
        "weight_kg": float(weight_kg or 0.0),
        "reps": int(reps or 0),
        "rir": 0.0 if rir is None else float(rir),
    }


def _normalize_initial_data(
    initial_data: pd.DataFrame | None,
    exercises: list[str],
) -> list[dict]:
    """
    Convert the existing flat workout rows into exercise groups.

    The database format remains unchanged. This grouping exists only for
    the workout-entry UI.
    """
    if initial_data is None or initial_data.empty:
        return [
            {
                "exercise": exercises[0] if exercises else "",
                "sets": [_blank_set()],
            }
        ]

    groups: list[dict] = []
    group_lookup: dict[str, int] = {}

    for _, row in initial_data.iterrows():
        exercise = str(row.get("exercise", "") or "").strip()
        if not exercise:
            continue

        key = exercise.casefold()

        if key not in group_lookup:
            group_lookup[key] = len(groups)
            groups.append(
                {
                    "exercise": exercise,
                    "sets": [],
                }
            )

        rir_value = row.get("rir")
        rir = None if pd.isna(rir_value) else float(rir_value)

        groups[group_lookup[key]]["sets"].append(
            _blank_set(
                weight_kg=float(row.get("weight_kg", 0.0) or 0.0),
                reps=int(row.get("reps", 0) or 0),
                rir=rir,
            )
        )

    if not groups:
        return [
            {
                "exercise": exercises[0] if exercises else "",
                "sets": [_blank_set()],
            }
        ]

    for group in groups:
        if not group["sets"]:
            group["sets"] = [_blank_set()]

    return groups


def _next_default_exercise(groups: list[dict], exercises: list[str]) -> str:
    selected = {
        str(group.get("exercise", "")).casefold()
        for group in groups
        if group.get("exercise")
    }

    for exercise in exercises:
        if exercise.casefold() not in selected:
            return exercise

    return exercises[0] if exercises else ""


def workout_editor(
    key: str = "workout_editor",
    initial_data: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Exercise-first workout editor.

    An exercise is selected once, then all of its sets are entered underneath it.
    The returned value is still the same flat DataFrame used by the rest of the
    app/database:

        exercise | set_number | weight_kg | reps | rir

    No database changes are required.
    """
    exercises = load_exercises()
    state_key = f"{key}_groups"

    if state_key not in st.session_state:
        st.session_state[state_key] = _normalize_initial_data(initial_data, exercises)

    groups = st.session_state[state_key]

    st.markdown(
        """
        <style>
        .rpl-exercise-card-title {
            margin-top: 0.2rem;
            margin-bottom: 0.4rem;
            color: #ffffff;
            font-size: 0.80rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .rpl-set-title {
            color: #aeb2b9;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            margin-top: 0.25rem;
            margin-bottom: -0.25rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.rpl-exercise-card-title) {
            background:
                radial-gradient(circle at 8% 0%, rgba(255, 42, 35, 0.09), transparent 31%),
                #101318;
            border-color: #30343b !important;
        }

        @media (max-width: 768px) {
            .rpl-exercise-card-title {
                font-size: 0.76rem;
                margin-bottom: 0.25rem;
            }

            div[class*="st-key-"][class*="_set_row_"] div[data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
                gap: 0.35rem !important;
            }

            div[class*="st-key-"][class*="_set_row_"] div[data-testid="column"] {
                min-width: 0 !important;
                width: auto !important;
                flex: 1 1 0 !important;
            }

            div[class*="st-key-"][class*="_exercise_actions_"] div[data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
                gap: 0.35rem !important;
            }

            div[class*="st-key-"][class*="_exercise_actions_"] div[data-testid="column"] {
                min-width: 0 !important;
                width: auto !important;
                flex: 1 1 0 !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    output_groups: list[dict] = []
    output_rows: list[dict] = []

    for exercise_idx, group in enumerate(groups):
        with st.container(border=True):
            st.markdown(
                f'<div class="rpl-exercise-card-title">Exercise {exercise_idx + 1}</div>',
                unsafe_allow_html=True,
            )

            current_exercise = str(group.get("exercise", "") or "")
            exercise_index = (
                exercises.index(current_exercise)
                if current_exercise in exercises
                else 0
            )

            selected_exercise = st.selectbox(
                "Exercise",
                exercises,
                index=exercise_index if exercises else None,
                key=f"{key}_exercise_{exercise_idx}",
                placeholder="Select exercise",
            )

            current_sets = group.get("sets") or [_blank_set()]
            updated_sets: list[dict] = []

            for set_idx, set_row in enumerate(current_sets):
                st.markdown(
                    f'<div class="rpl-set-title">Set {set_idx + 1}</div>',
                    unsafe_allow_html=True,
                )

                with st.container(key=f"{key}_set_row_{exercise_idx}_{set_idx}"):
                    weight_col, reps_col, rir_col = st.columns([1.2, 1, 1])

                    with weight_col:
                        weight = st.number_input(
                            "Weight (kg)",
                            min_value=0.0,
                            step=0.5,
                            value=float(set_row.get("weight_kg", 0.0)),
                            format="%.1f",
                            key=f"{key}_weight_{exercise_idx}_{set_idx}",
                        )

                    with reps_col:
                        reps = st.number_input(
                            "Reps",
                            min_value=0,
                            step=1,
                            value=int(set_row.get("reps", 0)),
                            key=f"{key}_reps_{exercise_idx}_{set_idx}",
                        )

                    with rir_col:
                        rir = st.number_input(
                            "RIR",
                            min_value=0.0,
                            max_value=10.0,
                            step=0.5,
                            value=float(set_row.get("rir", 0.0) or 0.0),
                            format="%.1f",
                            key=f"{key}_rir_{exercise_idx}_{set_idx}",
                        )

                updated_sets.append(
                    {
                        "weight_kg": weight,
                        "reps": reps,
                        "rir": rir,
                    }
                )

                output_rows.append(
                    {
                        "exercise": selected_exercise or "",
                        "set_number": set_idx + 1,
                        "weight_kg": weight,
                        "reps": reps,
                        "rir": rir,
                    }
                )

            output_groups.append(
                {
                    "exercise": selected_exercise or "",
                    "sets": updated_sets,
                }
            )

            with st.container(key=f"{key}_exercise_actions_{exercise_idx}"):
                add_set_col, remove_set_col, remove_exercise_col = st.columns(3)

                with add_set_col:
                    if st.button(
                        "＋ Add set",
                        use_container_width=True,
                        key=f"{key}_add_set_{exercise_idx}",
                    ):
                        # Persist everything already typed before changing the shape.
                        st.session_state[state_key] = output_groups + groups[len(output_groups):]

                        previous = updated_sets[-1] if updated_sets else _blank_set()
                        st.session_state[state_key][exercise_idx]["sets"].append(
                            {
                                # Copy the previous weight and RIR to speed up logging.
                                "weight_kg": previous["weight_kg"],
                                "reps": 0,
                                "rir": previous["rir"],
                            }
                        )
                        st.rerun()

                with remove_set_col:
                    if st.button(
                        "− Set",
                        use_container_width=True,
                        disabled=len(updated_sets) <= 1,
                        key=f"{key}_remove_set_{exercise_idx}",
                    ):
                        st.session_state[state_key] = output_groups + groups[len(output_groups):]
                        st.session_state[state_key][exercise_idx]["sets"] = updated_sets[:-1]
                        st.rerun()

                with remove_exercise_col:
                    if st.button(
                        "✕ Exercise",
                        use_container_width=True,
                        disabled=len(groups) <= 1,
                        key=f"{key}_remove_exercise_{exercise_idx}",
                    ):
                        st.session_state[state_key] = output_groups + groups[len(output_groups):]
                        del st.session_state[state_key][exercise_idx]
                        st.rerun()

        st.markdown('<div style="height:0.35rem;"></div>', unsafe_allow_html=True)

    # Keep all current widget values synchronized in session state.
    st.session_state[state_key] = output_groups

    if st.button(
        "＋ Add exercise",
        type="secondary",
        use_container_width=True,
        key=f"{key}_add_exercise",
    ):
        next_exercise = _next_default_exercise(output_groups, exercises)
        st.session_state[state_key].append(
            {
                "exercise": next_exercise,
                "sets": [_blank_set()],
            }
        )
        st.rerun()

    return pd.DataFrame(
        output_rows,
        columns=["exercise", "set_number", "weight_kg", "reps", "rir"],
    )
