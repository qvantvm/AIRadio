from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from ai_radio_gui.app import MainWindow
from ai_radio_gui.models.state import AppState
from ai_radio_gui.services.mock_backend import MockBackend


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("AI News Radio")
    state = AppState()
    backend = MockBackend(state)
    window = MainWindow(state, backend)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
