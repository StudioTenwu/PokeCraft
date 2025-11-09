"""
Round 19: Quest & Achievement System

Enable guided progression through quests that unlock capabilities and 
foster specific learning objectives. Achievements celebrate milestones 
and provide narrative arcs for player development.

Key concepts:
- Quest types with learning objectives
- Achievement tiers and progression
- Quest chains and dependencies
- Reward systems
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set


class QuestType(Enum):
    """Types of quests available"""
    TUTORIAL = "tutorial"  # Learning basics
    EXPLORATION = "exploration"  # Discover features
    MASTERY = "mastery"  # Develop skills
    CHALLENGE = "challenge"  # Test abilities
    COLLABORATION = "collaboration"  # Work with others
    CREATIVE = "creative"  # Make something


class QuestStatus(Enum):
    """Quest progression status"""
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class AchievementTier(Enum):
    """Achievement difficulty levels"""
    BRONZE = "bronze"  # Easy (10% of players)
    SILVER = "silver"  # Medium (40% of players)
    GOLD = "gold"  # Hard (80% of players)
    PLATINUM = "platinum"  # Expert (99% of players)


@dataclass
class Objective:
    """Individual objective within a quest"""
    objective_id: str
    description: str
    progress: float = 0.0  # 0.0-1.0
    target: float = 1.0  # Target completion
    completed: bool = False

    def advance_progress(self, amount: float = 0.1) -> bool:
        """Advance objective progress"""
        if self.completed:
            return False
        self.progress = min(self.target, self.progress + amount)
        if self.progress >= self.target:
            self.completed = True
        return True

    def to_dict(self) -> Dict:
        return {
            "objective_id": self.objective_id,
            "description": self.description,
            "progress": self.progress,
            "completed": self.completed
        }


@dataclass
class Quest:
    """A quest with objectives and rewards"""
    quest_id: str
    title: str
    description: str
    quest_type: QuestType
    status: QuestStatus = QuestStatus.AVAILABLE
    objectives: List[Objective] = field(default_factory=list)
    rewards: Dict[str, float] = field(default_factory=dict)  # skill_name → amount
    experience_reward: float = 100.0
    prerequisites: List[str] = field(default_factory=list)  # quest_ids
    difficulty: int = 1  # 1-5

    def start_quest(self) -> bool:
        """Start the quest"""
        if self.status != QuestStatus.AVAILABLE:
            return False
        self.status = QuestStatus.IN_PROGRESS
        return True

    def check_completion(self) -> bool:
        """Check if all objectives complete"""
        if not self.objectives:
            return False
        return all(obj.completed for obj in self.objectives)

    def complete_quest(self) -> bool:
        """Mark quest complete"""
        if not self.check_completion():
            return False
        self.status = QuestStatus.COMPLETED
        return True

    def abandon_quest(self) -> bool:
        """Abandon the quest"""
        if self.status == QuestStatus.COMPLETED:
            return False
        self.status = QuestStatus.ABANDONED
        return True

    def get_progress_percentage(self) -> float:
        """Get overall quest progress (0.0-1.0)"""
        if not self.objectives:
            return 0.0
        total_progress = sum(obj.progress for obj in self.objectives)
        return total_progress / len(self.objectives)

    def to_dict(self) -> Dict:
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "status": self.status.value,
            "progress": self.get_progress_percentage(),
            "difficulty": self.difficulty
        }


@dataclass
class Achievement:
    """An achievement/badge earned by player"""
    achievement_id: str
    title: str
    description: str
    tier: AchievementTier
    unlock_condition: str  # Description of how to unlock
    points: int = 10  # Achievement points
    unlocked: bool = False
    unlock_date: float = 0.0
    rarity: float = 0.5  # 0.0-1.0 (lower = rarer)

    def unlock_achievement(self) -> bool:
        """Unlock this achievement"""
        if self.unlocked:
            return False
        self.unlocked = True
        return True

    def to_dict(self) -> Dict:
        return {
            "achievement_id": self.achievement_id,
            "title": self.title,
            "tier": self.tier.value,
            "unlocked": self.unlocked,
            "points": self.points,
            "rarity": self.rarity
        }


@dataclass
class QuestChain:
    """A series of connected quests"""
    chain_id: str
    chain_name: str
    quests: List[str] = field(default_factory=list)  # quest_ids in order
    current_index: int = 0
    completed: bool = False

    def get_current_quest_id(self) -> Optional[str]:
        """Get current quest in chain"""
        if self.current_index < len(self.quests):
            return self.quests[self.current_index]
        return None

    def advance_to_next(self) -> bool:
        """Move to next quest in chain"""
        if self.completed:
            return False
        self.current_index += 1
        if self.current_index >= len(self.quests):
            self.completed = True
        return True

    def get_progress(self) -> float:
        """Get chain progress (0.0-1.0)"""
        if not self.quests:
            return 0.0
        return self.current_index / len(self.quests)

    def to_dict(self) -> Dict:
        return {
            "chain_id": self.chain_id,
            "chain_name": self.chain_name,
            "progress": self.get_progress(),
            "completed": self.completed
        }


class QuestManager:
    """Manage quests and achievements for a player"""

    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: Set[str] = set()
        self.completed_quests: Set[str] = set()
        self.achievements: Dict[str, Achievement] = {}
        self.quest_chains: Dict[str, QuestChain] = {}
        self.total_experience: float = 0.0
        self.achievement_points: int = 0

    def register_quest(self, quest: Quest) -> bool:
        """Register a new quest"""
        if quest.quest_id in self.quests:
            return False
        self.quests[quest.quest_id] = quest
        return True

    def register_achievement(self, achievement: Achievement) -> bool:
        """Register a new achievement"""
        if achievement.achievement_id in self.achievements:
            return False
        self.achievements[achievement.achievement_id] = achievement
        return True

    def accept_quest(self, quest_id: str) -> bool:
        """Accept a quest"""
        if quest_id not in self.quests:
            return False
        quest = self.quests[quest_id]
        if not quest.start_quest():
            return False
        self.active_quests.add(quest_id)
        return True

    def advance_objective(self, quest_id: str, objective_id: str, amount: float = 0.1) -> bool:
        """Advance a quest objective"""
        if quest_id not in self.active_quests:
            return False
        quest = self.quests[quest_id]
        for obj in quest.objectives:
            if obj.objective_id == objective_id:
                return obj.advance_progress(amount)
        return False

    def complete_quest(self, quest_id: str) -> bool:
        """Complete a quest"""
        if quest_id not in self.active_quests:
            return False
        quest = self.quests[quest_id]
        if not quest.complete_quest():
            return False
        self.active_quests.discard(quest_id)
        self.completed_quests.add(quest_id)
        self.total_experience += quest.experience_reward
        return True

    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement"""
        if achievement_id not in self.achievements:
            return False
        achievement = self.achievements[achievement_id]
        if not achievement.unlock_achievement():
            return False
        self.achievement_points += achievement.points
        return True

    def create_quest_chain(self, chain: QuestChain) -> bool:
        """Create a quest chain"""
        if chain.chain_id in self.quest_chains:
            return False
        self.quest_chains[chain.chain_id] = chain
        return True

    def get_active_quest_count(self) -> int:
        """Get number of active quests"""
        return len(self.active_quests)

    def get_unlocked_achievement_count(self) -> int:
        """Get number of unlocked achievements"""
        return sum(1 for a in self.achievements.values() if a.unlocked)

    def to_dict(self) -> Dict:
        return {
            "active_quests": len(self.active_quests),
            "completed_quests": len(self.completed_quests),
            "total_experience": self.total_experience,
            "achievements_unlocked": self.get_unlocked_achievement_count(),
            "achievement_points": self.achievement_points
        }


# ===== Tests =====

def test_objective_creation():
    """Test creating objectives"""
    obj = Objective(objective_id="obj_001", description="Complete first task")
    assert obj.objective_id == "obj_001"
    assert obj.progress == 0.0
    assert obj.completed is False


def test_objective_progress():
    """Test advancing objective progress"""
    obj = Objective(objective_id="obj_001", description="Learn skill", target=1.0)
    assert obj.advance_progress(0.25) is True
    assert obj.progress == 0.25
    assert obj.advance_progress(0.75) is True
    assert obj.progress == 1.0
    assert obj.completed is True


def test_quest_creation():
    """Test creating a quest"""
    quest = Quest(
        quest_id="quest_001",
        title="Learn Perception",
        description="Unlock perception modalities",
        quest_type=QuestType.TUTORIAL
    )
    assert quest.quest_id == "quest_001"
    assert quest.status == QuestStatus.AVAILABLE


def test_quest_lifecycle():
    """Test quest start and completion"""
    obj = Objective(objective_id="obj_001", description="Task 1")
    quest = Quest(
        quest_id="quest_001",
        title="First Quest",
        description="Get started",
        quest_type=QuestType.TUTORIAL,
        objectives=[obj]
    )
    
    assert quest.start_quest() is True
    assert quest.status == QuestStatus.IN_PROGRESS
    
    obj.advance_progress(1.0)
    assert quest.check_completion() is True
    assert quest.complete_quest() is True
    assert quest.status == QuestStatus.COMPLETED


def test_quest_progress_percentage():
    """Test calculating quest progress"""
    objs = [
        Objective(objective_id="obj_001", description="Task 1"),
        Objective(objective_id="obj_002", description="Task 2"),
        Objective(objective_id="obj_003", description="Task 3")
    ]
    quest = Quest(
        quest_id="quest_001",
        title="Multi-Objective Quest",
        description="Complete multiple tasks",
        quest_type=QuestType.CHALLENGE,
        objectives=objs
    )
    
    objs[0].advance_progress(1.0)  # 33% complete
    assert abs(quest.get_progress_percentage() - 0.333) < 0.01


def test_quest_abandonment():
    """Test abandoning a quest"""
    quest = Quest(
        quest_id="quest_001",
        title="Tough Quest",
        description="Too hard",
        quest_type=QuestType.CHALLENGE
    )
    quest.start_quest()
    assert quest.abandon_quest() is True
    assert quest.status == QuestStatus.ABANDONED


def test_achievement_creation():
    """Test creating achievements"""
    achievement = Achievement(
        achievement_id="ach_001",
        title="First Steps",
        description="Complete first quest",
        tier=AchievementTier.BRONZE,
        unlock_condition="Complete any quest"
    )
    assert achievement.achievement_id == "ach_001"
    assert achievement.unlocked is False


def test_achievement_unlock():
    """Test unlocking achievements"""
    achievement = Achievement(
        achievement_id="ach_001",
        title="Explorer",
        description="Discover 5 features",
        tier=AchievementTier.SILVER,
        unlock_condition="Unlock 5 modalities",
        points=25
    )
    assert achievement.unlock_achievement() is True
    assert achievement.unlocked is True


def test_quest_chain_creation():
    """Test quest chains"""
    chain = QuestChain(
        chain_id="chain_001",
        chain_name="Basic Training",
        quests=["quest_001", "quest_002", "quest_003"]
    )
    assert chain.get_current_quest_id() == "quest_001"
    assert chain.get_progress() == 0.0


def test_quest_chain_progression():
    """Test advancing through quest chain"""
    chain = QuestChain(
        chain_id="chain_001",
        chain_name="Story Arc",
        quests=["quest_001", "quest_002"]
    )
    
    assert chain.advance_to_next() is True
    assert chain.current_index == 1
    assert chain.get_progress() == 0.5
    
    assert chain.advance_to_next() is True
    assert chain.completed is True


def test_quest_manager_initialization():
    """Test quest manager creation"""
    manager = QuestManager()
    assert manager.get_active_quest_count() == 0
    assert manager.total_experience == 0.0


def test_quest_manager_register():
    """Test registering quests and achievements"""
    manager = QuestManager()
    quest = Quest(
        quest_id="q1",
        title="Tutorial",
        description="Learn basics",
        quest_type=QuestType.TUTORIAL
    )
    assert manager.register_quest(quest) is True

    achievement = Achievement(
        achievement_id="a1",
        title="Starter",
        description="Start playing",
        tier=AchievementTier.BRONZE,
        unlock_condition="Start the game"
    )
    assert manager.register_achievement(achievement) is True


def test_quest_manager_accept_quest():
    """Test accepting quests"""
    manager = QuestManager()
    quest = Quest(
        quest_id="q1",
        title="Test Quest",
        description="Test",
        quest_type=QuestType.TUTORIAL
    )
    manager.register_quest(quest)
    
    assert manager.accept_quest("q1") is True
    assert manager.get_active_quest_count() == 1


def test_quest_manager_complete_quest():
    """Test completing quests"""
    manager = QuestManager()
    obj = Objective(objective_id="obj1", description="Do it")
    quest = Quest(
        quest_id="q1",
        title="Simple Quest",
        description="Easy",
        quest_type=QuestType.TUTORIAL,
        objectives=[obj],
        experience_reward=50.0
    )
    manager.register_quest(quest)
    manager.accept_quest("q1")
    
    # Complete objective
    obj.completed = True
    
    assert manager.complete_quest("q1") is True
    assert manager.total_experience == 50.0
    assert len(manager.completed_quests) == 1


def test_quest_manager_achievements():
    """Test unlocking achievements"""
    manager = QuestManager()
    ach = Achievement(
        achievement_id="a1",
        title="First",
        description="First achievement",
        tier=AchievementTier.BRONZE,
        unlock_condition="Do something",
        points=10
    )
    manager.register_achievement(ach)
    
    assert manager.unlock_achievement("a1") is True
    assert manager.achievement_points == 10
    assert manager.get_unlocked_achievement_count() == 1


def test_complete_quest_workflow():
    """Test complete quest workflow"""
    manager = QuestManager()
    
    # Create quest with objectives
    objectives = [
        Objective(objective_id="obj1", description="Learn"),
        Objective(objective_id="obj2", description="Practice")
    ]
    quest = Quest(
        quest_id="q1",
        title="Learning Quest",
        description="Master a skill",
        quest_type=QuestType.MASTERY,
        objectives=objectives,
        experience_reward=100.0,
        difficulty=2
    )
    
    # Create achievement
    achievement = Achievement(
        achievement_id="a1",
        title="Learner",
        description="Complete learning quest",
        tier=AchievementTier.SILVER,
        unlock_condition="Complete mastery quest",
        points=50
    )
    
    # Register and play
    manager.register_quest(quest)
    manager.register_achievement(achievement)
    manager.accept_quest("q1")
    
    # Complete objectives
    for obj in objectives:
        obj.advance_progress(1.0)
    
    # Complete quest and unlock achievement
    assert manager.complete_quest("q1") is True
    assert manager.unlock_achievement("a1") is True
    
    # Verify state
    assert manager.total_experience == 100.0
    assert manager.achievement_points == 50
    assert manager.get_active_quest_count() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
