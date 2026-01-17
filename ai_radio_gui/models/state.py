from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class FeedStatus:
    name: str
    status: str
    last_fetch: str
    items: int


@dataclass
class EventEntry:
    event_id: str
    title: str
    status: str
    timestamp: str
    detail: str


@dataclass
class TimelineEntry:
    timestamp: str
    description: str


@dataclass
class SegmentEntry:
    title: str
    start_time: str
    duration_seconds: int
    remaining_seconds: int


@dataclass
class ScriptRole:
    role: str
    lines: int


@dataclass
class TrackEntry:
    name: str
    kind: str
    level: int


@dataclass
class StreamStats:
    status: str
    bitrate_kbps: int
    listeners: int
    url: str


@dataclass
class LogEntry:
    timestamp: str
    component: str
    severity: str
    message: str


@dataclass
class MetricEntry:
    name: str
    value: float
    unit: str
    component: str


@dataclass
class ConfigState:
    system_name: str
    timezone: str
    retention_days: int
    auto_update: bool
    policy_mode: str


class AppState(QObject):
    ingestion_updated = pyqtSignal()
    memory_updated = pyqtSignal()
    scheduler_updated = pyqtSignal()
    scripting_updated = pyqtSignal()
    audio_updated = pyqtSignal()
    streaming_updated = pyqtSignal()
    observability_updated = pyqtSignal()
    config_updated = pyqtSignal()
    system_updated = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.ingestion_feeds: List[FeedStatus] = []
        self.ingestion_last_fetch = "Never"
        self.ingestion_status = "Idle"

        self.memory_events: List[EventEntry] = []
        self.memory_timeline: List[TimelineEntry] = []
        self.memory_status = "Idle"

        self.scheduler_rundown: List[SegmentEntry] = []
        self.scheduler_upcoming: List[SegmentEntry] = []
        self.scheduler_paused = False

        self.scripting_last_script = ""
        self.scripting_roles: List[ScriptRole] = []
        self.scripting_humor = 40
        self.scripting_tone = 55

        self.audio_tracks: List[TrackEntry] = []
        self.audio_ducking = False
        self.audio_fallback = False

        self.streaming_stats = StreamStats(
            status="Offline", bitrate_kbps=0, listeners=0, url=""
        )

        self.logs: List[LogEntry] = []
        self.metrics: List[MetricEntry] = []

        self.config = ConfigState(
            system_name="AI News Radio",
            timezone="UTC",
            retention_days=30,
            auto_update=True,
            policy_mode="Balanced",
        )

        self.component_status: Dict[str, str] = {}
        self.component_details: Dict[str, Dict[str, str]] = {}
        self.component_last_update: Dict[str, str] = {}

    def update_ingestion(
        self, feeds: List[FeedStatus], last_fetch: str, status: str
    ) -> None:
        self.ingestion_feeds = feeds
        self.ingestion_last_fetch = last_fetch
        self.ingestion_status = status
        self.ingestion_updated.emit()

    def update_memory(
        self, events: List[EventEntry], timeline: List[TimelineEntry], status: str
    ) -> None:
        self.memory_events = events
        self.memory_timeline = timeline
        self.memory_status = status
        self.memory_updated.emit()

    def update_scheduler(
        self,
        rundown: List[SegmentEntry],
        upcoming: List[SegmentEntry],
        paused: bool,
    ) -> None:
        self.scheduler_rundown = rundown
        self.scheduler_upcoming = upcoming
        self.scheduler_paused = paused
        self.scheduler_updated.emit()

    def update_scripting(
        self,
        script_text: str,
        roles: List[ScriptRole],
        humor: int,
        tone: int,
    ) -> None:
        self.scripting_last_script = script_text
        self.scripting_roles = roles
        self.scripting_humor = humor
        self.scripting_tone = tone
        self.scripting_updated.emit()

    def update_audio(
        self, tracks: List[TrackEntry], ducking: bool, fallback: bool
    ) -> None:
        self.audio_tracks = tracks
        self.audio_ducking = ducking
        self.audio_fallback = fallback
        self.audio_updated.emit()

    def update_streaming(self, stats: StreamStats) -> None:
        self.streaming_stats = stats
        self.streaming_updated.emit()

    def update_logs(self, logs: List[LogEntry]) -> None:
        self.logs = logs
        self.observability_updated.emit()

    def update_metrics(self, metrics: List[MetricEntry]) -> None:
        self.metrics = metrics
        self.observability_updated.emit()

    def update_config(self, config: ConfigState) -> None:
        self.config = config
        self.config_updated.emit()

    def update_component_summary(
        self,
        component_key: str,
        status: str,
        details: Dict[str, str],
        last_update: str,
    ) -> None:
        self.component_status[component_key] = status
        self.component_details[component_key] = details
        self.component_last_update[component_key] = last_update
        self.system_updated.emit()
