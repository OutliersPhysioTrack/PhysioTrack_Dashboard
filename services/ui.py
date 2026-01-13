# services/ui.py
import streamlit as st

# =====================
# THEME TOKENS 
# =====================
BG_COLOR = "#FFFFFF"     
CARD_BG = "#FFFFFF"
TEXT_COLOR = "#2B3674"
TEXT_LIGHT = "#A3AED0"
PRIMARY = "#4318FF"
GREEN = "#05CD99"
YELLOW = "#FFB547"
ORANGE = "#FF8A00"
RED = "#EE5D50"


# =====================
# GLOBAL CSS
# =====================
def inject_global_css():
    st.markdown(
        f"""
        <style>
        /* =========================
           FONT: Inter (400/500/600)
           Safe: tidak override global span/div pakai !important (Material Icons aman)
           ========================= */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        /* App background */
        .stApp {{
          background: {BG_COLOR} !important;
        }}

        /* Layout paddings */
        .block-container {{
          padding-top: 72px !important;
          padding-bottom: 28px !important;
        }}

        /* Hide default Streamlit multi-page nav if any */
        [data-testid="stSidebarNav"] {{ display: none !important; }}

        /* =========================
           TYPOGRAPHY (SAFE)
           Jangan override "span" dan "div" secara global pakai !important,
           karena Material Icons (ligature) ada di span.
           ========================= */

        h1,h2,h3,h4,h5,h6, p, li, label {{
          font-family: "Inter", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI",
                       Roboto, Helvetica, Arial !important;
        }}

        div, span {{
          font-family: "Inter", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI",
                       Roboto, Helvetica, Arial;
        }}

        body {{
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }}
        p, li {{ font-weight: 400; }}
        label {{ font-weight: 500; }}
        h1,h2,h3,h4,h5,h6 {{
          font-weight: 600 !important;
          letter-spacing: -0.01em;
        }}

        span.material-icons,
        span.material-symbols-outlined,
        span.material-symbols-rounded,
        span.material-symbols-sharp,
        [data-testid="stIconMaterial"] span {{
          font-family: "Material Symbols Rounded" !important;
          font-weight: 400 !important;
          font-style: normal !important;
          font-size: 22px !important;
          line-height: 1 !important;
          letter-spacing: normal !important;
          text-transform: none !important;
          display: inline-block !important;
          white-space: nowrap !important;
          direction: ltr !important;
          -webkit-font-smoothing: antialiased !important;
        }}

        /* (OPSIONAL) Kalau kamu memang tidak butuh tombol collapse bawaan:
           hapus komentar di bawah ini. */
        /* [data-testid="collapsedControl"] {{ display: none !important; }} */

        /* Card component (legacy HTML card - kalau masih ada yang pakai) */
        .card {{
          background: {CARD_BG};
          border: 1px solid rgba(163,174,208,0.35);
          border-radius: 16px;
          padding: 18px 18px;
          box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
        }}
        .card-title {{
          font-size: 16px;
          font-weight: 600;
          color: {TEXT_COLOR};
          margin-bottom: 2px;
        }}
        .card-sub {{
          font-size: 13px;
          font-weight: 400;
          color: {TEXT_LIGHT};
          margin-bottom: 6px;
        }}

        /* Pills */
        .pill {{
          display:inline-flex;
          align-items:center;
          padding: 4px 10px;
          border-radius: 999px;
          font-size: 12px;
          font-weight: 600;
          border: 1px solid rgba(163,174,208,0.35);
          text-transform: lowercase;
          line-height: 1;
        }}
        .pill-red {{
          background: rgba(238,93,80,0.12);
          color: {RED};
          border-color: rgba(238,93,80,0.25);
        }}
        .pill-orange {{
          background: rgba(255,138,0,0.12);
          color: {ORANGE};
          border-color: rgba(255,138,0,0.25);
        }}
        .pill-yellow {{
          background: rgba(255,181,71,0.16);
          color: #B45309;
          border-color: rgba(255,181,71,0.25);
        }}
        .pill-green {{
          background: rgba(5,205,153,0.12);
          color: {GREEN};
          border-color: rgba(5,205,153,0.25);
        }}
        .pill-blue {{
          background: rgba(67,24,255,0.10);
          color: {PRIMARY};
          border-color: rgba(67,24,255,0.20);
        }}

        /* Topbar */
        .pt-topbar {{
          width: 100%;
          display:flex;
          align-items:center;
          justify-content:space-between;
          gap: 14px;
          margin-bottom: 18px;
        }}

        /* Search input styling (Streamlit text_input) */
        div[data-testid="stTextInput"] > div > div {{
          background: rgba(255,255,255,0.92) !important;
          border: 1px solid rgba(163,174,208,0.35) !important;
          border-radius: 14px !important;
        }}
        div[data-testid="stTextInput"] input {{
          height: 44px !important;
          border-radius: 14px !important;
          color: {TEXT_COLOR} !important;
          font-weight: 400 !important;
        }}

        /* Bell + avatar (legacy class - kalau masih dipakai) */
        .pt-icon-pill {{
          width: 44px;
          height: 44px;
          border-radius: 14px;
          background: rgba(255,255,255,0.92);
          border: 1px solid rgba(163,174,208,0.35);
          display:flex;
          align-items:center;
          justify-content:center;
          position: relative;
          user-select:none;
        }}
        .pt-badge {{
          position:absolute;
          top: -6px;
          right: -6px;
          width: 22px;
          height: 22px;
          border-radius: 999px;
          background: {RED};
          color: white;
          font-size: 12px;
          font-weight: 600;
          display:flex;
          align-items:center;
          justify-content:center;
          border: 2px solid {BG_COLOR};
        }}
        .pt-avatar {{
          width: 44px;
          height: 44px;
          border-radius: 14px;
          background: rgba(67,24,255,0.12);
          border: 1px solid rgba(67,24,255,0.20);
          display:flex;
          align-items:center;
          justify-content:center;
          color: {PRIMARY};
          font-weight: 600;
        }}
        .pt-right {{
          display:flex;
          gap: 10px;
          align-items:center;
        }}

        .stApp div[data-testid="stVerticalBlockBorderWrapper"] {{
          background: #FFFFFF !important;
          border: 1px solid rgba(163,174,208,0.35) !important;
          border-radius: 16px !important;
          box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06) !important;

          padding: 0 !important;            
          margin-bottom: 14px !important;   
        }}

        .stApp div[data-testid="stVerticalBlockBorderWrapper"] > div {{
          padding: 20px 20px 28px 20px !important;  
          box-sizing: border-box !important;
        }}

        /* =========================
           Popover buttons 
           ========================= */
        div[data-testid="stPopover"] > button {{
          width: 44px !important;
          height: 44px !important;
          min-width: 44px !important;
          border-radius: 14px !important;
          padding: 0 !important;
          background: rgba(255,255,255,0.92) !important;
          border: 1px solid rgba(163,174,208,0.35) !important;
          box-shadow: none !important;
        }}
        div[data-testid="stPopover"] > button:hover {{
          border-color: rgba(67,24,255,0.20) !important;
        }}

        /* =========================
           KPI CARD SPACING 
           ========================= */
        .kpi-card {{
          min-height: 130px;
          display:flex;
          flex-direction:column;
          justify-content:space-between;
          gap: 10px;
          padding: 2px 0 12px 0; 
          box-sizing: border-box;
        }}
        .kpi-head {{
          display:flex;
          align-items:flex-start;
          justify-content:space-between;
          gap: 12px;
        }}
        .kpi-title {{
          font-size: 14px;
          font-weight: 600;
          color: {TEXT_COLOR};
          line-height: 1.25;
        }}
        .kpi-icon {{
          font-size: 16px;
          opacity: .85;
          margin-top: 2px;
        }}
        .kpi-value {{
          font-size: 40px;
          font-weight: 600;
          color: {TEXT_COLOR};
          line-height: 1.0;
          margin-top: 2px;
        }}
        .kpi-delta {{
          font-size: 13px;
          font-weight: 500;
          line-height: 1.2;
          
        }}
        .kpi-green {{ color: {GREEN}; }}
        .kpi-red {{ color: {RED}; }}
        .kpi-muted {{ color: {TEXT_LIGHT}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )



# =====================
# NAV HELPERS
# =====================
def _set_qp_value(key: str, value: str):
    try:
        st.query_params[key] = value
    except Exception:
        st.experimental_set_query_params(**{key: value})


def goto_page(page_name: str):
    st.session_state.page = page_name
    _set_qp_value("page", page_name)


# =====================
# NOTIF + PROFILE (popover)
# =====================
_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _superscript(n: int) -> str:
    if n <= 0:
        return ""
    return str(n).translate(_SUP)


def notif_popover(repo=None):
    items = []
    open_count = 0

    if repo is not None:
        try:
            adf = repo.list_alerts(status="open")
            if adf is not None and len(adf) > 0:
                if "created_at" in adf.columns:
                    adf = adf.sort_values(["created_at"], ascending=False)
                open_count = int(len(adf))
                for _, r in adf.head(6).iterrows():
                    items.append(
                        {
                            "title": f"{str(r.get('severity','med')).upper()} • {r.get('patient_name','Patient')}",
                            "body": str(r.get("message", "")),
                            "meta": str(r.get("created_at", ""))[:16],
                        }
                    )
        except Exception:
            items = []
            open_count = 0

    label = f"🔔{_superscript(open_count)}" if open_count > 0 else "🔔"

    popover_fn = getattr(st, "popover", None)
    if popover_fn is None:
        with st.expander("Notifications", expanded=False):
            st.markdown("**Notifications**")
            if not items:
                st.caption("No open alerts.")
            else:
                for it in items:
                    st.markdown(f"**{it['title']}**")
                    if it.get("body"):
                        st.write(it["body"])
                    if it.get("meta"):
                        st.caption(it["meta"])
                    st.divider()
        return

    with popover_fn(label, use_container_width=False):
        st.markdown("**Notifications**")
        st.caption("Open alerts (real-time from database)")

        if not items:
            st.caption("No open alerts.")
        else:
            for it in items:
                st.markdown(f"**{it['title']}**")
                if it.get("body"):
                    st.write(it["body"])
                if it.get("meta"):
                    st.caption(it["meta"])
                st.divider()

        if st.button("View alerts", use_container_width=True, key="notif_view_alerts"):
            goto_page("Alerts")
            st.rerun()

def profile_popover():
    name = st.session_state.get("auth_name", "User")
    role = st.session_state.get("auth_role", "user")

    popover_fn = getattr(st, "popover", None)
    if popover_fn is None:
        # fallback
        if st.button("👤", key="profile_btn"):
            st.info(f"{name} • {role}")
        return

    with popover_fn("👤", use_container_width=False):
        st.markdown(f"**{name}**")
        st.caption(f"Role: {role}")
        st.write("")

        if st.button("Settings", use_container_width=True, key="profile_settings"):
            goto_page("Settings")
            st.rerun()

        from services.auth import logout  

        if st.button("Logout", use_container_width=True, key="profile_logout"):
            logout()
            st.rerun()


# =====================
# TOPBAR (Search + notif + profile) -> 1 wrapper border yang sama
# =====================
def topbar(repo=None):
    if "search_q" not in st.session_state:
        st.session_state["search_q"] = ""

    with st.container(border=True):
        left, right = st.columns([7.5, 1.5], gap="large")

        with left:
            st.text_input(
                label="Search",
                placeholder="Search patients, sessions, or devices...",
                value=st.session_state["search_q"],
                key="search_q",
                label_visibility="collapsed",
            )

        with right:
            c1, c2 = st.columns([1, 1], gap="small")
            with c1:
                notif_popover(repo)
            with c2:
                profile_popover()
