"""
Agent Persistence & World State Management for AICraft (Round 9).
Handles agent state persistence, world state tracking, and historical records.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """Types of world events."""
    AGENT_CREATED = "agent_created"
    AGENT_EVOLVED = "agent_evolved"
    TASK_COMPLETED = "task_completed"
    COLLABORATION_SUCCESS = "collaboration_success"
    CONFLICT_RESOLVED = "conflict_resolved"
    WORLD_CHANGE = "world_change"
    CUSTOM = "custom"


@dataclass
class AgentSnapshot:
    """A snapshot of agent state at a point in time."""
    agent_id: str
    snapshot_time: datetime
    state_data: Dict[str, Any] = field(default_factory=dict)
    version: int = 1

    def capture_state(self, state_dict: Dict[str, Any]):
        """Capture the current state."""
        self.state_data = state_dict.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize snapshot."""
        return {
            "agent_id": self.agent_id,
            "snapshot_time": self.snapshot_time.isoformat(),
            "version": self.version,
            "state_data": self.state_data
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AgentSnapshot':
        """Deserialize snapshot."""
        snapshot = AgentSnapshot(
            agent_id=data["agent_id"],
            snapshot_time=datetime.fromisoformat(data["snapshot_time"]),
            state_data=data["state_data"],
            version=data.get("version", 1)
        )
        return snapshot


@dataclass
class WorldEvent:
    """An event in world history."""
    timestamp: datetime
    event_type: str
    actor_id: str
    details: Dict[str, Any] = field(default_factory=dict)
    world_version: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "details": self.details,
            "world_version": self.world_version
        }


class WorldState:
    """Manages the current state of the world."""

    def __init__(self, world_id: str):
        self.world_id = world_id
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.events: List[WorldEvent] = []
        self.version = 0

    def update_agent_state(self, agent_id: str, state: Dict[str, Any]):
        """Update an agent's state in the world."""
        self.agents[agent_id] = state.copy()
        self.agents[agent_id]["last_updated"] = datetime.now().isoformat()
        self.last_updated = datetime.now()
        self.version += 1

    def record_event(self, event_type: str, actor_id: str, details: Dict[str, Any] = None):
        """Record an event in world history."""
        event = WorldEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            actor_id=actor_id,
            details=details or {},
            world_version=self.version
        )
        self.events.append(event)

    def get_agent_history(self, agent_id: str, limit: int = 10) -> List[WorldEvent]:
        """Get recent events for an agent."""
        history = [e for e in self.events if e.actor_id == agent_id]
        return history[-limit:] if limit else history

    def get_events_by_type(self, event_type: str) -> List[WorldEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]

    def get_events_since(self, since_time: datetime) -> List[WorldEvent]:
        """Get events since a specific time."""
        return [e for e in self.events if e.timestamp >= since_time]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize world state."""
        return {
            "world_id": self.world_id,
            "version": self.version,
            "agents": self.agents,
            "event_count": len(self.events),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }


class AgentPersistence:
    """Handles agent persistence to storage."""

    def __init__(self, storage_dir: str = "./agent_storage"):
        self.storage_dir = storage_dir
        self.snapshots: Dict[str, List[AgentSnapshot]] = {}
        os.makedirs(storage_dir, exist_ok=True)

    def save_agent_snapshot(self, agent_id: str, snapshot: AgentSnapshot) -> bool:
        """Save a snapshot of agent state."""
        if agent_id not in self.snapshots:
            self.snapshots[agent_id] = []

        self.snapshots[agent_id].append(snapshot)

        # Also write to disk
        filepath = os.path.join(
            self.storage_dir,
            f"{agent_id}_snapshot_{snapshot.snapshot_time.timestamp()}.json"
        )

        try:
            with open(filepath, 'w') as f:
                json.dump(snapshot.to_dict(), f, indent=2)
            return True
        except Exception:
            return False

    def load_agent_snapshots(self, agent_id: str) -> List[AgentSnapshot]:
        """Load all snapshots for an agent."""
        return self.snapshots.get(agent_id, [])

    def get_latest_snapshot(self, agent_id: str) -> Optional[AgentSnapshot]:
        """Get the most recent snapshot for an agent."""
        snapshots = self.snapshots.get(agent_id, [])
        return snapshots[-1] if snapshots else None

    def restore_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Restore agent state from latest snapshot."""
        snapshot = self.get_latest_snapshot(agent_id)
        if snapshot:
            return snapshot.state_data.copy()
        return None

    def prune_old_snapshots(self, agent_id: str, keep_count: int = 10) -> int:
        """Remove old snapshots, keeping only recent ones."""
        if agent_id not in self.snapshots:
            return 0

        snapshots = self.snapshots[agent_id]
        if len(snapshots) <= keep_count:
            return 0

        removed = len(snapshots) - keep_count
        self.snapshots[agent_id] = snapshots[-keep_count:]
        return removed

    def export_snapshots(self, agent_id: str, filepath: str) -> bool:
        """Export all snapshots to a JSON file."""
        snapshots = self.snapshots.get(agent_id, [])
        try:
            with open(filepath, 'w') as f:
                json.dump(
                    [s.to_dict() for s in snapshots],
                    f, indent=2
                )
            return True
        except Exception:
            return False

    def import_snapshots(self, agent_id: str, filepath: str) -> bool:
        """Import snapshots from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            if agent_id not in self.snapshots:
                self.snapshots[agent_id] = []

            for snapshot_data in data:
                snapshot = AgentSnapshot.from_dict(snapshot_data)
                self.snapshots[agent_id].append(snapshot)

            return True
        except Exception:
            return False


class HistoricalRecord:
    """Records historical events and state changes."""

    def __init__(self, record_id: str):
        self.record_id = record_id
        self.created_at = datetime.now()
        self.entries: List[Dict[str, Any]] = []

    def add_entry(
        self, category: str, description: str,
        data: Dict[str, Any] = None, severity: float = 0.5
    ):
        """Add a historical entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "description": description,
            "data": data or {},
            "severity": severity
        }
        self.entries.append(entry)

    def get_entries_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get entries from a specific category."""
        return [e for e in self.entries if e["category"] == category]

    def get_timeline(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get timeline of events."""
        timeline = self.entries
        if limit:
            timeline = timeline[-limit:]
        return timeline

    def get_entries_since(self, since_time: datetime) -> List[Dict[str, Any]]:
        """Get entries since a specific time."""
        return [
            e for e in self.entries
            if datetime.fromisoformat(e["timestamp"]) >= since_time
        ]

    def summarize(self) -> Dict[str, Any]:
        """Get summary of record."""
        categories = {}
        for entry in self.entries:
            cat = entry["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        return {
            "record_id": self.record_id,
            "entry_count": len(self.entries),
            "created_at": self.created_at.isoformat(),
            "categories": categories
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize record."""
        return {
            "record_id": self.record_id,
            "entry_count": len(self.entries),
            "created_at": self.created_at.isoformat(),
            "entries": self.entries
        }
