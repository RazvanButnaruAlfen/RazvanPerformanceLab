import base64
from pathlib import Path

import streamlit as st

from Components.auth_ui import render_auth_screen
from Pages.body_tracking import render as render_body_tracking
from Pages.log_workout import render as render_log_workout
from Pages.progress import render as render_progress
from Pages.workout_history import render as render_workout_history
from Services.auth import get_profile, is_authenticated, sign_out

APP_LOGO = Path("Assets/login_logo.png")
HEADER_TRAINING_BG = Path("Assets/header_training_bg.png")
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


def _data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


logo_uri = _data_uri(APP_LOGO)
training_bg_uri = _data_uri(HEADER_TRAINING_BG)

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
        max-width: 1580px;
        padding-top: 0.55rem;
        padding-bottom: 2rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }

    /* =========================
       TOP BRAND HEADER
       ========================= */
    .rpl-top-shell {
        display: grid;
        grid-template-columns: 1.2fr 1fr 0.42fr;
        gap: 0.9rem;
        align-items: stretch;
        margin-bottom: 0.8rem;
    }

    .rpl-logo-panel,
    .rpl-training-panel,
    .rpl-signout-panel {
        background:
            linear-gradient(180deg, rgba(18,20,24,0.98), rgba(8,10,13,0.98));
        border: 1px solid #252a31;
        border-radius: 14px;
        min-height: 154px;
        overflow: hidden;
        position: relative;
    }

    .rpl-logo-panel {
        display: flex;
        align-items: center;
        padding: 0.9rem 1.2rem;
    }

    .rpl-logo-panel img {
        width: 100%;
        max-width: 560px;
        height: auto;
        display: block;
    }

    .rpl-training-panel {
        background-image:
            linear-gradient(90deg, rgba(8,10,13,0.12) 0%, rgba(8,10,13,0.70) 44%, rgba(8,10,13,0.98) 78%),
            url("__TRAINING_BG__");
        background-size: cover;
        background-position: left center;
    }

    .rpl-training-copy {
        position: absolute;
        right: 1.25rem;
        top: 50%;
        transform: translateY(-50%);
        width: 55%;
        text-align: left;
    }

    .rpl-training-kicker {
        color: #d8dadd;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        margin-bottom: 0.18rem;
    }

    .rpl-training-name {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        line-height: 1;
        text-transform: uppercase;
        padding-bottom: 0.42rem;
        border-bottom: 1px solid #bd1b18;
        text-shadow: 0 0 16px rgba(255,255,255,0.08);
    }

    .rpl-training-tagline {
        color: #aeb2b9;
        font-size: 0.72rem;
        letter-spacing: 0.20em;
        margin-top: 0.5rem;
        text-transform: uppercase;
    }

    .rpl-signout-panel {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.8rem;
    }

    .st-key-header_sign_out {
        width: 100%;
    }

    .st-key-header_sign_out button {
        width: 100% !important;
        min-height: 3.55rem !important;
        background: linear-gradient(90deg, #c60b0b 0%, #ff2b23 100%) !important;
        border: 1px solid #ff463f !important;
        color: #fff !important;
        font-weight: 800 !important;
        letter-spacing: 0.045em !important;
        border-radius: 10px !important;
        box-shadow: 0 0 28px rgba(255, 42, 35, 0.20);
    }

    .st-key-header_sign_out button:hover {
        filter: brightness(1.08);
        border-color: #ff716c !important;
    }

    /* =========================
       NAVIGATION CARDS
       ========================= */
    .rpl-nav-section {
        margin-top: 0.2rem;
        margin-bottom: 1.25rem;
    }

    .rpl-nav-icon-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 64px;
        margin-bottom: 0.25rem;
    }

    .rpl-nav-icon-wrap img {
        width: 54px;
        height: 54px;
        object-fit: contain;
        display: block;
    }

    .st-key-navcard_log,
    .st-key-navcard_progress,
    .st-key-navcard_history,
    .st-key-navcard_bodyweight {
        border: 1px solid #343940 !important;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.025), rgba(255,255,255,0.0) 45%),
            #111419 !important;
        border-radius: 14px !important;
        padding: 0.75rem 0.75rem 0.55rem 0.75rem !important;
        min-height: 146px;
        transition: 0.16s ease;
        position: relative;
        overflow: hidden;
    }

    .st-key-navcard_log::after,
    .st-key-navcard_progress::after,
    .st-key-navcard_history::after,
    .st-key-navcard_bodyweight::after {
        content: "";
        position: absolute;
        left: 44%;
        right: 44%;
        bottom: 0.55rem;
        height: 3px;
        border-radius: 999px;
        background: #e32722;
        opacity: 0.78;
    }

    .st-key-navcard_log:hover,
    .st-key-navcard_progress:hover,
    .st-key-navcard_history:hover,
    .st-key-navcard_bodyweight:hover {
        transform: translateY(-2px);
        border-color: #60666f !important;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.0) 45%),
            #15191f !important;
    }

    .st-key-nav_log button,
    .st-key-nav_progress button,
    .st-key-nav_history button,
    .st-key-nav_bodyweight button {
        background: transparent !important;
        border: 0 !important;
        color: #f2f3f5 !important;
        font-weight: 750 !important;
        min-height: 2.2rem !important;
        width: 100% !important;
        box-shadow: none !important;
        text-align: center !important;
        justify-content: center !important;
        font-size: 0.98rem !important;
        padding: 0.2rem !important;
    }

    __ACTIVE_CSS__

    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        overflow-x: auto;
    }

    /* =========================
       MOBILE
       ========================= */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.35rem;
            padding-bottom: 1rem;
            padding-left: 0.6rem;
            padding-right: 0.6rem;
        }

        .rpl-top-shell {
            grid-template-columns: 1fr auto;
            grid-template-areas:
                "logo signout"
                "training training";
            gap: 0.5rem;
        }

        .rpl-logo-panel {
            grid-area: logo;
            min-height: 82px;
            padding: 0.55rem 0.7rem;
        }

        .rpl-logo-panel img {
            max-width: 265px;
        }

        .rpl-signout-panel {
            grid-area: signout;
            min-height: 82px;
            width: 108px;
            padding: 0.45rem;
        }

        .rpl-training-panel {
            grid-area: training;
            min-height: 106px;
            background-position: left center;
        }

        .rpl-training-copy {
            right: 0.8rem;
            width: 60%;
        }

        .rpl-training-kicker {
            font-size: 0.62rem;
            letter-spacing: 0.22em;
        }

        .rpl-training-name {
            font-size: 1.45rem;
        }

        .rpl-training-tagline {
            font-size: 0.56rem;
            letter-spacing: 0.12em;
        }

        .st-key-header_sign_out button {
            min-height: 2.6rem !important;
            font-size: 0.72rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        .st-key-rpl_nav div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.45rem !important;
        }

        .st-key-rpl_nav div[data-testid="column"] {
            min-width: calc(50% - 0.25rem) !important;
            width: calc(50% - 0.25rem) !important;
            flex: 1 1 calc(50% - 0.25rem) !important;
        }

        .st-key-navcard_log,
        .st-key-navcard_progress,
        .st-key-navcard_history,
        .st-key-navcard_bodyweight {
            min-height: 118px;
            padding: 0.5rem 0.4rem 0.45rem 0.4rem !important;
            border-radius: 11px !important;
        }

        .rpl-nav-icon-wrap {
            height: 48px;
        }

        .rpl-nav-icon-wrap img {
            width: 40px;
            height: 40px;
        }

        .st-key-nav_log button,
        .st-key-nav_progress button,
        .st-key-nav_history button,
        .st-key-nav_bodyweight button {
            font-size: 0.78rem !important;
            line-height: 1.05 !important;
        }
    }
    </style>
    """.replace("__TRAINING_BG__", training_bg_uri),
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
            background:
                radial-gradient(circle at 18% 20%, rgba(255,50,40,0.24) 0%, rgba(255,50,40,0.10) 28%, rgba(255,50,40,0.02) 52%, rgba(0,0,0,0) 72%),
                linear-gradient(135deg, rgba(255,45,35,0.18) 0%, rgba(92,10,12,0.14) 42%, rgba(255,255,255,0.0) 76%),
                #171216 !important;
            box-shadow:
                inset 0 -4px 0 #ff2a23,
                inset 0 0 34px rgba(255,42,35,0.08),
                0 0 28px rgba(255,42,35,0.18);
        }
        .st-key-nav_log button { color: #ff4640 !important; }
    """,
    "progress": """
        .st-key-navcard_progress {
            border: 1px solid #ff3932 !important;
            background:
                radial-gradient(circle at 18% 20%, rgba(255,50,40,0.24) 0%, rgba(255,50,40,0.10) 28%, rgba(255,50,40,0.02) 52%, rgba(0,0,0,0) 72%),
                linear-gradient(135deg, rgba(255,45,35,0.18) 0%, rgba(92,10,12,0.14) 42%, rgba(255,255,255,0.0) 76%),
                #171216 !important;
            box-shadow:
                inset 0 -4px 0 #ff2a23,
                inset 0 0 34px rgba(255,42,35,0.08),
                0 0 28px rgba(255,42,35,0.18);
        }
        .st-key-nav_progress button { color: #ff4640 !important; }
    """,
    "history": """
        .st-key-navcard_history {
            border: 1px solid #ff3932 !important;
            background:
                radial-gradient(circle at 18% 20%, rgba(255,50,40,0.24) 0%, rgba(255,50,40,0.10) 28%, rgba(255,50,40,0.02) 52%, rgba(0,0,0,0) 72%),
                linear-gradient(135deg, rgba(255,45,35,0.18) 0%, rgba(92,10,12,0.14) 42%, rgba(255,255,255,0.0) 76%),
                #171216 !important;
            box-shadow:
                inset 0 -4px 0 #ff2a23,
                inset 0 0 34px rgba(255,42,35,0.08),
                0 0 28px rgba(255,42,35,0.18);
        }
        .st-key-nav_history button { color: #ff4640 !important; }
    """,
    "bodyweight": """
        .st-key-navcard_bodyweight {
            border: 1px solid #ff3932 !important;
            background:
                radial-gradient(circle at 18% 20%, rgba(255,50,40,0.24) 0%, rgba(255,50,40,0.10) 28%, rgba(255,50,40,0.02) 52%, rgba(0,0,0,0) 72%),
                linear-gradient(135deg, rgba(255,45,35,0.18) 0%, rgba(92,10,12,0.14) 42%, rgba(255,255,255,0.0) 76%),
                #171216 !important;
            box-shadow:
                inset 0 -4px 0 #ff2a23,
                inset 0 0 34px rgba(255,42,35,0.08),
                0 0 28px rgba(255,42,35,0.18);
        }
        .st-key-nav_bodyweight button { color: #ff4640 !important; }
    """,
}

st.markdown(f"<style>{active_css_map[active]}</style>", unsafe_allow_html=True)

# Dynamic top shell
st.markdown(
    f"""
    <div class="rpl-top-shell">
        <div class="rpl-logo-panel">
            <img src="{logo_uri}" alt="Razvan Performance Lab">
        </div>

        <div class="rpl-training-panel">
            <div class="rpl-training-copy">
                <div class="rpl-training-kicker">Training as</div>
                <div class="rpl-training-name">{display_name}</div>
                <div class="rpl-training-tagline">Train · Track · Progress</div>
            </div>
        </div>

        <div class="rpl-signout-panel"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Place the functional Streamlit sign-out button visually over the third panel.
st.markdown(
    """
    <style>
    .st-key-header_sign_out {
        margin-top: -8.05rem;
        margin-left: auto;
        width: calc((100% - 1.8rem) * 0.16);
        min-width: 165px;
        position: relative;
        z-index: 5;
        margin-right: 0.9rem;
        margin-bottom: 4.7rem;
    }

    @media (max-width: 768px) {
        .st-key-header_sign_out {
            margin-top: -11.5rem;
            width: 96px;
            min-width: 96px;
            margin-right: 0.45rem;
            margin-bottom: 7.2rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.button(
    "⏻ SIGN OUT",
    key="header_sign_out",
    type="primary",
    use_container_width=True,
):
    sign_out()
    st.rerun()


def icon_html(path: Path) -> str:
    uri = _data_uri(path)
    if not uri:
        return ""
    return (
        '<div class="rpl-nav-icon-wrap">'
        f'<img src="{uri}">'
        '</div>'
    )


with st.container(key="rpl_nav"):
    cols = st.columns(4)

    nav_items = [
        ("log", "Log Workout", ICON_WORKOUT, "navcard_log", "nav_log"),
        ("progress", "Progress", ICON_PROGRESS, "navcard_progress", "nav_progress"),
        ("history", "History", ICON_HISTORY, "navcard_history", "nav_history"),
        ("bodyweight", "Body Weight", ICON_BODY, "navcard_bodyweight", "nav_bodyweight"),
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

st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)

if active == "log":
    render_log_workout()
elif active == "progress":
    render_progress()
elif active == "history":
    render_workout_history()
else:
    render_body_tracking()
