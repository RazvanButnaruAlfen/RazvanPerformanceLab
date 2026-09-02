from pathlib import Path

import streamlit as st

from Services.auth import sign_in, sign_up

LOGIN_HERO = Path("Assets/login_hero.png")
LOGIN_LOGO = Path("Assets/login_logo.png")


def render_auth_screen():
    # This CSS is only loaded on the authentication screen because app.py
    # calls st.stop() immediately after this function.
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: #07090c !important;
            color: #f5f5f5 !important;
        }

        [data-testid="stAppViewContainer"] > .main {
            background: #07090c !important;
        }

        .block-container {
            max-width: 1540px !important;
            padding-top: 0.4rem !important;
            padding-bottom: 0.4rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        /* Right-side copy */
        .auth-subtitle {
            color: #8d9199;
            font-size: 0.98rem;
            margin: 0.6rem 0 1.35rem 0;
        }

        /* Tabs */
        div[data-baseweb="tab-list"] {
            border-bottom: 1px solid #383b42 !important;
            gap: 1.25rem !important;
        }

        button[data-baseweb="tab"] {
            color: #d3d5d9 !important;
            background: transparent !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ff2b2b !important;
        }

        div[data-baseweb="tab-highlight"] {
            background-color: #ff2b2b !important;
        }

        /* Form shell */
        [data-testid="stForm"] {
            background: transparent !important;
            border: 0 !important;
            padding: 0.8rem 0 0 0 !important;
        }

        /* Labels */
        [data-testid="stWidgetLabel"] p {
            color: #f3f3f3 !important;
            font-weight: 500 !important;
        }

        /* Inputs */
        div[data-baseweb="input"] {
            background: #16191e !important;
            border: 1px solid #444851 !important;
            border-radius: 8px !important;
        }

        div[data-baseweb="input"] input {
            color: #f5f5f5 !important;
            background: transparent !important;
        }

        div[data-baseweb="input"] input::placeholder {
            color: #777c85 !important;
            opacity: 1 !important;
        }

        /* Password icon */
        div[data-baseweb="input"] svg {
            fill: #f2f2f2 !important;
            color: #f2f2f2 !important;
        }

        /* Primary auth buttons */
        .stFormSubmitButton > button {
            min-height: 3.25rem !important;
            background: linear-gradient(90deg, #d90808 0%, #ff2a23 100%) !important;
            border: 1px solid #ff3932 !important;
            color: white !important;
            font-weight: 650 !important;
            letter-spacing: 0.04em !important;
            border-radius: 7px !important;
        }

        .stFormSubmitButton > button:hover {
            border-color: #ff5a55 !important;
            filter: brightness(1.06);
        }

        /* Alert boxes */
        [data-testid="stAlert"] {
            background: #17191e !important;
            border-color: #343840 !important;
            color: #f4f4f4 !important;
        }

        /* Keep the login panel vertically similar to the concept */
        .auth-spacer {
            height: 3.7rem;
        }

        /* Mobile */
        @media (max-width: 768px) {
            .block-container {
                padding: 0.35rem 0.65rem 1rem 0.65rem !important;
            }

            .auth-spacer {
                height: 0.4rem;
            }

            .auth-subtitle {
                margin-bottom: 0.75rem;
            }

            div[data-baseweb="tab-list"] {
                gap: 0.9rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    hero_col, form_col = st.columns([1.03, 1], gap="large")

    with hero_col:
        if LOGIN_HERO.exists():
            st.image(str(LOGIN_HERO), use_container_width=True)

    with form_col:
        st.markdown('<div class="auth-spacer"></div>', unsafe_allow_html=True)

        if LOGIN_LOGO.exists():
            st.image(str(LOGIN_LOGO), use_container_width=True)
        else:
            st.markdown("## Razvan Performance Lab")

        st.markdown(
            '<div class="auth-subtitle">Your personal training and bodyweight tracker.</div>',
            unsafe_allow_html=True,
        )

        login_tab, signup_tab = st.tabs(["Sign in", "Create account"])

        with login_tab:
            with st.form("sign_in_form"):
                email = st.text_input(
                    "Email",
                    placeholder="you@example.com",
                    key="login_email",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )
                submitted = st.form_submit_button(
                    "ENTER PERFORMANCE LAB",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not email or not password:
                    st.error("Enter your email and password.")
                else:
                    try:
                        sign_in(email, password)
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not sign in: {exc}")

        with signup_tab:
            with st.form("sign_up_form"):
                display_name = st.text_input(
                    "Name",
                    placeholder="Razvan",
                    key="signup_name",
                )
                email = st.text_input(
                    "Email",
                    placeholder="you@example.com",
                    key="signup_email",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    help="Use at least 6 characters.",
                    key="signup_password",
                )
                submitted = st.form_submit_button(
                    "CREATE ACCOUNT",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not display_name or not email or not password:
                    st.error("Enter your name, email and password.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        response = sign_up(email, password, display_name)
                        if response.session:
                            st.success("Account created.")
                            st.rerun()
                        else:
                            st.success(
                                "Account created. Check your email for the confirmation link, "
                                "then return here and sign in."
                            )
                    except Exception as exc:
                        st.error(f"Could not create account: {exc}")
