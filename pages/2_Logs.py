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

main.title("LOGS")
with main:
    alert_banner()

LOG = Path(__file__).parent.parent / "data" / "app.log"

c1, c2, c3 = main.columns([2, 2, 1])
service = c1.selectbox("service", ["all", "checkout", "cart", "auth", "inventory"])
level = c2.selectbox("level", ["all", "ERROR", "WARN", "INFO", "DEBUG"])
limit = c3.number_input("rows", 50, 2000, 300, step=50)

main.caption(f"`{LOG.name}` — {LOG.stat().st_size/1e6:.1f} MB on disk · stream-filtered")


def stream():
    n = 0
    with open(LOG) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if service != "all" and rec.get("service") != service:
                continue
            if level != "all" and rec.get("level") != level:
                continue
            yield rec
            n += 1
            if n >= limit:
                return


rows = list(stream())
fmt = "{ts}  {level:<5}  {service:<10}  {msg}"
main.code(
    "\n".join(
        fmt.format(
            ts=r.get("ts", "")[11:23],
            level=r.get("level", ""),
            service=r.get("service", ""),
            msg=str(r.get("msg", ""))[:120],
        )
        for r in rows
    )
    or "— no matching lines —",
    language=None,
)
