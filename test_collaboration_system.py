"""
Round 54: Real-Time Collaboration System
Enable agents to collaborate in real-time on shared tasks.
Features: session management, state synchronization, conflict resolution, shared goals.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class SessionState(Enum):
    """State of a collaboration session"""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ConflictType(Enum):
    """Types of conflicts between agent actions"""
    STATE_CONFLICT = "state_conflict"
    RESOURCE_CONFLICT = "resource_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"


@dataclass
class AgentState:
    """State snapshot of an agent in collaboration"""
    agent_id: str
    task_progress: float = 0.0  # 0.0-1.0
    resources_used: float = 0.0  # 0.0-1.0
    last_update: float = 0.0
    status: str = "idle"

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "progress": self.task_progress,
            "resources": self.resources_used,
            "status": self.status
        }


@dataclass
class SharedTask:
    """Task shared between collaborating agents"""
    task_id: str
    description: str = ""
    agents: List[str] = field(default_factory=list)
    completion: float = 0.0  # 0.0-1.0
    resource_pool: float = 1.0  # 0.0-1.0
    priority: float = 0.5  # 0.0-1.0

    def add_agent(self, agent_id: str) -> bool:
        if agent_id not in self.agents:
            self.agents.append(agent_id)
            return True
        return False

    def update_completion(self, progress: float) -> bool:
        if 0.0 <= progress <= 1.0:
            self.completion = progress
            return True
        return False

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "agents": len(self.agents),
            "completion": self.completion,
            "priority": self.priority
        }


@dataclass
class StateUpdate:
    """Update to shared state from an agent"""
    update_id: str
    agent_id: str
    task_id: str
    new_state: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    confidence: float = 0.8  # 0.0-1.0

    def to_dict(self) -> Dict:
        return {
            "id": self.update_id,
            "agent": self.agent_id,
            "task": self.task_id,
            "confidence": self.confidence
        }


@dataclass
class ConflictResolution:
    """Resolution of a conflict between agents"""
    conflict_id: str
    conflict_type: ConflictType
    agent_ids: List[str] = field(default_factory=list)
    resolution_strategy: str = "consensus"  # consensus, priority, resource_fair, merge
    resolution_strength: float = 0.5  # 0.0-1.0

    def to_dict(self) -> Dict:
        return {
            "conflict_id": self.conflict_id,
            "type": self.conflict_type.value,
            "strategy": self.resolution_strategy,
            "strength": self.resolution_strength
        }


class CollaborationSession:
    """Manages real-time collaboration between agents"""

    def __init__(self, session_id: str, task_id: str):
        self.session_id = session_id
        self.task_id = task_id
        self.state = SessionState.CREATED
        self.agents: Dict[str, AgentState] = {}
        self.shared_task: Optional[SharedTask] = None
        self.state_updates: List[StateUpdate] = []
        self.conflicts: List[ConflictResolution] = []

    def join_session(self, agent_id: str) -> bool:
        """Agent joins collaboration session"""
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentState(agent_id=agent_id)
            return True
        return False

    def activate_session(self) -> bool:
        """Transition session to active state"""
        if self.state == SessionState.CREATED and len(self.agents) > 0:
            self.state = SessionState.ACTIVE
            return True
        return False

    def submit_state_update(self, agent_id: str, new_state: Dict) -> StateUpdate:
        """Agent submits state update"""
        update = StateUpdate(
            update_id=f"upd_{len(self.state_updates)}",
            agent_id=agent_id,
            task_id=self.task_id,
            new_state=new_state,
            timestamp=0.0
        )
        self.state_updates.append(update)
        return update

    def apply_state_update(self, agent_id: str, progress: float, resources: float) -> bool:
        """Apply state update to agent's tracked state"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.task_progress = max(0.0, min(1.0, progress))
            agent.resources_used = max(0.0, min(1.0, resources))
            return True
        return False

    def detect_conflict(self, conflict_type: ConflictType, agent_ids: List[str]) -> bool:
        """Detect conflict between agents"""
        if len(agent_ids) >= 2:
            resolution = ConflictResolution(
                conflict_id=f"conf_{len(self.conflicts)}",
                conflict_type=conflict_type,
                agent_ids=agent_ids
            )
            self.conflicts.append(resolution)
            return True
        return False

    def resolve_conflict(self, conflict_id: str, strategy: str) -> bool:
        """Resolve detected conflict"""
        for conflict in self.conflicts:
            if conflict.conflict_id == conflict_id:
                conflict.resolution_strategy = strategy
                conflict.resolution_strength = 0.9
                return True
        return False

    def complete_session(self) -> bool:
        """Complete collaboration session"""
        if self.state == SessionState.ACTIVE:
            self.state = SessionState.COMPLETED
            return True
        return False

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "state": self.state.value,
            "agents": len(self.agents),
            "updates": len(self.state_updates),
            "conflicts": len(self.conflicts)
        }


class SyncManager:
    """Manages state synchronization across agents"""

    def __init__(self):
        self.synced_states: Dict[str, Dict] = {}
        self.sync_history: List[Dict] = []
        self.last_sync_time: float = 0.0

    def sync_agent_state(self, agent_id: str, state: Dict) -> bool:
        """Synchronize agent state with others"""
        self.synced_states[agent_id] = state
        self.sync_history.append({
            "agent": agent_id,
            "state": state
        })
        return True

    def get_synchronized_state(self, agent_id: str) -> Optional[Dict]:
        """Get latest synchronized state for agent"""
        return self.synced_states.get(agent_id)

    def consolidate_states(self, agent_ids: List[str]) -> Dict:
        """Consolidate states from multiple agents"""
        consolidated = {}
        for agent_id in agent_ids:
            if agent_id in self.synced_states:
                consolidated[agent_id] = self.synced_states[agent_id]
        return consolidated

    def to_dict(self) -> Dict:
        return {
            "synchronized_agents": len(self.synced_states),
            "sync_events": len(self.sync_history)
        }


class GoalTracker:
    """Tracks progress toward shared collaboration goals"""

    def __init__(self):
        self.shared_goals: Dict[str, float] = {}  # goal_id -> completion 0.0-1.0
        self.agent_contributions: Dict[str, List[str]] = {}  # agent_id -> [goal_ids]
        self.goal_achieved_count: int = 0

    def create_shared_goal(self, goal_id: str) -> bool:
        """Create a new shared goal"""
        if goal_id not in self.shared_goals:
            self.shared_goals[goal_id] = 0.0
            return True
        return False

    def assign_goal_to_agent(self, agent_id: str, goal_id: str) -> bool:
        """Assign goal to agent"""
        if agent_id not in self.agent_contributions:
            self.agent_contributions[agent_id] = []
        if goal_id not in self.agent_contributions[agent_id]:
            self.agent_contributions[agent_id].append(goal_id)
            return True
        return False

    def update_goal_progress(self, goal_id: str, progress: float) -> bool:
        """Update progress toward goal"""
        if goal_id in self.shared_goals and 0.0 <= progress <= 1.0:
            self.shared_goals[goal_id] = progress
            if progress >= 1.0:
                self.goal_achieved_count += 1
            return True
        return False

    def get_overall_progress(self) -> float:
        """Get overall progress toward all goals"""
        if not self.shared_goals:
            return 0.0
        return sum(self.shared_goals.values()) / len(self.shared_goals)

    def to_dict(self) -> Dict:
        return {
            "total_goals": len(self.shared_goals),
            "goals_achieved": self.goal_achieved_count,
            "overall_progress": self.get_overall_progress()
        }


class CollaborationManager:
    """Central manager for real-time agent collaboration"""

    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.sync_manager = SyncManager()
        self.goal_tracker = GoalTracker()
        self.shared_tasks: Dict[str, SharedTask] = {}

    def create_session(self, session_id: str, task_id: str) -> CollaborationSession:
        """Create new collaboration session"""
        session = CollaborationSession(session_id, task_id)
        self.sessions[session_id] = session
        return session

    def create_shared_task(self, task_id: str, description: str = "") -> SharedTask:
        """Create shared task for collaboration"""
        task = SharedTask(task_id=task_id, description=description)
        self.shared_tasks[task_id] = task
        return task

    def join_collaboration(self, session_id: str, agent_id: str) -> bool:
        """Agent joins collaboration"""
        if session_id in self.sessions:
            return self.sessions[session_id].join_session(agent_id)
        return False

    def activate_collaboration(self, session_id: str) -> bool:
        """Activate collaboration session"""
        if session_id in self.sessions:
            return self.sessions[session_id].activate_session()
        return False

    def sync_collaboration_state(self, session_id: str) -> bool:
        """Synchronize state across all agents in session"""
        if session_id not in self.sessions:
            return False
        session = self.sessions[session_id]
        for agent_id, agent_state in session.agents.items():
            self.sync_manager.sync_agent_state(agent_id, agent_state.to_dict())
        return True

    def complete_collaboration(self, session_id: str) -> bool:
        """Complete collaboration session"""
        if session_id in self.sessions:
            return self.sessions[session_id].complete_session()
        return False

    def to_dict(self) -> Dict:
        return {
            "active_sessions": len(self.sessions),
            "shared_tasks": len(self.shared_tasks),
            "synced_agents": self.sync_manager.to_dict()["synchronized_agents"]
        }


# ===== Tests =====

def test_agent_state_creation():
    state = AgentState("agent1")
    assert state.agent_id == "agent1"
    assert state.task_progress == 0.0


def test_shared_task_creation():
    task = SharedTask("task1", "test task")
    assert task.task_id == "task1"
    assert task.completion == 0.0


def test_shared_task_add_agent():
    task = SharedTask("task1")
    assert task.add_agent("agent1") is True
    assert len(task.agents) == 1


def test_shared_task_completion():
    task = SharedTask("task1")
    assert task.update_completion(0.5) is True
    assert task.completion == 0.5


def test_collaboration_session_creation():
    session = CollaborationSession("sess1", "task1")
    assert session.session_id == "sess1"
    assert session.state == SessionState.CREATED


def test_collaboration_session_join():
    session = CollaborationSession("sess1", "task1")
    assert session.join_session("agent1") is True
    assert len(session.agents) == 1


def test_collaboration_session_activate():
    session = CollaborationSession("sess1", "task1")
    session.join_session("agent1")
    assert session.activate_session() is True
    assert session.state == SessionState.ACTIVE


def test_state_update_submission():
    session = CollaborationSession("sess1", "task1")
    update = session.submit_state_update("agent1", {"progress": 0.5})
    assert update is not None
    assert len(session.state_updates) == 1


def test_apply_state_update():
    session = CollaborationSession("sess1", "task1")
    session.join_session("agent1")
    assert session.apply_state_update("agent1", 0.5, 0.3) is True
    assert session.agents["agent1"].task_progress == 0.5


def test_conflict_detection():
    session = CollaborationSession("sess1", "task1")
    session.join_session("agent1")
    session.join_session("agent2")
    assert session.detect_conflict(ConflictType.RESOURCE_CONFLICT, ["agent1", "agent2"]) is True


def test_conflict_resolution():
    session = CollaborationSession("sess1", "task1")
    session.join_session("agent1")
    session.join_session("agent2")
    session.detect_conflict(ConflictType.RESOURCE_CONFLICT, ["agent1", "agent2"])
    assert session.resolve_conflict("conf_0", "consensus") is True


def test_sync_manager_sync():
    sync_mgr = SyncManager()
    state = {"progress": 0.5, "status": "working"}
    assert sync_mgr.sync_agent_state("agent1", state) is True


def test_sync_manager_retrieve():
    sync_mgr = SyncManager()
    state = {"progress": 0.5}
    sync_mgr.sync_agent_state("agent1", state)
    retrieved = sync_mgr.get_synchronized_state("agent1")
    assert retrieved == state


def test_goal_tracker_create():
    tracker = GoalTracker()
    assert tracker.create_shared_goal("goal1") is True


def test_goal_tracker_assign():
    tracker = GoalTracker()
    tracker.create_shared_goal("goal1")
    assert tracker.assign_goal_to_agent("agent1", "goal1") is True


def test_goal_tracker_progress():
    tracker = GoalTracker()
    tracker.create_shared_goal("goal1")
    assert tracker.update_goal_progress("goal1", 0.8) is True
    assert tracker.shared_goals["goal1"] == 0.8


def test_goal_tracker_achievement():
    tracker = GoalTracker()
    tracker.create_shared_goal("goal1")
    tracker.update_goal_progress("goal1", 1.0)
    assert tracker.goal_achieved_count == 1


def test_collaboration_manager_create_session():
    mgr = CollaborationManager()
    session = mgr.create_session("sess1", "task1")
    assert session is not None


def test_collaboration_manager_join():
    mgr = CollaborationManager()
    mgr.create_session("sess1", "task1")
    assert mgr.join_collaboration("sess1", "agent1") is True


def test_collaboration_manager_activate():
    mgr = CollaborationManager()
    session = mgr.create_session("sess1", "task1")
    session.join_session("agent1")
    assert mgr.activate_collaboration("sess1") is True


def test_collaboration_manager_sync():
    mgr = CollaborationManager()
    session = mgr.create_session("sess1", "task1")
    session.join_session("agent1")
    session.activate_session()
    assert mgr.sync_collaboration_state("sess1") is True


def test_complete_collaboration_workflow():
    mgr = CollaborationManager()

    # Create task and session
    task = mgr.create_shared_task("task1", "important task")
    session = mgr.create_session("sess1", "task1")

    # Multiple agents join
    assert mgr.join_collaboration("sess1", "agent1") is True
    assert mgr.join_collaboration("sess1", "agent2") is True

    # Activate collaboration
    assert mgr.activate_collaboration("sess1") is True

    # Agents make progress
    assert session.apply_state_update("agent1", 0.6, 0.4) is True
    assert session.apply_state_update("agent2", 0.4, 0.5) is True

    # Sync state
    assert mgr.sync_collaboration_state("sess1") is True

    # Complete collaboration
    assert mgr.complete_collaboration("sess1") is True
    assert session.state == SessionState.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
