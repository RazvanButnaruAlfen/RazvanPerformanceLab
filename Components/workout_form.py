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
        normalized = name.casefold()
        if normalized not in seen:
            seen.add(normalized)
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
    if initial_data is None or initial_data.empty:
        return [
            {
                "exercise": exercises[0] if exercises else "",
                "sets": [_blank_set()],
            }
        ]

    groups: list[dict] = []
    lookup: dict[str, int] = {}

    for _, row in initial_data.iterrows():
        exercise = str(row.get("exercise", "") or "").strip()
        if not exercise:
            continue

        normalized = exercise.casefold()
        if normalized not in lookup:
            lookup[normalized] = len(groups)
            groups.append({"exercise": exercise, "sets": []})

        rir_value = row.get("rir")
        rir = None if pd.isna(rir_value) else float(rir_value)

        groups[lookup[normalized]]["sets"].append(
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


def _sync_widgets_to_groups(key: str) -> list[dict]:
    """
    Copy the currently visible widget values into our durable editor state.

    This runs from button callbacks BEFORE Streamlit redraws the page. That is
    important: it means adding/removing an exercise cannot wipe values that
    were already typed into earlier exercise cards.
    """
    state_key = f"{key}_groups"
    groups = st.session_state.get(state_key, [])

    synced: list[dict] = []

    for exercise_idx, group in enumerate(groups):
        exercise_widget_key = f"{key}_exercise_{exercise_idx}"
        exercise = st.session_state.get(
            exercise_widget_key,
            group.get("exercise", ""),
        )

        synced_sets: list[dict] = []
        for set_idx, set_row in enumerate(group.get("sets", []) or [_blank_set()]):
            synced_sets.append(
                {
                    "weight_kg": float(
                        st.session_state.get(
                            f"{key}_weight_{exercise_idx}_{set_idx}",
                            set_row.get("weight_kg", 0.0),
                        )
                        or 0.0
                    ),
                    "reps": int(
                        st.session_state.get(
                            f"{key}_reps_{exercise_idx}_{set_idx}",
                            set_row.get("reps", 0),
                        )
                        or 0
                    ),
                    "rir": float(
                        st.session_state.get(
                            f"{key}_rir_{exercise_idx}_{set_idx}",
                            set_row.get("rir", 0.0),
                        )
                        or 0.0
                    ),
                }
            )

        synced.append(
            {
                "exercise": exercise or "",
                "sets": synced_sets,
            }
        )

    st.session_state[state_key] = synced
    return synced


def _add_exercise(key: str, exercises: list[str]) -> None:
    groups = _sync_widgets_to_groups(key)
    groups.append(
        {
            "exercise": _next_default_exercise(groups, exercises),
            "sets": [_blank_set()],
        }
    )
    st.session_state[f"{key}_groups"] = groups
    st.session_state[f"{key}_active_exercise"] = len(groups) - 1


def _add_set(key: str, exercise_idx: int) -> None:
    groups = _sync_widgets_to_groups(key)
    st.session_state[f"{key}_active_exercise"] = exercise_idx
    if exercise_idx >= len(groups):
        return

    previous = groups[exercise_idx]["sets"][-1] if groups[exercise_idx]["sets"] else _blank_set()

    groups[exercise_idx]["sets"].append(
        {
            "weight_kg": previous["weight_kg"],
            "reps": 0,
            "rir": previous["rir"],
        }
    )
    st.session_state[f"{key}_groups"] = groups


def _remove_set(key: str, exercise_idx: int) -> None:
    groups = _sync_widgets_to_groups(key)
    st.session_state[f"{key}_active_exercise"] = exercise_idx
    if exercise_idx >= len(groups):
        return

    if len(groups[exercise_idx]["sets"]) > 1:
        groups[exercise_idx]["sets"].pop()

    st.session_state[f"{key}_groups"] = groups


def _remove_exercise(key: str, exercise_idx: int) -> None:
    groups = _sync_widgets_to_groups(key)

    if len(groups) <= 1 or exercise_idx >= len(groups):
        return

    groups.pop(exercise_idx)
    st.session_state[f"{key}_groups"] = groups
    st.session_state[f"{key}_active_exercise"] = min(
        exercise_idx,
        max(0, len(groups) - 1),
    )

    # Exercise indices shift after deletion. Remove old widget keys so Streamlit
    # rebuilds the remaining cards from the synchronized group data.
    prefixes = (
        f"{key}_exercise_",
        f"{key}_weight_",
        f"{key}_reps_",
        f"{key}_rir_",
    )
    for session_key in list(st.session_state.keys()):
        if session_key.startswith(prefixes):
            del st.session_state[session_key]


def workout_editor(
    key: str = "workout_editor",
    initial_data: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Exercise-first workout editor.

    Select each exercise once and enter all of its sets underneath it.
    The returned DataFrame remains compatible with the existing database:
        exercise | set_number | weight_kg | reps | rir
    """
    exercises = load_exercises()
    state_key = f"{key}_groups"

    if state_key not in st.session_state:
        st.session_state[state_key] = _normalize_initial_data(initial_data, exercises)

    active_key = f"{key}_active_exercise"
    if active_key not in st.session_state:
        st.session_state[active_key] = max(0, len(st.session_state[state_key]) - 1)

    groups = st.session_state[state_key]
    active_exercise = min(
        int(st.session_state.get(active_key, 0)),
        max(0, len(groups) - 1),
    )

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

        div[data-testid="stExpander"]:has(.rpl-exercise-card-title) {
            background:
                radial-gradient(circle at 8% 0%, rgba(255, 42, 35, 0.09), transparent 31%),
                #101318;
            border: 1px solid #30343b !important;
            border-radius: 12px !important;
        }

        div[data-testid="stExpander"] summary {
            font-weight: 800 !important;
        }

        @media (max-width: 768px) {
            .rpl-exercise-card-title {
                font-size: 0.76rem;
                margin-bottom: 0.25rem;
            }

            div[class*="st-key-"][class*="_set_row_"] div[data-testid="stHorizontalBlock"],
            div[class*="st-key-"][class*="_exercise_actions_"] div[data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
                gap: 0.35rem !important;
            }

            div[class*="st-key-"][class*="_set_row_"] div[data-testid="column"],
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

    output_rows: list[dict] = []

    for exercise_idx, group in enumerate(groups):
        current_exercise = str(group.get("exercise", "") or "")
        exercise_label = current_exercise.strip() or f"Exercise {exercise_idx + 1}"

        with st.expander(
            f"{exercise_idx + 1}. {exercise_label}",
            expanded=(exercise_idx == active_exercise),
        ):
            st.markdown(
                f'<div class="rpl-exercise-card-title">Exercise {exercise_idx + 1}</div>',
                unsafe_allow_html=True,
            )

            exercise_index = exercises.index(current_exercise) if current_exercise in exercises else 0

            selected_exercise = st.selectbox(
                "Exercise",
                exercises,
                index=exercise_index if exercises else None,
                key=f"{key}_exercise_{exercise_idx}",
                placeholder="Select exercise",
            )

            current_sets = group.get("sets") or [_blank_set()]

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

                output_rows.append(
                    {
                        "exercise": selected_exercise or "",
                        "set_number": set_idx + 1,
                        "weight_kg": weight,
                        "reps": reps,
                        "rir": rir,
                    }
                )

            with st.container(key=f"{key}_exercise_actions_{exercise_idx}"):
                add_set_col, remove_set_col, remove_exercise_col = st.columns(3)

                with add_set_col:
                    st.button(
                        "＋ Add set",
                        use_container_width=True,
                        key=f"{key}_add_set_{exercise_idx}",
                        on_click=_add_set,
                        args=(key, exercise_idx),
                    )

                with remove_set_col:
                    st.button(
                        "− Set",
                        use_container_width=True,
                        disabled=len(current_sets) <= 1,
                        key=f"{key}_remove_set_{exercise_idx}",
                        on_click=_remove_set,
                        args=(key, exercise_idx),
                    )

                with remove_exercise_col:
                    st.button(
                        "✕ Exercise",
                        use_container_width=True,
                        disabled=len(groups) <= 1,
                        key=f"{key}_remove_exercise_{exercise_idx}",
                        on_click=_remove_exercise,
                        args=(key, exercise_idx),
                    )

        st.markdown('<div style="height:0.35rem;"></div>', unsafe_allow_html=True)

    st.button(
        "＋ Add exercise",
        type="secondary",
        use_container_width=True,
        key=f"{key}_add_exercise",
        on_click=_add_exercise,
        args=(key, exercises),
    )

    # Synchronize the rendered widget values back into the editor data on every run.
    # This keeps the DataFrame returned to the Save Workout button current.
    synced_groups = []
    for exercise_idx, group in enumerate(st.session_state[state_key]):
        exercise = st.session_state.get(
            f"{key}_exercise_{exercise_idx}",
            group.get("exercise", ""),
        )
        synced_sets = []

        for set_idx, set_row in enumerate(group.get("sets", []) or [_blank_set()]):
            synced_sets.append(
                {
                    "weight_kg": float(
                        st.session_state.get(
                            f"{key}_weight_{exercise_idx}_{set_idx}",
                            set_row.get("weight_kg", 0.0),
                        )
                        or 0.0
                    ),
                    "reps": int(
                        st.session_state.get(
                            f"{key}_reps_{exercise_idx}_{set_idx}",
                            set_row.get("reps", 0),
                        )
                        or 0
                    ),
                    "rir": float(
                        st.session_state.get(
                            f"{key}_rir_{exercise_idx}_{set_idx}",
                            set_row.get("rir", 0.0),
                        )
                        or 0.0
                    ),
                }
            )

        synced_groups.append({"exercise": exercise or "", "sets": synced_sets})

    st.session_state[state_key] = synced_groups

    # Rebuild output rows from the synchronized state so Save Workout always sees
    # the latest values, even on a button-triggered rerun.
    output_rows = []
    for group in synced_groups:
        for set_idx, set_row in enumerate(group["sets"]):
            output_rows.append(
                {
                    "exercise": group["exercise"],
                    "set_number": set_idx + 1,
                    "weight_kg": set_row["weight_kg"],
                    "reps": set_row["reps"],
                    "rir": set_row["rir"],
                }
            )

    return pd.DataFrame(
        output_rows,
        columns=["exercise", "set_number", "weight_kg", "reps", "rir"],
    )
