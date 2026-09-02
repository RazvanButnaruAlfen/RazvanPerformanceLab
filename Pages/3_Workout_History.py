import streamlit as st

from Services.analytics import add_set_metrics
from Services.database import get_workout_sets

st.title("🗂️ Workout History")

df = get_workout_sets()

if df.empty:
    st.info("No workouts logged yet.")
    st.stop()

df = add_set_metrics(df)
df["workout_date"] = df["workout_date"].astype(str)

dates = ["All"] + sorted(df["workout_date"].unique().tolist(), reverse=True)
selected_date = st.selectbox("Date", dates)

filtered = df if selected_date == "All" else df[df["workout_date"] == selected_date]

for workout_id, workout in filtered.groupby("workout_id", sort=False):
    workout_name = workout["workout_name"].iloc[0]
    workout_date = workout["workout_date"].iloc[0]
    title = f"{workout_date} — {workout_name or 'Workout'}"

    with st.expander(title, expanded=(selected_date != "All")):
        display = workout[
            ["exercise", "set_number", "weight_kg", "reps", "rir", "volume_kg"]
        ].copy()
        display.columns = ["Exercise", "Set", "Weight (kg)", "Reps", "RIR", "Volume (kg)"]
        st.dataframe(display, use_container_width=True, hide_index=True)

        notes = workout["notes"].iloc[0]
        if notes:
            st.caption(f"Notes: {notes}")
