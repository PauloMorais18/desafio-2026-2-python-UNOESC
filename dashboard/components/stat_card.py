"""Statistic-card component for the dashboard prototype."""

import streamlit as st


def render_stat_card(title: str, value: str, detail: str) -> None:
    """Render one compact dashboard statistic card."""
    st.markdown(
        f"""
        <div class="stat-card">
          <p>{title}</p>
          <h2>{value}</h2>
          <span>{detail}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
