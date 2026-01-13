import os
import base64
from pathlib import Path

import streamlit as st

from services.repo import get_repo
from services.auth import require_auth
from services.ui import inject_global_css, topbar

from app_pages import Dashboard, Patients, Sessions, Programs, Alerts, Devices, Settings
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=3000, key="app_autorefresh")  

APP_TITLE = "PhysioTrack Pro"

NAV_ITEMS = [
    ("Dashboard", "Dashboard", "📊"),
    ("Patients",  "Patients",  "🧑‍⚕️"),
    ("Sessions",  "Sessions",  "📅"),
    ("Programs",  "Programs",  "🧩"),
    ("Alerts",    "Alerts",    "🔔"),
    ("Devices",   "Devices",   "📟"),
    ("Settings",  "Settings",  "⚙️"),
]

PAGES = {
    "Dashboard": Dashboard.render,
    "Patients": Patients.render,
    "Sessions": Sessions.render,
    "Programs": Programs.render,
    "Alerts": Alerts.render,
    "Devices": Devices.render,
    "Settings": Settings.render,
}


def _logo_data_uri() -> str | None:
    try:
        assets_dir = Path(__file__).resolve().parent / "assets"
        p = assets_dir / "pt_logo.jpeg"
        if not p.exists():
            return None
        b = p.read_bytes()
        return "data:image/jpeg;base64," + base64.b64encode(b).decode("ascii")
    except Exception:
        return None


def _init_state():
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("search_q", "")
    st.session_state.setdefault("selected_patient_id", None)
    st.session_state.setdefault("selected_session_id", None)
    st.session_state.setdefault("selected_device_id", None)
    st.session_state.setdefault("api_base_url", os.getenv("PHYSIOTRACK_API_BASE_URL", "http://127.0.0.1:8000"))


def _get_qp_value(key: str):
    try:
        v = st.query_params.get(key, None)
    except Exception:
        v = st.experimental_get_query_params().get(key, None)

    if isinstance(v, list):
        return v[0] if v else None
    return v


def _set_qp_value(key: str, value: str):
    try:
        st.query_params[key] = value
    except Exception:
        st.experimental_set_query_params(**{key: value})


def _sync_page_from_query():
    qp_page = _get_qp_value("page")
    valid = {name for name, _, _ in NAV_ITEMS}

    if qp_page in valid:
        st.session_state.page = qp_page
        return

    cur = st.session_state.get("page", "Dashboard")
    if cur not in valid:
        cur = "Dashboard"
    st.session_state.page = cur
    _set_qp_value("page", cur)


def _sidebar_nav():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none; }

        /* brand header */
        .pt-brand {
          display:flex; gap:10px; align-items:center;
          padding: 6px 10px 10px 10px;
          margin-bottom: 6px;
        }
        .pt-logo {
          width: 36px; height: 36px; border-radius: 10px;
          background: #4318FF;
          display:flex; align-items:center; justify-content:center;
          color: white; font-weight: 900;
          overflow: hidden;
        }
        .pt-logo img{
          width:100%;
          height:100%;
          object-fit:cover;
          display:block;
        }
        .pt-title { font-weight: 800; color: #2B3674; line-height: 1; }
        .pt-sub { color: #A3AED0; font-size: 12px; margin-top: 2px; }

        /* rapatkan spacing antar element di sidebar */
        [data-testid="stSidebar"] div[data-testid="element-container"]{
          margin: 2px 0 !important;
          padding: 0 !important;
        }

        /* base style semua button sidebar */
        [data-testid="stSidebar"] div[data-testid="stButton"] > button{
          width: 100% !important;
          justify-content: flex-start !important;

          min-height: 36px !important;
          height: 36px !important;
          padding: 6px 10px !important;

          border-radius: 12px !important;
          border: 0 !important;
          box-shadow: none !important;

          background: transparent !important;
          color: #2B3674 !important;
          font-weight: 600 !important;
          line-height: 1 !important;
        }

        /* hover -> abu-abu */
        [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover{
          background: rgba(148, 163, 184, 0.22) !important;
        }

        /* teks button */
        [data-testid="stSidebar"] div[data-testid="stButton"] > button p{
          margin: 0 !important;
          width: 100% !important;
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
          font-size: 14px !important;
        }

        /* ACTIVE STATE (Streamlit 1.52 cenderung pakai kind="primary") */
        [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"],
        [data-testid="stSidebar"] button[kind="primary"],
        [data-testid="stSidebar"] button[data-testid="baseButton-primary"]{
          background: rgba(148, 163, 184, 0.40) !important; /* abu-abu gelap */
          color: #0F172A !important;
        }
        [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover,
        [data-testid="stSidebar"] button[kind="primary"]:hover,
        [data-testid="stSidebar"] button[data-testid="baseButton-primary"]:hover{
          background: rgba(148, 163, 184, 0.50) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    current = st.session_state.get("page", "Dashboard")
    logo_uri = _logo_data_uri()

    if logo_uri:
        logo_html = f"<img src='{logo_uri}' alt='PhysioTrack' />"
    else:
        logo_html = "∿"

    with st.sidebar:
        st.markdown(
            f"""
            <div class="pt-brand">
              <div class="pt-logo">{logo_html}</div>
              <div>
                <div class="pt-title">PhysioTrack</div>
              
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for name, label, icon in NAV_ITEMS:
            btn_type = "primary" if name == current else "secondary"
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{name}",
                use_container_width=True,
                type=btn_type,
            ):
                st.session_state.page = name
                _set_qp_value("page", name)
                st.rerun()


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="💙", layout="wide")
    _init_state()

    if not require_auth():
        return

    _sync_page_from_query()

    inject_global_css()
    repo = get_repo()

    _sidebar_nav()
    topbar(repo)

    render_fn = PAGES.get(st.session_state.page, Dashboard.render)
    render_fn(repo)


if __name__ == "__main__":
    main()
