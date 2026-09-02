from pathlib import Path

from PIL import Image
import streamlit as st

from Components.auth_ui import render_auth_screen
from Pages.body_tracking import render as render_body_tracking
from Pages.log_workout import render as render_log_workout
from Pages.progress import render as render_progress
from Pages.workout_history import render as render_workout_history
from Services.auth import get_profile, is_authenticated, sign_out

APP_ICON = Path("Assets/app_icon.png")
APP_LOGO = Path("Assets/app_logo.png")

page_icon = Image.open(APP_ICON) if APP_ICON.exists() else "🏋️"

st.set_page_config(
    page_title="Razvan Performance Lab",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Hide Streamlit chrome / Fork controls */
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    #MainMenu {
        visibility: hidden !important;
    }

    header[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Main layout */
    .block-container {
        max-width: 1500px;
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    .rpl-userline {
        opacity: 0.72;
        font-size: 0.95rem;
        margin-top: 0.1rem;
    }

    div[data-baseweb="tab-list"] {
        gap: 0.35rem;
        overflow-x: auto;
        scrollbar-width: thin;
        white-space: nowrap;
    }

    button[data-baseweb="tab"] {
        flex-shrink: 0;
        min-width: max-content;
        font-size: 0.98rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        overflow-x: auto;
    }

    /* Mobile */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.55rem;
            padding-bottom: 1.25rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }

        .rpl-userline {
            font-size: 0.84rem;
            margin-top: 0;
        }

        h1 {
            font-size: 1.7rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        h3 {
            font-size: 1.1rem !important;
        }

        button[data-baseweb="tab"] {
            font-size: 0.84rem;
            padding-left: 0.55rem;
            padding-right: 0.55rem;
        }

        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
        }

        div[data-testid="column"] {
            min-width: 100% !important;
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        .stFormSubmitButton > button {
            width: 100%;
        }

        input,
        textarea {
            font-size: 16px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not is_authenticated():
    render_auth_screen()
    st.stop()

profile = get_profile()
display_name = (
    profile.get("display_name")
    if profile and profile.get("display_name")
    else "Athlete"
)
avatar = (
    profile.get("avatar_emoji")
    if profile and profile.get("avatar_emoji")
    else "🏋️"
)

header_left, header_right = st.columns([6, 1], vertical_alignment="center")

with header_left:
    if APP_LOGO.exists():
        st.image(str(APP_LOGO), width=430)
    else:
        st.title("🏋️ Razvan Performance Lab")

    st.markdown(
        f'<div class="rpl-userline">{avatar} Training as <strong>{display_name}</strong></div>',
        unsafe_allow_html=True,
    )

with header_right:
    if st.button("Sign out", key="header_sign_out", use_container_width=True):
        sign_out()
        st.rerun()

tab_log, tab_progress, tab_history, tab_body = st.tabs(
    [
        "🏋️ Log Workout",
        "📈 Progress",
        "🗂️ History",
        "⚖️ Body",
    ]
)

with tab_log:
    render_log_workout()

with tab_progress:
    render_progress()

with tab_history:
    render_workout_history()

with tab_body:
    render_body_tracking()
