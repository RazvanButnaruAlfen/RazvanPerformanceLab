from pathlib import Path

import streamlit as st

from Services.auth import sign_in, sign_up

LOGIN_HERO = Path("Assets/login_hero.png")
APP_LOGO = Path("Assets/app_logo.png")


def render_auth_screen():
    # Desktop: artwork and login side-by-side.
    # Mobile: Streamlit stacks the columns vertically.
    hero_col, form_col = st.columns([1.05, 1], gap="large")

    with hero_col:
        if LOGIN_HERO.exists():
            st.image(str(LOGIN_HERO), use_container_width=True)
        elif APP_LOGO.exists():
            st.image(str(APP_LOGO), use_container_width=True)

    with form_col:
        if APP_LOGO.exists():
            st.image(str(APP_LOGO), width=430)
        else:
            st.markdown(
                """
                <div style="text-align:center;">
                    <div style="font-size:3rem;">🏋️</div>
                    <h1>Razvan Performance Lab</h1>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption("Your personal training and bodyweight tracker.")

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
