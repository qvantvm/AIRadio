from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton

from ai_radio_gui.models.state import AppState, SegmentEntry
from ai_radio_gui.tabs.base import BaseTab


class SchedulerTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Scheduler") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        status_group, status_layout = self._create_section("Scheduler Status")
        self.status_label = QLabel("Status: Running")
        status_layout.addWidget(self.status_label)

        rundown_group, rundown_layout = self._create_section("Current Rundown")
        self.rundown_table, self.rundown_model = self._create_table(
            ["Segment", "Start", "Duration", "Remaining"]
        )
        rundown_layout.addWidget(self.rundown_table)

        upcoming_group, upcoming_layout = self._create_section("Upcoming Segments")
        self.upcoming_table, self.upcoming_model = self._create_table(
            ["Segment", "Start", "Duration", "Remaining"]
        )
        upcoming_layout.addWidget(self.upcoming_table)

        controls_group, controls_layout = self._create_section("Controls")
        self.pause_button = QPushButton("Pause Scheduling")
        self.pause_button.clicked.connect(self.backend.toggle_scheduler_pause)
        skip_button = QPushButton("Skip Current Segment")
        skip_button.clicked.connect(self.backend.skip_current_segment)
        controls_row = QHBoxLayout()
        controls_row.addWidget(self.pause_button)
        controls_row.addWidget(skip_button)
        controls_row.addStretch()
        controls_layout.addLayout(controls_row)

        self._layout.addWidget(status_group)
        self._layout.addWidget(rundown_group)
        self._layout.addWidget(upcoming_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.scheduler_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        status_text = "Paused" if self.state.scheduler_paused else "Running"
        self.status_label.setText(f"Status: {status_text}")
        self.pause_button.setText(
            "Resume Scheduling" if self.state.scheduler_paused else "Pause Scheduling"
        )
        self._populate_table(
            self.rundown_model, [self._segment_row(seg) for seg in self.state.scheduler_rundown]
        )
        self._populate_table(
            self.upcoming_model,
            [self._segment_row(seg) for seg in self.state.scheduler_upcoming],
        )

    def _segment_row(self, segment: SegmentEntry) -> list[str]:
        return [
            segment.title,
            segment.start_time,
            self._format_time(segment.duration_seconds),
            self._format_time(segment.remaining_seconds),
        ]

    @staticmethod
    def _format_time(seconds: int) -> str:
        minutes, secs = divmod(max(seconds, 0), 60)
        return f"{minutes:02d}:{secs:02d}"
