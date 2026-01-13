import pandas as pd
import random


_SEV_RANK = {
    "low": 1,
    "info": 1,
    "med": 2,
    "medium": 2,
    "warning": 3,
    "high": 3,
    "critical": 4,
}


def _to_day(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.floor("D")


def kpi_dashboard(repo):
    patients = repo.list_patients()
    sessions = repo.list_sessions()

    active_patients = int(len(patients)) if patients is not None else 0

    try:
        alerts_open = repo.list_alerts(status="open")
    except Exception:
        alerts_open = pd.DataFrame(columns=["severity", "status"])

    open_alerts = int(len(alerts_open)) if alerts_open is not None else 0

    high_risk_open = 0
    if alerts_open is not None and len(alerts_open) > 0 and "severity" in alerts_open.columns:
        sev = alerts_open["severity"].astype(str).str.lower()
        high_risk_open = int(sev.map(_SEV_RANK).fillna(2).ge(3).sum())

    today_sessions = 0
    if sessions is not None and len(sessions) > 0 and "started_at" in sessions.columns:
        df = sessions.copy()
        df["day"] = _to_day(df["started_at"])
        df = df.dropna(subset=["day"])
        if len(df) > 0:
            latest_day = df["day"].max()
            today_sessions = int((df["day"] == latest_day).sum())

    avg_adherence_pct = 0
    if sessions is not None and len(sessions) > 0 and "adherence" in sessions.columns:
        adh = pd.to_numeric(sessions["adherence"], errors="coerce").dropna()
        if len(adh) > 0:
            avg_adherence_pct = int(round(float(adh.clip(lower=0, upper=1).mean()) * 100))

    return {
        "active_patients": active_patients,
        "open_alerts": open_alerts,
        "high_risk_open_alerts": high_risk_open,
        "today_sessions": today_sessions,
        "avg_adherence_pct": avg_adherence_pct,
    }


def chart_daily_adherence_training(repo, days: int = 14) -> pd.DataFrame:
    sessions = repo.list_sessions()
    if sessions is None or len(sessions) == 0 or "started_at" not in sessions.columns:
        return pd.DataFrame({"day": [], "adherence_pct": []})

    df = sessions.copy()
    df["day"] = _to_day(df["started_at"])
    df = df.dropna(subset=["day"])

    if "status" in df.columns:
        df = df[df["status"] == "completed"]

    if "adherence" not in df.columns:
        return pd.DataFrame({"day": [], "adherence_pct": []})

    adh = pd.to_numeric(df["adherence"], errors="coerce").fillna(0).clip(lower=0, upper=1)
    df["adherence_pct"] = (adh * 100.0).round(0).astype(int)

    end = df["day"].max()
    start = end - pd.Timedelta(days=days - 1)
    df = df[(df["day"] >= start) & (df["day"] <= end)]

    g = df.groupby("day", as_index=False)["adherence_pct"].mean()
    g["adherence_pct"] = g["adherence_pct"].round(0).astype(int)

    all_days = pd.date_range(start, end, freq="D")
    g = g.set_index("day").reindex(all_days).rename_axis("day").reset_index()
    g["adherence_pct"] = g["adherence_pct"].fillna(0).astype(int)
    return g


def chart_training_quality_seconds(repo, days: int = 14) -> pd.DataFrame:
    sessions = repo.list_sessions()
    if sessions is None or len(sessions) == 0 or "started_at" not in sessions.columns:
        return pd.DataFrame({"day": [], "quality_seconds": []})

    df = sessions.copy()
    df["day"] = _to_day(df["started_at"])
    df = df.dropna(subset=["day"])

    if "status" in df.columns:
        df = df[df["status"] == "completed"]

    duration_sec = pd.to_numeric(df.get("duration_sec", 0), errors="coerce").fillna(0)
    adh = pd.to_numeric(df.get("adherence", 0), errors="coerce").fillna(0).clip(lower=0, upper=1)

    df["quality_seconds"] = (duration_sec * adh).round(0).astype(int)

    end = df["day"].max()
    start = end - pd.Timedelta(days=days - 1)
    df = df[(df["day"] >= start) & (df["day"] <= end)]

    g = df.groupby("day", as_index=False)["quality_seconds"].mean()
    g["quality_seconds"] = g["quality_seconds"].round(0).astype(int)

    all_days = pd.date_range(start, end, freq="D")
    g = g.set_index("day").reindex(all_days).rename_axis("day").reset_index()
    g["quality_seconds"] = g["quality_seconds"].fillna(0).astype(int)
    return g


def chart_grip_improvement(repo, weeks: int = 6) -> pd.DataFrame:
    sessions = repo.list_sessions()
    if sessions is None or len(sessions) == 0 or "started_at" not in sessions.columns:
        return pd.DataFrame({"week": [], "grip_kg": []})

    df = sessions.copy()
    df["week"] = pd.to_datetime(df["started_at"], errors="coerce").dt.to_period("W").dt.start_time
    df = df.dropna(subset=["week"])

    if "grip_avg_kg" not in df.columns:
        return pd.DataFrame({"week": [], "grip_kg": []})

    grip = pd.to_numeric(df["grip_avg_kg"], errors="coerce")
    df = df.assign(grip_kg=grip)
    df = df.dropna(subset=["grip_kg"])
    if len(df) == 0:
        return pd.DataFrame({"week": [], "grip_kg": []})

    max_week = df["week"].max()
    min_week = max_week - pd.Timedelta(weeks=weeks - 1)
    df = df[df["week"] >= min_week]

    g = df.groupby("week", as_index=False)["grip_kg"].mean()
    g["grip_kg"] = g["grip_kg"].round(2)

    g = g.sort_values("week")
    g["week_label"] = g["week"].dt.strftime("%Y-%m-%d")
    return g[["week_label", "grip_kg"]]
