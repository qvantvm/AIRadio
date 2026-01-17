from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem


@dataclass
class NavNode:
    node_id: str
    label: str
    children: List["NavNode"] = field(default_factory=list)


NAV_ROOT = NavNode(
    node_id="root",
    label="AI News Radio",
    children=[
        NavNode(
            node_id="ingestion",
            label="Ingestion",
            children=[
                NavNode("ingestion.news_feeds", "News Feeds"),
                NavNode("ingestion.guardrails", "Guardrails"),
            ],
        ),
        NavNode(
            node_id="memory",
            label="Memory",
            children=[
                NavNode("memory.event_store", "Event Store"),
                NavNode("memory.timeline", "Timeline Viewer"),
            ],
        ),
        NavNode(
            node_id="scheduling",
            label="Scheduling",
            children=[
                NavNode("scheduling.broadcast", "Broadcast Scheduler"),
                NavNode("scheduling.planner", "Segment Planner"),
            ],
        ),
        NavNode(
            node_id="scripting",
            label="Scripting",
            children=[
                NavNode("scripting.director", "Scripting Director"),
                NavNode("scripting.prompts", "Prompt Templates"),
                NavNode("scripting.guardrails", "Script Guardrails"),
            ],
        ),
        NavNode(
            node_id="audio",
            label="Audio",
            children=[
                NavNode("audio.tts", "TTS Engine"),
                NavNode("audio.library", "Music Library"),
                NavNode("audio.mixer", "Audio Mixer"),
                NavNode("audio.buffer", "Buffer & Fallback"),
            ],
        ),
        NavNode(
            node_id="streaming",
            label="Streaming",
            children=[
                NavNode("streaming.encoder", "Encoder (FFmpeg)"),
                NavNode("streaming.server", "Streaming Server"),
            ],
        ),
        NavNode(
            node_id="observability",
            label="Observability",
            children=[
                NavNode("observability.logs", "Logs"),
                NavNode("observability.metrics", "Metrics"),
                NavNode("observability.audit", "Audit Trail"),
            ],
        ),
        NavNode(
            node_id="configuration",
            label="Configuration",
            children=[
                NavNode("configuration.settings", "System Settings"),
                NavNode("configuration.policies", "Policies"),
            ],
        ),
    ],
)


class NavigationTree(QTreeWidget):
    node_selected = pyqtSignal(str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setUniformRowHeights(True)
        self.setExpandsOnDoubleClick(False)
        self._build_tree()
        self.itemClicked.connect(self._handle_item_clicked)

    def _build_tree(self) -> None:
        root_item = QTreeWidgetItem([NAV_ROOT.label])
        root_item.setData(0, Qt.ItemDataRole.UserRole, NAV_ROOT.node_id)
        self.addTopLevelItem(root_item)
        for child in NAV_ROOT.children:
            self._add_children(root_item, child)
        self.expandItem(root_item)

    def _add_children(self, parent_item: QTreeWidgetItem, node: NavNode) -> None:
        item = QTreeWidgetItem([node.label])
        item.setData(0, Qt.ItemDataRole.UserRole, node.node_id)
        parent_item.addChild(item)
        for child in node.children:
            self._add_children(item, child)

    def _handle_item_clicked(self, item: QTreeWidgetItem) -> None:
        node_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not node_id:
            return
        self.node_selected.emit(str(node_id), item.text(0))
