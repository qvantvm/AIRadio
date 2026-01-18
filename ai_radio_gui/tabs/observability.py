from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)

from ai_radio_gui.models.state import AppState
from ai_radio_gui.tabs.base import BaseTab
from ai_radio_gui.utils.logging import format_log_entries


class ObservabilityTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Logs") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        filter_group, filter_layout = self._create_section("Filter")
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Component"))
        self.component_filter = QComboBox()
        self.component_filter.addItem("All Components")
        self.component_filter.currentTextChanged.connect(self._refresh_logs)
        filter_row.addWidget(self.component_filter)
        filter_row.addStretch()
        filter_layout.addLayout(filter_row)

        logs_group, logs_layout = self._create_section("Log Viewer")
        self.logs_view = QTextEdit()
        self.logs_view.setReadOnly(True)
        logs_layout.addWidget(self.logs_view)

        controls_group, controls_layout = self._create_section("Controls")
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.backend.clear_logs)
        controls_layout.addWidget(clear_button)

        self._layout.addWidget(filter_group)
        self._layout.addWidget(logs_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.observability_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        self._refresh_filter_options()
        self._refresh_logs()

    def _refresh_filter_options(self) -> None:
        current = self.component_filter.currentText()
        components = sorted({entry.component for entry in self.state.logs})
        self.component_filter.blockSignals(True)
        self.component_filter.clear()
        self.component_filter.addItem("All Components")
        for component in components:
            self.component_filter.addItem(component)
        index = self.component_filter.findText(current)
        if index >= 0:
            self.component_filter.setCurrentIndex(index)
        self.component_filter.blockSignals(False)

    def _refresh_logs(self) -> None:
        component = self.component_filter.currentText()
        if component == "All Components":
            entries = self.state.logs
        else:
            entries = [entry for entry in self.state.logs if entry.component == component]
        self.logs_view.setHtml(format_log_entries(entries[-200:]))


class MetricsTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Metrics") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        metrics_group, metrics_layout = self._create_section("Metric Snapshot")
        self.metrics_table, self.metrics_model = self._create_table(
            ["Metric", "Value", "Component"]
        )
        metrics_layout.addWidget(self.metrics_table)

        controls_group, controls_layout = self._create_section("Controls")
        refresh_button = QPushButton("Refresh Metrics")
        refresh_button.clicked.connect(self.backend.force_metrics_refresh)
        controls_layout.addWidget(refresh_button)

        self._layout.addWidget(metrics_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.observability_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        rows = [
            [metric.name, f"{metric.value:.2f} {metric.unit}", metric.component]
            for metric in self.state.metrics
        ]
        self._populate_table(self.metrics_model, rows)
