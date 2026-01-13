import streamlit as st


def pill(text: str, variant: str = "blue"):
    cls = {
        "green": "pill pill-green",
        "yellow": "pill pill-yellow",
        "red": "pill pill-red",
        "blue": "pill pill-blue",
    }.get(variant, "pill pill-blue")
    st.markdown(f'<span class="{cls}">{text}</span>', unsafe_allow_html=True)


def kpi_card(title: str, value: str, delta: str = "", delta_variant: str = "green", icon: str = ""):
    cls = {
        "green": "kpi-green",
        "red": "kpi-red",
        "muted": "kpi-muted",
        "yellow": "kpi-muted",
        "orange": "kpi-muted",
        "blue": "kpi-muted",
    }.get(delta_variant, "kpi-muted")

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="kpi-card">
              <div class="kpi-head">
                <div class="kpi-title">{title}</div>
                <div class="kpi-icon">{icon or ""}</div>
              </div>

              <div class="kpi-value">{value}</div>

              <div class="kpi-delta {cls}">{delta or ""}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def section_title(title: str, sub: str = "", right_html: str = ""):
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin:2px 0 10px;">
          <div>
            <div style="font-size:26px;font-weight:800;color:#2B3674;">{title}</div>
            <div style="color:#A3AED0;margin-top:2px;">{sub}</div>
          </div>
          <div>{right_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def simple_card(title: str, subtitle: str, body_html: str):
    with st.container(border=True):
        st.markdown(f"<div style='font-size:16px;font-weight:900;color:#2B3674;'>{title}</div>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<div style='color:#A3AED0;font-size:13px;margin-top:2px;'>{subtitle}</div>", unsafe_allow_html=True)
        if body_html:
            st.markdown(body_html, unsafe_allow_html=True)
