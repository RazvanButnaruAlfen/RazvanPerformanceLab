from __future__ import annotations

import streamlit as st
from supabase import create_client


def get_supabase_client():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except Exception as exc:
        raise RuntimeError(
            "Supabase is not configured. Add [supabase] url and key to Streamlit secrets."
        ) from exc

    if not url or not key:
        raise RuntimeError(
            "Supabase is not configured. Add [supabase] url and key to Streamlit secrets."
        )

    client = create_client(url, key)

    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")

    if access_token and refresh_token:
        try:
            client.auth.set_session(access_token, refresh_token)
        except Exception:
            clear_auth_session()

    return client


def current_user():
    user = st.session_state.get("auth_user")
    if user:
        return user

    try:
        client = get_supabase_client()
        response = client.auth.get_user()
        if response and response.user:
            st.session_state["auth_user"] = response.user
            return response.user
    except Exception:
        return None

    return None


def is_authenticated() -> bool:
    return current_user() is not None


def sign_in(email: str, password: str):
    client = get_supabase_client()
    response = client.auth.sign_in_with_password(
        {
            "email": email.strip(),
            "password": password,
        }
    )

    if not response.session or not response.user:
        raise RuntimeError("Sign in failed.")

    st.session_state["access_token"] = response.session.access_token
    st.session_state["refresh_token"] = response.session.refresh_token
    st.session_state["auth_user"] = response.user
    return response.user


def sign_up(email: str, password: str, display_name: str):
    client = get_supabase_client()
    response = client.auth.sign_up(
        {
            "email": email.strip(),
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name.strip() or email.split("@")[0],
                }
            },
        }
    )

    if response.session and response.user:
        st.session_state["access_token"] = response.session.access_token
        st.session_state["refresh_token"] = response.session.refresh_token
        st.session_state["auth_user"] = response.user

    return response


def sign_out():
    try:
        client = get_supabase_client()
        client.auth.sign_out()
    except Exception:
        pass

    clear_auth_session()


def clear_auth_session():
    for key in [
        "access_token",
        "refresh_token",
        "auth_user",
        "profile",
    ]:
        st.session_state.pop(key, None)


def get_profile():
    if "profile" in st.session_state:
        return st.session_state["profile"]

    user = current_user()
    if not user:
        return None

    client = get_supabase_client()
    result = (
        client.table("profiles")
        .select("id, display_name, avatar_emoji")
        .eq("id", str(user.id))
        .single()
        .execute()
    )

    profile = result.data if result.data else None
    st.session_state["profile"] = profile
    return profile
