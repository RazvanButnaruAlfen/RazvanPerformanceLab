import streamlit as st


def line_chart(df, x, y, title=None):
    if title:
        st.subheader(title)
    if df.empty:
        st.info("Not enough data yet.")
        return
    st.line_chart(df.set_index(x)[y])
