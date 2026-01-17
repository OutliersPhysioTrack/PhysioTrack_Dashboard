import streamlit as st
import pandas as pd

from views.cards import section_title, simple_card


def _progression_rule_item(title: str, rule_text: str, toggle_key: str, default_enabled: bool = True):
    with st.container(border=True):
        cL, cR = st.columns([0.86, 0.14], gap="small")
        with cL:
            st.markdown(f"<div class='card-title'>{title}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='card-sub' style='margin-top:2px;'>{rule_text}</div>",
                unsafe_allow_html=True,
            )
        with cR:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            st.toggle("Enabled", value=default_enabled, key=toggle_key)

def _progression_rules_card():
    with st.container(border=True):
        st.markdown("<div class='card-title'>Progression Rules</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='card-sub'>Automatic program adjustments based on performance</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        _progression_rule_item(
            title="Increase Intensity Rule",
            rule_text="IF completion ≥ 80% AND pain ≤ 3 THEN increase intensity by 10%",
            toggle_key="prog_rule_increase_intensity_enabled",
            default_enabled=True,
        )

        _progression_rule_item(
            title="Safety Pause Rule",
            rule_text="IF SpO2 < 90% THEN pause program and alert therapist",
            toggle_key="prog_rule_safety_pause_enabled",
            default_enabled=True,
        )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if st.button("Save Program", type="primary", key="save_program_btn", use_container_width=False):
            st.info("Program Saved!")


def render(repo):
    section_title("Programs", "Create and manage rehabilitation programs", right_html="")

    patients = repo.list_patients()
    if patients is None or len(patients) == 0:
        st.info("No patients available.")
        return

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

    def _patient_label(pid: str) -> str:
        return id_to_name.get(str(pid), str(pid))

    default_pid = st.session_state.get("selected_patient_id")
    opts = patients["patient_id"].astype(str).tolist()
    idx = opts.index(default_pid) if default_pid in opts else 0
    pid = st.selectbox("Patient", options=opts, index=idx, format_func=_patient_label)
    st.session_state.selected_patient_id = pid

    p = repo.get_patient(pid) or {}
    with st.container(border=True):
        simple_card(
            "Patient",
            "",
            f"<b>{p.get('name','—')}</b><div style='color:#A3AED0;font-size:12px;'>Condition: {p.get('primary_condition') or '—'}</div>",
        )

    exercises = repo.list_exercises()
    if exercises is None or len(exercises) == 0:
        st.warning("Exercise library is empty. Create exercises in backend first.")
        return

    with st.container(border=True):
        st.markdown(
            "<div class='card-title'>Create Assignment</div><div class='card-sub'>Creates rows in assignments table</div>",
            unsafe_allow_html=True,
        )

        ex_opts = exercises["exercise_id"].astype(str).tolist()
        ex_id = st.selectbox(
            "Exercise",
            options=ex_opts,
            format_func=lambda x: exercises.loc[exercises["exercise_id"].astype(str) == x, "exercise_name"].values[0],
        )

        ex_row = exercises[exercises["exercise_id"].astype(str) == ex_id].iloc[0].to_dict()
        c1, c2 = st.columns(2, gap="large")
        with c1:
            sets = st.number_input("Sets", min_value=1, max_value=20, value=int(ex_row.get("default_sets") or 3))
        with c2:
            reps = st.number_input("Reps", min_value=1, max_value=100, value=int(ex_row.get("default_reps") or 10))

        notes = st.text_area("Notes (optional)", placeholder="Any therapist instruction...")

        if st.button("Create Assignment", type="primary"):
            repo.create_assignment(patient_id=pid, exercise_id=ex_id, sets=int(sets), reps=int(reps), notes=notes.strip())
            st.success("Assignment created.")
            st.rerun()

    ass = repo.list_assignments(patient_id=pid)
    with st.container(border=True):
        st.markdown("<div class='card-title'>Current Assignments</div><div class='card-sub'>Latest first</div>", unsafe_allow_html=True)
        if ass is None or len(ass) == 0:
            st.caption("No assignments for this patient yet.")
        else:
            show_cols = ["assignment_id", "exercise_name", "sets", "reps", "status", "notes"]
            st.dataframe(ass[[c for c in show_cols if c in ass.columns]], use_container_width=True, hide_index=True)

    _progression_rules_card()

    with st.container(border=True):
        st.markdown("<div class='card-title'>Exercise Library</div><div class='card-sub'>", unsafe_allow_html=True)
        show_cols = ["exercise_id", "exercise_name", "default_sets", "default_reps", "notes"]
        st.dataframe(exercises[[c for c in show_cols if c in exercises.columns]], use_container_width=True, hide_index=True)
