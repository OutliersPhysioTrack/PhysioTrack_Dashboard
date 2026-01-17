import streamlit as st
import pandas as pd

from views.cards import section_title, kpi_card
from views.tables import alert_cards



def render(repo):
    section_title("Alerts Center", "Monitor and triage patient alerts requiring attention", right_html="")

    alerts_all = repo.list_alerts()
    alerts_all = alerts_all if isinstance(alerts_all, pd.DataFrame) else pd.DataFrame()

    if len(alerts_all) and "status" in alerts_all.columns:
        open_n = int((alerts_all["status"].astype(str).str.lower() == "open").sum())
        resolved_n = int((alerts_all["status"].astype(str).str.lower() == "resolved").sum())
    else:
        open_n = 0
        resolved_n = 0

    total_n = int(len(alerts_all))

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        kpi_card("Open Alerts", str(open_n), "", "red" if open_n else "muted", "⛔")
    with c2:
        kpi_card("Resolved", str(resolved_n), "", "green" if resolved_n else "muted", "✅")
    with c3:
        kpi_card("Total Alerts", str(total_n), "", "muted", "📦")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    sev_vals = alerts_all["severity"].astype(str).str.lower().unique().tolist() if (len(alerts_all) and "severity" in alerts_all.columns) else []
    st_vals = alerts_all["status"].astype(str).str.lower().unique().tolist() if (len(alerts_all) and "status" in alerts_all.columns) else []
    sev_opts = ["All"] + sorted({v for v in sev_vals if v and v != "nan"})
    st_opts = ["All"] + sorted({v for v in st_vals if v and v != "nan"})

    f1, f2 = st.columns([1, 1], gap="large")
    with f1:
        severity = st.selectbox("Severity", sev_opts, index=0)
    with f2:
        status = st.selectbox("Status", st_opts, index=0)

    df = repo.list_alerts(severity=severity, status=status)
    st.caption(f"Showing {len(df)} alerts")

    alert_cards(df)

    with st.container(border=True):
        st.markdown(
            "<div class='card-title'>Update Alert</div>"
            "<div class='card-sub'>Change status and/or message</div>",
            unsafe_allow_html=True,
        )
        aid = st.selectbox("Alert ID", options=[""] + (df["alert_id"].astype(str).tolist() if len(df) else []))
        if aid:
            new_status = st.selectbox("Status", ["open", "resolved"])
            msg = st.text_area("Message (optional)", placeholder="Update message...")
            if st.button("Save Update", type="primary"):
                repo.update_alert(aid, new_status, msg.strip())
                st.success("Alert updated.")
                st.rerun()
