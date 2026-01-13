import streamlit as st
import pandas as pd


def patients_table(df: pd.DataFrame) -> str | None:
    if df is None or len(df) == 0:
        st.info("No patients found in database.")
        return None

    id_col = "patient_id" if "patient_id" in df.columns else None
    name_col = "name" if "name" in df.columns else ("patient_name" if "patient_name" in df.columns else None)
    id_to_name = {}
    if id_col and name_col:
        try:
            id_to_name = dict(zip(df[id_col].astype(str).tolist(), df[name_col].astype(str).fillna("—").tolist()))
        except Exception:
            id_to_name = {}

    def _label(pid: str) -> str:
        if not pid:
            return ""
        return id_to_name.get(str(pid), str(pid))

    cols = [
        "patient_id",
        "name",
        "age",
        "primary_condition",
        "risk_level",
        "active_alerts_count",
        "device_status",
    ]
    show = df[[c for c in cols if c in df.columns]].copy()
    st.dataframe(show, use_container_width=True, hide_index=True)

    pid = st.selectbox(
        "Select patient to view details",
        options=[""] + df["patient_id"].astype(str).tolist(),
        index=0,
        format_func=_label,
    )
    return pid or None


def sessions_table(df: pd.DataFrame) -> str | None:
    if df is None or len(df) == 0:
        st.info("No sessions found.")
        return None

    cols = [
        "session_id",
        "started_at",
        "duration_min",
        "rep_count",
        "adherence_pct",
        "rom_avg_deg",
        "grip_avg_kg",
        "status",
    ]
    show = df[[c for c in cols if c in df.columns]].copy()

    if "started_at" in show.columns:
        show["started_at"] = pd.to_datetime(show["started_at"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(show, use_container_width=True, hide_index=True)

    sid = st.selectbox("Select session to review", options=[""] + df["session_id"].astype(str).tolist(), index=0)
    return sid or None


def devices_table(df: pd.DataFrame) -> str | None:
    if df is None or len(df) == 0:
        st.info("No devices registered.")
        return None

    show_cols = ["device_id", "patient_name", "status", "last_seen_at"]
    show = df[[c for c in show_cols if c in df.columns]].copy()
    if "last_seen_at" in show.columns:
        show["last_seen_at"] = pd.to_datetime(show["last_seen_at"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(show, use_container_width=True, hide_index=True)

    did = st.selectbox("Select device to view details", options=[""] + df["device_id"].astype(str).tolist(), index=0)
    return did or None


def alert_cards(df: pd.DataFrame):
    if df is None or len(df) == 0:
        st.info("No alerts found.")
        return

    for _, r in df.iterrows():
        sev = str(r.get("severity", "med")).lower()
        status = str(r.get("status", "open")).lower()

        badge = "pill-red" if sev in ("critical",) else ("pill-yellow" if sev in ("warning", "high") else "pill-blue")

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
                  <div style="font-weight:900;color:#2B3674;font-size:16px;">
                    {r.get("patient_name","—")}
                    <span class="pill {badge}" style="margin-left:8px;">{sev}</span>
                    <span class="pill pill-blue" style="margin-left:6px;">{status}</span>
                  </div>
                  <div style="color:#A3AED0;font-size:12px;">Type: {r.get("type","—")}</div>
                </div>
                <div style="margin-top:6px;color:#2B3674;">{r.get("message","") or "—"}</div>
                <div style="margin-top:8px;color:#A3AED0;font-size:12px;">
                  Created: {str(r.get("created_at",""))[:16]}
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
