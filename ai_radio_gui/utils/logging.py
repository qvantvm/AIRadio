from __future__ import annotations

import html

from ai_radio_gui.models.state import LogEntry

SEVERITY_COLORS = {
    "DEBUG": "#6c757d",
    "INFO": "#1f7a8c",
    "WARN": "#c17d11",
    "ERROR": "#b52b2b",
}


def format_log_entry(entry: LogEntry) -> str:
    color = SEVERITY_COLORS.get(entry.severity.upper(), "#2f2f2f")
    timestamp = html.escape(entry.timestamp)
    component = html.escape(entry.component)
    severity = html.escape(entry.severity)
    message = html.escape(entry.message)
    return (
        f'<span style="color:{color};">[{timestamp}] '
        f"[{component}] {severity}: {message}</span>"
    )


def format_log_entries(entries: list[LogEntry]) -> str:
    lines = [format_log_entry(entry) for entry in entries]
    return "<br>".join(lines)
