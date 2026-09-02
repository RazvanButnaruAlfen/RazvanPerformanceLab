import streamlit as st

from Components.charts import line_chart
from Components.metrics import metric_row
from Services.analytics import exercise_summary
from Services.database import get_workout_sets
from Services.progression import next_target_message

st.title("📈 Progress")

df = get_workout_sets()

if df.empty:
    st.info("Log a workout first and your exercise progression will appear here.")
    st.stop()

exercises = sorted(df["exercise"].dropna().unique().tolist())
exercise = st.selectbox("Exercise", exercises)

summary = exercise_summary(df, exercise)

if summary.empty:
    st.info("No data available for this exercise.")
    st.stop()

latest = summary.iloc[-1]
previous = summary.iloc[-2] if len(summary) > 1 else None

e1rm_delta = None
volume_delta = None
if previous is not None:
    e1rm_delta = f"{latest['best_e1rm'] - previous['best_e1rm']:+.1f} kg"
    volume_delta = f"{latest['total_volume_kg'] - previous['total_volume_kg']:+.0f} kg"

metric_row(
    [
        {
            "label": "Latest top weight",
            "value": f"{latest['top_weight_kg']:.1f} kg",
        },
        {
            "label": "Best estimated 1RM",
            "value": f"{latest['best_e1rm']:.1f} kg",
            "delta": e1rm_delta,
        },
        {
            "label": "Session volume",
            "value": f"{latest['total_volume_kg']:.0f} kg",
            "delta": volume_delta,
        },
    ]
)

st.subheader("Next-session suggestion")
st.success(next_target_message(df, exercise))

line_chart(
    summary,
    "workout_date",
    "best_e1rm",
    "Estimated 1RM trend",
)

line_chart(
    summary,
    "workout_date",
    "total_volume_kg",
    "Training volume trend",
)

with st.expander("Session data"):
    st.dataframe(summary, use_container_width=True, hide_index=True)
