from __future__ import annotations

from typing import Callable, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QSplitter, QTabWidget, QVBoxLayout, QWidget

from ai_radio_gui.models.state import AppState
from ai_radio_gui.navigation.tree import NavigationTree
from ai_radio_gui.tabs.audio import AudioTab
from ai_radio_gui.tabs.base import ComponentTab, OverviewTab
from ai_radio_gui.tabs.config import ConfigTab
from ai_radio_gui.tabs.ingestion import IngestionTab
from ai_radio_gui.tabs.memory import MemoryTab, TimelineTab
from ai_radio_gui.tabs.observability import MetricsTab, ObservabilityTab
from ai_radio_gui.tabs.scheduler import SchedulerTab
from ai_radio_gui.tabs.scripting import ScriptingTab
from ai_radio_gui.tabs.streaming import StreamingTab


class MainWindow(QMainWindow):
    def __init__(self, state: AppState, backend) -> None:
        super().__init__()
        self.state = state
        self.backend = backend

        self.setWindowTitle("AI News Radio Control Dashboard")
        self.resize(1280, 820)

        self._tab_factories: Dict[str, Callable[[], QWidget]] = {}
        self._tab_by_node: Dict[str, QWidget] = {}
        self._node_by_widget: Dict[QWidget, str] = {}

        self.nav_tree = NavigationTree()
        self.nav_tree.setMinimumWidth(240)
        self.nav_tree.node_selected.connect(self._open_tab)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.nav_tree)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(splitter)
        self.setCentralWidget(container)

        self._build_tab_factories()
        self._open_tab("root", "AI News Radio")

    def _build_tab_factories(self) -> None:
        self._tab_factories = {
            "root": lambda: OverviewTab(self.state, self.backend),
            "ingestion": lambda: IngestionTab(self.state, self.backend, "Ingestion Overview"),
            "ingestion.news_feeds": lambda: IngestionTab(self.state, self.backend, "News Feeds"),
            "ingestion.guardrails": lambda: ComponentTab(
                self.state, self.backend, "Ingestion Guardrails", "Guardrails"
            ),
            "memory": lambda: MemoryTab(self.state, self.backend, "Memory Overview"),
            "memory.event_store": lambda: MemoryTab(self.state, self.backend, "Event Store"),
            "memory.timeline": lambda: TimelineTab(self.state, self.backend, "Timeline Viewer"),
            "scheduling": lambda: SchedulerTab(self.state, self.backend, "Scheduling Overview"),
            "scheduling.broadcast": lambda: SchedulerTab(
                self.state, self.backend, "Broadcast Scheduler"
            ),
            "scheduling.planner": lambda: ComponentTab(
                self.state, self.backend, "Segment Planner", "Segment Planner"
            ),
            "scripting": lambda: ScriptingTab(self.state, self.backend, "Scripting Overview"),
            "scripting.director": lambda: ScriptingTab(
                self.state, self.backend, "Scripting Director"
            ),
            "scripting.prompts": lambda: ComponentTab(
                self.state, self.backend, "Prompt Templates", "Prompt Templates"
            ),
            "scripting.guardrails": lambda: ComponentTab(
                self.state, self.backend, "Script Guardrails", "Script Guardrails"
            ),
            "audio": lambda: AudioTab(self.state, self.backend, "Audio Overview"),
            "audio.tts": lambda: ComponentTab(
                self.state, self.backend, "TTS Engine", "TTS Engine"
            ),
            "audio.library": lambda: ComponentTab(
                self.state, self.backend, "Music Library", "Music Library"
            ),
            "audio.mixer": lambda: AudioTab(self.state, self.backend, "Audio Mixer"),
            "audio.buffer": lambda: ComponentTab(
                self.state, self.backend, "Buffer & Fallback", "Buffer & Fallback"
            ),
            "streaming": lambda: StreamingTab(self.state, self.backend, "Streaming Overview"),
            "streaming.encoder": lambda: ComponentTab(
                self.state, self.backend, "Encoder (FFmpeg)", "Encoder (FFmpeg)"
            ),
            "streaming.server": lambda: ComponentTab(
                self.state, self.backend, "Streaming Server", "Streaming Server"
            ),
            "observability": lambda: ObservabilityTab(
                self.state, self.backend, "Observability Logs"
            ),
            "observability.logs": lambda: ObservabilityTab(self.state, self.backend, "Logs"),
            "observability.metrics": lambda: MetricsTab(self.state, self.backend, "Metrics"),
            "observability.audit": lambda: ComponentTab(
                self.state, self.backend, "Audit Trail", "Audit Trail"
            ),
            "configuration": lambda: ConfigTab(self.state, self.backend, "Configuration"),
            "configuration.settings": lambda: ConfigTab(
                self.state, self.backend, "System Settings"
            ),
            "configuration.policies": lambda: ComponentTab(
                self.state, self.backend, "Policies", "Policies"
            ),
        }

    def _open_tab(self, node_id: str, label: str) -> None:
        if node_id in self._tab_by_node:
            widget = self._tab_by_node[node_id]
            index = self.tabs.indexOf(widget)
            if index >= 0:
                self.tabs.setCurrentIndex(index)
            return
        factory = self._tab_factories.get(node_id)
        if not factory:
            return
        widget = factory()
        index = self.tabs.addTab(widget, label)
        self.tabs.setCurrentIndex(index)
        self._tab_by_node[node_id] = widget
        self._node_by_widget[widget] = node_id

    def _close_tab(self, index: int) -> None:
        widget = self.tabs.widget(index)
        if widget is None:
            return
        node_id = self._node_by_widget.pop(widget, None)
        if node_id:
            self._tab_by_node.pop(node_id, None)
        self.tabs.removeTab(index)
        widget.deleteLater()
