# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
"""Tiny shared UI helpers — load CSS and render the alert banner."""
from pathlib import Path
import streamlit as st

_ROOT = Path(__file__).parent


def inject_style():
    css = (_ROOT / "assets" / "style.css").read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def alert_banner():
    st.markdown(
        """
<div class="pager-alert">
  <span class="badge">CRITICAL</span>
  <span class="title">checkout · p99 latency 10× baseline</span>
  <div class="meta">triggered 2026-04-22 14:32:07 UTC · policy: page-oncall · ack: —</div>
</div>
""",
        unsafe_allow_html=True,
    )


PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0b0e14",
    plot_bgcolor="#11151c",
    font=dict(family="IBM Plex Mono, monospace", color="#c9d1d9", size=11),
    margin=dict(l=40, r=20, t=30, b=40),
    xaxis=dict(gridcolor="#1e2530", zeroline=False),
    yaxis=dict(gridcolor="#1e2530", zeroline=False),
    hoverlabel=dict(font_family="IBM Plex Mono"),
)
