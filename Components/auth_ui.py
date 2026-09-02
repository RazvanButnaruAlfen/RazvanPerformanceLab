from pathlib import Path

import streamlit as st

from Services.auth import sign_in, sign_up

LOGIN_HERO = Path("Assets/login_hero.png")
APP_LOGO = Path("Assets/app_logo.png")


def render_auth_screen():
    st.markdown(
        """
        <style>
        .auth-copy {
            opacity: 0.72;
            margin-top: -0.25rem;
            margin-bottom: 1.1rem;
        }

        @media (max-width: 768px) {
            .auth-mobile-logo img {
                max-width: 310px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Desktop: artwork left, real form right.
    # Mobile: Streamlit stacks these vertically.
    hero_col, form_col = st.columns([1.05, 1], gap="large")

    with hero_col:
        if LOGIN_HERO.exists():
            st.image(str(LOGIN_HERO), use_container_width=True)

    with form_col:
        if APP_LOGO.exists():
            st.markdown('<div class="auth-mobile-logo">', unsafe_allow_html=True)
            st.image(str(APP_LOGO), width=360)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.title("Razvan Performance Lab")

        st.markdown(
            '<div class="auth-copy">Your personal training and bodyweight tracker.</div>',
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
                    "Enter Performance Lab",
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
                    "Create my profile",
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
