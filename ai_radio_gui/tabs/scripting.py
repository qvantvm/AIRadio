from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton, QSlider, QTextEdit

from ai_radio_gui.models.state import AppState
from ai_radio_gui.tabs.base import BaseTab


class ScriptingTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Scripting Director") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        script_group, script_layout = self._create_section("Latest Script")
        self.script_view = QTextEdit()
        self.script_view.setReadOnly(True)
        script_layout.addWidget(self.script_view)

        roles_group, roles_layout = self._create_section("Role Breakdown")
        self.roles_table, self.roles_model = self._create_table(["Role", "Lines"])
        roles_layout.addWidget(self.roles_table)

        controls_group, controls_layout = self._create_section("Tone Controls")
        self.humor_label = QLabel("Humor: 0")
        self.humor_slider = QSlider(Qt.Orientation.Horizontal)
        self.humor_slider.setRange(0, 100)
        self.humor_slider.valueChanged.connect(self._humor_changed)
        self.tone_label = QLabel("Tone: 0")
        self.tone_slider = QSlider(Qt.Orientation.Horizontal)
        self.tone_slider.setRange(0, 100)
        self.tone_slider.valueChanged.connect(self._tone_changed)
        regen_button = QPushButton("Regenerate Script")
        regen_button.clicked.connect(self.backend.regenerate_script)

        controls_layout.addWidget(self.humor_label)
        controls_layout.addWidget(self.humor_slider)
        controls_layout.addWidget(self.tone_label)
        controls_layout.addWidget(self.tone_slider)
        controls_layout.addWidget(regen_button)

        self._layout.addWidget(script_group)
        self._layout.addWidget(roles_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.scripting_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        self.script_view.setText(self.state.scripting_last_script)
        self._populate_table(
            self.roles_model,
            [[role.role, str(role.lines)] for role in self.state.scripting_roles],
        )
        self._set_slider(self.humor_slider, self.state.scripting_humor)
        self._set_slider(self.tone_slider, self.state.scripting_tone)
        self.humor_label.setText(f"Humor: {self.state.scripting_humor}")
        self.tone_label.setText(f"Tone: {self.state.scripting_tone}")

    def _set_slider(self, slider: QSlider, value: int) -> None:
        slider.blockSignals(True)
        slider.setValue(value)
        slider.blockSignals(False)

    def _humor_changed(self, value: int) -> None:
        self.humor_label.setText(f"Humor: {value}")
        self.backend.set_scripting_humor(value)

    def _tone_changed(self, value: int) -> None:
        self.tone_label.setText(f"Tone: {value}")
        self.backend.set_scripting_tone(value)
