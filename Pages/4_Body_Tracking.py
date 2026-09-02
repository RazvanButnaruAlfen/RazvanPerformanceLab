from datetime import date

import pandas as pd
import streamlit as st

from Components.metrics import metric_row
from Services.database import get_bodyweight_entries, save_bodyweight

st.title("⚖️ Body Tracking")
st.caption("A weekly bodyweight check-in is enough to track the long-term trend.")

entries = get_bodyweight_entries()

with st.form("weight_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        entry_date = st.date_input("Date", value=date.today())
    with col2:
        weight_kg = st.number_input(
            "Bodyweight (kg)",
            min_value=30.0,
            max_value=250.0,
            step=0.1,
            format="%.1f",
        )

    notes = st.text_input("Notes", placeholder="Optional")
    submitted = st.form_submit_button("Save bodyweight", type="primary")

if submitted:
    save_bodyweight(entry_date, weight_kg, notes)
    st.success("Bodyweight saved.")
    st.rerun()

entries = get_bodyweight_entries()

if entries.empty:
    st.info("No bodyweight entries yet.")
    st.stop()

entries["entry_date"] = pd.to_datetime(entries["entry_date"])
entries = entries.sort_values("entry_date")

latest = entries.iloc[-1]
start = entries.iloc[0]
previous = entries.iloc[-2] if len(entries) > 1 else None

latest_delta = None
if previous is not None:
    latest_delta = f"{latest['weight_kg'] - previous['weight_kg']:+.1f} kg"

metric_row(
    [
        {
            "label": "Current bodyweight",
            "value": f"{latest['weight_kg']:.1f} kg",
            "delta": latest_delta,
        },
        {
            "label": "Change from first entry",
            "value": f"{latest['weight_kg'] - start['weight_kg']:+.1f} kg",
        },
        {
            "label": "Check-ins",
            "value": str(len(entries)),
        },
    ]
)

days_since = (pd.Timestamp.today().normalize() - latest["entry_date"].normalize()).days
if days_since >= 7:
    st.warning(f"Bodyweight check-in due — last entry was {days_since} days ago.")
else:
    st.caption(f"Last check-in: {days_since} day(s) ago.")

st.subheader("Bodyweight trend")
chart = entries.set_index("entry_date")[["weight_kg"]]
st.line_chart(chart)

with st.expander("Bodyweight history"):
    display = entries[["entry_date", "weight_kg", "notes"]].copy()
    display["entry_date"] = display["entry_date"].dt.date
    display.columns = ["Date", "Weight (kg)", "Notes"]
    st.dataframe(display, use_container_width=True, hide_index=True)
