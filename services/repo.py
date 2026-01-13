from __future__ import annotations

from typing import Any, Optional

import os

import pandas as pd
import requests
import streamlit as st

DEFAULT_BASE_URL = os.getenv("PHYSIOTRACK_API_BASE_URL", "http://127.0.0.1:8000").strip().rstrip("/")


class ApiRepo:
    def __init__(self, base_url: str):
        self.base_url = (base_url or "").strip().rstrip("/")
        if not self.base_url:
            raise ValueError("base_url is empty")

    # ---------- low-level ----------
    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _get(self, path: str, params: Optional[dict] = None) -> Any:
        r = requests.get(self._url(path), params=params, timeout=12)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, json_body: dict) -> Any:
        r = requests.post(self._url(path), json=json_body, timeout=15)
        r.raise_for_status()
        return r.json()

    def _patch(self, path: str, json_body: dict) -> Any:
        r = requests.patch(self._url(path), json=json_body, timeout=15)
        r.raise_for_status()
        return r.json()

    # ---------- basics ----------
    def health(self) -> bool:
        try:
            return bool(self._get("/health").get("ok"))
        except Exception:
            return False

    # ---------- patients ----------
    def list_patients(self) -> pd.DataFrame:
        patients = self._get("/patients") or []
        devices = self._get("/devices") or []
        alerts = self._get("/alerts/all") or []

        dev_by_pid: dict[str, dict] = {}
        for d in devices:
            pid = d.get("patient_id")
            if pid:
                dev_by_pid[str(pid)] = d
        sev_rank = {"low": 1, "info": 1, "med": 2, "medium": 2, "warning": 3, "high": 3, "critical": 4}
        worst: dict[str, int] = {}
        open_cnt: dict[str, int] = {}
        for a in alerts:
            pid = a.get("patient_id")
            if not pid:
                continue
            pid = str(pid)
            if (a.get("status") or "open").lower() == "open":
                open_cnt[pid] = open_cnt.get(pid, 0) + 1
                s = (a.get("severity") or "med").lower()
                worst[pid] = max(worst.get(pid, 0), sev_rank.get(s, 2))

        rows = []
        for p in patients:
            pid = str(p.get("patient_id"))
            d = dev_by_pid.get(pid, {})

            risk_num = worst.get(pid, 0)
            if risk_num >= 4:
                risk = "Critical"
            elif risk_num == 3:
                risk = "High"
            elif risk_num == 2:
                risk = "Medium"
            else:
                risk = "Low"

            rows.append(
                {
                    "patient_id": pid,
                    "name": p.get("name") or "—",
                    "age": p.get("age"),
                    "primary_condition": p.get("primary_condition") or "—",
                    "assigned_therapist_id": str(p.get("assigned_therapist_id")) if p.get("assigned_therapist_id") else None,
                    "phone": p.get("phone"),
                    "email": p.get("email"),
                    "risk_level": risk,
                    "active_alerts_count": int(open_cnt.get(pid, 0)),
                    "device_id": d.get("device_id"),
                    "device_status": d.get("status") or "unknown",
                    "last_seen_at": pd.to_datetime(d.get("last_seen_at")) if d.get("last_seen_at") else pd.NaT,
                }
            )

        return pd.DataFrame(rows)

    def get_patient(self, patient_id: str) -> dict | None:
        try:
            return self._get(f"/patients/{patient_id}")
        except Exception:
            return None

    # ---------- sessions ----------
    def list_sessions(self, patient_id: Optional[str] = None) -> pd.DataFrame:
        params = {"patient_id": patient_id} if patient_id else None
        items = self._get("/sessions", params=params) or []

        ex_map = {str(x["exercise_id"]): x.get("exercise_name") for x in (self._get("/exercises") or []) if x.get("exercise_id")}

        rows = []
        for s in items:
            started = pd.to_datetime(s.get("started_at")) if s.get("started_at") else pd.NaT
            ended = pd.to_datetime(s.get("ended_at")) if s.get("ended_at") else pd.NaT
            duration_sec = int(s.get("duration_sec") or 0)

            adh = s.get("adherence")
            try:
                adh_f = float(adh) if adh is not None else None
            except Exception:
                adh_f = None
            if adh_f is None:
                adh_norm = None
            else:
                adh_norm = adh_f / 100.0 if adh_f > 1.5 else adh_f

            rows.append(
                {
                    "session_id": str(s.get("session_id")),
                    "patient_id": str(s.get("patient_id")),
                    "exercise_id": str(s.get("exercise_id")) if s.get("exercise_id") else None,
                    "exercise_name": ex_map.get(str(s.get("exercise_id")), "—") if s.get("exercise_id") else "—",
                    "started_at": started,
                    "ended_at": ended,
                    "status": "completed" if pd.notna(ended) else "in_progress",
                    "duration_sec": duration_sec,
                    "duration_min": int(round(duration_sec / 60.0)) if duration_sec else 0,
                    "rep_count": int(s.get("rep_count") or 0),
                    "adherence": adh_norm,  # 0..1
                    "adherence_pct": int(round((adh_norm or 0) * 100)) if adh_norm is not None else 0,
                    "rom_avg_deg": s.get("rom_avg_deg"),
                    "grip_avg_kg": s.get("grip_avg_kg"),
                    "pain_score": s.get("pain_score"),
                }
            )

        return pd.DataFrame(rows)

    def get_session(self, session_id: str) -> dict | None:
        try:
            s = self._get(f"/sessions/{session_id}")
        except Exception:
            return None

        ex_name = "—"
        if s.get("exercise_id"):
            try:
                ex = self._get(f"/exercises/{s['exercise_id']}")
                ex_name = ex.get("exercise_name") or "—"
            except Exception:
                pass

        started = pd.to_datetime(s.get("started_at")) if s.get("started_at") else pd.NaT
        ended = pd.to_datetime(s.get("ended_at")) if s.get("ended_at") else pd.NaT
        duration_sec = int(s.get("duration_sec") or 0)

        adh = s.get("adherence")
        try:
            adh_f = float(adh) if adh is not None else None
        except Exception:
            adh_f = None
        if adh_f is None:
            adh_norm = None
        else:
            adh_norm = adh_f / 100.0 if adh_f > 1.5 else adh_f

        return {
            "session_id": str(s.get("session_id")),
            "patient_id": str(s.get("patient_id")),
            "exercise_id": str(s.get("exercise_id")) if s.get("exercise_id") else None,
            "exercise_name": ex_name,
            "started_at": started,
            "ended_at": ended,
            "status": "completed" if pd.notna(ended) else "in_progress",
            "duration_sec": duration_sec,
            "duration_min": int(round(duration_sec / 60.0)) if duration_sec else 0,
            "rep_count": int(s.get("rep_count") or 0),
            "adherence": adh_norm,
            "adherence_pct": int(round((adh_norm or 0) * 100)) if adh_norm is not None else 0,
            "rom_avg_deg": s.get("rom_avg_deg"),
            "grip_avg_kg": s.get("grip_avg_kg"),
            "pain_score": s.get("pain_score"),
        }

    def list_rep_metrics(self, session_id: str) -> pd.DataFrame:
        return pd.DataFrame(columns=["rep_index", "rom_deg"])

    # ---------- devices ----------
    def list_devices(self) -> pd.DataFrame:
        devices = self._get("/devices") or []
        patients = self._get("/patients") or []
        name_by_id = {str(p["patient_id"]): p.get("name") for p in patients if p.get("patient_id")}
        dev_ids = [str(d.get("device_id") or "") for d in devices]
        dev_ids_sorted = sorted([x for x in dev_ids if x])
        demo_by_device: dict[str, str] = {did: f"" for i, did in enumerate(dev_ids_sorted)}

        rows = []
        for d in devices:
            pid = d.get("patient_id")
            pid_s = str(pid) if pid else None
            nm = name_by_id.get(pid_s) if pid_s else None
            nm = (nm or "").strip() if isinstance(nm, str) else nm

            if nm:
                patient_name = nm
            elif pid_s:
                patient_name = f"Patient {pid_s[-6:]}" 
            else:
                patient_name = demo_by_device.get(str(d.get("device_id")), "Demo Patient")

            rows.append(
                {
                    "device_id": d.get("device_id"),
                    "patient_id": pid_s,
                    "patient_name": patient_name,
                    "label": d.get("label") or "—",
                    "status": d.get("status") or "unknown",
                    "last_seen_at": pd.to_datetime(d.get("last_seen_at")) if d.get("last_seen_at") else pd.NaT,
                }
            )
        return pd.DataFrame(rows)

    def get_device(self, device_id: str) -> dict | None:
        try:
            return self._get(f"/devices/{device_id}/status")
        except Exception:
            return None

    def get_latest_sensor_reading(self, device_id: str) -> dict:
        try:
            items = self._get(f"/devices/{device_id}/sensor-readings/latest") or []
        except Exception:
            return {}
        out: dict[str, Any] = {}
        for r in items:
            m = r.get("metric")
            if m:
                out[m] = r.get("value")
        return out

    def get_latest_ai(self, device_id: str) -> dict:
        try:
            return self._get(f"/devices/{device_id}/ai/latest") or {}
        except Exception:
            return {}

    def media_url(self, stream_path: str) -> str:
        if not stream_path:
            return ""
        p = str(stream_path).strip()
        if not p.startswith("/"):
            p = "/" + p
        return self._url(p)

    def list_highlights(self, session_id: str) -> list[dict]:
        try:
            return self._get("/highlights", params={"session_id": session_id}) or []
        except Exception:
            return []

    # ---------- alerts ----------
    def list_alerts(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        patient_id: Optional[str] = None,
    ) -> pd.DataFrame:
        params: dict[str, str] = {}
        if severity and severity != "All":
            params["severity"] = severity
        if status and status != "All":
            params["status"] = status
        if patient_id:
            params["patient_id"] = patient_id

        items = self._get("/alerts/all", params=params or None) or []


        pats = self._get("/patients") or []
        name_by_id = {str(p["patient_id"]): p.get("name") for p in pats if p.get("patient_id")}

        rows = []
        for a in items:
            pid = a.get("patient_id")
            pid_s = str(pid) if pid else None
            rows.append(
                {
                    "alert_id": str(a.get("alert_id")),
                    "patient_id": pid_s,
                    "patient_name": name_by_id.get(pid_s, "—") if pid_s else "—",
                    "type": a.get("type") or "—",
                    "severity": (a.get("severity") or "med"),
                    "status": (a.get("status") or "open"),
                    "message": a.get("message") or "",
                    "created_at": pd.to_datetime(a.get("created_at")) if a.get("created_at") else pd.NaT,
                    "resolved_at": pd.to_datetime(a.get("resolved_at")) if a.get("resolved_at") else pd.NaT,
                }
            )
        return pd.DataFrame(rows)

    def update_alert(self, alert_id: str, status: str, message: str = ""):
        payload = {"status": status}
        if message:
            payload["message"] = message
        self._patch(f"/alerts/{alert_id}", payload)

    # ---------- exercises ----------
    def list_exercises(self) -> pd.DataFrame:
        items = self._get("/exercises") or []
        rows = []
        for e in items:
            rows.append(
                {
                    "exercise_id": str(e.get("exercise_id")),
                    "exercise_name": e.get("exercise_name") or "—",
                    "default_sets": e.get("default_sets"),
                    "default_reps": e.get("default_reps"),
                    "notes": e.get("notes") or "",
                }
            )
        return pd.DataFrame(rows)

    # ---------- assignments ----------
    def list_assignments(self, patient_id: Optional[str] = None) -> pd.DataFrame:
        params = {"patient_id": patient_id} if patient_id else None
        items = self._get("/assignments", params=params) or []
        ex_map = {str(x["exercise_id"]): x.get("exercise_name") for x in (self._get("/exercises") or []) if x.get("exercise_id")}

        rows = []
        for a in items:
            eid = a.get("exercise_id")
            rows.append(
                {
                    "assignment_id": str(a.get("assignment_id")),
                    "patient_id": str(a.get("patient_id")),
                    "exercise_id": str(eid) if eid else None,
                    "exercise_name": ex_map.get(str(eid), "—") if eid else "—",
                    "sets": a.get("sets"),
                    "reps": a.get("reps"),
                    "status": a.get("status") or "assigned",
                    "notes": a.get("notes") or "",
                    "created_at": pd.to_datetime(a.get("created_at")) if a.get("created_at") else pd.NaT,
                }
            )
        return pd.DataFrame(rows)

    def create_assignment(
        self,
        patient_id: str,
        exercise_id: str,
        sets: Optional[int] = None,
        reps: Optional[int] = None,
        notes: str = "",
        status: str = "assigned",
    ) -> str:
        payload: dict[str, Any] = {
            "patient_id": patient_id,
            "exercise_id": exercise_id,
            "status": status,
        }
        if sets is not None:
            payload["sets"] = int(sets)
        if reps is not None:
            payload["reps"] = int(reps)
        if notes:
            payload["notes"] = notes
        out = self._post("/assignments", payload)
        return str(out.get("assignment_id"))

    # ---------- notes ----------
    def create_note(self, patient_id: str, body: str, session_id: Optional[str] = None, title: Optional[str] = None) -> str:
        payload: dict[str, Any] = {"patient_id": patient_id, "body": body}
        if session_id:
            payload["session_id"] = session_id
        if title:
            payload["title"] = title
        out = self._post("/notes", payload)
        return str(out.get("note_id"))

    def list_notes(self, patient_id: str, only_new: bool = False) -> pd.DataFrame:
        params = {"patient_id": patient_id, "only_new": str(bool(only_new)).lower()}
        items = self._get("/notes", params=params) or []
        rows = []
        for n in items:
            rows.append(
                {
                    "note_id": str(n.get("note_id")),
                    "patient_id": str(n.get("patient_id")),
                    "session_id": str(n.get("session_id")) if n.get("session_id") else None,
                    "title": n.get("title") or "",
                    "body": n.get("body") or "",
                    "is_new": bool(n.get("is_new")),
                    "created_at": pd.to_datetime(n.get("created_at")) if n.get("created_at") else pd.NaT,
                    "seen_at": pd.to_datetime(n.get("seen_at")) if n.get("seen_at") else pd.NaT,
                }
            )
        return pd.DataFrame(rows)


def get_repo() -> ApiRepo:
    base = (st.session_state.get("api_base_url") or DEFAULT_BASE_URL or "").strip().rstrip("/")
    if base:
        st.session_state["api_base_url"] = base
    if not base:
        st.error("API Base URL kosong. Set env PHYSIOTRACK_API_BASE_URL atau ubah di Settings → API Connection.")
        st.stop()

    cur = st.session_state.get("repo")
    if not isinstance(cur, ApiRepo) or getattr(cur, "base_url", "") != base:
        st.session_state.repo = ApiRepo(base)

    repo: ApiRepo = st.session_state.repo

    if not repo.health():
        st.error(f"Tidak bisa terhubung ke backend di: {base}. Pastikan FastAPI berjalan dan CORS sudah benar.")
        st.stop()

    return repo
