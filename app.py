import streamlit as st

st.set_page_config(
    page_title="Razvan Performance Lab",
    page_icon="🏋️",
    layout="wide",
)

pages = {
    "Training": [
        st.Page("Pages/1_Log_Workout.py", title="Log Workout", icon="🏋️"),
        st.Page("Pages/2_Progress.py", title="Progress", icon="📈"),
        st.Page("Pages/3_Workout_History.py", title="Workout History", icon="🗂️"),
    ],
    "Body": [
        st.Page("Pages/4_Body_Tracking.py", title="Body Tracking", icon="⚖️"),
    ],
}

pg = st.navigation(pages)

st.logo("https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f3cb.png")
pg.run()
