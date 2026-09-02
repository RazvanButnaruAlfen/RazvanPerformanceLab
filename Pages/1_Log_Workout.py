from datetime import date

import streamlit as st

from Components.workout_form import workout_editor
from Services.database import init_db, save_workout, using_supabase

init_db()

st.title("🏋️ Log Workout")
st.caption("Record every working set so progression can be compared session by session.")

if not using_supabase():
    st.info(
        "Local mode: data is being stored in SQLite. "
        "For permanent Streamlit Cloud storage, connect Supabase using the included setup files."
    )

col1, col2 = st.columns([1, 2])
with col1:
    workout_date = st.date_input("Workout date", value=date.today())
with col2:
    workout_name = st.text_input(
        "Workout name",
        placeholder="e.g. Push / Chest + Shoulders + Triceps",
    )

st.subheader("Sets")
edited = workout_editor()

notes = st.text_area("Workout notes", placeholder="DOMS, energy, unusual performance, etc.")

if st.button("Save workout", type="primary", use_container_width=True):
    clean = edited.copy()
    clean = clean.dropna(subset=["exercise", "weight_kg", "reps"])
    clean = clean[clean["exercise"].astype(str).str.strip() != ""]
    clean = clean[clean["reps"] > 0]

    if clean.empty:
        st.error("Add at least one valid set with an exercise and reps.")
    else:
        rows = clean.to_dict(orient="records")
        workout_id = save_workout(workout_date, workout_name, notes, rows)
        st.success(f"Workout saved. Session ID: {workout_id}")
