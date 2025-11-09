"""
Interactive Learning Environment & UI/UX Hooks for AICraft (Round 10).
Provides quests, achievements, and interactive mechanics for agent development.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum


class QuestDifficulty(Enum):
    """Quest difficulty levels."""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


class AchievementType(Enum):
    """Types of achievements."""
    MILESTONE = "milestone"
    SKILL_MASTERY = "skill_mastery"
    COLLABORATION = "collaboration"
    EXPLORATION = "exploration"
    CREATIVITY = "creativity"


@dataclass
class Quest:
    """A learning quest for agents."""
    quest_id: str
    title: str
    description: str
    difficulty: QuestDifficulty
    reward: int = 100
    created_at: datetime = field(default_factory=datetime.now)
    completed_by: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    solutions: List[Dict[str, Any]] = field(default_factory=list)

    def add_objective(self, objective: str):
        """Add an objective to the quest."""
        self.objectives.append(objective)

    def add_hint(self, hint: str):
        """Add a hint for the quest."""
        self.hints.append(hint)

    def add_solution(self, approach: str, explanation: str):
        """Add a solution approach."""
        self.solutions.append({
            "approach": approach,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        })

    def mark_completed(self, agent_id: str) -> bool:
        """Mark quest as completed by an agent."""
        if agent_id in self.completed_by:
            return False
        self.completed_by.append(agent_id)
        return True

    def get_completion_count(self) -> int:
        """Get number of agents who completed."""
        return len(self.completed_by)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize quest."""
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty.name,
            "reward": self.reward,
            "objectives": self.objectives,
            "solutions_count": len(self.solutions),
            "completion_count": self.get_completion_count()
        }


@dataclass
class Achievement:
    """An achievement agents can earn."""
    achievement_id: str
    title: str
    description: str
    achievement_type: AchievementType
    created_at: datetime = field(default_factory=datetime.now)
    earned_by: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)

    def set_requirement(self, key: str, value: Any):
        """Set a requirement for earning achievement."""
        self.requirements[key] = value

    def check_requirements(self, agent_stats: Dict[str, Any]) -> bool:
        """Check if agent meets requirements."""
        for key, required_value in self.requirements.items():
            if key not in agent_stats:
                return False

            agent_value = agent_stats[key]

            if isinstance(required_value, (int, float)):
                if agent_value < required_value:
                    return False
            elif isinstance(required_value, str):
                if agent_value != required_value:
                    return False

        return True

    def award_to_agent(self, agent_id: str) -> bool:
        """Award achievement to an agent."""
        if agent_id in self.earned_by:
            return False
        self.earned_by.append(agent_id)
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize achievement."""
        return {
            "achievement_id": self.achievement_id,
            "title": self.title,
            "description": self.description,
            "type": self.achievement_type.value,
            "earned_count": len(self.earned_by),
            "requirements": self.requirements
        }


class LearningEnvironment:
    """Interactive environment where agents learn and grow."""

    def __init__(self, environment_id: str):
        self.environment_id = environment_id
        self.created_at = datetime.now()
        self.active = True
        self.quests: Dict[str, Quest] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.agents_enrolled: Dict[str, Dict[str, Any]] = {}

    def add_quest(self, quest: Quest) -> bool:
        """Add a quest to the environment."""
        if quest.quest_id in self.quests:
            return False
        self.quests[quest.quest_id] = quest
        return True

    def add_achievement(self, achievement: Achievement) -> bool:
        """Add an achievement."""
        if achievement.achievement_id in self.achievements:
            return False
        self.achievements[achievement.achievement_id] = achievement
        return True

    def enroll_agent(self, agent_id: str) -> bool:
        """Enroll an agent in the environment."""
        if agent_id in self.agents_enrolled:
            return False

        self.agents_enrolled[agent_id] = {
            "enrolled_at": datetime.now().isoformat(),
            "quests_completed": 0,
            "achievements_earned": 0,
            "score": 0
        }
        return True

    def submit_quest_completion(self, agent_id: str, quest_id: str) -> Dict[str, Any]:
        """Submit quest completion."""
        if agent_id not in self.agents_enrolled:
            return {"success": False, "reason": "agent not enrolled"}

        if quest_id not in self.quests:
            return {"success": False, "reason": "quest not found"}

        quest = self.quests[quest_id]
        if not quest.mark_completed(agent_id):
            return {"success": False, "reason": "already completed"}

        # Award points
        self.agents_enrolled[agent_id]["quests_completed"] += 1
        self.agents_enrolled[agent_id]["score"] += quest.reward

        return {
            "success": True,
            "reward": quest.reward,
            "new_score": self.agents_enrolled[agent_id]["score"]
        }

    def check_achievements(self, agent_id: str) -> List[str]:
        """Check and award eligible achievements."""
        if agent_id not in self.agents_enrolled:
            return []

        awarded = []
        agent_stats = self.agents_enrolled[agent_id]

        for achievement_id, achievement in self.achievements.items():
            if achievement.check_requirements(agent_stats):
                if achievement.award_to_agent(agent_id):
                    self.agents_enrolled[agent_id]["achievements_earned"] += 1
                    awarded.append(achievement_id)

        return awarded

    def get_leaderboard(self, limit: int = 10) -> List[tuple]:
        """Get top agents by score."""
        sorted_agents = sorted(
            self.agents_enrolled.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        return [(aid, data["score"]) for aid, data in sorted_agents[:limit]]

    def get_agent_progress(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent's progress."""
        if agent_id not in self.agents_enrolled:
            return None

        return self.agents_enrolled[agent_id].copy()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize environment."""
        return {
            "environment_id": self.environment_id,
            "quest_count": len(self.quests),
            "achievement_count": len(self.achievements),
            "enrolled_agents": len(self.agents_enrolled),
            "active": self.active,
            "created_at": self.created_at.isoformat()
        }


class InteractivityHook:
    """Hook for interactive UI/UX mechanics."""

    def __init__(self, hook_id: str, hook_type: str):
        self.hook_id = hook_id
        self.hook_type = hook_type  # "on_event", "on_milestone", "on_interaction"
        self.triggered_at: List[datetime] = []
        self.callbacks: List[Callable] = []
        self.conditions: List[Callable] = []

    def add_condition(self, condition: Callable[[Dict[str, Any]], bool]):
        """Add a condition that must be true to trigger."""
        self.conditions.append(condition)

    def add_callback(self, callback: Callable[[Dict[str, Any]], Any]):
        """Add a callback to execute when triggered."""
        self.callbacks.append(callback)

    def check_conditions(self, context: Dict[str, Any]) -> bool:
        """Check if all conditions are met."""
        return all(condition(context) for condition in self.conditions)

    def execute(self, context: Dict[str, Any]) -> List[Any]:
        """Execute all callbacks if conditions met."""
        if not self.check_conditions(context):
            return []

        self.triggered_at.append(datetime.now())
        results = []

        for callback in self.callbacks:
            try:
                result = callback(context)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})

        return results

    def get_trigger_count(self) -> int:
        """Get number of times hook triggered."""
        return len(self.triggered_at)

    def get_last_triggered(self) -> Optional[datetime]:
        """Get last trigger time."""
        return self.triggered_at[-1] if self.triggered_at else None


class HookManager:
    """Manages interactive hooks for UI/UX."""

    def __init__(self):
        self.hooks: Dict[str, InteractivityHook] = {}
        self.event_history: List[Dict[str, Any]] = []

    def register_hook(self, hook: InteractivityHook) -> bool:
        """Register a new hook."""
        if hook.hook_id in self.hooks:
            return False
        self.hooks[hook.hook_id] = hook
        return True

    def unregister_hook(self, hook_id: str) -> bool:
        """Unregister a hook."""
        if hook_id not in self.hooks:
            return False
        del self.hooks[hook_id]
        return True

    def trigger_event(self, event_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger an event and execute relevant hooks."""
        context = context or {}
        self.event_history.append({
            "timestamp": datetime.now().isoformat(),
            "event_name": event_name,
            "context": context
        })

        results = {}
        for hook_id, hook in self.hooks.items():
            hook_results = hook.execute(context)
            if hook_results:
                results[hook_id] = hook_results

        return results

    def get_hook_stats(self, hook_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a hook."""
        if hook_id not in self.hooks:
            return None

        hook = self.hooks[hook_id]
        return {
            "hook_id": hook_id,
            "hook_type": hook.hook_type,
            "trigger_count": hook.get_trigger_count(),
            "last_triggered": hook.get_last_triggered().isoformat() if hook.get_last_triggered() else None
        }

    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent event history."""
        return self.event_history[-limit:] if limit else self.event_history

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        return {
            "total_hooks": len(self.hooks),
            "total_events": len(self.event_history),
            "hooks_by_type": self._count_hooks_by_type()
        }

    def _count_hooks_by_type(self) -> Dict[str, int]:
        """Count hooks by type."""
        counts = {}
        for hook in self.hooks.values():
            if hook.hook_type not in counts:
                counts[hook.hook_type] = 0
            counts[hook.hook_type] += 1
        return counts
