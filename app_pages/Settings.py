import streamlit as st
import pandas as pd

from services.auth import logout


def _df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def _safe_list_users(repo) -> pd.DataFrame:
    try:
        fn = getattr(repo, "list_users", None)
        if callable(fn):
            df = fn()
            if df is None:
                return pd.DataFrame()
            if isinstance(df, pd.DataFrame):
                return df
            return pd.DataFrame(df)
    except Exception:
        pass
    return pd.DataFrame()


def render(repo):
    st.title("Settings")
    st.caption("Manage users and system preferences")

    tab_users, tab_export = st.tabs(["Users & Permissions", "Data & Export"])

    # --------------------------------
    # Users & Permissions (from backend)
    # --------------------------------
    with tab_users:
        st.subheader("Users & Permissions")
        st.caption("Manage staff accounts and roles")

        users_df = _safe_list_users(repo)

        if users_df is None or len(users_df) == 0:
            st.info("No users data available.")
        else:
            preferred = ["name", "email", "role"]
            show_cols = [c for c in preferred if c in users_df.columns]
            if not show_cols:
                show_cols = list(users_df.columns)
            st.dataframe(users_df[show_cols], use_container_width=True, hide_index=True)

        st.markdown("---")

        st.subheader("Invite User")

        c1, c2 = st.columns([1.2, 0.8], gap="large")
        with c1:
            invite_email = st.text_input("Email Address", value="", placeholder="user@clinic.com", key="invite_user_email")
        with c2:
            invite_role = st.selectbox("Role", options=["Therapist", "Admin"], index=0, key="invite_user_role")

        if st.button("Send Invite", type="primary", key="invite_user_btn"):
            fn = getattr(repo, "invite_user", None)
            if callable(fn):
                try:
                    fn(email=invite_email.strip(), role=invite_role)
                    st.success("Invite sent.")
                except Exception as e:
                    st.error(f"Failed to send invite: {e}")
            else:
                st.info("Invite flow is not wired to backend yet.")

    # ---------------------------
    # Data & Export
    # ---------------------------
    with tab_export:
        st.subheader("Export (CSV)")
      
        patients_df = repo.list_patients()
        sessions_df = repo.list_sessions()
        devices_df = repo.list_devices()
        alerts_df = repo.list_alerts()

        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.download_button(
                "⬇️  Export Patients",
                data=_df_to_csv_bytes(patients_df if patients_df is not None else pd.DataFrame()),
                file_name="patients.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "⬇️  Export Devices",
                data=_df_to_csv_bytes(devices_df if devices_df is not None else pd.DataFrame()),
                file_name="devices.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "⬇️  Export Sessions",
                data=_df_to_csv_bytes(sessions_df if sessions_df is not None else pd.DataFrame()),
                file_name="sessions.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "⬇️  Export Alerts",
                data=_df_to_csv_bytes(alerts_df if alerts_df is not None else pd.DataFrame()),
                file_name="alerts.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # ---------------------------
    # Account 
    # ---------------------------
    st.markdown("---")
    st.subheader("Account")
    st.caption("End your session securely.")

    st.markdown(
        """
        <style>
        div[id*="settings_logout_btn"] button{
          background: rgba(238, 93, 80, 0.14) !important;
          color: #EE5D50 !important;
          border: 0 !important;
          border-radius: 12px !important;
          font-weight: 700 !important;
        }
        div[id*="settings_logout_btn"] button:hover{
          background: rgba(238, 93, 80, 0.20) !important;
          color: #EE5D50 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("⎋  Logout", key="settings_logout_btn", use_container_width=True, type="secondary"):
        logout()
        st.rerun()
