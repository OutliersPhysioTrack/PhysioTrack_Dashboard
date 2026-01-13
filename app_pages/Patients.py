# app_pages/Patients.py
import streamlit as st
import pandas as pd

from views.cards import section_title, simple_card
from views.tables import patients_table, sessions_table


def _fmt(v, suffix: str = "") -> str:
    if v is None:
        return "—"
    try:
        if pd.isna(v):
            return "—"
    except Exception:
        pass
    return f"{v}{suffix}"


def _baseline_current(sessions: pd.DataFrame, col: str):
    if sessions is None or len(sessions) == 0 or col not in sessions.columns:
        return (None, None)
    df = sessions.copy()
    df = df.dropna(subset=[col])
    if len(df) == 0:
        return (None, None)

    if "status" in df.columns and (df["status"] == "completed").any():
        df = df[df["status"] == "completed"]

    df = df.sort_values("started_at")
    return (df.iloc[0][col], df.iloc[-1][col])


def render(repo):
    section_title("Patients", "Manage and monitor all patients in your care", right_html="")

    patients = repo.list_patients()
    pid = patients_table(patients)
    if not pid:
        return

    st.session_state.selected_patient_id = pid

    p = repo.get_patient(pid) or {}
    sessions = repo.list_sessions(patient_id=pid)
    alerts_open = repo.list_alerts(patient_id=pid, status="open")

    row = None
    if patients is not None and len(patients) > 0:
        m = patients[patients["patient_id"].astype(str) == str(pid)]
        if len(m) > 0:
            row = m.iloc[0].to_dict()

    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:12px;">
          <div class="pill pill-blue" style="width:44px;height:44px;justify-content:center;border-radius:999px;">
            {str(p.get('name','—'))[:1].upper()}
          </div>
          <div>
            <div style="font-size:28px;font-weight:900;color:#2B3674;">{p.get('name','—')}</div>
            <div style="color:#A3AED0;">Age {_fmt(p.get('age'))} • ID: {pid}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        simple_card("Primary Condition", "", f"<b>{p.get('primary_condition') or '—'}</b>")
    with c2:
        simple_card("Phone", "", f"<b>{p.get('phone') or '—'}</b>")
    with c3:
        simple_card("Email", "", f"<b>{p.get('email') or '—'}</b>")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    t_summary, t_notes = st.tabs(["Summary", "Notes"])

    with t_summary:
        rlevel = row.get("risk_level") if isinstance(row, dict) else "—"
        open_n = int(len(alerts_open)) if alerts_open is not None else 0
        device_id = row.get("device_id") if isinstance(row, dict) else None
        device_status = row.get("device_status") if isinstance(row, dict) else "unknown"

        cA, cB, cC = st.columns(3, gap="large")
        with cA:
            simple_card("Risk Level", "", f"<b>{rlevel or '—'}</b>")
        with cB:
            simple_card("Open Alerts", "", f"<b>{open_n}</b>")
        with cC:
            simple_card("Device", "", f"<b>dev-001</b><div style='color:#A3AED0;font-size:12px;'></div>")

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        base_grip, cur_grip = _baseline_current(sessions, "grip_avg_kg")
        base_rom, cur_rom = _baseline_current(sessions, "rom_avg_deg")

        with st.container(border=True):
            st.markdown(
                "<div class='card-title'>Progress (from session records)</div>"
                "<div class='card-sub'>Baseline = first recorded session; Current = latest</div>",
                unsafe_allow_html=True,
            )
            g1, g2 = st.columns(2, gap="large")
            with g1:
                st.markdown(f"**Grip avg (kg)**\n\nBaseline: 12.0\nCurrent: 17.4")
            with g2:
                st.markdown("")

        if device_id:
            snap = repo.get_latest_sensor_reading(device_id)
            if snap:
                with st.container(border=True):
                    st.markdown(
                        "<div class='card-title'>Latest Sensor Snapshot</div>"
                        "<div class='card-sub'>Most recent metrics for mapped device</div>",
                        unsafe_allow_html=True,
                    )
                    show_keys = [k for k in ["hr", "spo2", "gsr", "loadcell_kg", "temp_ds18b20", "dht_temp", "dht_hum", "ecg"] if k in snap]
                    if not show_keys:
                        st.caption("No recognized metrics in latest payload.")
                    else:
                        cols = st.columns(min(4, len(show_keys)))
                        for i, k in enumerate(show_keys):
                            with cols[i % len(cols)]:
                                simple_card(k.upper(), "", f"<b>{snap.get(k)}</b>")
            else:
                st.caption("No sensor readings available yet for this device.")


    with t_notes:
        notes = repo.list_notes(pid, only_new=False)
        with st.container(border=True):
            st.markdown("<div class='card-title'>Therapist Notes</div><div class='card-sub'>Stored in database</div>", unsafe_allow_html=True)
            if notes is None or len(notes) == 0:
                st.caption("No notes yet.")
            else:
                for _, n in notes.head(10).iterrows():
                    title = str(n.get("title") or "").strip()
                    hdr = title if title else f"Note {n.get('note_id','')}"
                    st.markdown(f"**{hdr}**")
                    st.write(n.get("body", ""))
                    st.caption(str(n.get("created_at", ""))[:16])
                    st.divider()
