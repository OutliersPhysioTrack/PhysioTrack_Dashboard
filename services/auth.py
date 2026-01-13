import base64
from pathlib import Path

import streamlit as st

_USERS = {
    "therapist@clinic.com": {"password": "therapist123", "role": "therapist", "name": "Therapist"},
}

LOGIN_CSS_SAFE = """
<style>
.stApp { background: #F4F7FE !important; }
.block-container { padding-top: 70px !important; }

/* Card wrapper via columns + container */
.login-wrap { max-width: 520px; margin: 0 auto; }
.login-header { text-align: center; margin-bottom: 14px; }
.login-title { font-size: 30px; font-weight: 800; color: #2B3674; margin-top: 10px; }
.login-sub { color: #A3AED0; margin-top: 6px; }

/* Form jadi card */
div[data-testid="stForm"]{
  background: #ffffff !important;
  border: 1px solid rgba(163, 174, 208, 0.35) !important;
  border-radius: 16px !important;
  padding: 22px !important;
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08) !important;
}

/* Inputs & button */
[data-testid="stTextInput"] input{
  height: 44px !important;
  border-radius: 10px !important;
}
div[data-testid="stForm"] [data-testid="stButton"] button{
  height: 44px !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}
</style>
"""


def _logo_data_uri() -> str | None:
    try:
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        p = assets_dir / "pt_logo.jpeg"
        if not p.exists():
            return None
        b = p.read_bytes()
        return "data:image/jpeg;base64," + base64.b64encode(b).decode("ascii")
    except Exception:
        return None


def is_authed() -> bool:
    return bool(st.session_state.get("auth_user"))


def logout():
    for k in ("auth_user", "auth_role", "auth_name"):
        st.session_state.pop(k, None)


def logout_button():
    if st.button("Logout", use_container_width=True):
        logout()
        st.rerun()


def require_auth() -> bool:
    if is_authed():
        return True

    st.markdown(LOGIN_CSS_SAFE, unsafe_allow_html=True)

    logo_uri = _logo_data_uri()
    if logo_uri:
        logo_html = (
            f"<img src='{logo_uri}' "
            "style='width:54px;height:54px;border-radius:16px;object-fit:cover;"
            "display:block;margin:0 auto;' />"
        )
    else:
        # fallback lama
        logo_html = (
            "<div style='width:54px;height:54px;border-radius:16px;background:#4318FF;"
            "display:flex;align-items:center;justify-content:center;"
            "margin:0 auto;color:white;font-weight:900;'>∿</div>"
        )

    st.markdown(
        f"""
        <div class="login-wrap">
          <div class="login-header">
            {logo_html}
            <div class="login-title">PhysioTrack</div>
            <div class="login-sub">Remote Rehabilitation Management Platform</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, mid, right = st.columns([1, 1.4, 1])
    with mid:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### Welcome Back")
            st.caption("Enter your credentials to access your dashboard")
            email = st.text_input("Email Address", placeholder="your.email@clinic.com")
            pwd = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Sign In  →", use_container_width=True)

        if submit:
            key = (email or "").strip().lower()
            user = _USERS.get(key)
            if (not user) or (user["password"] != (pwd or "")):
                st.error("Invalid email or password.")
                return False

            st.session_state.auth_user = key
            st.session_state.auth_role = user["role"]
            st.session_state.auth_name = user["name"]
            st.rerun()

    return False
