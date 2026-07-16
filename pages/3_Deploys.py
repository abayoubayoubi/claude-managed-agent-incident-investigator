# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path

import streamlit as st

from ui import alert_banner
from provided import chat_panel

main, side = st.columns([5, 3], gap="large")
with side:
    chat_panel()

main.title("DEPLOYS")
with main:
    alert_banner()

DATA = Path(__file__).parent.parent / "data"
deploys = json.loads((DATA / "deploys.json").read_text())
diff_text = (DATA / "diff.txt").read_text()

main.caption("last 6h · all services")

for d in sorted(deploys, key=lambda x: x["ts"], reverse=True):
    suspect = d["service"] == "checkout" and d["ts"].startswith("2026-04-22T14:31")
    cls = "deploy-row suspect" if suspect else "deploy-row"
    main.markdown(
        f"<div class='{cls}'>"
        f"<span class='ts'>{d['ts']}</span> · "
        f"<b>{d['service']}</b> · "
        f"<span class='sha'>{d['commit']}</span> · "
        f"{d['author']}"
        f"</div>",
        unsafe_allow_html=True,
    )

main.divider()
sel = main.selectbox("inspect commit", [d["commit"] for d in deploys])
if sel and sel.startswith("a3f9c21"):
    main.code(diff_text, language="diff")
else:
    main.caption("diff not available for this commit")
