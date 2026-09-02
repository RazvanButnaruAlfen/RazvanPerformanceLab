import streamlit as st
from streamlit_js_eval import streamlit_js_eval


MOBILE_BREAKPOINT = 768


def detect_viewport() -> int | None:
    """
    Read the real browser viewport width using JavaScript.
    The value is stored in session_state so the rest of the app
    can render a genuinely different mobile or desktop layout.
    """
    width = streamlit_js_eval(
        js_expressions="window.innerWidth",
        key="rpl_viewport_width",
        want_output=True,
    )

    if width is not None:
        try:
            width = int(width)
            st.session_state["viewport_width"] = width
        except (TypeError, ValueError):
            pass

    return st.session_state.get("viewport_width")


def is_mobile() -> bool:
    width = detect_viewport()
    if width is None:
        # Safe fallback while JS initializes.
        return False
    return width <= MOBILE_BREAKPOINT
