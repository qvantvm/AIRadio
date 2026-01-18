from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton

from ai_radio_gui.models.state import AppState
from ai_radio_gui.tabs.base import BaseTab


class IngestionTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "News Ingestion") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        status_group, status_layout = self._create_section("Ingestion Status")
        self.status_label = QLabel("Status: Idle")
        self.last_fetch_label = QLabel("Last fetch: Never")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.last_fetch_label)

        feeds_group, feeds_layout = self._create_section("Feed List")
        self.feed_table, self.feed_model = self._create_table(
            ["Feed", "Status", "Last Fetch", "Items"]
        )
        feeds_layout.addWidget(self.feed_table)

        controls_group, controls_layout = self._create_section("Controls")
        refresh_button = QPushButton("Force Refresh")
        refresh_button.clicked.connect(self.backend.force_ingestion_refresh)
        controls_row = QHBoxLayout()
        controls_row.addWidget(refresh_button)
        controls_row.addStretch()
        controls_layout.addLayout(controls_row)

        self._layout.addWidget(status_group)
        self._layout.addWidget(feeds_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.ingestion_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        self.status_label.setText(f"Status: {self.state.ingestion_status}")
        self.last_fetch_label.setText(f"Last fetch: {self.state.ingestion_last_fetch}")
        rows = [
            [feed.name, feed.status, feed.last_fetch, str(feed.items)]
            for feed in self.state.ingestion_feeds
        ]
        self._populate_table(self.feed_model, rows)
