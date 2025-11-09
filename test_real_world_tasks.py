"""
Round 32: Real-World Task Integration

Enable agents to tackle real-world problems: homework assignments, essays,
coding challenges, math problems, and creative projects. Track performance
and learning from real-world engagement.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class TaskDomain(Enum):
    """Real-world domains agents can tackle"""
    MATHEMATICS = "mathematics"
    WRITING = "writing"
    CODING = "coding"
    SCIENCE = "science"
    HISTORY = "history"
    ART = "art"
    MUSIC = "music"
    LOGIC = "logic"


class TaskDifficulty(Enum):
    """Task complexity level"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class CompletionStatus(Enum):
    """Task completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"


@dataclass
class RealWorldTask:
    """A real-world problem agents can solve"""
    task_id: str
    domain: TaskDomain
    title: str
    description: str
    difficulty: TaskDifficulty
    status: CompletionStatus = CompletionStatus.NOT_STARTED
    requirements: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    estimated_difficulty: float = 0.5  # 0.0-1.0
    time_limit: Optional[int] = None  # Minutes
    solution_quality: float = 0.0  # 0.0-1.0 after completion
    completion_time: int = 0  # Time taken

    def start(self) -> bool:
        """Begin working on task"""
        if self.status != CompletionStatus.NOT_STARTED:
            return False
        self.status = CompletionStatus.IN_PROGRESS
        return True

    def complete(self, quality: float) -> bool:
        """Mark task as completed"""
        if self.status != CompletionStatus.IN_PROGRESS:
            return False
        if not (0.0 <= quality <= 1.0):
            return False
        self.status = CompletionStatus.COMPLETED
        self.solution_quality = quality
        return True

    def fail(self) -> bool:
        """Mark task as failed"""
        if self.status != CompletionStatus.IN_PROGRESS:
            return False
        self.status = CompletionStatus.FAILED
        return True

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "domain": self.domain.value,
            "difficulty": self.difficulty.value,
            "status": self.status.value,
            "solution_quality": self.solution_quality
        }


@dataclass
class AgentPerformance:
    """Track agent's performance on tasks"""
    agent_id: str
    tasks_completed: int = 0
    tasks_attempted: int = 0
    tasks_failed: int = 0
    avg_quality: float = 0.5  # 0.0-1.0
    domain_expertise: Dict[str, float] = field(default_factory=dict)  # Domain → proficiency
    learning_rate: float = 0.5  # 0.0-1.0, how fast improves
    confidence: float = 0.5  # 0.0-1.0 in own abilities

    def attempt_task(self) -> bool:
        """Record task attempt"""
        self.tasks_attempted += 1
        return True

    def complete_task(self, quality: float, domain: str) -> bool:
        """Record completed task"""
        if not (0.0 <= quality <= 1.0):
            return False

        self.tasks_completed += 1
        self.avg_quality = (self.avg_quality * (self.tasks_completed - 1) + quality) / self.tasks_completed

        # Update domain expertise
        current_expertise = self.domain_expertise.get(domain, 0.0)
        self.domain_expertise[domain] = min(1.0, current_expertise + quality * self.learning_rate * 0.1)

        # Increase confidence with success
        self.confidence = min(1.0, self.confidence + quality * 0.05)

        return True

    def fail_task(self, domain: str) -> bool:
        """Record failed task"""
        self.tasks_failed += 1
        # Failure reduces confidence
        self.confidence = max(0.1, self.confidence - 0.1)
        return True

    def improve_learning_rate(self, amount: float = 0.1) -> bool:
        """Agent learns to learn better"""
        if not (0.0 <= amount <= 1.0):
            return False
        self.learning_rate = min(1.0, self.learning_rate + amount)
        return True

    def get_expertise_in_domain(self, domain: str) -> float:
        """Get expertise level in domain (0.0-1.0)"""
        return self.domain_expertise.get(domain, 0.0)

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.tasks_attempted == 0:
            return 0.0
        return self.tasks_completed / self.tasks_attempted

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "tasks_completed": self.tasks_completed,
            "success_rate": self.get_success_rate(),
            "avg_quality": self.avg_quality,
            "confidence": self.confidence
        }


class RealWorldTaskSystem:
    """Manage real-world tasks and agent performance"""

    def __init__(self):
        self.tasks: Dict[str, RealWorldTask] = {}
        self.agent_performances: Dict[str, AgentPerformance] = {}
        self.task_history: List[Dict] = []
        self.total_tasks_completed: int = 0
        self.average_quality_across_system: float = 0.5

    def register_agent(self, agent_id: str) -> bool:
        """Register agent for task-solving"""
        if agent_id in self.agent_performances:
            return False
        self.agent_performances[agent_id] = AgentPerformance(agent_id=agent_id)
        return True

    def create_task(self, task: RealWorldTask) -> bool:
        """Create a real-world task"""
        if task.task_id in self.tasks:
            return False
        self.tasks[task.task_id] = task
        return True

    def assign_task(self, agent_id: str, task_id: str) -> bool:
        """Assign task to agent"""
        if agent_id not in self.agent_performances or task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        performance = self.agent_performances[agent_id]

        if task.start():
            performance.attempt_task()
            return True
        return False

    def submit_solution(self, agent_id: str, task_id: str, quality: float) -> bool:
        """Agent submits solution to task"""
        if agent_id not in self.agent_performances or task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        performance = self.agent_performances[agent_id]

        if task.complete(quality):
            performance.complete_task(quality, task.domain.value)
            self.total_tasks_completed += 1

            # Update system average quality
            self.average_quality_across_system = (
                (self.average_quality_across_system * (self.total_tasks_completed - 1) + quality) /
                self.total_tasks_completed
            )

            # Log to history
            self.task_history.append({
                "agent_id": agent_id,
                "task_id": task_id,
                "domain": task.domain.value,
                "quality": quality,
                "timestamp": len(self.task_history)
            })

            return True
        return False

    def fail_task(self, agent_id: str, task_id: str) -> bool:
        """Agent gives up on task"""
        if agent_id not in self.agent_performances or task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        performance = self.agent_performances[agent_id]

        if task.fail():
            performance.fail_task(task.domain.value)
            return True
        return False

    def get_agent_performance(self, agent_id: str) -> Dict:
        """Get agent's performance metrics"""
        if agent_id not in self.agent_performances:
            return {}
        return self.agent_performances[agent_id].to_dict()

    def get_domain_leaderboard(self, domain: str) -> List[Dict]:
        """Get top agents in a domain"""
        leaderboard = []
        for perf in self.agent_performances.values():
            expertise = perf.get_expertise_in_domain(domain)
            if expertise > 0.0:
                leaderboard.append({
                    "agent_id": perf.agent_id,
                    "expertise": expertise,
                    "quality": perf.avg_quality
                })

        return sorted(leaderboard, key=lambda x: x["expertise"], reverse=True)

    def get_agent_strengths_weaknesses(self, agent_id: str) -> Dict:
        """Identify what domains agent excels in"""
        if agent_id not in self.agent_performances:
            return {}

        perf = self.agent_performances[agent_id]
        domains = perf.domain_expertise

        if not domains:
            return {"strengths": [], "weaknesses": []}

        sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
        strengths = [d[0] for d in sorted_domains[:2]]
        weaknesses = [d[0] for d in sorted_domains[-2:]]

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "top_domain_expertise": sorted_domains[0][1] if sorted_domains else 0.0
        }

    def recommend_tasks(self, agent_id: str) -> List[str]:
        """Recommend tasks based on agent's level"""
        if agent_id not in self.agent_performances:
            return []

        perf = self.agent_performances[agent_id]
        recommended = []

        # Recommend based on current success rate
        for task in self.tasks.values():
            if task.status == CompletionStatus.NOT_STARTED:
                # Recommend challenging but achievable tasks
                if perf.get_success_rate() > 0.6:
                    if task.difficulty in [TaskDifficulty.HARD, TaskDifficulty.EXPERT]:
                        recommended.append(task.task_id)
                else:
                    if task.difficulty in [TaskDifficulty.EASY, TaskDifficulty.MEDIUM]:
                        recommended.append(task.task_id)

        return recommended

    def get_system_statistics(self) -> Dict:
        """Get overall system statistics"""
        return {
            "total_tasks": len(self.tasks),
            "total_completed": self.total_tasks_completed,
            "agents_active": len(self.agent_performances),
            "average_quality": self.average_quality_across_system
        }

    def to_dict(self) -> Dict:
        return {
            "tasks": len(self.tasks),
            "agents": len(self.agent_performances),
            "completed_tasks": self.total_tasks_completed,
            "avg_quality": self.average_quality_across_system
        }


# ===== Tests =====

def test_task_creation():
    """Test creating a real-world task"""
    task = RealWorldTask(
        task_id="t1",
        domain=TaskDomain.MATHEMATICS,
        title="Algebra Problem Set",
        description="Solve 10 algebra problems",
        difficulty=TaskDifficulty.MEDIUM
    )
    assert task.domain == TaskDomain.MATHEMATICS


def test_task_lifecycle():
    """Test task from start to completion"""
    task = RealWorldTask(
        task_id="t1",
        domain=TaskDomain.WRITING,
        title="Essay",
        description="Write 500-word essay",
        difficulty=TaskDifficulty.HARD
    )
    assert task.start() is True
    assert task.status == CompletionStatus.IN_PROGRESS
    assert task.complete(0.8) is True
    assert task.solution_quality == 0.8


def test_agent_performance_tracking():
    """Test tracking agent performance"""
    perf = AgentPerformance(agent_id="a1")
    assert perf.attempt_task() is True
    assert perf.complete_task(0.9, "mathematics") is True
    assert perf.tasks_completed == 1


def test_domain_expertise():
    """Test domain expertise tracking"""
    perf = AgentPerformance(agent_id="a1")
    perf.complete_task(0.8, "coding")
    perf.complete_task(0.7, "coding")

    expertise = perf.get_expertise_in_domain("coding")
    assert expertise > 0.0


def test_success_rate():
    """Test calculating success rate"""
    perf = AgentPerformance(agent_id="a1")
    perf.attempt_task()
    perf.complete_task(0.8, "math")
    perf.attempt_task()
    perf.fail_task("science")

    rate = perf.get_success_rate()
    assert rate == 0.5


def test_learning_rate_improvement():
    """Test improving learning rate"""
    perf = AgentPerformance(agent_id="a1", learning_rate=0.5)
    assert perf.improve_learning_rate(0.2) is True
    assert perf.learning_rate == 0.7


def test_real_world_task_system():
    """Test creating task system"""
    system = RealWorldTaskSystem()
    assert system.register_agent("a1") is True


def test_create_task_in_system():
    """Test creating task in system"""
    system = RealWorldTaskSystem()
    task = RealWorldTask(
        task_id="homework1",
        domain=TaskDomain.MATHEMATICS,
        title="Homework",
        description="Do homework",
        difficulty=TaskDifficulty.EASY
    )
    assert system.create_task(task) is True


def test_assign_and_complete_task():
    """Test assigning and completing task"""
    system = RealWorldTaskSystem()
    system.register_agent("a1")

    task = RealWorldTask(
        task_id="t1",
        domain=TaskDomain.WRITING,
        title="Essay",
        description="Write essay",
        difficulty=TaskDifficulty.MEDIUM
    )
    system.create_task(task)

    assert system.assign_task("a1", "t1") is True
    assert system.submit_solution("a1", "t1", 0.85) is True
    assert system.total_tasks_completed == 1


def test_domain_leaderboard():
    """Test getting domain leaderboard"""
    system = RealWorldTaskSystem()
    system.register_agent("a1")
    system.register_agent("a2")

    # Make agents complete coding tasks
    for agent_id in ["a1", "a2"]:
        task = RealWorldTask(
            task_id=f"coding_{agent_id}",
            domain=TaskDomain.CODING,
            title="Code Challenge",
            description="Write code",
            difficulty=TaskDifficulty.HARD
        )
        system.create_task(task)
        system.assign_task(agent_id, f"coding_{agent_id}")

    system.submit_solution("a1", "coding_a1", 0.9)
    system.submit_solution("a2", "coding_a2", 0.7)

    leaderboard = system.get_domain_leaderboard("coding")
    assert len(leaderboard) == 2
    assert leaderboard[0]["agent_id"] == "a1"


def test_strengths_weaknesses():
    """Test identifying agent strengths"""
    system = RealWorldTaskSystem()
    system.register_agent("a1")

    # Agent excels at math, weak at writing
    math_task = RealWorldTask(
        task_id="m1",
        domain=TaskDomain.MATHEMATICS,
        title="Math",
        description="Math problem",
        difficulty=TaskDifficulty.EASY
    )
    write_task = RealWorldTask(
        task_id="w1",
        domain=TaskDomain.WRITING,
        title="Write",
        description="Essay",
        difficulty=TaskDifficulty.EASY
    )

    system.create_task(math_task)
    system.create_task(write_task)

    system.assign_task("a1", "m1")
    system.submit_solution("a1", "m1", 0.95)

    system.assign_task("a1", "w1")
    system.submit_solution("a1", "w1", 0.4)

    analysis = system.get_agent_strengths_weaknesses("a1")
    assert "mathematics" in analysis["strengths"]


def test_task_recommendations():
    """Test recommending tasks based on ability"""
    system = RealWorldTaskSystem()
    system.register_agent("a1")

    # Create various difficulty tasks
    easy_task = RealWorldTask(
        task_id="e1",
        domain=TaskDomain.LOGIC,
        title="Easy",
        description="Easy logic",
        difficulty=TaskDifficulty.EASY
    )
    hard_task = RealWorldTask(
        task_id="h1",
        domain=TaskDomain.LOGIC,
        title="Hard",
        description="Hard logic",
        difficulty=TaskDifficulty.HARD
    )

    system.create_task(easy_task)
    system.create_task(hard_task)

    # Agent with low success rate gets easy tasks
    recommendations = system.recommend_tasks("a1")
    # Before trying any, should get some recommendations

    # Agent completes several tasks successfully
    system.assign_task("a1", "e1")
    system.submit_solution("a1", "e1", 0.95)

    recommendations = system.recommend_tasks("a1")
    # With high success rate, might recommend harder tasks


def test_complete_real_world_workflow():
    """Test complete workflow: agent solves multiple tasks"""
    system = RealWorldTaskSystem()
    system.register_agent("brilliant_coder")

    # Create task set
    tasks = [
        RealWorldTask("code1", TaskDomain.CODING, "FizzBuzz", "Implement FizzBuzz", TaskDifficulty.EASY),
        RealWorldTask("code2", TaskDomain.CODING, "Sorting", "Implement quicksort", TaskDifficulty.MEDIUM),
        RealWorldTask("code3", TaskDomain.CODING, "Graph", "Graph traversal", TaskDifficulty.HARD),
        RealWorldTask("math1", TaskDomain.MATHEMATICS, "Calculus", "Find derivative", TaskDifficulty.MEDIUM),
    ]

    for task in tasks:
        system.create_task(task)

    # Agent tackles coding tasks
    system.assign_task("brilliant_coder", "code1")
    system.submit_solution("brilliant_coder", "code1", 1.0)

    system.assign_task("brilliant_coder", "code2")
    system.submit_solution("brilliant_coder", "code2", 0.95)

    system.assign_task("brilliant_coder", "code3")
    system.submit_solution("brilliant_coder", "code3", 0.8)

    # Agent tries math, not strong
    system.assign_task("brilliant_coder", "math1")
    system.fail_task("brilliant_coder", "math1")

    # Check final performance
    perf = system.get_agent_performance("brilliant_coder")
    assert perf["tasks_completed"] == 3
    assert perf["success_rate"] == 0.75

    # Check strengths
    analysis = system.get_agent_strengths_weaknesses("brilliant_coder")
    assert "coding" in analysis["strengths"]

    # Check system stats
    stats = system.get_system_statistics()
    assert stats["total_completed"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
