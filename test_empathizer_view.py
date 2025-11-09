"""
Test suite for First-Person Empathizer View (Round 12).
Tests first-person perspective, agent experience, and empathy mechanics.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum


class ViewPerspective(Enum):
    """Different perspectives in the game."""
    THIRD_PERSON = "third_person"  # Watch agent from outside
    FIRST_PERSON = "first_person"  # Experience as the agent
    MANAGER = "manager"  # Overview of all agents


class TaskConstraint:
    """A constraint or limitation the agent operates under."""

    def __init__(self, constraint_id: str, description: str, severity: float = 0.5):
        self.constraint_id = constraint_id
        self.description = description
        self.severity = severity  # How limiting (0.0-1.0)
        self.discovered_by_player = False
        self.workarounds: List[str] = []

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
        self.empathy_score: float = 0.0  # How much player understands agent

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


# ===== TESTS =====

def test_view_perspective_enum():
    """Test perspective types."""
    assert ViewPerspective.FIRST_PERSON.value == "first_person"
    assert ViewPerspective.THIRD_PERSON.value == "third_person"


def test_task_constraint_creation():
    """Test creating task constraints."""
    constraint = TaskConstraint("limited_memory", "Agent has limited working memory", 0.7)
    assert constraint.constraint_id == "limited_memory"
    assert constraint.severity == 0.7
    assert not constraint.discovered_by_player


def test_task_constraint_discovery():
    """Test discovering constraints."""
    constraint = TaskConstraint("no_math", "Cannot perform math", 0.6)
    assert constraint.discover()
    assert constraint.discovered_by_player
    assert not constraint.discover()  # Can't discover twice


def test_task_constraint_workarounds():
    """Test finding workarounds."""
    constraint = TaskConstraint("slow_processing", "Slow to process", 0.5)
    assert constraint.add_workaround("Break into smaller steps")
    assert constraint.add_workaround("Use approximations")
    assert len(constraint.workarounds) == 2


def test_first_person_experience_init():
    """Test first-person experience initialization."""
    experience = FirstPersonExperience("agent_1")
    assert experience.current_perspective == ViewPerspective.THIRD_PERSON
    assert experience.empathy_score == 0.0


def test_perspective_switching():
    """Test switching perspectives."""
    experience = FirstPersonExperience("agent_1")

    assert experience.switch_to_first_person()
    assert experience.current_perspective == ViewPerspective.FIRST_PERSON

    assert experience.switch_to_third_person()
    assert experience.current_perspective == ViewPerspective.THIRD_PERSON


def test_adding_information_and_tools():
    """Test adding available information and tools."""
    experience = FirstPersonExperience("agent_1")

    assert experience.add_available_information("Current task description")
    assert experience.add_accessible_tool("text_processor")

    assert len(experience.available_information) == 1
    assert len(experience.accessible_tools) == 1


def test_constraint_management():
    """Test managing constraints."""
    experience = FirstPersonExperience("agent_1")
    constraint = TaskConstraint("vision_limitation", "No vision access", 0.8)

    assert experience.add_constraint(constraint)
    assert constraint.constraint_id in experience.constraints


def test_constraint_discovery_increases_empathy():
    """Test that discovering constraints increases empathy."""
    experience = FirstPersonExperience("agent_1")
    constraint = TaskConstraint("memory_limit", "Limited memory", 0.6)
    experience.add_constraint(constraint)

    initial_empathy = experience.empathy_score
    assert experience.discover_constraint("memory_limit")
    assert experience.empathy_score > initial_empathy


def test_solving_constraints_increases_empathy():
    """Test that solving constraints increases empathy more."""
    experience = FirstPersonExperience("agent_1")
    constraint = TaskConstraint("no_web", "Cannot access web", 0.7)
    experience.add_constraint(constraint)

    assert experience.solve_constraint("no_web", "Use local knowledge base")
    assert experience.empathy_score >= 0.15


def test_memory_editor_creation():
    """Test memory editor initialization."""
    editor = MemoryEditor("agent_1")
    assert editor.agent_id == "agent_1"
    assert editor.therapeutic_sessions == 0


def test_memory_editing():
    """Test editing memories."""
    editor = MemoryEditor("agent_1")

    assert editor.edit_memory("mem_1", "Updated content", "Process trauma")
    assert len(editor.edits) == 1


def test_supportive_memory_adding():
    """Test adding supportive memories."""
    editor = MemoryEditor("agent_1")

    assert editor.add_supportive_memory("You did well on that task")
    assert editor.therapeutic_sessions == 1


def test_therapeutic_impact():
    """Test calculating therapeutic impact."""
    editor = MemoryEditor("agent_1")

    editor.add_supportive_memory("Supportive message 1")
    editor.add_supportive_memory("Supportive message 2")

    impact = editor.get_therapeutic_impact()
    assert impact > 0.0


def test_empathy_development():
    """Test developing empathy."""
    empathy = EmpathyDevelopment("player_1")

    assert empathy.gain_empathy(0.3, "Discovered agent's limitation") > 0.0
    assert empathy.total_empathy == 0.3


def test_empathy_milestones():
    """Test empathy milestones."""
    empathy = EmpathyDevelopment("player_1")

    empathy.gain_empathy(0.5, "Reason 1")
    assert "halfway" in empathy.milestone_reached

    empathy.gain_empathy(0.3, "Reason 2")
    assert "deep_understanding" in empathy.milestone_reached


def test_empathy_level_description():
    """Test empathy level descriptions."""
    empathy = EmpathyDevelopment("player_1")

    empathy.total_empathy = 0.1
    assert "beginning" in empathy.get_empathy_level_description()

    empathy.total_empathy = 0.5
    assert "Genuine" in empathy.get_empathy_level_description()

    empathy.total_empathy = 0.9
    assert "Deep" in empathy.get_empathy_level_description()


def test_empathy_profile():
    """Test getting empathy profile."""
    empathy = EmpathyDevelopment("player_1")
    empathy.gain_empathy(0.6, "Understanding")

    profile = empathy.get_empathy_profile()
    assert profile["player_id"] == "player_1"
    assert profile["total_empathy"] == 0.6


def test_experience_logging():
    """Test logging experiences."""
    experience = FirstPersonExperience("agent_1")

    experience.switch_to_first_person()
    assert len(experience.experience_log) == 1


def test_empathy_report():
    """Test getting empathy report."""
    experience = FirstPersonExperience("agent_1")

    constraint1 = TaskConstraint("limited_memory", "Limited memory", 0.5)
    constraint2 = TaskConstraint("no_vision", "No vision", 0.7)

    experience.add_constraint(constraint1)
    experience.add_constraint(constraint2)

    experience.discover_constraint("limited_memory")
    experience.solve_constraint("no_vision", "Use text descriptions")

    report = experience.get_empathy_report()
    assert report["constraints_discovered"] == 1
    assert report["workarounds_found"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
