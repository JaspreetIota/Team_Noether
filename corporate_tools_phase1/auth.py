"""Password authentication backed by Streamlit Secrets."""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import time

import streamlit as st

MAX_ATTEMPTS = 5
LOCK_SECONDS = 60


def verify_password(password: str, encoded_hash: str) -> bool:
    """Verify a password against an encoded scrypt hash."""
    try:
        algorithm, n, r, p, salt, expected = encoded_hash.split("$", 5)
        if algorithm != "scrypt":
            return False
        expected_bytes = base64.urlsafe_b64decode(expected)
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=base64.urlsafe_b64decode(salt),
            n=int(n), r=int(r), p=int(p), dklen=len(expected_bytes),
        )
        return hmac.compare_digest(digest, expected_bytes)
    except (ValueError, TypeError):
        return False


def _configured_users() -> dict[str, str]:
    try:
        return {str(name).lower(): str(value) for name, value in st.secrets["auth"]["users"].items()}
    except (KeyError, FileNotFoundError):
        return {}


def require_login() -> str:
    """Render the login gate and return the authenticated username."""
    if st.session_state.get("authenticated") and st.session_state.get("username"):
        return str(st.session_state["username"])

    users = _configured_users()
    st.markdown(
        "<div class='auth-hero'><div class='auth-mark'>N</div>"
        "<div class='tool-kicker'>Secure workspace</div>"
        "<h1>Welcome back</h1><p>Sign in to access Corporate Tools.</p></div>",
        unsafe_allow_html=True,
    )
    if not users:
        st.error("Authentication is not configured. Add the user hashes to Streamlit Secrets.")
        st.code('[auth.users]\nbhawna = "scrypt$..."\njaspreet = "scrypt$..."', language="toml")
        st.stop()

    locked_until = float(st.session_state.get("login_locked_until", 0))
    remaining = max(0, int(locked_until - time.monotonic()))
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input("Password", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True, disabled=remaining > 0)

    if remaining > 0:
        st.warning(f"Too many unsuccessful attempts. Try again in {remaining} seconds.")
    elif submitted:
        normalized = username.strip().lower()
        stored_hash = users.get(normalized, "")
        if stored_hash and verify_password(password, stored_hash):
            st.session_state["authenticated"] = True
            st.session_state["username"] = normalized
            st.session_state["login_attempts"] = 0
            st.session_state.pop("login_locked_until", None)
            st.rerun()
        else:
            attempts = int(st.session_state.get("login_attempts", 0)) + 1
            st.session_state["login_attempts"] = attempts
            if attempts >= MAX_ATTEMPTS:
                st.session_state["login_attempts"] = 0
                st.session_state["login_locked_until"] = time.monotonic() + LOCK_SECONDS
                st.error("Too many unsuccessful attempts. Sign-in is temporarily locked.")
            else:
                st.error("Incorrect username or password.")
    st.stop()


def render_account(username: str) -> None:
    """Show the active user and provide a session logout action."""
    st.markdown(
        f"<div class='account-note'><span>Signed in as</span><strong>{html.escape(username.title())}</strong></div>",
        unsafe_allow_html=True,
    )
    if st.button("Sign out", use_container_width=True):
        for key in ("authenticated", "username", "login_attempts", "login_locked_until"):
            st.session_state.pop(key, None)
        st.rerun()
