from __future__ import annotations

import time

import streamlit as st


def _elapsed_seconds(prefix: str) -> int:
    accumulated = float(st.session_state.get(f"{prefix}_accumulated", 0.0))
    started_at = st.session_state.get(f"{prefix}_started_at")
    running = bool(st.session_state.get(f"{prefix}_running", False))

    if running and started_at is not None:
        accumulated += max(0.0, time.time() - float(started_at))

    return max(0, int(accumulated))


def _format_elapsed(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def _start(prefix: str) -> None:
    if not st.session_state.get(f"{prefix}_running", False):
        st.session_state[f"{prefix}_started_at"] = time.time()
        st.session_state[f"{prefix}_running"] = True


def _pause(prefix: str) -> None:
    if not st.session_state.get(f"{prefix}_running", False):
        return

    started_at = st.session_state.get(f"{prefix}_started_at")
    if started_at is not None:
        accumulated = float(st.session_state.get(f"{prefix}_accumulated", 0.0))
        accumulated += max(0.0, time.time() - float(started_at))
        st.session_state[f"{prefix}_accumulated"] = accumulated

    st.session_state[f"{prefix}_started_at"] = None
    st.session_state[f"{prefix}_running"] = False


def _reset(prefix: str) -> None:
    st.session_state[f"{prefix}_accumulated"] = 0.0
    st.session_state[f"{prefix}_started_at"] = None
    st.session_state[f"{prefix}_running"] = False


def get_session_seconds(prefix: str = "session_timer") -> int:
    return _elapsed_seconds(prefix)


def reset_session_timer(prefix: str = "session_timer") -> None:
    _reset(prefix)


@st.fragment(run_every=1)
def render_session_timer(prefix: str = "session_timer") -> None:
    running = bool(st.session_state.get(f"{prefix}_running", False))
    elapsed = _elapsed_seconds(prefix)
    status = "RUNNING" if running else ("PAUSED" if elapsed > 0 else "READY")

    st.markdown(
        """
        <style>
        .rpl-session-timer-card {
            border: 1px solid #343940;
            border-radius: 12px;
            background:
                radial-gradient(circle at 10% 20%, rgba(255,42,35,0.12), rgba(0,0,0,0) 40%),
                #111419;
            padding: 0.75rem 0.9rem 0.65rem 0.9rem;
            margin: 0.25rem 0 0.75rem 0;
        }

        .rpl-session-timer-label {
            color: #aeb2b9;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        .rpl-session-timer-value {
            color: #ffffff;
            font-size: 2.15rem;
            line-height: 1.05;
            font-weight: 800;
            letter-spacing: 0.04em;
            margin-top: 0.1rem;
        }

        .rpl-session-timer-status {
            color: #ff4a45;
            font-size: 0.70rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }

        @media (max-width: 768px) {
            .rpl-session-timer-card {
                padding: 0.65rem 0.7rem 0.55rem 0.7rem;
            }

            .rpl-session-timer-value {
                font-size: 1.8rem;
            }

            .st-key-session_timer_controls div[data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap !important;
                gap: 0.35rem !important;
            }

            .st-key-session_timer_controls div[data-testid="column"] {
                min-width: 0 !important;
                width: auto !important;
                flex: 1 1 0 !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="rpl-session-timer-card">
            <div class="rpl-session-timer-label">Session Timer</div>
            <div class="rpl-session-timer-value">{_format_elapsed(elapsed)}</div>
            <div class="rpl-session-timer-status">{status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="session_timer_controls"):
        start_col, pause_col, reset_col = st.columns(3)

        with start_col:
            if st.button(
                "Start" if elapsed == 0 else "Resume",
                key=f"{prefix}_start_button",
                use_container_width=True,
                disabled=running,
            ):
                _start(prefix)
                st.rerun(scope="fragment")

        with pause_col:
            if st.button(
                "Pause",
                key=f"{prefix}_pause_button",
                use_container_width=True,
                disabled=not running,
            ):
                _pause(prefix)
                st.rerun(scope="fragment")

        with reset_col:
            if st.button(
                "Reset",
                key=f"{prefix}_reset_button",
                use_container_width=True,
                disabled=(elapsed == 0 and not running),
            ):
                _reset(prefix)
                st.rerun(scope="fragment")
