from pathlib import Path

import streamlit as st

from Components.auth_ui import render_auth_screen
from Pages.body_tracking import render as render_body_tracking
from Pages.log_workout import render as render_log_workout
from Pages.progress import render as render_progress
from Pages.workout_history import render as render_workout_history
from Services.auth import get_profile, is_authenticated, sign_out

APP_LOGO = Path("Assets/login_logo.png")
ICON_WORKOUT = Path("Assets/icon_workout.png")
ICON_PROGRESS = Path("Assets/icon_progress.png")
ICON_HISTORY = Path("Assets/icon_history.png")
ICON_BODY = Path("Assets/icon_body.png")

st.set_page_config(
    page_title="Razvan Performance Lab",
    page_icon="Assets/app_icon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"],
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

    .block-container {
        max-width: 1500px;
        padding-top: 0.7rem;
        padding-bottom: 2rem;
        padding-left: 1.7rem;
        padding-right: 1.7rem;
    }

    .rpl-inside-header {
        display: flex;
        align-items: center;
        min-height: 88px;
    }

    .rpl-inside-logo {
        display: block;
        width: 430px;
        max-width: 100%;
        height: auto;
    }

    .rpl-userline {
        color: #a8abb1;
        font-size: 0.95rem;
        margin-top: 0.15rem;
    }

    /* Sign out */
    .st-key-header_sign_out button {
        background: linear-gradient(90deg, #c90909 0%, #ff2a23 100%) !important;
        border: 1px solid #ff443e !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: 0.035em !important;
        min-height: 2.85rem !important;
        border-radius: 8px !important;
        box-shadow: 0 0 20px rgba(255, 42, 35, 0.14);
    }

    .st-key-header_sign_out button:hover {
        filter: brightness(1.08);
        border-color: #ff625d !important;
    }

    /* Custom navigation */
    .rpl-nav-wrap {
        border-bottom: 1px solid #2d3036;
        margin-top: 0.15rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.25rem;
    }

    .rpl-nav-icon {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 36px;
        margin-bottom: -0.15rem;
    }

    .rpl-nav-icon img {
        width: 30px;
        height: 30px;
        object-fit: contain;
    }

    .st-key-nav_log button,
    .st-key-nav_progress button,
    .st-key-nav_history button,
    .st-key-nav_bodyweight button {
        background: transparent !important;
        border: 0 !important;
        border-radius: 0 !important;
        color: #d8dadd !important;
        font-weight: 600 !important;
        padding: 0.35rem 0.35rem 0.55rem 0.35rem !important;
        min-height: 2.2rem !important;
        box-shadow: none !important;
    }

    .st-key-nav_log button:hover,
    .st-key-nav_progress button:hover,
    .st-key-nav_history button:hover,
    .st-key-nav_bodyweight button:hover {
        color: #ff4a45 !important;
        border-bottom: 2px solid #7a201e !important;
    }

    .rpl-active-nav button {
        color: #ff3530 !important;
        border-bottom: 2px solid #ff2a23 !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        overflow-x: auto;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.4rem;
            padding-bottom: 1.2rem;
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }

        .rpl-inside-header {
            min-height: 64px;
        }

        .rpl-inside-logo {
            width: 300px;
        }

        .rpl-userline {
            font-size: 0.82rem;
        }

        .st-key-rpl_header div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            align-items: center !important;
        }

        .st-key-rpl_header div[data-testid="column"]:first-child {
            min-width: 0 !important;
            width: auto !important;
            flex: 1 1 auto !important;
        }

        .st-key-rpl_header div[data-testid="column"]:last-child {
            min-width: 105px !important;
            width: 105px !important;
            flex: 0 0 105px !important;
        }

        .st-key-header_sign_out button {
            min-height: 2.4rem !important;
            font-size: 0.76rem !important;
        }

        .st-key-rpl_nav div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 0.15rem !important;
        }

        .st-key-rpl_nav div[data-testid="column"] {
            min-width: 0 !important;
            width: 25% !important;
            flex: 1 1 25% !important;
        }

        .rpl-nav-icon {
            height: 30px;
        }

        .rpl-nav-icon img {
            width: 25px;
            height: 25px;
        }

        .st-key-nav_log button,
        .st-key-nav_progress button,
        .st-key-nav_history button,
        .st-key-nav_bodyweight button {
            font-size: 0.70rem !important;
            line-height: 1.05 !important;
            white-space: normal !important;
            padding-left: 0.1rem !important;
            padding-right: 0.1rem !important;
        }

        h1 {
            font-size: 1.65rem !important;
        }

        h2 {
            font-size: 1.3rem !important;
        }

        h3 {
            font-size: 1.08rem !important;
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

with st.container(key="rpl_header"):
    header_left, header_right = st.columns([6, 1], vertical_alignment="center")

    with header_left:
        if APP_LOGO.exists():
            st.markdown(
                f"""
                <div class="rpl-inside-header">
                    <div>
                        <img class="rpl-inside-logo" src="data:image/png;base64,{__import__('base64').b64encode(APP_LOGO.read_bytes()).decode()}">
                        <div class="rpl-userline">Training as <strong>{display_name}</strong></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.title("Razvan Performance Lab")
            st.caption(f"Training as {display_name}")

    with header_right:
        if st.button(
            "⏻ SIGN OUT",
            key="header_sign_out",
            type="primary",
            use_container_width=True,
        ):
            sign_out()
            st.rerun()

if "active_section" not in st.session_state:
    st.session_state["active_section"] = "log"

active = st.session_state["active_section"]

with st.container(key="rpl_nav"):
    nav_cols = st.columns(4)

    nav_items = [
        ("log", "Log Workout", ICON_WORKOUT, "nav_log"),
        ("progress", "Progress", ICON_PROGRESS, "nav_progress"),
        ("history", "History", ICON_HISTORY, "nav_history"),
        ("bodyweight", "Body Weight", ICON_BODY, "nav_bodyweight"),
    ]

    for col, (section, label, icon_path, key) in zip(nav_cols, nav_items):
        with col:
            if icon_path.exists():
                st.image(str(icon_path), width=30)

            # Wrapper class used to style active item.
            if active == section:
                st.markdown('<div class="rpl-active-nav">', unsafe_allow_html=True)

            if st.button(label, key=key, use_container_width=True):
                st.session_state["active_section"] = section
                st.rerun()

            if active == section:
                st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="rpl-nav-wrap"></div>', unsafe_allow_html=True)

if active == "log":
    render_log_workout()
elif active == "progress":
    render_progress()
elif active == "history":
    render_workout_history()
else:
    render_body_tracking()
