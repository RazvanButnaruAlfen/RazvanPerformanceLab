import streamlit as st


def metric_row(items):
    columns = st.columns(len(items))
    for col, item in zip(columns, items):
        with col:
            st.metric(
                item["label"],
                item["value"],
                delta=item.get("delta"),
            )
