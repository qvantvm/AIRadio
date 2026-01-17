from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QTextEdit

from ai_radio_gui.models.state import AppState, EventEntry
from ai_radio_gui.tabs.base import BaseTab


class MemoryTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Event Store") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend
        self._events: list[EventEntry] = []

        status_group, status_layout = self._create_section("Memory Status")
        self.status_label = QLabel("Status: Idle")
        status_layout.addWidget(self.status_label)

        events_group, events_layout = self._create_section("Event Store")
        events_row = QHBoxLayout()
        self.event_table, self.event_model = self._create_table(
            ["ID", "Title", "Status", "Timestamp"]
        )
        self.event_detail = QTextEdit()
        self.event_detail.setReadOnly(True)
        self.event_detail.setPlaceholderText("Select an event to see details.")
        events_row.addWidget(self.event_table, stretch=3)
        events_row.addWidget(self.event_detail, stretch=2)
        events_layout.addLayout(events_row)

        timeline_group, timeline_layout = self._create_section("Timeline Viewer")
        self.timeline_table, self.timeline_model = self._create_table(
            ["Timestamp", "Entry"]
        )
        timeline_layout.addWidget(self.timeline_table)

        self._layout.addWidget(status_group)
        self._layout.addWidget(events_group)
        self._layout.addWidget(timeline_group)
        self._layout.addStretch()

        self.event_table.selectionModel().selectionChanged.connect(
            self._handle_event_selection
        )
        self.state.memory_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        self.status_label.setText(f"Status: {self.state.memory_status}")
        self._events = list(self.state.memory_events)
        self._populate_table(
            self.event_model,
            [
                [event.event_id, event.title, event.status, event.timestamp]
                for event in self._events
            ],
        )
        self._populate_table(
            self.timeline_model,
            [
                [entry.timestamp, entry.description]
                for entry in self.state.memory_timeline
            ],
        )
        if not self._events:
            self.event_detail.setText("No events available.")

    def _handle_event_selection(self) -> None:
        selection = self.event_table.selectionModel().selectedRows()
        if not selection:
            return
        row = selection[0].row()
        if 0 <= row < len(self._events):
            event = self._events[row]
            detail_text = (
                f"{event.title}\n\nStatus: {event.status}\n"
                f"Timestamp: {event.timestamp}\n\n{event.detail}"
            )
            self.event_detail.setText(detail_text)


class TimelineTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Timeline Viewer") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        status_group, status_layout = self._create_section("Timeline Status")
        self.status_label = QLabel("Status: Idle")
        status_layout.addWidget(self.status_label)

        timeline_group, timeline_layout = self._create_section("Timeline Entries")
        self.timeline_table, self.timeline_model = self._create_table(
            ["Timestamp", "Entry"]
        )
        timeline_layout.addWidget(self.timeline_table)

        self._layout.addWidget(status_group)
        self._layout.addWidget(timeline_group)
        self._layout.addStretch()

        self.state.memory_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        self.status_label.setText(f"Status: {self.state.memory_status}")
        self._populate_table(
            self.timeline_model,
            [
                [entry.timestamp, entry.description]
                for entry in self.state.memory_timeline
            ],
        )
