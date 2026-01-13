# views/charts.py
import streamlit as st
import plotly.express as px


def _apply_white_card_layout(fig, y_range=None, height=280):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",

        showlegend=False,
    )

    fig.update_xaxes(
        title=None,
        showgrid=False,
        zeroline=False,
        ticks="outside",
    )

    fig.update_yaxes(
        title=None,
        range=y_range,
        showgrid=True,
        gridcolor="rgba(163,174,208,0.35)",
        zeroline=False,
        ticks="outside",
    )
    return fig


def line_chart(df, x, y, y_range=None, height=280):
    fig = px.line(df, x=x, y=y, markers=True)
    fig.update_traces(mode="lines+markers")
    _apply_white_card_layout(fig, y_range=y_range, height=height)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )


def bar_chart(df, x, y, y_range=None, height=280):
    fig = px.bar(df, x=x, y=y)
    _apply_white_card_layout(fig, y_range=y_range, height=height)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True},
    )
