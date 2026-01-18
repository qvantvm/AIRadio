from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
)

from ai_radio_gui.models.state import AppState, ConfigState
from ai_radio_gui.tabs.base import BaseTab


class ConfigTab(BaseTab):
    def __init__(self, state: AppState, backend, title: str = "Configuration") -> None:
        super().__init__(title)
        self.state = state
        self.backend = backend

        settings_group, settings_layout = self._create_section("System Settings")
        form = QFormLayout()
        self.system_name_field = QLineEdit()
        self.timezone_field = QLineEdit()
        self.retention_field = QSpinBox()
        self.retention_field.setRange(1, 365)
        self.auto_update_checkbox = QCheckBox("Enable automatic updates")
        self.policy_mode_field = QComboBox()
        self.policy_mode_field.addItems(["Balanced", "Strict", "Creative"])
        form.addRow("System Name", self.system_name_field)
        form.addRow("Timezone", self.timezone_field)
        form.addRow("Retention (days)", self.retention_field)
        form.addRow("Auto Updates", self.auto_update_checkbox)
        form.addRow("Policy Mode", self.policy_mode_field)
        settings_layout.addLayout(form)

        controls_group, controls_layout = self._create_section("Controls")
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self._save_settings)
        controls_layout.addWidget(save_button)

        self._layout.addWidget(settings_group)
        self._layout.addWidget(controls_group)
        self._layout.addStretch()

        self.state.config_updated.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        config = self.state.config
        self.system_name_field.setText(config.system_name)
        self.timezone_field.setText(config.timezone)
        self.retention_field.setValue(config.retention_days)
        self.auto_update_checkbox.setChecked(config.auto_update)
        index = self.policy_mode_field.findText(config.policy_mode)
        if index >= 0:
            self.policy_mode_field.setCurrentIndex(index)

    def _save_settings(self) -> None:
        config = ConfigState(
            system_name=self.system_name_field.text().strip() or "AI News Radio",
            timezone=self.timezone_field.text().strip() or "UTC",
            retention_days=self.retention_field.value(),
            auto_update=self.auto_update_checkbox.isChecked(),
            policy_mode=self.policy_mode_field.currentText(),
        )
        self.backend.apply_config(config)
