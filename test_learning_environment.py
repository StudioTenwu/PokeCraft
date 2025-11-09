"""
Test suite for Interactive Learning Environment & UI/UX Hooks (Round 10).
Tests the learning environment, quests, achievements, and interactive mechanics.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
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


class Quest:
    """A learning quest for agents."""

    def __init__(
        self, quest_id: str, title: str, description: str,
        difficulty: QuestDifficulty, reward: int = 100
    ):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.reward = reward
        self.created_at = datetime.now()
        self.completed_by: List[str] = []
        self.objectives: List[str] = []
        self.hints: List[str] = []
        self.solutions: List[Dict[str, Any]] = []

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

    def get_completion_rate(self) -> float:
        """Get completion rate (agents who completed / unique attempts)."""
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
            "completion_count": len(self.completed_by)
        }


class Achievement:
    """An achievement agents can earn."""

    def __init__(self, achievement_id: str, title: str, description: str, achievement_type: AchievementType):
        self.achievement_id = achievement_id
        self.title = title
        self.description = description
        self.achievement_type = achievement_type
        self.created_at = datetime.now()
        self.earned_by: List[str] = []
        self.requirements: Dict[str, Any] = {}

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
    """Interactive environment where agents learn."""

    def __init__(self, environment_id: str):
        self.environment_id = environment_id
        self.created_at = datetime.now()
        self.active = True
        self.quests: Dict[str, Quest] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.agents_enrolled: Dict[str, Dict[str, Any]] = {}
        self.leaderboard: List[tuple] = []  # (agent_id, score)

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
            "enrolled_at": datetime.now(),
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

    def trigger_event(self, event_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an event and execute relevant hooks."""
        self.event_history.append({
            "timestamp": datetime.now(),
            "event_name": event_name,
            "context": context
        })

        results = {}
        for hook_id, hook in self.hooks.items():
            hook_results = hook.execute(context)
            if hook_results:
                results[hook_id] = hook_results

        return results

    def get_hook_stats(self, hook_id: str) -> Dict[str, Any]:
        """Get statistics for a hook."""
        if hook_id not in self.hooks:
            return {}

        hook = self.hooks[hook_id]
        return {
            "hook_id": hook_id,
            "hook_type": hook.hook_type,
            "trigger_count": hook.get_trigger_count(),
            "last_triggered": hook.triggered_at[-1].isoformat() if hook.triggered_at else None
        }


# ===== TESTS =====

def test_quest_creation():
    """Test creating a quest."""
    quest = Quest("quest_1", "Learn Basics", "Learn agent basics", QuestDifficulty.BEGINNER, reward=50)

    assert quest.quest_id == "quest_1"
    assert quest.difficulty == QuestDifficulty.BEGINNER
    assert quest.reward == 50


def test_quest_objectives():
    """Test adding objectives to quest."""
    quest = Quest("quest_1", "Title", "Desc", QuestDifficulty.INTERMEDIATE)

    quest.add_objective("Objective 1")
    quest.add_objective("Objective 2")

    assert len(quest.objectives) == 2


def test_quest_hints_and_solutions():
    """Test adding hints and solutions."""
    quest = Quest("quest_1", "Title", "Desc", QuestDifficulty.ADVANCED)

    quest.add_hint("Try this approach...")
    quest.add_hint("Consider this alternative...")
    quest.add_solution("approach_1", "This works because...")

    assert len(quest.hints) == 2
    assert len(quest.solutions) == 1


def test_quest_completion():
    """Test marking quest as completed."""
    quest = Quest("quest_1", "Title", "Desc", QuestDifficulty.BEGINNER)

    assert quest.mark_completed("agent_1")
    assert not quest.mark_completed("agent_1")  # Can't complete twice
    assert quest.mark_completed("agent_2")
    assert len(quest.completed_by) == 2


def test_achievement_creation():
    """Test creating an achievement."""
    achievement = Achievement("ach_1", "First Steps", "Complete first quest", AchievementType.MILESTONE)

    assert achievement.achievement_id == "ach_1"
    assert achievement.achievement_type == AchievementType.MILESTONE


def test_achievement_requirements():
    """Test setting and checking requirements."""
    achievement = Achievement("ach_1", "Expert", "Become an expert", AchievementType.SKILL_MASTERY)

    achievement.set_requirement("tasks_completed", 10)
    achievement.set_requirement("skills_mastered", 5)

    # Agent meets requirements
    agent_stats = {"tasks_completed": 15, "skills_mastered": 5}
    assert achievement.check_requirements(agent_stats)

    # Agent doesn't meet requirements
    agent_stats = {"tasks_completed": 5, "skills_mastered": 2}
    assert not achievement.check_requirements(agent_stats)


def test_achievement_awarding():
    """Test awarding achievements."""
    achievement = Achievement("ach_1", "Title", "Desc", AchievementType.MILESTONE)

    assert achievement.award_to_agent("agent_1")
    assert not achievement.award_to_agent("agent_1")  # Can't award twice
    assert achievement.award_to_agent("agent_2")
    assert len(achievement.earned_by) == 2


def test_learning_environment_creation():
    """Test creating learning environment."""
    env = LearningEnvironment("env_1")

    assert env.environment_id == "env_1"
    assert env.active
    assert len(env.quests) == 0


def test_environment_enroll_agent():
    """Test enrolling agents."""
    env = LearningEnvironment("env_1")

    assert env.enroll_agent("agent_1")
    assert not env.enroll_agent("agent_1")  # Can't enroll twice
    assert env.enroll_agent("agent_2")
    assert len(env.agents_enrolled) == 2


def test_environment_quest_submission():
    """Test submitting quest completions."""
    env = LearningEnvironment("env_1")
    quest = Quest("quest_1", "Title", "Desc", QuestDifficulty.BEGINNER, reward=50)

    env.add_quest(quest)
    env.enroll_agent("agent_1")

    result = env.submit_quest_completion("agent_1", "quest_1")
    assert result["success"]
    assert result["reward"] == 50
    assert env.agents_enrolled["agent_1"]["score"] == 50


def test_environment_achievements():
    """Test achieving achievements."""
    env = LearningEnvironment("env_1")
    achievement = Achievement("ach_1", "Novice", "Start learning", AchievementType.MILESTONE)
    achievement.set_requirement("quests_completed", 1)

    env.add_achievement(achievement)
    env.enroll_agent("agent_1")

    # Agent completes 1 quest
    env.agents_enrolled["agent_1"]["quests_completed"] = 1

    awarded = env.check_achievements("agent_1")
    assert "ach_1" in awarded
    assert env.agents_enrolled["agent_1"]["achievements_earned"] == 1


def test_leaderboard():
    """Test leaderboard generation."""
    env = LearningEnvironment("env_1")

    env.enroll_agent("agent_1")
    env.agents_enrolled["agent_1"]["score"] = 500

    env.enroll_agent("agent_2")
    env.agents_enrolled["agent_2"]["score"] = 1000

    env.enroll_agent("agent_3")
    env.agents_enrolled["agent_3"]["score"] = 300

    leaderboard = env.get_leaderboard()
    assert leaderboard[0] == ("agent_2", 1000)
    assert leaderboard[1] == ("agent_1", 500)
    assert leaderboard[2] == ("agent_3", 300)


def test_interactivity_hook():
    """Test creating and triggering hooks."""
    hook = InteractivityHook("hook_1", "on_event")

    # Add condition
    hook.add_condition(lambda ctx: ctx.get("score", 0) > 100)

    # Add callback
    results = []
    hook.add_callback(lambda ctx: results.append(f"Hook triggered! Score: {ctx['score']}"))

    # Trigger with context that meets condition
    context = {"score": 150}
    hook_results = hook.execute(context)

    assert len(results) == 1
    assert hook.get_trigger_count() == 1


def test_hook_manager():
    """Test managing multiple hooks."""
    manager = HookManager()

    hook1 = InteractivityHook("hook_1", "on_event")
    hook1.add_condition(lambda ctx: ctx.get("event_type") == "achievement")
    hook1.add_callback(lambda ctx: f"Achievement unlocked!")

    hook2 = InteractivityHook("hook_2", "on_milestone")
    hook2.add_condition(lambda ctx: ctx.get("level", 0) >= 10)
    hook2.add_callback(lambda ctx: f"Milestone reached!")

    assert manager.register_hook(hook1)
    assert manager.register_hook(hook2)

    # Trigger event
    context = {"event_type": "achievement", "level": 15}
    results = manager.trigger_event("milestone_reached", context)

    assert "hook_1" in results
    assert "hook_2" in results


def test_hook_statistics():
    """Test hook statistics."""
    manager = HookManager()
    hook = InteractivityHook("hook_1", "on_event")
    hook.add_condition(lambda ctx: True)
    hook.add_callback(lambda ctx: "executed")

    manager.register_hook(hook)

    for i in range(5):
        manager.trigger_event(f"event_{i}", {})

    stats = manager.get_hook_stats("hook_1")
    assert stats["trigger_count"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
