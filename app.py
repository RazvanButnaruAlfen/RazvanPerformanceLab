import base64
from pathlib import Path

import streamlit as st

from Components.auth_ui import render_auth_screen
from Pages.body_tracking import render as render_body_tracking
from Pages.log_workout import render as render_log_workout
from Pages.progress import render as render_progress
from Pages.workout_history import render as render_workout_history
from Services.auth import get_profile, is_authenticated, sign_out

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
        min-height: 92px;
    }

    .rpl-inside-logo {
        display: block;
        width: 455px;
        max-width: 100%;
        height: auto;
    }

    .rpl-userline {
        color: #a8abb1;
        font-size: 0.95rem;
        margin-top: 0.2rem;
    }

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

    .rpl-nav-icon-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 42px;
        margin-bottom: 0.25rem;
    }

    .rpl-nav-icon-wrap img {
        width: 34px;
        height: 34px;
        object-fit: contain;
        display: block;
    }

    /* Navigation cards */
    .st-key-navcard_log,
    .st-key-navcard_progress,
    .st-key-navcard_history,
    .st-key-navcard_bodyweight {
        border: 1px solid #2d3138 !important;
        background: #111419 !important;
        border-radius: 12px !important;
        padding: 0.55rem 0.55rem 0.45rem 0.55rem !important;
        min-height: 108px;
        transition: 0.15s ease;
    }

    .st-key-navcard_log:hover,
    .st-key-navcard_progress:hover,
    .st-key-navcard_history:hover,
    .st-key-navcard_bodyweight:hover {
        border-color: #5b626c !important;
        background: #15191f !important;
        transform: translateY(-1px);
    }

    .st-key-nav_log button,
    .st-key-nav_progress button,
    .st-key-nav_history button,
    .st-key-nav_bodyweight button {
        background: transparent !important;
        border: 0 !important;
        color: #eceef1 !important;
        font-weight: 650 !important;
        min-height: 2.3rem !important;
        width: 100% !important;
        box-shadow: none !important;
        text-align: center !important;
        justify-content: center !important;
        padding: 0.25rem !important;
    }

    __ACTIVE_CSS__

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
            min-height: 66px;
        }

        .rpl-inside-logo {
            width: 310px;
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
            flex: 1 1 auto !important;
        }

        .st-key-rpl_header div[data-testid="column"]:last-child {
            min-width: 105px !important;
            width: 105px !important;
            flex: 0 0 105px !important;
        }

        .st-key-rpl_nav div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 0.35rem !important;
        }

        .st-key-rpl_nav div[data-testid="column"] {
            min-width: 0 !important;
            width: 25% !important;
            flex: 1 1 25% !important;
        }

        .st-key-navcard_log,
        .st-key-navcard_progress,
        .st-key-navcard_history,
        .st-key-navcard_bodyweight {
            min-height: 94px;
            padding: 0.4rem 0.2rem 0.35rem 0.2rem !important;
            border-radius: 10px !important;
        }

        .rpl-nav-icon-wrap {
            height: 34px;
            margin-bottom: 0.1rem;
        }

        .rpl-nav-icon-wrap img {
            width: 28px;
            height: 28px;
        }

        .st-key-nav_log button,
        .st-key-nav_progress button,
        .st-key-nav_history button,
        .st-key-nav_bodyweight button {
            font-size: 0.68rem !important;
            line-height: 1.05 !important;
            white-space: normal !important;
            min-height: 2rem !important;
        }

        .st-key-header_sign_out button {
            min-height: 2.4rem !important;
            font-size: 0.76rem !important;
        }
    }
    </style>
    """.replace(
        "__ACTIVE_CSS__",
        st.session_state.get("_nav_active_css", "")
    ),
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

if "active_section" not in st.session_state:
    st.session_state["active_section"] = "log"

active = st.session_state["active_section"]

active_css_map = {
    "log": """
        .st-key-navcard_log {
            border: 1px solid #ff3932 !important;
            background: linear-gradient(180deg, #1c1718 0%, #131519 100%) !important;
            box-shadow: inset 0 -3px 0 #ff2a23, 0 0 18px rgba(255,42,35,0.10);
        }
        .st-key-nav_log button { color: #ff4a45 !important; }
    """,
    "progress": """
        .st-key-navcard_progress {
            border: 1px solid #ff3932 !important;
            background: linear-gradient(180deg, #1c1718 0%, #131519 100%) !important;
            box-shadow: inset 0 -3px 0 #ff2a23, 0 0 18px rgba(255,42,35,0.10);
        }
        .st-key-nav_progress button { color: #ff4a45 !important; }
    """,
    "history": """
        .st-key-navcard_history {
            border: 1px solid #ff3932 !important;
            background: linear-gradient(180deg, #1c1718 0%, #131519 100%) !important;
            box-shadow: inset 0 -3px 0 #ff2a23, 0 0 18px rgba(255,42,35,0.10);
        }
        .st-key-nav_history button { color: #ff4a45 !important; }
    """,
    "bodyweight": """
        .st-key-navcard_bodyweight {
            border: 1px solid #ff3932 !important;
            background: linear-gradient(180deg, #1c1718 0%, #131519 100%) !important;
            box-shadow: inset 0 -3px 0 #ff2a23, 0 0 18px rgba(255,42,35,0.10);
        }
        .st-key-nav_bodyweight button { color: #ff4a45 !important; }
    """,
}
st.session_state["_nav_active_css"] = active_css_map[active]

# Re-inject active state immediately on this run.
st.markdown(f"<style>{active_css_map[active]}</style>", unsafe_allow_html=True)

with st.container(key="rpl_header"):
    header_left, header_right = st.columns([6, 1], vertical_alignment="center")

    with header_left:
        logo_path = Path("Assets/login_logo.png")
        if logo_path.exists():
            logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
            st.markdown(
                f"""
                <div class="rpl-inside-header">
                    <div>
                        <img class="rpl-inside-logo"
                             src="data:image/png;base64,{logo_b64}"
                             alt="Razvan Performance Lab">
                        <div class="rpl-userline">
                            Training as <strong>{display_name}</strong>
                        </div>
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


def icon_html(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    data = base64.b64encode(p.read_bytes()).decode()
    return (
        '<div class="rpl-nav-icon-wrap">'
        f'<img src="data:image/png;base64,{data}">'
        '</div>'
    )


with st.container(key="rpl_nav"):
    cols = st.columns(4)

    nav_items = [
        ("log", "Log Workout", "Assets/icon_workout.png", "navcard_log", "nav_log"),
        ("progress", "Progress", "Assets/icon_progress.png", "navcard_progress", "nav_progress"),
        ("history", "History", "Assets/icon_history.png", "navcard_history", "nav_history"),
        ("bodyweight", "Body Weight", "Assets/icon_body.png", "navcard_bodyweight", "nav_bodyweight"),
    ]

    for col, (section, label, icon, card_key, button_key) in zip(cols, nav_items):
        with col:
            with st.container(key=card_key):
                st.markdown(icon_html(icon), unsafe_allow_html=True)

                if st.button(
                    label,
                    key=button_key,
                    use_container_width=True,
                ):
                    st.session_state["active_section"] = section
                    st.rerun()

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

if active == "log":
    render_log_workout()
elif active == "progress":
    render_progress()
elif active == "history":
    render_workout_history()
else:
    render_body_tracking()
