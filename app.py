import base64
from pathlib import Path

import streamlit as st

from Components.auth_ui import render_auth_screen
from Pages.body_tracking import render as render_body_tracking
from Pages.log_workout import render as render_log_workout
from Pages.progress import render as render_progress
from Pages.workout_history import render as render_workout_history
from Services.auth import get_profile, is_authenticated, sign_out
from Services.responsive import is_mobile

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


def _icon_html(path: Path, css_class: str = "rpl-nav-icon") -> str:
    uri = _data_uri(path)
    if not uri:
        return ""
    return f'<img class="{css_class}" src="{uri}">'


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
        padding-top: 0.5rem;
        padding-bottom: 2rem;
        padding-left: 1.1rem;
        padding-right: 1.1rem;
    }

    .rpl-logo-card,
    .rpl-training-card {
        min-height: 150px;
        border: 1px solid #2c3138;
        border-radius: 14px;
        background: #101318;
        overflow: hidden;
    }

    .rpl-logo-card {
        display: flex;
        align-items: center;
        padding: 0.9rem 1.15rem;
    }

    .rpl-logo-card img {
        width: 100%;
        max-width: 560px;
        height: auto;
        display: block;
    }

    .rpl-training-card {
        position: relative;
        background-image:
            linear-gradient(90deg, rgba(7,9,12,0.10), rgba(7,9,12,0.62) 45%, rgba(7,9,12,0.97) 78%),
            url("__TRAINING_BG__");
        background-size: cover;
        background-position: center;
    }

    .rpl-training-copy {
        position: absolute;
        right: 1.1rem;
        top: 50%;
        width: 56%;
        transform: translateY(-50%);
    }

    .rpl-kicker {
        font-size: 0.72rem;
        letter-spacing: 0.26em;
        font-weight: 700;
        color: #d7d9dd;
        text-transform: uppercase;
    }

    .rpl-name {
        margin-top: 0.15rem;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
        color: white;
        text-transform: uppercase;
        padding-bottom: 0.42rem;
        border-bottom: 1px solid #ba1d19;
    }

    .rpl-tagline {
        margin-top: 0.5rem;
        color: #b2b5bb;
        font-size: 0.70rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }

    .st-key-header_sign_out button {
        min-height: 3.4rem !important;
        background: linear-gradient(90deg, #c90b0b, #ff2b23) !important;
        border: 1px solid #ff4540 !important;
        color: white !important;
        font-weight: 800 !important;
        letter-spacing: 0.04em !important;
        border-radius: 10px !important;
        box-shadow: 0 0 26px rgba(255,42,35,0.18);
    }

    .rpl-nav-icon {
        width: 64px;
        height: 64px;
        object-fit: contain;
        display: block;
        margin: 0 auto 0.15rem auto;
    }

    .st-key-navcard_log,
    .st-key-navcard_progress,
    .st-key-navcard_history,
    .st-key-navcard_bodyweight {
        min-height: 150px;
        border: 1px solid #343940 !important;
        border-radius: 14px !important;
        background: #111419 !important;
        padding: 0.75rem 0.7rem 0.6rem 0.7rem !important;
        position: relative;
    }

    .st-key-nav_log button,
    .st-key-nav_progress button,
    .st-key-nav_history button,
    .st-key-nav_bodyweight button {
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        color: #f3f4f6 !important;
        font-weight: 750 !important;
        width: 100% !important;
        justify-content: center !important;
        text-align: center !important;
    }

    .rpl-mobile-logo img {
        max-width: 270px;
        width: 100%;
        height: auto;
        display: block;
    }

    .rpl-mobile-training {
        border: 1px solid #2e333a;
        border-radius: 10px;
        padding: 0.55rem 0.7rem;
        background: linear-gradient(90deg, #111419, #171217);
    }

    .rpl-mobile-training .rpl-kicker {
        font-size: 0.58rem;
    }

    .rpl-mobile-training .rpl-name {
        font-size: 1.15rem;
        border: 0;
        padding: 0;
        margin-top: 0.1rem;
    }

    .rpl-mobile-training .rpl-tagline {
        font-size: 0.52rem;
        margin-top: 0.2rem;
        letter-spacing: 0.10em;
    }

    .rpl-mobile-nav-icon {
        width: 42px;
        height: 42px;
        object-fit: contain;
        display: block;
        margin: 0 auto 0.05rem auto;
    }

    .st-key-mobile_navcard_log,
    .st-key-mobile_navcard_progress,
    .st-key-mobile_navcard_history,
    .st-key-mobile_navcard_bodyweight {
        min-height: 108px;
        border: 1px solid #333840 !important;
        border-radius: 11px !important;
        background: #111419 !important;
        padding: 0.45rem 0.35rem 0.4rem 0.35rem !important;
        position: relative;
    }

    .st-key-mobile_nav_log button,
    .st-key-mobile_nav_progress button,
    .st-key-mobile_nav_history button,
    .st-key-mobile_nav_bodyweight button {
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        color: #f2f3f5 !important;
        width: 100% !important;
        justify-content: center !important;
        text-align: center !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        min-height: 1.85rem !important;
        padding: 0.1rem !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.3rem;
            padding-left: 0.55rem;
            padding-right: 0.55rem;
            padding-bottom: 1rem;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        input,
        textarea {
            font-size: 16px !important;
        }
    }
    </style>
    """.replace("__TRAINING_BG__", training_bg_uri),
    unsafe_allow_html=True,
)

if not is_authenticated():
    render_auth_screen()
    st.stop()

mobile = is_mobile()
st.session_state["is_mobile"] = mobile

profile = get_profile()
display_name = (
    profile.get("display_name")
    if profile and profile.get("display_name")
    else "Athlete"
)

if "active_section" not in st.session_state:
    st.session_state["active_section"] = "log"

active = st.session_state["active_section"]


def active_card_css(prefix: str, section: str) -> str:
    return f"""
    .st-key-{prefix}_{section} {{
        border-color: #ff3932 !important;
        background:
            radial-gradient(circle at 18% 20%, rgba(255,50,40,0.24), rgba(255,50,40,0.08) 32%, rgba(0,0,0,0) 70%),
            #171216 !important;
        box-shadow:
            inset 0 -4px 0 #ff2a23,
            inset 0 0 28px rgba(255,42,35,0.06),
            0 0 24px rgba(255,42,35,0.15);
    }}

    .st-key-{prefix}_{section}::after {{
        content: "";
        position: absolute;
        left: 42%;
        right: 42%;
        bottom: 0.45rem;
        height: 4px;
        border-radius: 999px;
        background: #ff2a23;
        box-shadow: 0 0 10px rgba(255,42,35,0.45);
    }}
    """


if mobile:
    st.markdown(
        f"<style>{active_card_css('mobile_navcard', active)}</style>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"<style>{active_card_css('navcard', active)}</style>",
        unsafe_allow_html=True,
    )


def render_desktop_header():
    logo_col, training_col, signout_col = st.columns(
        [1.18, 1.0, 0.38],
        gap="medium",
        vertical_alignment="center",
    )

    with logo_col:
        st.markdown(
            f"""
            <div class="rpl-logo-card">
                <img src="{logo_uri}">
            </div>
            """,
            unsafe_allow_html=True,
        )

    with training_col:
        st.markdown(
            f"""
            <div class="rpl-training-card">
                <div class="rpl-training-copy">
                    <div class="rpl-kicker">Training as</div>
                    <div class="rpl-name">{display_name}</div>
                    <div class="rpl-tagline">Train · Track · Progress</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with signout_col:
        if st.button(
            "⏻ SIGN OUT",
            key="header_sign_out",
            type="primary",
            use_container_width=True,
        ):
            sign_out()
            st.rerun()


def render_mobile_header():
    brand_col, signout_col = st.columns(
        [1, 0.42],
        gap="small",
        vertical_alignment="center",
    )

    with brand_col:
        st.markdown(
            f'<div class="rpl-mobile-logo"><img src="{logo_uri}"></div>',
            unsafe_allow_html=True,
        )

    with signout_col:
        if st.button(
            "⏻ OUT",
            key="header_sign_out",
            type="primary",
            use_container_width=True,
        ):
            sign_out()
            st.rerun()

    st.markdown(
        f"""
        <div class="rpl-mobile-training">
            <div class="rpl-kicker">Training as</div>
            <div class="rpl-name">{display_name}</div>
            <div class="rpl-tagline">Train · Track · Progress</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_desktop_navigation():
    cols = st.columns(4, gap="medium")

    items = [
        ("log", "Log Workout", ICON_WORKOUT, "navcard_log", "nav_log"),
        ("progress", "Progress", ICON_PROGRESS, "navcard_progress", "nav_progress"),
        ("history", "History", ICON_HISTORY, "navcard_history", "nav_history"),
        ("bodyweight", "Body Weight", ICON_BODY, "navcard_bodyweight", "nav_bodyweight"),
    ]

    for col, (section, label, icon, card_key, button_key) in zip(cols, items):
        with col:
            with st.container(key=card_key):
                st.markdown(_icon_html(icon), unsafe_allow_html=True)
                if st.button(label, key=button_key, use_container_width=True):
                    st.session_state["active_section"] = section
                    st.rerun()


def render_mobile_navigation():
    rows = [
        [
            ("log", "Log Workout", ICON_WORKOUT, "mobile_navcard_log", "mobile_nav_log"),
            ("progress", "Progress", ICON_PROGRESS, "mobile_navcard_progress", "mobile_nav_progress"),
        ],
        [
            ("history", "History", ICON_HISTORY, "mobile_navcard_history", "mobile_nav_history"),
            ("bodyweight", "Body Weight", ICON_BODY, "mobile_navcard_bodyweight", "mobile_nav_bodyweight"),
        ],
    ]

    for row in rows:
        cols = st.columns(2, gap="small")
        for col, (section, label, icon, card_key, button_key) in zip(cols, row):
            with col:
                with st.container(key=card_key):
                    st.markdown(
                        _icon_html(icon, "rpl-mobile-nav-icon"),
                        unsafe_allow_html=True,
                    )
                    if st.button(label, key=button_key, use_container_width=True):
                        st.session_state["active_section"] = section
                        st.rerun()


if mobile:
    render_mobile_header()
    st.markdown("<div style='height:0.45rem'></div>", unsafe_allow_html=True)
    render_mobile_navigation()
else:
    render_desktop_header()
    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    render_desktop_navigation()

st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

if active == "log":
    render_log_workout()
elif active == "progress":
    render_progress()
elif active == "history":
    render_workout_history()
else:
    render_body_tracking()
