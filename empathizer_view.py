"""
First-Person Empathizer View for AICraft (Round 12).
Enables players to experience the agent's perspective and develop empathy.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ViewPerspective(Enum):
    """Different perspectives in the game."""
    THIRD_PERSON = "third_person"  # Watch agent from outside
    FIRST_PERSON = "first_person"  # Experience as the agent
    MANAGER = "manager"  # Overview of all agents


@dataclass
class TaskConstraint:
    """A constraint or limitation the agent operates under."""
    constraint_id: str
    description: str
    severity: float = 0.5  # How limiting (0.0-1.0)
    discovered_by_player: bool = False
    workarounds: List[str] = field(default_factory=list)

    def discover(self) -> bool:
        """Player discovers this constraint."""
        if self.discovered_by_player:
            return False
        self.discovered_by_player = True
        return True

    def add_workaround(self, workaround: str) -> bool:
        """Player finds a workaround to constraint."""
        if workaround not in self.workarounds:
            self.workarounds.append(workaround)
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize constraint."""
        return {
            "constraint_id": self.constraint_id,
            "description": self.description,
            "severity": self.severity,
            "discovered": self.discovered_by_player,
            "workarounds": self.workarounds
        }


class FirstPersonExperience:
    """Simulates first-person agent experience."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_perspective = ViewPerspective.THIRD_PERSON
        self.available_information: List[str] = []
        self.accessible_tools: List[str] = []
        self.constraints: Dict[str, TaskConstraint] = {}
        self.experience_log: List[Dict[str, Any]] = []
        self.empathy_score: float = 0.0

    def switch_to_first_person(self) -> bool:
        """Enter first-person view."""
        if self.current_perspective == ViewPerspective.FIRST_PERSON:
            return False
        self.current_perspective = ViewPerspective.FIRST_PERSON
        self.log_experience("perspective_change", {"from": "third_person", "to": "first_person"})
        return True

    def switch_to_third_person(self) -> bool:
        """Return to third-person view."""
        if self.current_perspective != ViewPerspective.FIRST_PERSON:
            return False
        self.current_perspective = ViewPerspective.THIRD_PERSON
        self.log_experience("perspective_change", {"from": "first_person", "to": "third_person"})
        return True

    def add_available_information(self, info: str) -> bool:
        """Add information available to agent in first-person view."""
        if info not in self.available_information:
            self.available_information.append(info)
            return True
        return False

    def add_accessible_tool(self, tool: str) -> bool:
        """Add tool agent can access in first-person view."""
        if tool not in self.accessible_tools:
            self.accessible_tools.append(tool)
            return True
        return False

    def add_constraint(self, constraint: TaskConstraint) -> bool:
        """Add a constraint agent operates under."""
        if constraint.constraint_id in self.constraints:
            return False
        self.constraints[constraint.constraint_id] = constraint
        return True

    def discover_constraint(self, constraint_id: str) -> bool:
        """Player discovers a constraint about the agent."""
        if constraint_id not in self.constraints:
            return False

        constraint = self.constraints[constraint_id]
        if constraint.discover():
            self.empathy_score = min(1.0, self.empathy_score + 0.1)
            self.log_experience("constraint_discovered", {"constraint": constraint_id})
            return True
        return False

    def solve_constraint(self, constraint_id: str, workaround: str) -> bool:
        """Player finds workaround for constraint."""
        if constraint_id not in self.constraints:
            return False

        constraint = self.constraints[constraint_id]
        if constraint.add_workaround(workaround):
            self.empathy_score = min(1.0, self.empathy_score + 0.15)
            self.log_experience("constraint_solved", {
                "constraint": constraint_id,
                "workaround": workaround
            })
            return True
        return False

    def log_experience(self, experience_type: str, details: Dict[str, Any]):
        """Log player experience."""
        self.experience_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": experience_type,
            "details": details
        })

    def get_empathy_report(self) -> Dict[str, Any]:
        """Get report on player empathy development."""
        constraints_discovered = sum(1 for c in self.constraints.values() if c.discovered_by_player)
        total_workarounds = sum(len(c.workarounds) for c in self.constraints.values())

        return {
            "agent_id": self.agent_id,
            "empathy_score": self.empathy_score,
            "constraints_discovered": constraints_discovered,
            "total_constraints": len(self.constraints),
            "workarounds_found": total_workarounds,
            "information_accessed": len(self.available_information),
            "tools_used": len(self.accessible_tools),
            "perspective": self.current_perspective.value
        }


class MemoryEditor:
    """Tool for editing agent memories to help it process experience."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.edits: List[Dict[str, Any]] = []
        self.therapeutic_sessions: int = 0

    def view_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """View a memory entry."""
        return {"memory_id": memory_id, "content": "memory content"}

    def edit_memory(self, memory_id: str, new_content: str, edit_reason: str) -> bool:
        """Edit a memory to help agent process it."""
        self.edits.append({
            "timestamp": datetime.now().isoformat(),
            "memory_id": memory_id,
            "new_content": new_content,
            "reason": edit_reason
        })
        return True

    def add_supportive_memory(self, content: str) -> bool:
        """Add new supportive memory to help agent."""
        self.edits.append({
            "timestamp": datetime.now().isoformat(),
            "type": "new_memory",
            "content": content,
            "purpose": "supportive"
        })
        self.therapeutic_sessions += 1
        return True

    def get_edit_history(self) -> List[Dict[str, Any]]:
        """Get all memory edits."""
        return self.edits.copy()

    def get_therapeutic_impact(self) -> float:
        """Assess therapeutic impact of memory editing."""
        if not self.edits:
            return 0.0
        supportive_edits = sum(1 for e in self.edits if e.get("purpose") == "supportive")
        return min(1.0, supportive_edits * 0.2)


class EmpathyDevelopment:
    """Tracks player's empathy development toward agent."""

    def __init__(self, player_id: str):
        self.player_id = player_id
        self.total_empathy: float = 0.0
        self.empathy_events: List[Dict[str, Any]] = []
        self.milestone_reached: List[str] = []

    def gain_empathy(self, amount: float, reason: str) -> float:
        """Increase empathy through understanding."""
        if not 0.0 <= amount <= 1.0:
            return self.total_empathy

        self.total_empathy = min(1.0, self.total_empathy + amount)
        self.empathy_events.append({
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "amount": amount,
            "new_total": self.total_empathy
        })

        # Check milestones
        if self.total_empathy >= 0.5 and "halfway" not in self.milestone_reached:
            self.milestone_reached.append("halfway")
        if self.total_empathy >= 0.8 and "deep_understanding" not in self.milestone_reached:
            self.milestone_reached.append("deep_understanding")

        return self.total_empathy

    def get_empathy_level_description(self) -> str:
        """Get human-readable empathy level."""
        if self.total_empathy < 0.2:
            return "Just beginning to understand"
        elif self.total_empathy < 0.4:
            return "Growing understanding"
        elif self.total_empathy < 0.6:
            return "Genuine empathy developing"
        elif self.total_empathy < 0.8:
            return "Strong empathy and connection"
        else:
            return "Deep understanding and compassion"

    def get_empathy_profile(self) -> Dict[str, Any]:
        """Get empathy profile."""
        return {
            "player_id": self.player_id,
            "total_empathy": self.total_empathy,
            "level": self.get_empathy_level_description(),
            "milestones": self.milestone_reached,
            "events": len(self.empathy_events)
        }
