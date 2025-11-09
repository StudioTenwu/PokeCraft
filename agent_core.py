"""
Core Agent class for AICraft.
Integrates all 4 primitives: Personality, Memory, Toolkit, Communication.
Represents the central entity in the microworld - the agent being raised.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import uuid


class AgentState(Enum):
    """Agent lifecycle states."""
    CREATED = "created"        # Just hatched
    DEVELOPING = "developing"  # Growing and learning
    CAPABLE = "capable"        # Ready for deployment
    DEPLOYED = "deployed"      # In active use
    RESTING = "resting"        # Idle/sleeping
    EVOLVED = "evolved"        # Matured/mastered


@dataclass
class Task:
    """Represents a task for an agent to complete."""
    task_id: str
    description: str
    category: str  # "learning", "service", "exploration", "collaboration"
    difficulty: float = 0.5  # 0.0-1.0
    reward: int = 10
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None

    def is_active(self) -> bool:
        """Check if task is currently being worked on."""
        return self.status == "in_progress"

    def is_complete(self) -> bool:
        """Check if task is done."""
        return self.status in ["completed", "failed"]

    def success(self) -> bool:
        """Check if task was successful."""
        return self.status == "completed"


class Agent:
    """
    Integrated agent with all 4 primitives.

    An Agent represents a character in the AICraft microworld that:
    - Has a personality (communication style, quirks, traits)
    - Learns through memory (episodic, semantic, procedural)
    - Develops capabilities through toolkit mastery
    - Collaborates with other agents via communication bus
    """

    def __init__(self, agent_id: str, name: str = ""):
        self.agent_id = agent_id or str(uuid.uuid4())[:8]
        self.name = name or f"Agent-{self.agent_id}"
        self.state = AgentState.CREATED
        self.created_at = datetime.now()
        self.last_activity = self.created_at

        # Module injection (dependency injection pattern)
        self.personality = None  # PersonalityModule
        self.memory = None       # MemoryStore
        self.toolkit = None      # Toolkit
        self.communication_bus = None  # AgentCommunicationBus

        # Agent stats
        self.experience_points = 0
        self.level = 1  # Could evolve over time
        self.lifetime_tasks_completed = 0
        self.lifetime_tasks_failed = 0
        self.lifetime_collaborations = 0

        # Current state
        self.current_task: Optional[Task] = None
        self.collaborators: List[str] = []  # IDs of agents collaborated with
        self.task_history: List[Task] = []

        # Agent relationships
        self.relationships: Dict[str, float] = {}  # agent_id -> affinity (-1 to 1)

    # ===== Module Injection =====

    def set_personality(self, personality) -> None:
        """Inject personality module."""
        self.personality = personality

    def set_memory(self, memory) -> None:
        """Inject memory module."""
        self.memory = memory

    def set_toolkit(self, toolkit) -> None:
        """Inject toolkit module."""
        self.toolkit = toolkit

    def set_communication_bus(self, bus) -> None:
        """Inject communication bus."""
        self.communication_bus = bus

    # ===== State Management =====

    def transition_to_state(self, new_state: AgentState) -> bool:
        """Transition agent to a new state with validation."""
        valid_transitions = {
            AgentState.CREATED: [AgentState.DEVELOPING],
            AgentState.DEVELOPING: [AgentState.CAPABLE, AgentState.RESTING],
            AgentState.CAPABLE: [AgentState.DEPLOYED, AgentState.RESTING],
            AgentState.DEPLOYED: [AgentState.RESTING, AgentState.EVOLVED],
            AgentState.RESTING: [AgentState.DEVELOPING, AgentState.DEPLOYED, AgentState.CAPABLE],
            AgentState.EVOLVED: [AgentState.DEPLOYED, AgentState.RESTING]
        }

        if new_state in valid_transitions.get(self.state, []):
            old_state = self.state
            self.state = new_state

            # Record state transition in memory
            if self.memory:
                from agent_memory import Memory, MemoryType
                mem = Memory(
                    memory_id=str(uuid.uuid4())[:8],
                    memory_type=MemoryType.SEMANTIC,
                    content={
                        "event": "state_transition",
                        "from": old_state.value,
                        "to": new_state.value
                    },
                    timestamp=datetime.now(),
                    agent_id=self.agent_id,
                    tags=["lifecycle", "state"]
                )
                self.memory.add_memory(mem)

            return True
        return False

    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self.state

    # ===== Task Management =====

    def start_task(self, task: Task) -> bool:
        """Begin working on a task."""
        # Can only work on tasks in certain states
        if self.state not in [AgentState.CAPABLE, AgentState.DEPLOYED, AgentState.EVOLVED]:
            return False

        if self.current_task is not None:
            return False  # Already working on something

        task.status = "in_progress"
        task.started_at = datetime.now()
        self.current_task = task
        self.last_activity = datetime.now()

        return True

    def complete_task(self, success: bool, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark current task as complete."""
        if not self.current_task:
            return

        self.current_task.status = "completed" if success else "failed"
        self.current_task.completed_at = datetime.now()
        self.current_task.result = result or {}

        # Record in history
        self.task_history.append(self.current_task)

        if success:
            self.lifetime_tasks_completed += 1
            reward = int(self.current_task.reward)
            self.experience_points += reward
            self._update_level()

            # Update personality from success
            if self.personality:
                self.personality.gain_experience(reward)

            # Store memory of success
            if self.memory:
                from agent_memory import Memory, MemoryType
                mem = Memory(
                    memory_id=str(uuid.uuid4())[:8],
                    memory_type=MemoryType.EPISODIC,
                    content={
                        "event": "task_success",
                        "task_id": self.current_task.task_id,
                        "category": self.current_task.category,
                        "result": result
                    },
                    timestamp=datetime.now(),
                    agent_id=self.agent_id,
                    tags=["success", self.current_task.category],
                    associated_emotions=["pride", "accomplishment"]
                )
                self.memory.add_memory(mem)

            # Update toolkit mastery if applicable
            if self.toolkit and "tool_used" in result:
                self.toolkit.use_tool(result["tool_used"], {}, success=True)
        else:
            self.lifetime_tasks_failed += 1

            # Update personality from failure
            if self.personality:
                self.personality.adjust_trait("caution", 0.02)

        self.current_task = None
        self.last_activity = datetime.now()

    def get_current_task(self) -> Optional[Task]:
        """Get the task agent is currently working on."""
        return self.current_task

    def get_task_history(self, limit: int = 10) -> List[Task]:
        """Get recent task history."""
        return self.task_history[-limit:]

    # ===== Collaboration =====

    def collaborate_with(self, other_agent_id: str) -> None:
        """Record collaboration with another agent."""
        if other_agent_id not in self.collaborators:
            self.collaborators.append(other_agent_id)
            self.lifetime_collaborations += 1

            # Initialize relationship if not exists
            if other_agent_id not in self.relationships:
                self.relationships[other_agent_id] = 0.0

    def adjust_relationship(self, agent_id: str, delta: float) -> None:
        """Adjust relationship with another agent."""
        if agent_id not in self.relationships:
            self.relationships[agent_id] = 0.0

        self.relationships[agent_id] = max(-1.0, min(1.0, self.relationships[agent_id] + delta))

    def get_relationship(self, agent_id: str) -> float:
        """Get relationship affinity with another agent (-1 to 1)."""
        return self.relationships.get(agent_id, 0.0)

    # ===== Capabilities =====

    def can_perform_action(self, action: str) -> bool:
        """Check if agent can perform an action based on state and capabilities."""
        if self.state in [AgentState.CREATED, AgentState.RESTING]:
            return False

        if self.state == AgentState.DEVELOPED and action not in ["learn", "explore"]:
            return False

        # Could check toolkit for specific actions
        return True

    def is_capable(self) -> bool:
        """Check if agent is ready for tasks."""
        return self.state in [AgentState.CAPABLE, AgentState.DEPLOYED, AgentState.EVOLVED]

    # ===== Introspection =====

    def get_status(self) -> Dict[str, Any]:
        """Get complete agent status snapshot."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state.value,
            "level": self.level,
            "experience_points": self.experience_points,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "tasks_completed": self.lifetime_tasks_completed,
            "tasks_failed": self.lifetime_tasks_failed,
            "collaborations": self.lifetime_collaborations,
            "current_task": {
                "task_id": self.current_task.task_id,
                "description": self.current_task.description,
                "status": self.current_task.status
            } if self.current_task else None,
            "collaborators": self.collaborators,
            "relationships": self.relationships,
            "personality": self.personality.to_dict() if self.personality else None,
            "memory_stats": self.memory.get_memory_stats() if self.memory else None,
            "toolkit_stats": self.toolkit.get_tool_stats() if self.toolkit else None
        }

    def get_profile(self) -> str:
        """Generate human-readable agent profile."""
        profile = f"\n{'='*50}\n"
        profile += f"**{self.name}'s Profile**\n"
        profile += f"{'='*50}\n"
        profile += f"Agent ID: {self.agent_id}\n"
        profile += f"State: {self.state.value.upper()}\n"
        profile += f"Level: {self.level}\n"
        profile += f"Experience: {self.experience_points} pts\n"
        profile += f"Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        profile += f"**Accomplishments:**\n"
        profile += f"- Tasks Completed: {self.lifetime_tasks_completed}\n"
        profile += f"- Tasks Failed: {self.lifetime_tasks_failed}\n"
        profile += f"- Collaborations: {self.lifetime_collaborations}\n\n"

        if self.personality:
            profile += f"**Personality:**\n"
            profile += f"- Style: {self.personality.expression_style.value}\n"
            profile += f"- Quirks: {', '.join(self.personality.quirks) if self.personality.quirks else 'None'}\n\n"

        if self.toolkit:
            stats = self.toolkit.get_tool_stats()
            profile += f"**Toolkit:**\n"
            profile += f"- Tools Mastered: {stats['mastered_tools']}/{stats['total_tools_registered']}\n"
            profile += f"- Avg Proficiency: {stats['avg_proficiency']:.0%}\n\n"

        if self.memory:
            stats = self.memory.get_memory_stats()
            profile += f"**Memory:**\n"
            profile += f"- Episodic Memories: {stats['episodic']}\n"
            profile += f"- Semantic Knowledge: {stats['semantic']}\n"
            profile += f"- Skills Learned: {stats['procedural']}\n\n"

        if self.collaborators:
            profile += f"**Relationships:**\n"
            for agent_id, affinity in self.relationships.items():
                status = "💚" if affinity > 0 else "💔" if affinity < 0 else "⚪"
                profile += f"- {agent_id}: {status} ({affinity:+.1f})\n"

        profile += f"{'='*50}\n"
        return profile

    # ===== Private Methods =====

    def _update_level(self) -> None:
        """Update agent level based on experience."""
        new_level = 1 + (self.experience_points // 100)
        if new_level > self.level:
            self.level = new_level

            # Record level up in memory
            if self.memory:
                from agent_memory import Memory, MemoryType
                mem = Memory(
                    memory_id=str(uuid.uuid4())[:8],
                    memory_type=MemoryType.SEMANTIC,
                    content={"event": "level_up", "new_level": new_level},
                    timestamp=datetime.now(),
                    agent_id=self.agent_id,
                    tags=["progression", "level_up"],
                    associated_emotions=["joy", "pride"]
                )
                self.memory.add_memory(mem)
