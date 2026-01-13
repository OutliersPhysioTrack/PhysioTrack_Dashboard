# app_pages/Dashboard.py
import streamlit as st
import textwrap
import pandas as pd
from datetime import datetime, timedelta, timezone

from views.cards import section_title, kpi_card
from views.charts import line_chart, bar_chart
from services.metrics import (
    kpi_dashboard,
    chart_daily_adherence_training,
    chart_training_quality_seconds,
    chart_grip_improvement,
)


def _dedent(html: str) -> str:
    return textwrap.dedent(html).strip()


def _inject_chart_card_css():
    st.markdown(
        """
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"]{
          background: #FFFFFF !important;
          border: 1px solid rgba(163,174,208,0.35) !important;
          border-radius: 16px !important;
          box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div{
          background: #FFFFFF !important;
          border-radius: 16px !important;
          padding: 18px 18px 10px 18px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] *{ background-color: transparent; }
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stVerticalBlockBorderWrapper"] > div,
        div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPlotlyChart"],
        div[data-testid="stVerticalBlockBorderWrapper"] .stPlotlyChart{
          background: #FFFFFF !important;
        }
        .pt-card-title{
          font-size: 20px;
          font-weight: 700;
          letter-spacing: -0.01em;
          color: #0F172A;
          margin: 0 0 4px 0;
          line-height: 1.15;
        }
        .pt-card-sub{
          font-size: 14px;
          font-weight: 500;
          color: #64748B;
          margin: 0 0 14px 0;
          line-height: 1.35;
        }

        /* Live sensor card */
        .pt-sensor-wrap{
          padding-bottom: 14px; /* roomy bottom */
        }
        .pt-sensor-grid{
          display:grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
          margin-top: 6px;
        }
        .pt-sensor-tile{
          border: 1px solid rgba(163,174,208,0.25);
          border-radius: 14px;
          padding: 12px 12px 10px 12px;
          background: rgba(163,174,208,0.06);
        }
        .pt-sensor-label{
          font-size: 12px;
          font-weight: 700;
          color:#64748B;
          margin-bottom: 6px;
        }
        .pt-sensor-value{
          font-size: 20px;
          font-weight: 800;
          color:#0F172A;
          line-height: 1.1;
          display:flex;
          align-items:baseline;
          gap: 6px;
        }
        .pt-sensor-unit{
          font-size: 12px;
          font-weight: 700;
          color:#64748B;
        }

        /* ==========================
           Premium AI Health Card
           ========================== */
        /* ==========================
   AI Health Card (FULL COLOR GRADIENT like Kotlin)
   ========================== */
        .pt-ai-premium{
        position: relative;
        border-radius: 18px;
        padding: 16px 16px 14px 16px;
        border: 1px solid rgba(255,255,255,1);
        overflow: hidden;
        color: #FFFFFF;
        }

        /* Themes = full gradient */
        .pt-ai-theme-optimal{
        background: linear-gradient(180deg, rgba(34,197,94,1) 0%, rgba(22,163,74,1) 100%);
        }
        .pt-ai-theme-low{
        background: linear-gradient(180deg, rgba(251,191,36,1) 0%, rgba(245,158,11,1) 100%);
        }
        .pt-ai-theme-high{
        background: linear-gradient(180deg, rgba(239,68,68,1) 0%, rgba(220,38,38,1) 100%);
        }

        /* Soft blobs like Kotlin */
        .pt-ai-premium::before{
        content:"";
        position:absolute;
        width:240px;height:240px;
        right:-90px;top:-110px;
        border-radius:999px;
        background: rgba(255,255,255,0.18);
        }
        .pt-ai-premium::after{
        content:"";
        position:absolute;
        width:300px;height:300px;
        left:-140px;bottom:-160px;
        border-radius:999px;
        background: rgba(255,255,255,0.12);
        }

        .pt-ai-top{
        position: relative;
        z-index: 1;
        display:flex;
        justify-content: space-between;
        gap: 12px;
        align-items: flex-start;
        margin-bottom: 10px;
        }

        /* Title/subtitle in white */
        .pt-ai-kicker{
        font-size: 14px;
        font-weight: 900;
        letter-spacing: -0.01em;
        color: rgba(255,255,255,1);
        margin: 0;
        }
        .pt-ai-subkicker{
        font-size: 12px;
        font-weight: 700;
        color: rgba(255,255,255,0.85);
        margin: 2px 0 0 0;
        }

        /* Glass panel like Kotlin */
        .pt-ai-status{
        position: relative;
        z-index: 1;
        margin-top: 8px;
        border-radius: 16px;
        padding: 14px 14px;
        border: 1px solid rgba(255,255,255,0.22);
        background: rgba(255,255,255,0.16);
        backdrop-filter: blur(6px);
        }

        .pt-ai-status-label{
        font-size: 12px;
        font-weight: 800;
        color: rgba(255,255,255,0.90);
        margin: 0 0 6px 0;
        }
        .pt-ai-status-value{
        font-size: 28px;
        font-weight: 950;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.05;
        color: rgba(255,255,255,1);
        }
        .pt-ai-status-meta{
        font-size: 12px;
        font-weight: 800;
        color: rgba(255,255,255,0.88);
        margin-top: 6px;
        }


        # .pt-ai-theme-optimal .pt-ai-status-value{ color: rgba(16,185,129,1); }
        # .pt-ai-theme-low .pt-ai-status-value{ color: rgba(234,179,8,1); }
        # .pt-ai-theme-high .pt-ai-status-value{ color: rgba(239,68,68,1); }

        .pt-ai-section{
          position: relative;
          z-index: 1;
          margin-top: 12px;
        }
        .pt-ai-section-title{
          font-size: 12px;
          font-weight: 900;
          color:#64748B;
          margin: 0 0 10px 0;
          text-transform: none;
        }

        .pt-ai-row{
          display:flex;
          justify-content: space-between;
          align-items: baseline;
          gap: 10px;
          margin-top: 8px;
        }
        .pt-ai-row-label{
          font-size: 12px;
          font-weight: 900;
          color:#0F172A;
        }
        .pt-ai-row-pct{
          font-size: 12px;
          font-weight: 900;
          color:#0F172A;
        }

        .pt-ai-bar{
          height: 10px;
          border-radius: 999px;
          background: rgba(148,163,184,0.18);
          border: 1px solid rgba(148,163,184,0.22);
          overflow: hidden;
        }
        .pt-ai-fill{
          height: 100%;
          border-radius: 999px;
          width: 0%;
        }

        .pt-ai-fill-low{ background: rgba(234,179,8,1); }
        .pt-ai-fill-optimal{ background: rgba(16,185,129,1); }
        .pt-ai-fill-high{ background: rgba(239,68,68,1); }

        .pt-ai-note{
          position: relative;
          z-index: 1;
          margin-top: 10px;
          font-size: 11px;
          font-weight: 700;
          color: rgba(100,116,139,1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _fmt(val, decimals: int | None = None) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    try:
        f = float(val)
        if decimals is None:
            if abs(f - round(f)) < 1e-9:
                return str(int(round(f)))
            return str(f)
        return f"{f:.{decimals}f}"
    except Exception:
        return str(val)


def _pick_metric(snap: dict, aliases: list[str]):
    for a in aliases:
        if a in snap:
            return snap.get(a)
        if a.upper() in snap:
            return snap.get(a.upper())
        if a.lower() in snap:
            return snap.get(a.lower())
    return None


def _get_devices_df(repo) -> pd.DataFrame:
    df = repo.list_devices()
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()


def _pick_device_id(repo) -> str:
    devices_df = _get_devices_df(repo)
    default_dev = st.session_state.get("selected_device_id")
    if not default_dev:
        if len(devices_df) and "device_id" in devices_df.columns:
            default_dev = str(devices_df["device_id"].iloc[0])
        else:
            default_dev = "dev-001"
    return str(default_dev)


def _device_selector(repo, key_prefix: str = "dash"):
    devices_df = _get_devices_df(repo)
    default_dev = _pick_device_id(repo)

    if len(devices_df) and "device_id" in devices_df.columns:
        opts = devices_df["device_id"].astype(str).tolist()
        name_map = {}
        if "patient_name" in devices_df.columns:
            name_map = dict(zip(devices_df["device_id"].astype(str), devices_df["patient_name"].astype(str)))

        def _dev_label(did: str) -> str:
            pn = name_map.get(did)
            return f"{did} — {pn}" if pn and pn != "—" else did

        idx = opts.index(default_dev) if default_dev in opts else 0
        device_id = st.selectbox(
            "Device",
            options=opts,
            index=idx,
            format_func=_dev_label,
            label_visibility="collapsed",
            key=f"{key_prefix}_sensor_device_select",
        )
    else:
        device_id = st.text_input(
            "Device",
            value=default_dev,
            label_visibility="collapsed",
            key=f"{key_prefix}_sensor_device_input",
        )

    st.session_state.selected_device_id = str(device_id)
    return str(device_id)


def _render_live_sensor_card(repo):
    with st.container(border=True):
        headL, headR = st.columns([0.72, 0.28], gap="large")
        with headL:
            st.markdown("<div class='pt-card-title'>Live Sensor Readings</div>", unsafe_allow_html=True)
            st.markdown("<div class='pt-card-sub'>Latest snapshot per metric from the device stream</div>", unsafe_allow_html=True)

        with headR:
            device_id = _device_selector(repo, key_prefix="dash_live")

        snap = repo.get_latest_sensor_reading(device_id)
        if not snap:
            st.caption("No sensor readings yet for this device.")
            return

        fields = [
            ("Heart Rate", ["Heart Rate", "hr"], "bpm", 0),
            ("SpO₂", ["SPO2", "spo2"], "%", 0),
            ("ECG", ["ECG", "ecg"], "", 2),
            ("Body Temperature", ["Body Temperature", "temp_ds18b20"], "°C", 1),
            ("Room Temperature", ["Room Temperature", "dht_temp"], "°C", 1),
            ("Room Humidity", ["Room Humidity", "dht_hum"], "%", 1),
            ("Sweat", ["Sweat", "gsr"], "", 0),
            ("Loadcell", ["LOADCELL_KG", "loadcell_kg"], "kg", 1),
        ]

        tiles = []
        for label, aliases, unit, dec in fields:
            v = _pick_metric(snap, aliases)
            v_txt = _fmt(v, dec)
            if unit and v_txt != "—":
                value_html = f"{v_txt}<span class='pt-sensor-unit'>{unit}</span>"
            else:
                value_html = f"{v_txt}"
            tiles.append(
                f"<div class='pt-sensor-tile'>"
                f"<div class='pt-sensor-label'>{label}</div>"
                f"<div class='pt-sensor-value'>{value_html}</div>"
                f"</div>"
            )

        html = "<div class='pt-sensor-wrap'><div class='pt-sensor-grid'>" + "".join(tiles) + "</div></div>"
        st.markdown(html, unsafe_allow_html=True)


def _iso_z(dt: datetime) -> str:
    # backend accepts ISO with Z
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _fetch_sensor_series(repo, device_id: str, metric_code: str, minutes: int = 30, limit: int = 1500) -> pd.DataFrame:
    """
    Pull timeseries from backend:
      GET /sensor-readings?device_id=...&metric=HR&start=...&order=asc&limit=...
    """
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(minutes=minutes)

    params = {
        "device_id": device_id,
        "metric": metric_code,
        "start": _iso_z(start_dt),
        "end": _iso_z(end_dt),
        "order": "asc",
        "limit": int(limit),
    }

    getter = getattr(repo, "_get", None)
    if not callable(getter):
        return pd.DataFrame(columns=["ts", "value", "unit"])

    try:
        items = getter("/sensor-readings", params=params) or []
    except Exception:
        return pd.DataFrame(columns=["ts", "value", "unit"])

    rows = []
    for x in items:
        rows.append(
            {
                "ts": pd.to_datetime(x.get("ts"), errors="coerce"),
                "value": x.get("value"),
                "unit": x.get("unit") or "",
            }
        )
    df = pd.DataFrame(rows)
    if len(df):
        df = df.dropna(subset=["ts"]).sort_values("ts")

        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])
    return df


def _render_sensor_visualization_card(repo):
    with st.container(border=True):
        headL, headR = st.columns([0.72, 0.28], gap="large")
        with headL:
            st.markdown("<div class='pt-card-title'>Sensor Visualization</div>", unsafe_allow_html=True)
            st.markdown("<div class='pt-card-sub'>Select one sensor and view recent readings</div>", unsafe_allow_html=True)

        with headR:
            device_id = _device_selector(repo, key_prefix="dash_vis")

        metric_options = [
            ("Heart Rate", "HR"),
            ("SpO₂", "SPO2"),
            ("ECG", "ECG"),
            ("Body Temperature", "TEMP_DS18B20"),
            ("Room Temperature", "DHT_TEMP"),
            ("Room Humidity", "DHT_HUM"),
            ("Sweat", "GSR"),
            ("Loadcell (kg)", "LOADCELL_KG"),
        ]

        # persist selection
        default_code = st.session_state.get("dash_vis_metric_code") or "HR"
        codes = [c for _, c in metric_options]
        try:
            default_idx = codes.index(default_code)
        except Exception:
            default_idx = 0

        label, metric_code = st.selectbox(
            "Sensor",
            options=metric_options,
            index=default_idx,
            format_func=lambda x: x[0],
            key="dash_vis_metric_select",
        )
        metric_code = metric_code  
        st.session_state["dash_vis_metric_code"] = metric_code

        df = _fetch_sensor_series(repo, device_id=device_id, metric_code=metric_code, minutes=30, limit=2000)

        if df is None or len(df) == 0:
            st.caption("No data available for the selected sensor (last 30 minutes).")
            return

        unit = (df["unit"].dropna().iloc[-1] if "unit" in df.columns and len(df["unit"].dropna()) else "").strip()
        last_val = df["value"].iloc[-1]
        unit_txt = f" {unit}" if unit else ""

        st.markdown(
            f"<div style='color:#64748B;font-weight:600;margin-top:-6px;margin-bottom:8px;'>Latest: {_fmt(last_val, 2)}{unit_txt}</div>",
            unsafe_allow_html=True,
        )

        plot_df = df[["ts", "value"]].copy()
        line_chart(plot_df, x="ts", y="value", y_range=None, height=300)


def _render_ai_health_prediction_card(repo):

    with st.container(border=True):
        headL, headR = st.columns([0.72, 0.28], gap="large")
        with headL:
            st.markdown("<div class='pt-card-title'>AI Health Prediction</div>", unsafe_allow_html=True)

        with headR:
            device_id = _device_selector(repo, key_prefix="dash_ai")

        snap = {}
        getter = getattr(repo, "get_latest_ai", None)
        if callable(getter):
            try:
                snap = getter(device_id) or {}
            except Exception:
                snap = {}

        if not snap:
            getter2 = getattr(repo, "_get", None)
            if callable(getter2):
                try:
                    snap = getter2(f"/devices/{device_id}/ai/latest") or {}
                except Exception:
                    snap = {}

        if not snap:
            st.caption("No AI prediction available yet for this device.")
            return

        raw_label = (snap.get("ai_label") or snap.get("label") or "").strip()
        raw_conf = snap.get("ai_conf", snap.get("conf", None))

        # Normalize label -> SAFE / WARNING / DANGER (unchanged logic intent)
        norm = raw_label.lower().strip()
        if norm in {"safe", "optimal", "ok", "normal"}:
            status_key = "optimal"
            status_text = "SAFE"
        elif norm in {"warning", "low", "low_risk", "low risk", "caution"}:
            status_key = "low"
            status_text = "WARNING"
        elif norm in {"danger", "high", "high_risk", "high risk", "critical"}:
            status_key = "high"
            status_text = "DANGER"
        else:
            status_key = "low"
            status_text = raw_label.upper() if raw_label else "UNKNOWN"

        conf_pct = 0.0
        try:
            if raw_conf is not None:
                c = float(raw_conf)
                conf_pct = (c * 100.0) if 0.0 <= c <= 1.0 else c
                conf_pct = max(0.0, min(100.0, conf_pct))
        except Exception:
            conf_pct = 0.0

        theme_cls = {"optimal": "pt-ai-theme-optimal", "low": "pt-ai-theme-low", "high": "pt-ai-theme-high"}[status_key]

        html = f"""
        <div class="pt-ai-premium {theme_cls}">
          <div class="pt-ai-top">
            <div>
              <div class="pt-ai-kicker">AI Health Prediction</div>
              <div class="pt-ai-subkicker">Current status & confidence snapshot</div>
            </div>
          </div>

          <div class="pt-ai-status">
            <div class="pt-ai-status-label">Current Status</div>
            <div class="pt-ai-status-value">{status_text}</div>
            <div class="pt-ai-status-meta">Confidence: {int(round(conf_pct))}%</div>
          </div>
        </div>
        """
        st.markdown(_dedent(html), unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

def render(repo):
    _inject_chart_card_css()

    section_title(
        "Dashboard Overview",
        "Monitor patient progress, adherence, and open alerts",
        right_html="",
    )

    kpi = kpi_dashboard(repo)
    c1, c2, c3, c4 = st.columns(4, gap="large")

    with c1:
        kpi_card("Active Patients", str(kpi["active_patients"]), "", "muted", "👥")
    with c2:
        delta = f"High-risk open: {kpi['high_risk_open_alerts']}" if kpi["open_alerts"] else "No open alerts"
        kpi_card("Open Alerts", str(kpi["open_alerts"]), delta, "red" if kpi["open_alerts"] else "muted", "🔔")
    with c3:
        kpi_card("Latest-day Sessions", str(kpi["today_sessions"]), "", "muted", "📅")
    with c4:
        kpi_card("Avg. Adherence", f"100%", "", "green", "📈")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    _render_ai_health_prediction_card(repo)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    _render_live_sensor_card(repo)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    _render_sensor_visualization_card(repo)


    

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        with st.container(border=True):
            st.markdown("<div class='pt-card-title'>Daily Adherence</div>", unsafe_allow_html=True)
            st.markdown("<div class='pt-card-sub'>Mean adherence per day (last 14 days)</div>", unsafe_allow_html=True)
            df = chart_daily_adherence_training(repo, days=14)
            line_chart(df, "day", "adherence_pct", y_range=[0, 100])

    with c2:
        with st.container(border=True):
            st.markdown("<div class='pt-card-title'>Training Quality</div>", unsafe_allow_html=True)
            st.markdown("<div class='pt-card-sub'>duration_sec × adherence (last 14 days)</div>", unsafe_allow_html=True)
            df = chart_training_quality_seconds(repo, days=14)
            bar_chart(df, "day", "quality_seconds", y_range=None)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
