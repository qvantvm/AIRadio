from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton

from ai_radio_gui.models.state import AppState
from ai_radio_gui.tabs.base import BaseTab


class StreamingTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Streaming") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        status_group, status_layout = self._create_section("Encoder Status")
        self.status_label = QLabel("Status: Offline")
        self.bitrate_label = QLabel("Bitrate: 0 kbps")
        self.listeners_label = QLabel("Listeners: 0")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.bitrate_label)
        status_layout.addWidget(self.listeners_label)

        url_group, url_layout = self._create_section("Stream URL")
        self.url_field = QLineEdit()
        self.url_field.setReadOnly(True)
        url_layout.addWidget(self.url_field)

        controls_group, controls_layout = self._create_section("Controls")
        restart_button = QPushButton("Restart Encoder")
        restart_button.clicked.connect(self.backend.restart_encoder)
        refresh_button = QPushButton("Refresh Stats")
        refresh_button.clicked.connect(self.backend.force_stream_refresh)
        controls_row = QHBoxLayout()
        controls_row.addWidget(restart_button)
        controls_row.addWidget(refresh_button)
        controls_row.addStretch()
        controls_layout.addLayout(controls_row)

        self._layout.addWidget(status_group)
        self._layout.addWidget(url_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.streaming_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        stats = self.state.streaming_stats
        self.status_label.setText(f"Status: {stats.status}")
        self.bitrate_label.setText(f"Bitrate: {stats.bitrate_kbps} kbps")
        self.listeners_label.setText(f"Listeners: {stats.listeners}")
        self.url_field.setText(stats.url)
