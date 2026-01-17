from __future__ import annotations

import random
from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, QTimer

from ai_radio_gui.models.state import (
    AppState,
    ConfigState,
    EventEntry,
    FeedStatus,
    LogEntry,
    MetricEntry,
    ScriptRole,
    SegmentEntry,
    StreamStats,
    TimelineEntry,
    TrackEntry,
)


class MockBackend(QObject):
    def __init__(self, state: AppState, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self._random = random.Random()
        self._feed_names = [
            "Global Wire",
            "Tech Pulse",
            "Markets Daily",
            "Civic Watch",
            "Science Desk",
        ]
        self._segment_titles = [
            "Top of Hour Headlines",
            "Market Snapshot",
            "Tech Briefing",
            "Weather Update",
            "Live Reporter Hit",
            "Deep Dive Interview",
        ]
        self._headline_pool = [
            "Global markets stabilize after early turbulence.",
            "AI safety coalition announces new guardrails.",
            "Satellite imagery confirms arctic melt acceleration.",
            "Major rail corridor restored after overnight outage.",
            "Health agency updates vaccination guidance.",
            "Municipal elections see record turnout.",
        ]
        self._track_catalog = [
            ("Anchor Voice", "Voice"),
            ("Ambient Bed", "Music"),
            ("Breaking SFX", "Effects"),
            ("Field Reporter", "Voice"),
        ]
        self._component_keys = [
            "Ingestion Guardrails",
            "Segment Planner",
            "Prompt Templates",
            "Script Guardrails",
            "TTS Engine",
            "Music Library",
            "Buffer & Fallback",
            "Encoder (FFmpeg)",
            "Streaming Server",
            "Metrics",
            "Audit Trail",
            "Policies",
            "System Settings",
            "System",
        ]
        self._scheduler_rundown: list[SegmentEntry] = []
        self._scheduler_upcoming: list[SegmentEntry] = []
        self._scripting_humor = state.scripting_humor
        self._scripting_tone = state.scripting_tone
        self._last_script = ""
        self._last_roles: list[ScriptRole] = []
        self._audio_ducking = False
        self._audio_fallback = False
        self._restart_in_progress = False

        self._init_state()
        self._init_timers()

    def _init_state(self) -> None:
        self._update_ingestion()
        self._update_memory()
        self._init_scheduler()
        self._update_scripting()
        self._update_audio()
        self._update_streaming()
        self._update_metrics()
        self._update_component_health()
        self._log("System", "INFO", "Mock backend initialized.")

    def _init_timers(self) -> None:
        self._ingestion_timer = QTimer(self)
        self._ingestion_timer.timeout.connect(self._update_ingestion)
        self._ingestion_timer.start(8000)

        self._memory_timer = QTimer(self)
        self._memory_timer.timeout.connect(self._update_memory)
        self._memory_timer.start(7000)

        self._scheduler_timer = QTimer(self)
        self._scheduler_timer.timeout.connect(self._tick_scheduler)
        self._scheduler_timer.start(1000)

        self._scripting_timer = QTimer(self)
        self._scripting_timer.timeout.connect(self._update_scripting)
        self._scripting_timer.start(12000)

        self._audio_timer = QTimer(self)
        self._audio_timer.timeout.connect(self._update_audio)
        self._audio_timer.start(1500)

        self._streaming_timer = QTimer(self)
        self._streaming_timer.timeout.connect(self._update_streaming)
        self._streaming_timer.start(2500)

        self._metrics_timer = QTimer(self)
        self._metrics_timer.timeout.connect(self._update_metrics)
        self._metrics_timer.start(5000)

        self._component_timer = QTimer(self)
        self._component_timer.timeout.connect(self._update_component_health)
        self._component_timer.start(9000)

    def _now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _now_short(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _log(self, component: str, severity: str, message: str) -> None:
        entry = LogEntry(
            timestamp=self._now(),
            component=component,
            severity=severity,
            message=message,
        )
        logs = list(self.state.logs) + [entry]
        if len(logs) > 300:
            logs = logs[-300:]
        self.state.update_logs(logs)

    def _update_ingestion(self) -> None:
        feeds: list[FeedStatus] = []
        error_count = 0
        for name in self._feed_names:
            status = self._random.choices(
                ["Healthy", "Lagging", "Error"], weights=[0.7, 0.2, 0.1]
            )[0]
            if status == "Error":
                error_count += 1
            feeds.append(
                FeedStatus(
                    name=name,
                    status=status,
                    last_fetch=self._now_short(),
                    items=self._random.randint(12, 120),
                )
            )
        overall = "Degraded" if error_count else "Healthy"
        last_fetch = self._now()
        self.state.update_ingestion(feeds, last_fetch, overall)
        self.state.update_component_summary(
            "Ingestion",
            overall,
            {
                "Feeds Active": str(len(feeds)),
                "Errors": str(error_count),
                "Last Fetch": last_fetch,
            },
            last_fetch,
        )
        self._log("Ingestion", "INFO", "Feed polling cycle completed.")

    def _update_memory(self) -> None:
        events: list[EventEntry] = []
        statuses = []
        for idx in range(1, 6):
            status = self._random.choices(
                ["Breaking", "Ongoing", "Resolved"], weights=[0.2, 0.5, 0.3]
            )[0]
            statuses.append(status)
            title = self._random.choice(self._headline_pool)
            events.append(
                EventEntry(
                    event_id=f"E{idx:03d}",
                    title=title,
                    status=status,
                    timestamp=self._now_short(),
                    detail=f"{title} Analysts are tracking updates and verifying sources.",
                )
            )
        timeline: list[TimelineEntry] = []
        for step in range(6):
            time_stamp = (datetime.now() - timedelta(minutes=step * 3)).strftime(
                "%H:%M:%S"
            )
            timeline.append(
                TimelineEntry(
                    timestamp=time_stamp,
                    description=self._random.choice(self._headline_pool),
                )
            )
        if "Breaking" in statuses:
            memory_status = "Breaking"
        elif "Ongoing" in statuses:
            memory_status = "Monitoring"
        else:
            memory_status = "Stable"
        last_update = self._now()
        self.state.update_memory(events, timeline, memory_status)
        self.state.update_component_summary(
            "Memory",
            memory_status,
            {
                "Active Events": str(len(events)),
                "Timeline Entries": str(len(timeline)),
                "Last Sync": last_update,
            },
            last_update,
        )
        self._log("Memory", "INFO", "Event store synchronized.")

    def _init_scheduler(self) -> None:
        self._scheduler_rundown = [
            self._create_segment(offset) for offset in range(3)
        ]
        self._scheduler_upcoming = [
            self._create_segment(offset + 3) for offset in range(4)
        ]
        self.state.update_scheduler(
            self._scheduler_rundown, self._scheduler_upcoming, False
        )

    def _create_segment(self, offset_index: int) -> SegmentEntry:
        title = self._random.choice(self._segment_titles)
        duration = self._random.randint(90, 300)
        start_time = (datetime.now() + timedelta(seconds=duration * offset_index)).strftime(
            "%H:%M:%S"
        )
        return SegmentEntry(
            title=title,
            start_time=start_time,
            duration_seconds=duration,
            remaining_seconds=duration,
        )

    def _tick_scheduler(self) -> None:
        if not self._scheduler_rundown:
            self._init_scheduler()
            return
        if self.state.scheduler_paused:
            self.state.update_scheduler(
                self._scheduler_rundown, self._scheduler_upcoming, True
            )
            return
        current = self._scheduler_rundown[0]
        current.remaining_seconds = max(0, current.remaining_seconds - 1)
        if current.remaining_seconds == 0:
            finished = self._scheduler_rundown.pop(0)
            if self._scheduler_upcoming:
                self._scheduler_rundown.append(self._scheduler_upcoming.pop(0))
            self._scheduler_upcoming.append(self._create_segment(len(self._scheduler_upcoming)))
            self._log("Scheduling", "INFO", f"Segment completed: {finished.title}.")
        last_update = self._now()
        self.state.update_scheduler(
            self._scheduler_rundown, self._scheduler_upcoming, False
        )
        self.state.update_component_summary(
            "Scheduling",
            "Running",
            {
                "Rundown Segments": str(len(self._scheduler_rundown)),
                "Upcoming Segments": str(len(self._scheduler_upcoming)),
                "Last Tick": last_update,
            },
            last_update,
        )

    def _update_scripting(self) -> None:
        segments = self._random.sample(self._headline_pool, k=3)
        script_lines = [
            f"Anchor: {segments[0]}",
            f"Analyst: {segments[1]}",
            f"Reporter: {segments[2]}",
        ]
        self._last_script = "\n\n".join(script_lines)
        self._last_roles = [
            ScriptRole("Anchor", self._random.randint(4, 7)),
            ScriptRole("Analyst", self._random.randint(3, 6)),
            ScriptRole("Reporter", self._random.randint(2, 5)),
        ]
        self.state.update_scripting(
            self._last_script, self._last_roles, self._scripting_humor, self._scripting_tone
        )
        last_update = self._now()
        self.state.update_component_summary(
            "Scripting",
            "Active",
            {
                "Last Script": last_update,
                "Roles": str(len(self._last_roles)),
                "Tone": str(self._scripting_tone),
            },
            last_update,
        )
        self._log("Scripting", "INFO", "New script generated.")

    def _update_audio(self) -> None:
        tracks: list[TrackEntry] = []
        for name, kind in self._track_catalog:
            base_level = self._random.randint(40, 90)
            if kind == "Music" and self._audio_ducking:
                base_level = int(base_level * 0.6)
            tracks.append(TrackEntry(name=name, kind=kind, level=base_level))
        self.state.update_audio(tracks, self._audio_ducking, self._audio_fallback)
        last_update = self._now()
        self.state.update_component_summary(
            "Audio",
            "Fallback" if self._audio_fallback else "Active",
            {
                "Active Tracks": str(len(tracks)),
                "Ducking": "Enabled" if self._audio_ducking else "Disabled",
                "Last Mix": last_update,
            },
            last_update,
        )

    def _update_streaming(self) -> None:
        if self._restart_in_progress:
            return
        status = self._random.choices(
            ["Live", "Degraded", "Offline"], weights=[0.75, 0.2, 0.05]
        )[0]
        bitrate = self._random.randint(96, 256) if status != "Offline" else 0
        listeners = self._random.randint(18, 140) if status != "Offline" else 0
        stats = StreamStats(
            status=status,
            bitrate_kbps=bitrate,
            listeners=listeners,
            url="https://stream.ai-news-radio.example/live",
        )
        self.state.update_streaming(stats)
        last_update = self._now()
        self.state.update_component_summary(
            "Streaming",
            status,
            {
                "Bitrate": f"{bitrate} kbps",
                "Listeners": str(listeners),
                "Endpoint": "Primary",
            },
            last_update,
        )
        self._log("Streaming", "INFO", f"Streaming heartbeat: {status}.")

    def _update_metrics(self) -> None:
        metrics = [
            MetricEntry("CPU Usage", self._random.uniform(22, 74), "%", "System"),
            MetricEntry("Memory Usage", self._random.uniform(40, 85), "%", "System"),
            MetricEntry("Ingestion Lag", self._random.uniform(0.2, 4.8), "min", "Ingestion"),
            MetricEntry("Script Queue", self._random.uniform(1, 6), "items", "Scripting"),
            MetricEntry("Audio Buffer", self._random.uniform(30, 90), "%", "Audio"),
            MetricEntry("Outbound Latency", self._random.uniform(0.5, 2.5), "s", "Streaming"),
        ]
        self.state.update_metrics(metrics)
        last_update = self._now()
        self.state.update_component_summary(
            "Metrics",
            "Healthy",
            {
                "Series": str(len(metrics)),
                "Refresh": "5s",
                "Last Update": last_update,
            },
            last_update,
        )

    def _update_component_health(self) -> None:
        for key in self._component_keys:
            status = self._random.choices(
                ["Healthy", "Warning", "Degraded"], weights=[0.7, 0.2, 0.1]
            )[0]
            details = {
                "Last Check": self._now_short(),
                "Throughput": f"{self._random.randint(85, 110)}%",
                "Queue Depth": str(self._random.randint(0, 12)),
            }
            if key in {"System Settings", "Policies"}:
                details.update({"Mode": self.state.config.policy_mode})
            if key == "Audit Trail":
                details.update({"Entries": str(self._random.randint(120, 220))})
            if key == "Streaming Server":
                details.update({"Connections": str(self._random.randint(1, 4))})
            if key == "Encoder (FFmpeg)":
                details.update({"Profile": "AAC 128k"})
            if key == "Buffer & Fallback":
                details.update(
                    {"Fallback": "Enabled" if self._audio_fallback else "Idle"}
                )
            self.state.update_component_summary(key, status, details, self._now())

    def force_ingestion_refresh(self) -> None:
        self._log("Ingestion", "WARN", "Manual refresh requested.")
        self._update_ingestion()

    def toggle_scheduler_pause(self) -> None:
        paused = not self.state.scheduler_paused
        self.state.update_scheduler(
            self._scheduler_rundown, self._scheduler_upcoming, paused
        )
        self._log(
            "Scheduling",
            "WARN" if paused else "INFO",
            "Scheduler paused." if paused else "Scheduler resumed.",
        )

    def skip_current_segment(self) -> None:
        if not self._scheduler_rundown:
            return
        skipped = self._scheduler_rundown.pop(0)
        if self._scheduler_upcoming:
            self._scheduler_rundown.append(self._scheduler_upcoming.pop(0))
        self._scheduler_upcoming.append(self._create_segment(len(self._scheduler_upcoming)))
        self.state.update_scheduler(
            self._scheduler_rundown, self._scheduler_upcoming, self.state.scheduler_paused
        )
        self._log("Scheduling", "WARN", f"Segment skipped: {skipped.title}.")

    def regenerate_script(self) -> None:
        self._log("Scripting", "INFO", "Manual script regeneration.")
        self._update_scripting()

    def set_scripting_humor(self, value: int) -> None:
        self._scripting_humor = value
        self.state.update_scripting(
            self._last_script, self._last_roles, self._scripting_humor, self._scripting_tone
        )

    def set_scripting_tone(self, value: int) -> None:
        self._scripting_tone = value
        self.state.update_scripting(
            self._last_script, self._last_roles, self._scripting_humor, self._scripting_tone
        )

    def toggle_ducking(self) -> None:
        self._audio_ducking = not self._audio_ducking
        self._log(
            "Audio",
            "INFO",
            "Ducking enabled." if self._audio_ducking else "Ducking disabled.",
        )
        self._update_audio()

    def toggle_fallback(self) -> None:
        self._audio_fallback = not self._audio_fallback
        self._log(
            "Audio",
            "WARN",
            "Fallback engaged." if self._audio_fallback else "Fallback cleared.",
        )
        self._update_audio()

    def restart_encoder(self) -> None:
        if self._restart_in_progress:
            return
        self._restart_in_progress = True
        self._log("Streaming", "WARN", "Encoder restart initiated.")
        self.state.update_streaming(
            StreamStats(
                status="Restarting",
                bitrate_kbps=0,
                listeners=self.state.streaming_stats.listeners,
                url="https://stream.ai-news-radio.example/live",
            )
        )
        QTimer.singleShot(2000, self._finish_restart)

    def _finish_restart(self) -> None:
        self._restart_in_progress = False
        self._log("Streaming", "INFO", "Encoder restart complete.")
        self._update_streaming()

    def force_stream_refresh(self) -> None:
        self._update_streaming()

    def clear_logs(self) -> None:
        self.state.update_logs([])

    def force_metrics_refresh(self) -> None:
        self._update_metrics()

    def apply_config(self, config: ConfigState) -> None:
        self.state.update_config(config)
        self._log("Configuration", "INFO", "Configuration updated.")
        self.state.update_component_summary(
            "System Settings",
            "Healthy",
            {
                "Timezone": config.timezone,
                "Retention": f"{config.retention_days} days",
                "Policy": config.policy_mode,
            },
            self._now(),
        )

    def refresh_all(self) -> None:
        self._update_ingestion()
        self._update_memory()
        self._update_scripting()
        self._update_audio()
        self._update_streaming()
        self._update_metrics()
        self._update_component_health()
        self._log("System", "INFO", "Full refresh executed.")

    def component_action(self, component_key: str, action: str) -> None:
        self._log(component_key, "INFO", f"{action} triggered.")
        self.state.update_component_summary(
            component_key,
            "Healthy",
            {
                "Last Action": action,
                "Operator": "Control Room",
                "Timestamp": self._now_short(),
            },
            self._now(),
        )
