"""
Round 24: Player-Agent Synchronization System

Enable players and agents to grow together through shared learning,
asymmetric skill transfer, and parallel development paths.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class SkillCategory(Enum):
    """Categories of learnable skills"""
    REASONING = "reasoning"
    CREATIVITY = "creativity"
    EMPATHY = "empathy"
    TECHNICAL = "technical"
    COMMUNICATION = "communication"
    PERCEPTION = "perception"


class SyncMode(Enum):
    """How player and agent learning is synchronized"""
    MIRRORED = "mirrored"  # Player and agent learn identical skills
    COMPLEMENTARY = "complementary"  # Player learns what agent struggles with
    ASYMMETRIC = "asymmetric"  # Agent learns faster than player in some areas


@dataclass
class Skill:
    """Individual learnable skill"""
    skill_id: str
    category: SkillCategory
    name: str
    proficiency: float = 0.0  # 0.0-1.0
    mastery_level: int = 0  # 0-10
    practice_hours: int = 0
    last_practiced: int = 0  # timestamp-like counter

    def practice(self, amount: float = 0.1) -> bool:
        """Increase proficiency through practice"""
        if self.proficiency >= 1.0:
            return False
        self.proficiency = min(1.0, self.proficiency + amount)
        self.practice_hours += 1
        self.last_practiced += 1
        if self.proficiency >= 1.0 and self.mastery_level < 10:
            self.mastery_level += 1
            self.proficiency = 0.0  # Start new mastery level
        return True

    def to_dict(self) -> Dict:
        return {
            "skill_id": self.skill_id,
            "category": self.category.value,
            "name": self.name,
            "proficiency": self.proficiency,
            "mastery_level": self.mastery_level,
            "practice_hours": self.practice_hours
        }


@dataclass
class Player:
    """Player entity with learnable skills"""
    player_id: str
    level: int = 1
    experience: float = 0.0  # 0.0-1.0
    skills: Dict[str, Skill] = field(default_factory=dict)
    agent_affinity: float = 0.5  # How well player understands their agent (0.0-1.0)
    learning_style: str = "balanced"

    def acquire_skill(self, skill: Skill) -> bool:
        """Learn a new skill"""
        if skill.skill_id in self.skills:
            return False
        self.skills[skill.skill_id] = skill
        return True

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get skill by ID"""
        return self.skills.get(skill_id)

    def practice_skill(self, skill_id: str, amount: float = 0.1) -> bool:
        """Practice a skill"""
        if skill_id not in self.skills:
            return False
        return self.skills[skill_id].practice(amount)

    def gain_experience(self, amount: float) -> bool:
        """Gain experience points"""
        if self.experience >= 1.0:
            return False
        self.experience = min(1.0, self.experience + amount)
        if self.experience >= 1.0:
            self.level += 1
            self.experience = 0.0
        return True

    def improve_agent_affinity(self, amount: float) -> bool:
        """Improve understanding of agent"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.agent_affinity = min(1.0, self.agent_affinity + amount)
        return True

    def to_dict(self) -> Dict:
        return {
            "player_id": self.player_id,
            "level": self.level,
            "experience": self.experience,
            "agent_affinity": self.agent_affinity,
            "skills": {k: v.to_dict() for k, v in self.skills.items()}
        }


@dataclass
class Agent:
    """Agent entity with learnable skills"""
    agent_id: str
    level: int = 1
    experience: float = 0.0  # 0.0-1.0
    skills: Dict[str, Skill] = field(default_factory=dict)
    player_affinity: float = 0.5  # Trust in player guidance (0.0-1.0)
    learning_speed: float = 1.0  # 0.5-2.0

    def acquire_skill(self, skill: Skill) -> bool:
        """Learn a new skill"""
        if skill.skill_id in self.skills:
            return False
        self.skills[skill.skill_id] = skill
        return True

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get skill by ID"""
        return self.skills.get(skill_id)

    def practice_skill(self, skill_id: str, amount: float = 0.1) -> bool:
        """Practice a skill with learning speed modifier"""
        if skill_id not in self.skills:
            return False
        skill = self.skills[skill_id]
        # Agent learns faster based on learning_speed multiplier
        return skill.practice(amount * self.learning_speed)

    def gain_experience(self, amount: float) -> bool:
        """Gain experience (affected by learning speed)"""
        if self.experience >= 1.0:
            return False
        exp_gain = min(1.0, amount * self.learning_speed)
        self.experience = min(1.0, self.experience + exp_gain)
        if self.experience >= 1.0:
            self.level += 1
            self.experience = 0.0
        return True

    def update_player_affinity(self, amount: float) -> bool:
        """Update trust in player"""
        if not (-0.2 <= amount <= 0.2):  # Bounded updates
            return False
        self.player_affinity = max(0.0, min(1.0, self.player_affinity + amount))
        return True

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "level": self.level,
            "experience": self.experience,
            "player_affinity": self.player_affinity,
            "skills": {k: v.to_dict() for k, v in self.skills.items()}
        }


@dataclass
class SyncEvent:
    """Record of synchronization between player and agent"""
    event_id: str
    player_id: str
    agent_id: str
    skill_id: str
    direction: str  # "player_to_agent" or "agent_to_player"
    effectiveness: float = 0.5  # 0.0-1.0
    timestamp: int = 0

    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "player_id": self.player_id,
            "agent_id": self.agent_id,
            "skill_id": self.skill_id,
            "direction": self.direction,
            "effectiveness": self.effectiveness
        }


class SynchronizationSystem:
    """Manage player-agent synchronization and parallel growth"""

    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.agents: Dict[str, Agent] = {}
        self.pairings: Dict[str, str] = {}  # player_id → agent_id
        self.sync_events: List[SyncEvent] = []
        self.sync_mode: SyncMode = SyncMode.MIRRORED

    def register_player(self, player: Player) -> bool:
        """Register a player"""
        if player.player_id in self.players:
            return False
        self.players[player.player_id] = player
        return True

    def register_agent(self, agent: Agent) -> bool:
        """Register an agent"""
        if agent.agent_id in self.agents:
            return False
        self.agents[agent.agent_id] = agent
        return True

    def pair_player_agent(self, player_id: str, agent_id: str) -> bool:
        """Create player-agent pairing"""
        if player_id not in self.players or agent_id not in self.agents:
            return False
        if player_id in self.pairings:
            return False
        self.pairings[player_id] = agent_id
        return True

    def transfer_skill_player_to_agent(self, player_id: str, skill_id: str) -> bool:
        """Player teaches skill to agent"""
        if player_id not in self.pairings:
            return False

        player = self.players[player_id]
        agent_id = self.pairings[player_id]
        agent = self.agents[agent_id]

        if skill_id not in player.skills:
            return False

        player_skill = player.skills[skill_id]

        # Agent can only learn what player has proficiency in or mastery of
        if player_skill.proficiency < 0.5 and player_skill.mastery_level < 1:
            return False

        # Create new skill for agent if not exists
        if skill_id not in agent.skills:
            new_skill = Skill(
                skill_id=skill_id,
                category=player_skill.category,
                name=player_skill.name,
                proficiency=player_skill.proficiency * agent.learning_speed
            )
            agent.acquire_skill(new_skill)
        else:
            # Boost existing skill
            agent.skills[skill_id].proficiency = min(
                1.0,
                agent.skills[skill_id].proficiency + (0.1 * agent.learning_speed)
            )

        # Record event
        event = SyncEvent(
            event_id=f"sync_{len(self.sync_events)}",
            player_id=player_id,
            agent_id=agent_id,
            skill_id=skill_id,
            direction="player_to_agent",
            effectiveness=player_skill.proficiency * agent.player_affinity
        )
        self.sync_events.append(event)

        # Improve agent's affinity with player
        agent.update_player_affinity(0.05)

        return True

    def transfer_skill_agent_to_player(self, player_id: str, skill_id: str) -> bool:
        """Agent assists player with skill"""
        if player_id not in self.pairings:
            return False

        player = self.players[player_id]
        agent_id = self.pairings[player_id]
        agent = self.agents[agent_id]

        if skill_id not in agent.skills:
            return False

        agent_skill = agent.skills[skill_id]

        # Create new skill for player if not exists
        if skill_id not in player.skills:
            new_skill = Skill(
                skill_id=skill_id,
                category=agent_skill.category,
                name=agent_skill.name,
                proficiency=agent_skill.proficiency * 0.7  # Slower for player
            )
            player.acquire_skill(new_skill)
        else:
            # Boost existing skill
            player.skills[skill_id].proficiency = min(
                1.0,
                player.skills[skill_id].proficiency + 0.15
            )

        # Record event
        event = SyncEvent(
            event_id=f"sync_{len(self.sync_events)}",
            player_id=player_id,
            agent_id=agent_id,
            skill_id=skill_id,
            direction="agent_to_player",
            effectiveness=agent_skill.proficiency * player.agent_affinity
        )
        self.sync_events.append(event)

        # Improve player's affinity with agent
        player.improve_agent_affinity(0.05)

        return True

    def get_player_agent_pair(self, player_id: str) -> Tuple[Optional[Player], Optional[Agent]]:
        """Get player and their paired agent"""
        if player_id not in self.pairings:
            return None, None
        player = self.players.get(player_id)
        agent = self.agents.get(self.pairings[player_id])
        return player, agent

    def get_synchronization_health(self, player_id: str) -> Dict:
        """Get health metrics for player-agent synchronization"""
        player, agent = self.get_player_agent_pair(player_id)
        if player is None or agent is None:
            return {}

        return {
            "player_level": player.level,
            "agent_level": agent.level,
            "player_affinity_with_agent": player.agent_affinity,
            "agent_affinity_with_player": agent.player_affinity,
            "shared_skills": len(set(player.skills.keys()) & set(agent.skills.keys())),
            "total_sync_events": len([e for e in self.sync_events if e.player_id == player_id])
        }

    def get_skill_alignment(self, player_id: str, skill_id: str) -> float:
        """Calculate how well player and agent are aligned on a skill (0.0-1.0)"""
        player, agent = self.get_player_agent_pair(player_id)
        if player is None or agent is None:
            return 0.0

        if skill_id not in player.skills or skill_id not in agent.skills:
            return 0.0

        player_prof = player.skills[skill_id].proficiency
        agent_prof = agent.skills[skill_id].proficiency

        # Perfect alignment = 1.0, complete divergence = 0.0
        alignment = 1.0 - abs(player_prof - agent_prof)
        return alignment


# ===== Tests =====

def test_player_creation():
    """Test creating players"""
    player = Player(player_id="p1")
    assert player.player_id == "p1"
    assert player.level == 1
    assert player.experience == 0.0


def test_agent_creation():
    """Test creating agents"""
    agent = Agent(agent_id="a1")
    assert agent.agent_id == "a1"
    assert agent.level == 1
    assert agent.learning_speed == 1.0


def test_skill_creation():
    """Test creating skills"""
    skill = Skill(skill_id="s1", category=SkillCategory.REASONING, name="Logic")
    assert skill.proficiency == 0.0
    assert skill.mastery_level == 0


def test_skill_practice():
    """Test practicing a skill"""
    skill = Skill(skill_id="s1", category=SkillCategory.CREATIVITY, name="Ideation")
    assert skill.practice(0.2) is True
    assert skill.proficiency == 0.2
    assert skill.practice_hours == 1


def test_skill_mastery():
    """Test reaching mastery level"""
    skill = Skill(skill_id="s1", category=SkillCategory.REASONING, name="Logic")
    for _ in range(11):
        skill.practice(0.1)
    assert skill.mastery_level >= 1
    assert skill.proficiency < 0.15


def test_player_acquire_skill():
    """Test player acquiring a skill"""
    player = Player(player_id="p1")
    skill = Skill(skill_id="s1", category=SkillCategory.CREATIVITY, name="Writing")
    assert player.acquire_skill(skill) is True
    assert player.get_skill("s1") is not None


def test_agent_acquire_skill():
    """Test agent acquiring a skill"""
    agent = Agent(agent_id="a1")
    skill = Skill(skill_id="s1", category=SkillCategory.TECHNICAL, name="Coding")
    assert agent.acquire_skill(skill) is True
    assert agent.get_skill("s1") is not None


def test_player_experience():
    """Test player gaining experience"""
    player = Player(player_id="p1")
    assert player.gain_experience(0.5) is True
    assert player.experience == 0.5
    assert player.level == 1


def test_player_level_up():
    """Test player leveling up"""
    player = Player(player_id="p1")
    assert player.gain_experience(0.6) is True
    assert player.gain_experience(0.5) is True
    assert player.level == 2


def test_agent_learning_speed():
    """Test agent learns faster with learning_speed multiplier"""
    agent = Agent(agent_id="a1", learning_speed=2.0)
    skill = Skill(skill_id="s1", category=SkillCategory.REASONING, name="Logic")
    agent.acquire_skill(skill)

    agent.practice_skill("s1", 0.1)
    assert agent.skills["s1"].proficiency == 0.2  # 0.1 * 2.0


def test_pairing_player_agent():
    """Test pairing player with agent"""
    system = SynchronizationSystem()
    player = Player(player_id="p1")
    agent = Agent(agent_id="a1")

    system.register_player(player)
    system.register_agent(agent)

    assert system.pair_player_agent("p1", "a1") is True


def test_transfer_skill_player_to_agent():
    """Test player teaching skill to agent"""
    system = SynchronizationSystem()
    player = Player(player_id="p1")
    agent = Agent(agent_id="a1")

    system.register_player(player)
    system.register_agent(agent)
    system.pair_player_agent("p1", "a1")

    # Player needs mastery to teach
    skill = Skill(skill_id="s1", category=SkillCategory.CREATIVITY, name="Art")
    skill.mastery_level = 2
    player.acquire_skill(skill)

    assert system.transfer_skill_player_to_agent("p1", "s1") is True
    assert agent.get_skill("s1") is not None


def test_transfer_skill_agent_to_player():
    """Test agent helping player with skill"""
    system = SynchronizationSystem()
    player = Player(player_id="p1")
    agent = Agent(agent_id="a1")

    system.register_player(player)
    system.register_agent(agent)
    system.pair_player_agent("p1", "a1")

    # Agent has skill
    skill = Skill(skill_id="s1", category=SkillCategory.TECHNICAL, name="Math")
    skill.proficiency = 0.8
    agent.acquire_skill(skill)

    assert system.transfer_skill_agent_to_player("p1", "s1") is True
    assert player.get_skill("s1") is not None


def test_affinity_improvements():
    """Test affinity improves with skill transfer"""
    system = SynchronizationSystem()
    player = Player(player_id="p1")
    agent = Agent(agent_id="a1")

    system.register_player(player)
    system.register_agent(agent)
    system.pair_player_agent("p1", "a1")

    initial_agent_affinity = agent.player_affinity

    skill = Skill(skill_id="s1", category=SkillCategory.REASONING, name="Logic")
    skill.mastery_level = 2
    player.acquire_skill(skill)

    system.transfer_skill_player_to_agent("p1", "s1")

    assert agent.player_affinity > initial_agent_affinity


def test_synchronization_health():
    """Test getting synchronization health metrics"""
    system = SynchronizationSystem()
    player = Player(player_id="p1")
    agent = Agent(agent_id="a1")

    system.register_player(player)
    system.register_agent(agent)
    system.pair_player_agent("p1", "a1")

    health = system.get_synchronization_health("p1")
    assert "player_level" in health
    assert "agent_level" in health
    assert "shared_skills" in health


def test_skill_alignment():
    """Test calculating skill alignment between player and agent"""
    system = SynchronizationSystem()
    player = Player(player_id="p1")
    agent = Agent(agent_id="a1")

    system.register_player(player)
    system.register_agent(agent)
    system.pair_player_agent("p1", "a1")

    skill = Skill(skill_id="s1", category=SkillCategory.CREATIVITY, name="Art")
    skill.proficiency = 0.8
    player.acquire_skill(skill)
    agent.acquire_skill(Skill(skill_id="s1", category=SkillCategory.CREATIVITY, name="Art", proficiency=0.7))

    alignment = system.get_skill_alignment("p1", "s1")
    assert 0.0 <= alignment <= 1.0
    assert alignment > 0.8  # Close proficiencies = high alignment


def test_complete_sync_workflow():
    """Test complete player-agent synchronization workflow"""
    system = SynchronizationSystem()

    # Create and register player
    player = Player(player_id="player_001")
    system.register_player(player)

    # Create and register agent
    agent = Agent(agent_id="agent_001", learning_speed=1.5)
    system.register_agent(agent)

    # Pair them
    assert system.pair_player_agent("player_001", "agent_001") is True

    # Player learns reasoning skill
    reasoning_skill = Skill(
        skill_id="logic_001",
        category=SkillCategory.REASONING,
        name="Critical Thinking"
    )
    player.acquire_skill(reasoning_skill)

    # Player practices to mastery
    for _ in range(10):
        player.practice_skill("logic_001", 0.1)

    # Player teaches agent
    assert system.transfer_skill_player_to_agent("player_001", "logic_001") is True

    # Agent practices and gets ahead
    for _ in range(5):
        agent.practice_skill("logic_001", 0.15)

    # Agent helps player with technical skill
    tech_skill = Skill(
        skill_id="code_001",
        category=SkillCategory.TECHNICAL,
        name="Programming"
    )
    tech_skill.proficiency = 0.6
    agent.acquire_skill(tech_skill)

    assert system.transfer_skill_agent_to_player("player_001", "code_001") is True

    # Check health
    health = system.get_synchronization_health("player_001")
    assert health["shared_skills"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
