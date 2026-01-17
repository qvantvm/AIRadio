from __future__ import annotations

from typing import Iterable, List, Tuple

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ai_radio_gui.models.state import AppState
from ai_radio_gui.utils.logging import format_log_entries


class BaseTab(QWidget):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._layout = QVBoxLayout(self)
        header = QLabel(title)
        header.setStyleSheet("font-size: 18px; font-weight: 600;")
        self._layout.addWidget(header)

    def _create_section(self, title: str) -> Tuple[QGroupBox, QVBoxLayout]:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        return group, layout

    def _create_table(self, columns: List[str]) -> Tuple[QTableView, QStandardItemModel]:
        model = QStandardItemModel(0, len(columns))
        model.setHorizontalHeaderLabels(columns)
        view = QTableView()
        view.setModel(model)
        view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        view.horizontalHeader().setStretchLastSection(True)
        view.verticalHeader().setVisible(False)
        view.setAlternatingRowColors(True)
        return view, model

    def _populate_table(self, model: QStandardItemModel, rows: Iterable[List[str]]) -> None:
        model.removeRows(0, model.rowCount())
        for row in rows:
            items = [QStandardItem(str(value)) for value in row]
            for item in items:
                item.setEditable(False)
            model.appendRow(items)


class OverviewTab(BaseTab):
    def __init__(self, state: AppState, backend) -> None:
        super().__init__("AI News Radio Overview")
        self.state = state
        self.backend = backend

        snapshot_group, snapshot_layout = self._create_section("System Snapshot")
        self.snapshot_table, self.snapshot_model = self._create_table(
            ["Subsystem", "Status", "Last Update"]
        )
        snapshot_layout.addWidget(self.snapshot_table)

        actions_group, actions_layout = self._create_section("Quick Actions")
        refresh_button = QPushButton("Refresh All")
        refresh_button.clicked.connect(self.backend.refresh_all)
        alert_button = QPushButton("Simulate Alert")
        alert_button.clicked.connect(lambda: self.backend.component_action("System", "Alert"))
        actions_row = QHBoxLayout()
        actions_row.addWidget(refresh_button)
        actions_row.addWidget(alert_button)
        actions_row.addStretch()
        actions_layout.addLayout(actions_row)

        self._layout.addWidget(snapshot_group)
        self._layout.addWidget(actions_group)
        self._layout.addStretch()

        self.state.system_updated.connect(self._update_snapshot)
        self.state.ingestion_updated.connect(self._update_snapshot)
        self.state.memory_updated.connect(self._update_snapshot)
        self.state.scheduler_updated.connect(self._update_snapshot)
        self.state.scripting_updated.connect(self._update_snapshot)
        self.state.audio_updated.connect(self._update_snapshot)
        self.state.streaming_updated.connect(self._update_snapshot)
        self._update_snapshot()

    def _update_snapshot(self) -> None:
        rows = [
            [
                "Ingestion",
                self.state.ingestion_status,
                self.state.component_last_update.get("Ingestion", "n/a"),
            ],
            [
                "Memory",
                self.state.memory_status,
                self.state.component_last_update.get("Memory", "n/a"),
            ],
            [
                "Scheduling",
                "Paused" if self.state.scheduler_paused else "Running",
                self.state.component_last_update.get("Scheduling", "n/a"),
            ],
            [
                "Scripting",
                "Active" if self.state.scripting_last_script else "Idle",
                self.state.component_last_update.get("Scripting", "n/a"),
            ],
            [
                "Audio",
                "Fallback" if self.state.audio_fallback else "Active",
                self.state.component_last_update.get("Audio", "n/a"),
            ],
            [
                "Streaming",
                self.state.streaming_stats.status,
                self.state.component_last_update.get("Streaming", "n/a"),
            ],
        ]
        self._populate_table(self.snapshot_model, rows)


class ComponentTab(BaseTab):
    def __init__(
        self, state: AppState, backend, component_key: str, title: str | None = None
    ) -> None:
        super().__init__(title or component_key)
        self.state = state
        self.backend = backend
        self.component_key = component_key

        status_group, status_layout = self._create_section("Status")
        self.status_label = QLabel("Unknown")
        self.last_update_label = QLabel("Last update: n/a")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.last_update_label)

        details_group, details_layout = self._create_section("Component Details")
        self.details_table, self.details_model = self._create_table(["Field", "Value"])
        details_layout.addWidget(self.details_table)

        logs_group, logs_layout = self._create_section("Recent Activity")
        self.logs_view = QTextEdit()
        self.logs_view.setReadOnly(True)
        logs_layout.addWidget(self.logs_view)

        controls_group, controls_layout = self._create_section("Controls")
        run_button = QPushButton("Run Check")
        run_button.clicked.connect(
            lambda: self.backend.component_action(self.component_key, "Run Check")
        )
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(
            lambda: self.backend.component_action(self.component_key, "Reset")
        )
        button_row = QHBoxLayout()
        button_row.addWidget(run_button)
        button_row.addWidget(reset_button)
        button_row.addStretch()
        controls_layout.addLayout(button_row)

        self._layout.addWidget(status_group)
        self._layout.addWidget(details_group)
        self._layout.addWidget(logs_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.system_updated.connect(self._refresh_details)
        self.state.observability_updated.connect(self._refresh_logs)
        self._refresh_details()
        self._refresh_logs()

    def _refresh_details(self) -> None:
        status = self.state.component_status.get(self.component_key, "Unknown")
        details = self.state.component_details.get(self.component_key, {})
        last_update = self.state.component_last_update.get(self.component_key, "n/a")
        self.status_label.setText(f"Status: {status}")
        self.last_update_label.setText(f"Last update: {last_update}")
        rows = [[key, value] for key, value in sorted(details.items())]
        self._populate_table(self.details_model, rows)

    def _refresh_logs(self) -> None:
        filtered = [
            entry
            for entry in self.state.logs
            if entry.component == self.component_key
        ]
        self.logs_view.setHtml(format_log_entries(filtered[-15:]))
