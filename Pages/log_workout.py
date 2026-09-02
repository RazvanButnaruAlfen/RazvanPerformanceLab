from datetime import date

import streamlit as st

from Components.workout_form import workout_editor
from Services.database import init_db, save_workout, using_supabase


def render():
    init_db()

    st.subheader("Log Workout")
    st.caption("Record working sets so each session can be compared with the previous one.")

    col1, col2 = st.columns([1, 2])

    with col1:
        workout_date = st.date_input(
            "Workout date",
            value=date.today(),
            key="log_workout_date",
        )

    with col2:
        workout_name = st.text_input(
            "Workout name",
            placeholder="e.g. Push / Chest + Shoulders + Triceps",
            key="log_workout_name",
        )

    st.markdown("### Sets")
    edited = workout_editor(key="main_workout_editor")

    notes = st.text_area(
        "Workout notes",
        placeholder="DOMS, energy, unusual performance, etc.",
        key="log_workout_notes",
    )

    if st.button(
        "Save workout",
        type="primary",
        use_container_width=True,
        key="save_workout_button",
    ):
        clean = edited.copy()
        clean = clean.dropna(subset=["exercise", "weight_kg", "reps"])
        clean = clean[clean["exercise"].astype(str).str.strip() != ""]
        clean = clean[clean["reps"] > 0]

        if clean.empty:
            st.error("Add at least one valid set with an exercise and reps.")
        else:
            rows = clean.to_dict(orient="records")
            workout_id = save_workout(
                workout_date,
                workout_name,
                notes,
                rows,
            )
            st.success(f"Workout saved. Session ID: {workout_id}")
