from datetime import datetime

import pandas as pd
import streamlit as st

from Components.workout_form import workout_editor
from Services.analytics import add_set_metrics
from Services.database import get_workout_sets, update_workout


def render():
    if st.session_state.pop("workout_updated_flash", False):
        st.success("Workout updated.")

    st.subheader("Workout History")
    st.caption("Review previous sessions and edit a workout if something was recorded incorrectly.")

    df = get_workout_sets()

    if df.empty:
        st.info("No workouts logged yet.")
        return

    df = add_set_metrics(df)
    df["workout_date"] = df["workout_date"].astype(str)

    dates = ["All"] + sorted(
        df["workout_date"].unique().tolist(),
        reverse=True,
    )

    selected_date = st.selectbox(
        "Date",
        dates,
        key="history_date_select",
    )

    filtered = df if selected_date == "All" else df[df["workout_date"] == selected_date]

    for workout_id, workout in filtered.groupby("workout_id", sort=False):
        workout_name = workout["workout_name"].iloc[0]
        workout_date = workout["workout_date"].iloc[0]
        title = f"{workout_date} — {workout_name or 'Workout'}"

        with st.expander(title, expanded=(selected_date != "All")):
            display = workout[
                [
                    "exercise",
                    "set_number",
                    "weight_kg",
                    "reps",
                    "rir",
                    "volume_kg",
                ]
            ].copy()

            display.columns = [
                "Exercise",
                "Set",
                "Weight (kg)",
                "Reps",
                "RIR",
                "Volume (kg)",
            ]

            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
            )

            notes = workout["notes"].iloc[0]
            if notes:
                st.caption(f"Notes: {notes}")

            st.markdown("#### Edit workout")

            edit_date = st.date_input(
                "Workout date",
                value=datetime.strptime(workout_date, "%Y-%m-%d").date(),
                key=f"edit_date_{workout_id}",
            )

            edit_name = st.text_input(
                "Workout name",
                value=workout_name or "",
                key=f"edit_name_{workout_id}",
            )

            initial_sets = workout[
                ["exercise", "set_number", "weight_kg", "reps", "rir"]
            ].copy()

            edited_sets = workout_editor(
                key=f"edit_sets_{workout_id}",
                initial_data=initial_sets,
            )

            edit_notes = st.text_area(
                "Notes",
                value=notes or "",
                key=f"edit_notes_{workout_id}",
            )

            if st.button(
                "Save changes",
                type="primary",
                use_container_width=True,
                key=f"save_edit_{workout_id}",
            ):
                clean = edited_sets.copy()
                clean = clean.dropna(subset=["exercise", "weight_kg", "reps"])
                clean = clean[clean["exercise"].astype(str).str.strip() != ""]
                clean = clean[clean["reps"] > 0]

                if clean.empty:
                    st.error("A workout must contain at least one valid set.")
                else:
                    update_workout(
                        int(workout_id),
                        edit_date,
                        edit_name,
                        edit_notes,
                        clean.to_dict(orient="records"),
                    )
                    st.session_state["workout_updated_flash"] = True
                    st.rerun()
