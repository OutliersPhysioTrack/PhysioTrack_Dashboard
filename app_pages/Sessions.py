import streamlit as st
import pandas as pd
import requests

from views.cards import section_title
from views.tables import sessions_table


def _inject_session_review_css():
    st.markdown(
        """
        <style>
        .sr-spacer{ height: 14px; }
        .sr-card-pad{ padding: 10px 6px 6px 6px; }
        .sr-title-row{ display:flex; justify-content:space-between; align-items:flex-start; gap: 14px; }
        .sr-name{ font-size: 18px; font-weight: 800; color:#2B3674; line-height: 1.2; }
        .sr-meta{ color:#A3AED0; font-size:12px; margin-top:4px; line-height:1.35; }

        .sr-metrics{ margin-top: 14px; display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }

        .sr-metric .lbl{ color:#A3AED0; font-size:12px; line-height:1.2; }
        .sr-metric .val{ font-weight:800; color:#2B3674; font-size:18px; margin-top:6px; line-height:1.1; }
        .sr-video-pad{ padding: 6px 6px 10px 6px; }
        .sr-video-box{
          margin-top:14px; min-height: 340px; height: 340px;
          border-radius: 14px; background: rgba(163,174,208,0.12);
          border: 1px solid rgba(163,174,208,0.25);
          display:flex; flex-direction:column; align-items:center; justify-content:center;
          color:#A3AED0; text-align:center; padding: 22px; box-sizing: border-box;
        }
        .sr-video-box span{ display:block; margin-top:8px; font-size:12px; }

        /* Rep-by-rep ROM list */
        .rr-pad{ padding: 8px 6px 6px 6px; }
        .rr-list{ margin-top: 10px; }
        .rr-row{
          display:flex;
          align-items:center;
          justify-content:space-between;
          gap: 14px;
          padding: 12px 4px;
          border-top: 1px solid rgba(163,174,208,0.25);
        }
        .rr-left{ display:flex; align-items:center; gap: 10px; }
        .rr-rom{
          color:#2B3674;
          font-weight:800;
          font-size:14px;
        }

        .sr-video-wrap{
          margin-top: 12px;
          width: 100%;
          display:flex;
          justify-content:center;
        }
        video.sr-video-player{
          width: 520px;
          max-width: 100%;
          height: 300px;
          border-radius: 14px;
          background: rgba(163,174,208,0.12);
          border: 1px solid rgba(163,174,208,0.25);
        }
        .sr-hl-meta{ margin-top: 8px; color:#A3AED0; font-size:12px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _rep_by_rep_df(repo, session_id: str, session_summary: dict) -> tuple[pd.DataFrame, str]:
    subtitle = "Motion details by repetition."
    df = None
    try:
        df = repo.list_rep_metrics(session_id)
    except Exception:
        df = None
    if df is None or len(df) == 0:
        df = pd.DataFrame(columns=["rep_index", "rom_deg"])
        subtitle = "Rep-by-rep ROM is not available for this session."

    if "rep_index" not in df.columns:
        df["rep_index"] = list(range(1, len(df) + 1))
    if "rom_deg" not in df.columns:
        df["rom_deg"] = None

    return df, subtitle


def _render_rep_by_rep_rom(repo, session_id: str, session_summary: dict):
    df, subtitle = _rep_by_rep_df(repo, session_id, session_summary)

    with st.container(border=True):
        st.markdown("<div class='rr-pad'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='card-title'>Rep-by-Rep ROM</div>"
            f"<div class='card-sub'>{subtitle}</div>",
            unsafe_allow_html=True,
        )

        if df is None or len(df) == 0:
            st.caption("Nothing to display yet.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.markdown("<div class='rr-list'>", unsafe_allow_html=True)

        for _, r in df.iterrows():
            rep_i = r.get("rep_index")
            rom = r.get("rom_deg")

            try:
                rep_i_int = int(rep_i)
            except Exception:
                rep_i_int = None

            if rom is None or (isinstance(rom, float) and pd.isna(rom)):
                rom_txt = "—"
            else:
                try:
                    rom_txt = f"{float(rom):.0f}°"
                except Exception:
                    rom_txt = f"{rom}°"

            rep_txt = f"rep {rep_i_int}" if rep_i_int is not None else "rep"

            st.markdown(
                f"""
                <div class="rr-row">
                  <div class="rr-left">
                    <span class="pill pill-blue">{rep_txt}</span>
                    <div class="rr-rom">ROM: {rom_txt}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div></div>", unsafe_allow_html=True)


def _fmt_ms(ms) -> str:
    try:
        if ms is None:
            return "—"
        return f"{int(ms) / 1000.0:.1f}s"
    except Exception:
        return "—"


def _api_get_json(base_url: str, path: str, params: dict | None = None):
    url = base_url.rstrip("/") + path
    try:
        r = requests.get(url, params=params, timeout=12)
        if r.status_code >= 400:
            return False, None, r.status_code, r.text
        return True, r.json(), r.status_code, ""
    except Exception as e:
        return False, None, 0, str(e)


def _full_media_url(base_url: str, stream_path_or_path: str) -> str:
    if not stream_path_or_path:
        return ""
    p = str(stream_path_or_path).strip()
    if not p.startswith("/"):
        p = "/" + p
    return base_url.rstrip("/") + p


def _render_video_small(video_url: str):
    st.markdown(
        f"""
        <div class="sr-video-wrap">
          <video class="sr-video-player" controls preload="metadata">
            <source src="{video_url}" type="video/mp4">
            Your browser does not support the video tag.
          </video>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_session_highlights(repo, session_id: str, patient_id: str):
    base_url = (getattr(repo, "base_url", "") or "").rstrip("/")
    st.markdown("<div class='sr-video-pad'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Session Highlights</div>", unsafe_allow_html=True)

    ok, data, status, err = _api_get_json(base_url, "/highlights", params={"session_id": session_id})
    highlights = data or [] if ok else []

    sub = "Auto clips recorded from the mobile app." if highlights else "No highlights available for this session."
    st.markdown(f"<div class='card-sub'>{sub}</div>", unsafe_allow_html=True)

    if not highlights:
        st.markdown(
            """<div class="sr-video-box">
                No highlights
                <span>If highlights are available, they will appear here.</span>
            </div>""",
            unsafe_allow_html=True,
        )

        with st.expander("Debug highlights", expanded=False):
            st.write("base_url:", base_url)
            st.write("session_id:", session_id)
            st.write("GET /highlights status:", status)
            if err:
                st.code(err[:1200])
            else:
                st.write("Response:", data)

        st.markdown("</div>", unsafe_allow_html=True)
        return

    try:
        highlights = sorted(highlights, key=lambda x: (x.get("created_at") or ""), reverse=True)
    except Exception:
        pass

    for i, h in enumerate(highlights):
        hid = h.get("highlight_id")
        st.markdown(f"**Highlight {i+1}** • {_fmt_ms(h.get('start_ms'))}–{_fmt_ms(h.get('end_ms'))} • `{hid}`")

        stream_path = h.get("stream_path") or (f"/highlights/{hid}/stream" if hid else "")
        video_url = _full_media_url(base_url, stream_path)

        if video_url:
            _render_video_small(video_url)
        else:
            st.warning("Highlight has no stream path / id.")

        st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)


def _session_review(repo, session_id: str):
    _inject_session_review_css()

    s = repo.get_session(session_id)
    if not s:
        st.warning("Session not found.")
        return

    patient = repo.get_patient(s["patient_id"]) or {}

    section_title("Session Review", "Review session metrics and add therapist notes", right_html="")
    st.markdown("<div class='sr-spacer'></div>", unsafe_allow_html=True)

    started = s.get("started_at")
    started_txt = (
        pd.to_datetime(started).strftime("%Y-%m-%d %H:%M")
        if started is not None and not pd.isna(started)
        else "—"
    )

    with st.container(border=True):
        st.markdown("<div class='sr-card-pad'>", unsafe_allow_html=True)

        pain_val = s.get("pain_score")
        pain_txt = "—" if pain_val is None or (isinstance(pain_val, float) and pd.isna(pain_val)) else str(pain_val)

        st.markdown(
            f"""
            <div class="sr-title-row">
              <div>
                <div class="sr-name">{patient.get('name','—')}</div>
                <div class="sr-meta">{started_txt} • {s.get('exercise_name','—')}</div>
              </div>
              <div><span class="pill pill-blue">{s.get('status','—')}</span></div>
            </div>

            <div class="sr-metrics">
              <div class="sr-metric">
                <div class="lbl">Duration</div>
                <div class="val">{s.get('duration_min',0)} min</div>
              </div>
              <div class="sr-metric">
                <div class="lbl">Rep Count</div>
                <div class="val">{s.get('rep_count',0)}</div>
              </div>
              <div class="sr-metric">
                <div class="lbl">Pain Score</div>
                <div class="val">{pain_txt}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sr-spacer'></div>", unsafe_allow_html=True)

    cL, cR = st.columns([1.6, 1], gap="large")

    with cL:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            _render_session_highlights(
                repo=repo,
                session_id=session_id,
                patient_id=str(s.get("patient_id")),
            )

        _render_rep_by_rep_rom(repo, session_id=session_id, session_summary=s)

    with cR:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='sr-card-pad'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>Therapist Note</div>", unsafe_allow_html=True)

            sent_key = f"note_sent_{session_id}"
            if st.session_state.get(sent_key):
                st.success("Note sent!")
                st.session_state[sent_key] = False

            nonce_key = f"note_nonce_{session_id}"
            nonce = int(st.session_state.get(nonce_key) or 0)

            title_key = f"note_title_{session_id}_{nonce}"
            body_key = f"note_body_{session_id}_{nonce}"

            st.text_input(
                "Title (optional)",
                placeholder="e.g., Form correction",
                key=title_key,
            )
            st.text_area(
                " ",
                placeholder="Write a note...",
                label_visibility="collapsed",
                key=body_key,
            )

            if st.button("Save Note", type="primary", use_container_width=True, key=f"save_note_{session_id}"):
                current_title = (st.session_state.get(title_key) or "").strip()
                current_body = (st.session_state.get(body_key) or "").strip()

                if not current_body:
                    st.warning("The note cannot be empty.")
                else:
                    repo.create_note(
                        patient_id=s["patient_id"],
                        session_id=session_id,
                        title=current_title or None,
                        body=current_body,
                    )

                    st.session_state[sent_key] = True
                    st.session_state[nonce_key] = nonce + 1
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


def render(repo):
    section_title("Sessions", "Review sessions and patient performance", right_html="")

    default_pid = st.session_state.get("selected_patient_id")

    patients = repo.list_patients()
    if patients is None or len(patients) == 0:
        st.info("No patients found. Showing all sessions.")
        pid = None
    else:
        name_col = "name" if "name" in patients.columns else ("patient_name" if "patient_name" in patients.columns else None)
        id_to_name = {}
        if name_col and "patient_id" in patients.columns:
            try:
                id_to_name = dict(
                    zip(
                        patients["patient_id"].astype(str).tolist(),
                        patients[name_col].astype(str).fillna("—").tolist(),
                    )
                )
            except Exception:
                id_to_name = {}

        def _patient_label(x: str) -> str:
            if not x:
                return "All patients"
            return id_to_name.get(str(x), str(x))

        opts = [""] + patients["patient_id"].astype(str).tolist()
        idx = opts.index(default_pid) if default_pid in opts else 0
        pid = st.selectbox("Filter by patient", options=opts, index=idx, format_func=_patient_label)
        pid = pid or None
        st.session_state.selected_patient_id = pid

    df = repo.list_sessions(patient_id=pid)
    sid = sessions_table(df)

    if sid:
        st.session_state.selected_session_id = sid
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        _session_review(repo, sid)
