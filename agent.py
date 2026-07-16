# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
"""
The SRE Agent. Seven functions, each a single Managed Agents API call.
Fill them in during the workshop. Everything else is in provided.py.
"""
import json
import uuid

import anthropic
import streamlit as st

from provided import DATA, SYSTEM, TOOLS, metrics, deploys, diff

client = anthropic.Anthropic()


# ── 1. Agent ──────────────────────────────────────────────────────────────
# What the agent IS: model, system prompt, tools. Create once, reuse forever.
# Hint: client.beta.agents.create(name=..., model=..., system=SYSTEM, tools=TOOLS)
@st.cache_resource
def setup_agent() -> str:
    agent = client.beta.agents.create(
        name="SRE Agent", model="claude-opus-4-7", system=SYSTEM, tools=TOOLS,
    )
    return agent.id


# ── 2. Environment ────────────────────────────────────────────────────────
# Where the agent's container runs. Create once, reuse forever.
# Hint: client.beta.environments.create(name=..., config={"type": "cloud", ...})
@st.cache_resource
def setup_environment() -> str:
    env = client.beta.environments.create(
        name=f"sre-agent-{uuid.uuid4().hex[:6]}",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )
    return env.id


# ── 3. Upload the log ─────────────────────────────────────────────────────
# Push data/app.log to the Files API so sessions can mount it.
# Hint: client.beta.files.upload(file=open(...))
@st.cache_resource
def upload_log() -> str:
    with open(DATA / "app.log", "rb") as f:
        return client.beta.files.upload(file=f).id


# ── 4. Session ────────────────────────────────────────────────────────────
# Bind agent + environment, mount the log under /mnt/session/uploads/.
# Hint: client.beta.sessions.create(agent=agent_id, environment_id=..., resources=[...])
def start_session(agent_id: str, env_id: str, log_file_id: str) -> str:
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=env_id,
        resources=[{"type": "file", "file_id": log_file_id, "mount_path": "app.log"}],
    )
    return session.id


# ── 5. Stream loop ────────────────────────────────────────────────────────
# Open the event stream, send the user's message, yield events. When you see
# agent.custom_tool_use, call handle_tool() and post the result back.
# Hint: with client.beta.sessions.events.stream(session_id) as s: ...events.send(...)
def stream_reply(session_id: str, user_text: str):
    with client.beta.sessions.events.stream(session_id) as stream:
        client.beta.sessions.events.send(
            session_id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_text}]}],
        )
        for ev in stream:
            if ev.type == "agent.custom_tool_use":
                result = handle_tool(ev.name, ev.input)
                client.beta.sessions.events.send(
                    session_id,
                    events=[{"type": "user.custom_tool_result", "custom_tool_use_id": ev.id,
                             "content": [{"type": "text", "text": result}]}],
                )
            yield ev


# ── 6. Local tool handlers ────────────────────────────────────────────────
# When the cloud agent calls get_metrics / get_recent_deploys / get_diff,
# answer from `metrics` / `deploys` / `diff` (already loaded from data/).
def handle_tool(name: str, args: dict) -> str:
    if name == "get_metrics":
        return json.dumps(metrics.get(args["service"], {}).get(args["metric"]) or {"error": "not found"})
    if name == "get_recent_deploys":
        return deploys
    if name == "get_diff":
        return diff if args["commit"][:7] in diff else "no diff for that commit"
    return f"unknown tool {name}"


# ── 7. Delete session ─────────────────────────────────────────────────────
# Sessions are real cloud resources — clean them up.
# Hint: client.beta.sessions.delete(session_id)
def delete_session(session_id: str) -> None:
    client.beta.sessions.delete(session_id)