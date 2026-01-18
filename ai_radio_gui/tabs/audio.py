from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ai_radio_gui.models.state import AppState
from ai_radio_gui.tabs.base import BaseTab


class AudioTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Audio Mixer") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        status_group, status_layout = self._create_section("Mixer Status")
        self.ducking_label = QLabel("Ducking: Disabled")
        self.fallback_label = QLabel("Fallback: Normal")
        status_layout.addWidget(self.ducking_label)
        status_layout.addWidget(self.fallback_label)

        tracks_group, tracks_layout = self._create_section("Active Tracks")
        self.track_table, self.track_model = self._create_table(
            ["Track", "Type", "Level"]
        )
        tracks_layout.addWidget(self.track_table)

        levels_group, levels_layout = self._create_section("Levels")
        self.levels_container = QWidget()
        self.levels_layout = QVBoxLayout(self.levels_container)
        levels_layout.addWidget(self.levels_container)

        controls_group, controls_layout = self._create_section("Controls")
        toggle_ducking = QPushButton("Toggle Ducking")
        toggle_ducking.clicked.connect(self.backend.toggle_ducking)
        trigger_fallback = QPushButton("Toggle Fallback")
        trigger_fallback.clicked.connect(self.backend.toggle_fallback)
        controls_row = QHBoxLayout()
        controls_row.addWidget(toggle_ducking)
        controls_row.addWidget(trigger_fallback)
        controls_row.addStretch()
        controls_layout.addLayout(controls_row)

        self._layout.addWidget(status_group)
        self._layout.addWidget(tracks_group)
        self._layout.addWidget(levels_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.audio_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        self.ducking_label.setText(
            f"Ducking: {'Enabled' if self.state.audio_ducking else 'Disabled'}"
        )
        self.fallback_label.setText(
            f"Fallback: {'Emergency' if self.state.audio_fallback else 'Normal'}"
        )
        self._populate_table(
            self.track_model,
            [
                [track.name, track.kind, f"{track.level}%"]
                for track in self.state.audio_tracks
            ],
        )
        self._refresh_levels()

    def _refresh_levels(self) -> None:
        for i in reversed(range(self.levels_layout.count())):
            item = self.levels_layout.takeAt(i)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for track in self.state.audio_tracks:
            row = QHBoxLayout()
            label = QLabel(track.name)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(track.level)
            bar.setFormat("%p%")
            row.addWidget(label)
            row.addWidget(bar)
            wrapper = QWidget()
            wrapper.setLayout(row)
            self.levels_layout.addWidget(wrapper)
