from datetime import date

import streamlit as st

from Components.session_timer import render_session_timer
from Components.workout_form import load_exercises, workout_editor
from Services.database import add_user_exercise, init_db, save_workout


def _version() -> int:
    return int(st.session_state.get("workout_form_version", 0))


def _reset_workout_form():
    st.session_state["workout_form_version"] = _version() + 1


def render():
    init_db()

    if st.session_state.pop("workout_saved_flash", False):
        st.success("Workout saved. The form has been cleared for a new workout.")

    st.subheader("Log Workout")
    st.caption("Record working sets so each session can be compared with the previous one.")

    render_session_timer()

    version = _version()

    with st.expander("➕ Add a new exercise"):
        new_exercise = st.text_input(
            "Exercise name",
            placeholder="e.g. Chest-Supported Dumbbell Row",
            key=f"new_exercise_{version}",
        )

        clean_name = " ".join(new_exercise.strip().split())
        existing = load_exercises()
        exists = clean_name.casefold() in {name.casefold() for name in existing} if clean_name else False

        if clean_name:
            if exists:
                st.info(f"“{clean_name}” is already in your exercise list.")
            else:
                st.caption(
                    f"“{clean_name}” is not in your list yet. "
                    "Add it and it will become available in the workout table."
                )
                if st.button(
                    f"Add “{clean_name}”",
                    type="primary",
                    key=f"add_exercise_button_{version}",
                ):
                    add_user_exercise(clean_name)
                    st.session_state["exercise_added_flash"] = clean_name
                    _reset_workout_form()
                    st.rerun()

    added = st.session_state.pop("exercise_added_flash", None)
    if added:
        st.success(f"Added “{added}” to your exercise list.")

    col1, col2 = st.columns([1, 2])

    with col1:
        workout_date = st.date_input(
            "Workout date",
            value=date.today(),
            key=f"log_workout_date_{version}",
        )

    with col2:
        workout_name = st.text_input(
            "Workout name",
            placeholder="e.g. Push / Chest + Shoulders + Triceps",
            key=f"log_workout_name_{version}",
        )

    st.markdown("### Sets")
    edited = workout_editor(key=f"main_workout_editor_{version}")

    notes = st.text_area(
        "Workout notes",
        placeholder="DOMS, energy, unusual performance, etc.",
        key=f"log_workout_notes_{version}",
    )

    if st.button(
        "Save workout",
        type="primary",
        use_container_width=True,
        key=f"save_workout_button_{version}",
    ):
        clean = edited.copy()
        clean = clean.dropna(subset=["exercise", "weight_kg", "reps"])
        clean = clean[clean["exercise"].astype(str).str.strip() != ""]
        clean = clean[clean["reps"] > 0]

        if clean.empty:
            st.error("Add at least one valid set with an exercise and reps.")
        else:
            rows = clean.to_dict(orient="records")
            save_workout(
                workout_date,
                workout_name,
                notes,
                rows,
            )

            # The new version gives every widget a fresh key, which clears the form.
            st.session_state["workout_saved_flash"] = True
            _reset_workout_form()
            st.rerun()
