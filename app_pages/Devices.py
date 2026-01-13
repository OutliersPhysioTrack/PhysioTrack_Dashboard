import streamlit as st
import pandas as pd

from views.cards import section_title, kpi_card, simple_card
from views.tables import devices_table


def render(repo):
    section_title("Device Management", "Monitor device status and connectivity", right_html="")

    df = repo.list_devices()
    df = df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    status = df["status"].astype(str).str.lower() if (len(df) and "status" in df.columns) else pd.Series(dtype=str)
    online_n = int((status == "online").sum()) if len(status) else 0
    offline_n = int((status == "offline").sum()) if len(status) else 0
    unknown_n = int(len(df) - online_n - offline_n) if len(df) else 0

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        kpi_card("Online", str(online_n), "", "green" if online_n else "muted", "📶")
    with c2:
        kpi_card("Offline", str(offline_n), "", "red" if offline_n else "muted", "📡")
    with c3:
        kpi_card("Unknown", str(unknown_n), "", "muted", "❔")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    did = devices_table(df)
    if not did:
        return

    st.session_state.selected_device_id = did
    dstat = repo.get_device(did) or {}
    last_seen = dstat.get("last_seen_at")
    status_txt = dstat.get("status") or "unknown"

    with st.container(border=True):
        st.markdown("<div class='card-title'>Device Details</div>", unsafe_allow_html=True)
        cA, cB, cC = st.columns(3, gap="large")
        with cA:
            simple_card("Device ID", "", f"<b>{did}</b>")
        with cB:
            simple_card("Status", "", f"<b>{status_txt}</b>")
        with cC:
            simple_card("Last Seen", "", f"<b>{str(last_seen)[:16] if last_seen else '—'}</b>")

    snap = repo.get_latest_sensor_reading(did)
    with st.container(border=True):
        st.markdown("<div class='card-title'>Latest Sensor Snapshot</div>", unsafe_allow_html=True)
        if not snap:
            st.caption("No sensor readings yet.")
        else:
            keys = sorted(snap.keys())
            cols = st.columns(min(4, len(keys)))
            for i, k in enumerate(keys):
                with cols[i % len(cols)]:
                    simple_card(k.upper(), "", f"<b>{snap.get(k)}</b>")
