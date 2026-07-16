# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
import json
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from ui import alert_banner, PLOTLY_LAYOUT
from provided import chat_panel

main, side = st.columns([5, 3], gap="large")
with side:
    chat_panel()

with main:
    st.title("METRICS")
    alert_banner()

DATA = Path(__file__).parent.parent / "data"
metrics = json.loads((DATA / "metrics.json").read_text())
DEPLOY_TS = datetime.fromisoformat("2026-04-22T14:31:18+00:00")


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))
COLORS = {"checkout": "#ff5c5c", "cart": "#7fd962", "auth": "#39bae6", "inventory": "#ffb454"}


def chart(metric_name: str, title: str, yfmt: str | None = None):
    fig = go.Figure()
    for svc, color in COLORS.items():
        series = metrics.get(svc, {}).get(metric_name)
        if not series:
            continue
        fig.add_scatter(
            x=[ts(d["ts"]) for d in series],
            y=[d["value"] for d in series],
            name=svc,
            mode="lines",
            line=dict(color=color, width=2),
        )
    fig.add_shape(
        type="line", x0=DEPLOY_TS, x1=DEPLOY_TS, y0=0, y1=1, yref="paper",
        line=dict(dash="dot", color="#6b7280", width=1),
    )
    fig.add_annotation(
        x=DEPLOY_TS, y=1.08, yref="paper", text="deploy a3f9c21",
        showarrow=False, font=dict(color="#6b7280", size=10),
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=280, showlegend=True)
    if yfmt:
        fig.update_yaxes(tickformat=yfmt)
    st.plotly_chart(fig, use_container_width=True)


with main:
    chart("p99_latency_ms", "P99 LATENCY (ms)")
    chart("error_rate", "ERROR RATE", ".1%")
    chart("db_pool_utilization", "DB POOL UTILIZATION", ".0%")
