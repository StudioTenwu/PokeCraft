"""
Test suite for Agent Persistence & World State (Round 9).
Tests agent persistence, world state management, and historical tracking.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from agent_core import Agent, AgentState, Task


class AgentSnapshot:
    """A snapshot of agent state at a point in time."""

    def __init__(self, agent_id: str, snapshot_time: datetime):
        self.agent_id = agent_id
        self.snapshot_time = snapshot_time
        self.state_data: Dict[str, Any] = {}
        self.version = 1

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


class WorldState:
    """Manages the current state of the world."""

    def __init__(self, world_id: str):
        self.world_id = world_id
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> state
        self.events: List[Dict[str, Any]] = []
        self.version = 0

    def update_agent_state(self, agent_id: str, state: Dict[str, Any]):
        """Update an agent's state in the world."""
        self.agents[agent_id] = state.copy()
        self.agents[agent_id]["last_updated"] = datetime.now().isoformat()
        self.last_updated = datetime.now()
        self.version += 1

    def record_event(self, event_type: str, actor_id: str, details: Dict[str, Any]):
        """Record an event in world history."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "actor_id": actor_id,
            "details": details,
            "world_version": self.version
        }
        self.events.append(event)

    def get_agent_history(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events for an agent."""
        return [
            e for e in self.events[-limit:]
            if e["actor_id"] == agent_id
        ]

    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get all events of a specific type."""
        return [e for e in self.events if e["event_type"] == event_type]

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

    def get_latest_snapshot(self, agent_id: str) -> AgentSnapshot:
        """Get the most recent snapshot for an agent."""
        snapshots = self.snapshots.get(agent_id, [])
        return snapshots[-1] if snapshots else None

    def restore_agent_state(self, agent_id: str) -> Dict[str, Any]:
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


class HistoricalRecord:
    """Records historical events and state changes."""

    def __init__(self, record_id: str):
        self.record_id = record_id
        self.created_at = datetime.now()
        self.entries: List[Dict[str, Any]] = []

    def add_entry(self, category: str, description: str, data: Dict[str, Any] = None):
        """Add a historical entry."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "description": description,
            "data": data or {}
        }
        self.entries.append(entry)

    def get_entries_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get entries from a specific category."""
        return [e for e in self.entries if e["category"] == category]

    def get_timeline(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get timeline of events."""
        timeline = self.entries
        if limit:
            timeline = timeline[-limit:]
        return timeline

    def to_dict(self) -> Dict[str, Any]:
        """Serialize record."""
        return {
            "record_id": self.record_id,
            "entry_count": len(self.entries),
            "created_at": self.created_at.isoformat(),
            "entries": self.entries
        }


# ===== TESTS =====

def test_agent_snapshot():
    """Test creating and saving agent snapshot."""
    snapshot = AgentSnapshot("agent_1", datetime.now())
    snapshot.capture_state({
        "state": "capable",
        "skills": ["task_1", "task_2"],
        "memory_size": 100
    })

    data = snapshot.to_dict()
    assert data["agent_id"] == "agent_1"
    assert data["state_data"]["state"] == "capable"


def test_world_state_management():
    """Test managing world state."""
    world = WorldState("world_1")

    world.update_agent_state("agent_1", {"status": "active", "location": "zone_a"})
    world.update_agent_state("agent_2", {"status": "resting", "location": "zone_b"})

    assert "agent_1" in world.agents
    assert "agent_2" in world.agents
    assert world.version == 2


def test_world_event_recording():
    """Test recording events in world."""
    world = WorldState("world_1")

    world.record_event("agent_created", "agent_1", {"name": "Alice"})
    world.record_event("agent_created", "agent_2", {"name": "Bob"})
    world.record_event("task_completed", "agent_1", {"task_id": "task_1"})

    assert len(world.events) == 3

    created_events = world.get_events_by_type("agent_created")
    assert len(created_events) == 2

    agent_1_history = world.get_agent_history("agent_1")
    assert len(agent_1_history) == 2


def test_agent_persistence_save():
    """Test saving agent snapshots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = AgentPersistence(tmpdir)

        snapshot = AgentSnapshot("agent_1", datetime.now())
        snapshot.capture_state({"state": "capable", "level": 5})

        assert persistence.save_agent_snapshot("agent_1", snapshot)
        assert len(persistence.snapshots["agent_1"]) == 1


def test_agent_persistence_load():
    """Test loading agent snapshots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = AgentPersistence(tmpdir)

        snapshot1 = AgentSnapshot("agent_1", datetime.now())
        snapshot1.capture_state({"state": "developing"})

        snapshot2 = AgentSnapshot("agent_1", datetime.now() + timedelta(seconds=1))
        snapshot2.capture_state({"state": "capable"})

        persistence.save_agent_snapshot("agent_1", snapshot1)
        persistence.save_agent_snapshot("agent_1", snapshot2)

        loaded = persistence.load_agent_snapshots("agent_1")
        assert len(loaded) == 2
        assert loaded[-1].state_data["state"] == "capable"


def test_agent_restoration():
    """Test restoring agent state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = AgentPersistence(tmpdir)

        snapshot = AgentSnapshot("agent_1", datetime.now())
        snapshot.capture_state({
            "name": "Alice",
            "level": 10,
            "experience": 5000
        })

        persistence.save_agent_snapshot("agent_1", snapshot)

        restored_state = persistence.restore_agent_state("agent_1")
        assert restored_state["name"] == "Alice"
        assert restored_state["level"] == 10


def test_snapshot_pruning():
    """Test pruning old snapshots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = AgentPersistence(tmpdir)

        # Create 15 snapshots
        for i in range(15):
            snapshot = AgentSnapshot("agent_1", datetime.now() + timedelta(seconds=i))
            snapshot.capture_state({"version": i})
            persistence.save_agent_snapshot("agent_1", snapshot)

        assert len(persistence.snapshots["agent_1"]) == 15

        # Prune to keep only 5
        removed = persistence.prune_old_snapshots("agent_1", keep_count=5)
        assert removed == 10
        assert len(persistence.snapshots["agent_1"]) == 5


def test_historical_record():
    """Test recording history."""
    record = HistoricalRecord("agent_1_history")

    record.add_entry("learning", "Learned new skill", {"skill": "task_execution"})
    record.add_entry("achievement", "Completed first task", {"task_id": "task_1"})
    record.add_entry("learning", "Mastered tool", {"tool": "communication"})

    assert len(record.entries) == 3

    learning_entries = record.get_entries_by_category("learning")
    assert len(learning_entries) == 2


def test_historical_timeline():
    """Test getting historical timeline."""
    record = HistoricalRecord("agent_1_history")

    for i in range(10):
        record.add_entry("event", f"Event {i}", {"order": i})

    timeline = record.get_timeline(limit=5)
    assert len(timeline) == 5
    assert timeline[-1]["data"]["order"] == 9


def test_world_state_serialization():
    """Test serializing world state."""
    world = WorldState("world_1")
    world.update_agent_state("agent_1", {"status": "active"})
    world.record_event("agent_created", "agent_1", {})

    data = world.to_dict()
    assert data["world_id"] == "world_1"
    assert data["version"] == 1
    assert data["event_count"] == 1


def test_multi_agent_world_tracking():
    """Test tracking multiple agents in world."""
    world = WorldState("world_1")

    agents = ["agent_1", "agent_2", "agent_3"]
    for agent_id in agents:
        world.record_event("agent_created", agent_id, {"timestamp": datetime.now().isoformat()})
        world.update_agent_state(agent_id, {"status": "developing", "tasks": 0})

    assert len(world.agents) == 3
    assert len(world.events) == 3

    # Simulate progress
    world.record_event("task_completed", "agent_1", {"task_id": "task_1"})
    world.update_agent_state("agent_1", {"status": "capable", "tasks": 1})

    agent_1_events = world.get_agent_history("agent_1")
    assert len(agent_1_events) == 2


def test_persistence_with_state_changes():
    """Test persistence across state changes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        persistence = AgentPersistence(tmpdir)

        # Initial state
        snap1 = AgentSnapshot("agent_1", datetime.now())
        snap1.capture_state({"state": "created", "tasks_completed": 0})
        persistence.save_agent_snapshot("agent_1", snap1)

        # After development
        snap2 = AgentSnapshot("agent_1", datetime.now() + timedelta(hours=1))
        snap2.capture_state({"state": "developing", "tasks_completed": 5})
        persistence.save_agent_snapshot("agent_1", snap2)

        # After maturation
        snap3 = AgentSnapshot("agent_1", datetime.now() + timedelta(hours=2))
        snap3.capture_state({"state": "evolved", "tasks_completed": 50})
        persistence.save_agent_snapshot("agent_1", snap3)

        restored = persistence.restore_agent_state("agent_1")
        assert restored["state"] == "evolved"
        assert restored["tasks_completed"] == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
