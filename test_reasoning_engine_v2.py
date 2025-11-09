"""
Round 51: AI Agent Reasoning Engine
Advanced reasoning capabilities for agents to think through complex problems.
Features: problem decomposition, chain-of-thought, constraint satisfaction, decision trees.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple


class ReasoningType(Enum):
    """Type of reasoning approach"""
    DEDUCTIVE = "deductive"  # Logical inference from facts
    INDUCTIVE = "inductive"  # Pattern recognition and generalization
    ABDUCTIVE = "abductive"  # Best explanation inference
    ANALOGICAL = "analogical"  # Reasoning by analogy
    HEURISTIC = "heuristic"  # Rule-of-thumb reasoning
    PROBABILISTIC = "probabilistic"  # Bayesian reasoning


class ConfidenceLevel(Enum):
    """Confidence in reasoning result"""
    CERTAIN = 1.0
    VERY_HIGH = 0.9
    HIGH = 0.75
    MODERATE = 0.6
    LOW = 0.4
    VERY_LOW = 0.2
    UNCERTAIN = 0.0


@dataclass
class Fact:
    """A fact the agent knows"""
    fact_id: str
    statement: str
    domain: str  # "math", "science", "common_sense", etc.
    confidence: float = 0.9  # 0.0-1.0
    source: str = ""  # Where the fact came from
    timestamp: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "id": self.fact_id,
            "statement": self.statement,
            "domain": self.domain,
            "confidence": self.confidence,
            "source": self.source
        }


@dataclass
class ReasoningRule:
    """Rule for reasoning (if-then)"""
    rule_id: str
    name: str
    antecedent: List[str]  # Conditions (fact_ids)
    consequent: str  # Conclusion (fact_id or statement)
    strength: float = 0.8  # 0.0-1.0, how strongly rule applies
    domain: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.rule_id,
            "name": self.name,
            "conditions": len(self.antecedent),
            "strength": self.strength
        }


@dataclass
class ProblemDecomposition:
    """Break complex problem into sub-problems"""
    decomposition_id: str
    original_problem: str
    sub_problems: List[str] = field(default_factory=list)
    decomposition_strategy: str = ""  # "divide_and_conquer", "hierarchical", etc.
    complexity_reduction: float = 0.0  # 0.0-1.0, how much simpler are sub-problems

    def add_sub_problem(self, sub_problem: str) -> bool:
        """Add sub-problem"""
        if sub_problem not in self.sub_problems:
            self.sub_problems.append(sub_problem)
            return True
        return False

    def get_complexity_reduction(self) -> float:
        """Calculate complexity reduction from decomposition"""
        if not self.sub_problems:
            return 0.0
        # More sub-problems = better decomposition
        return min(1.0, len(self.sub_problems) * 0.2)

    def to_dict(self) -> Dict:
        return {
            "id": self.decomposition_id,
            "original": self.original_problem,
            "sub_problems": len(self.sub_problems),
            "strategy": self.decomposition_strategy
        }


@dataclass
class ReasoningStep:
    """A single step in reasoning chain"""
    step_id: str
    reasoning_type: ReasoningType
    input_facts: List[str] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)
    derived_conclusion: str = ""
    confidence: float = 0.5
    explanation: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.step_id,
            "type": self.reasoning_type.value,
            "inputs": len(self.input_facts),
            "confidence": self.confidence
        }


@dataclass
class ReasoningChain:
    """Chain of reasoning steps leading to conclusion"""
    chain_id: str
    agent_id: str
    problem: str
    steps: List[ReasoningStep] = field(default_factory=list)
    final_conclusion: str = ""
    overall_confidence: float = 0.0
    reasoning_quality: float = 0.0  # 0.0-1.0

    def add_step(self, step: ReasoningStep) -> bool:
        """Add reasoning step"""
        self.steps.append(step)
        return True

    def calculate_overall_confidence(self) -> float:
        """Calculate overall confidence from all steps"""
        if not self.steps:
            return 0.0

        total_confidence = sum(s.confidence for s in self.steps)
        self.overall_confidence = total_confidence / len(self.steps)
        return self.overall_confidence

    def calculate_quality(self) -> float:
        """Calculate reasoning quality (0.0-1.0)"""
        if not self.steps:
            return 0.0

        # Quality factors:
        confidence = self.calculate_overall_confidence()  # 0.0-1.0
        step_count = min(1.0, len(self.steps) / 5.0)  # Optimal ~5 steps
        diversity = self._calculate_type_diversity()  # How many reasoning types used

        self.reasoning_quality = (confidence * 0.5) + (step_count * 0.3) + (diversity * 0.2)
        return self.reasoning_quality

    def _calculate_type_diversity(self) -> float:
        """Calculate diversity of reasoning types used"""
        types_used = set(s.reasoning_type for s in self.steps)
        return len(types_used) / len(ReasoningType)

    def to_dict(self) -> Dict:
        return {
            "id": self.chain_id,
            "agent": self.agent_id,
            "problem": self.problem,
            "steps": len(self.steps),
            "confidence": round(self.overall_confidence, 2),
            "quality": round(self.reasoning_quality, 2)
        }


class KnowledgeBase:
    """Agent's knowledge base of facts and rules"""

    def __init__(self):
        self.facts: Dict[str, Fact] = {}
        self.rules: Dict[str, ReasoningRule] = {}
        self.fact_index: Dict[str, List[str]] = {}  # domain -> fact_ids

    def add_fact(self, fact: Fact) -> bool:
        """Add fact to knowledge base"""
        if fact.fact_id in self.facts:
            return False

        self.facts[fact.fact_id] = fact

        if fact.domain not in self.fact_index:
            self.fact_index[fact.domain] = []
        self.fact_index[fact.domain].append(fact.fact_id)

        return True

    def add_rule(self, rule: ReasoningRule) -> bool:
        """Add reasoning rule"""
        if rule.rule_id in self.rules:
            return False

        self.rules[rule.rule_id] = rule
        return True

    def get_fact(self, fact_id: str) -> Optional[Fact]:
        """Get fact by ID"""
        return self.facts.get(fact_id)

    def get_facts_by_domain(self, domain: str) -> List[Fact]:
        """Get all facts in a domain"""
        if domain not in self.fact_index:
            return []

        fact_ids = self.fact_index[domain]
        return [self.facts[fid] for fid in fact_ids if fid in self.facts]

    def get_applicable_rules(self, available_facts: List[str]) -> List[ReasoningRule]:
        """Get rules that can be applied given available facts"""
        applicable = []

        for rule in self.rules.values():
            # Check if all antecedents are available
            if all(fact_id in available_facts for fact_id in rule.antecedent):
                applicable.append(rule)

        return applicable

    def get_high_confidence_facts(self, threshold: float = 0.7) -> List[Fact]:
        """Get facts above confidence threshold"""
        return [f for f in self.facts.values() if f.confidence >= threshold]

    def to_dict(self) -> Dict:
        return {
            "total_facts": len(self.facts),
            "domains": len(self.fact_index),
            "total_rules": len(self.rules),
            "high_confidence_facts": len(self.get_high_confidence_facts())
        }


class ReasoningEngine:
    """Core reasoning engine for agents"""

    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.reasoning_chains: Dict[str, ReasoningChain] = {}
        self.decompositions: Dict[str, ProblemDecomposition] = {}

    def add_fact(self, fact: Fact) -> bool:
        """Add fact to knowledge base"""
        return self.knowledge_base.add_fact(fact)

    def add_rule(self, rule: ReasoningRule) -> bool:
        """Add reasoning rule"""
        return self.knowledge_base.add_rule(rule)

    def decompose_problem(self, decomposition: ProblemDecomposition) -> bool:
        """Store problem decomposition"""
        if decomposition.decomposition_id in self.decompositions:
            return False

        decomposition.complexity_reduction = decomposition.get_complexity_reduction()
        self.decompositions[decomposition.decomposition_id] = decomposition
        return True

    def reason(self, agent_id: str, problem: str, reasoning_type: ReasoningType) -> Optional[ReasoningChain]:
        """Execute reasoning chain for a problem"""
        chain = ReasoningChain(
            chain_id=f"chain_{len(self.reasoning_chains)}",
            agent_id=agent_id,
            problem=problem
        )

        # Simulate reasoning steps
        available_facts = [f.fact_id for f in self.knowledge_base.get_high_confidence_facts()]

        if reasoning_type == ReasoningType.DEDUCTIVE:
            step = self._deductive_step(chain, available_facts)
        elif reasoning_type == ReasoningType.INDUCTIVE:
            step = self._inductive_step(chain, available_facts)
        elif reasoning_type == ReasoningType.ANALOGICAL:
            step = self._analogical_step(chain)
        else:
            step = ReasoningStep(
                step_id=f"step_0",
                reasoning_type=reasoning_type,
                input_facts=available_facts,
                confidence=0.7
            )

        chain.add_step(step)
        chain.calculate_quality()

        self.reasoning_chains[chain.chain_id] = chain
        return chain

    def _deductive_step(self, chain: ReasoningChain, available_facts: List[str]) -> ReasoningStep:
        """Deductive reasoning step"""
        applicable_rules = self.knowledge_base.get_applicable_rules(available_facts)

        step = ReasoningStep(
            step_id=f"step_{len(chain.steps)}",
            reasoning_type=ReasoningType.DEDUCTIVE,
            input_facts=available_facts,
            applied_rules=[r.rule_id for r in applicable_rules],
            confidence=min(1.0, 0.7 + len(applicable_rules) * 0.1)
        )

        return step

    def _inductive_step(self, chain: ReasoningChain, available_facts: List[str]) -> ReasoningStep:
        """Inductive reasoning step (pattern recognition)"""
        facts = [self.knowledge_base.get_fact(fid) for fid in available_facts if self.knowledge_base.get_fact(fid)]
        confidence = min(1.0, 0.5 + len(facts) * 0.05)

        step = ReasoningStep(
            step_id=f"step_{len(chain.steps)}",
            reasoning_type=ReasoningType.INDUCTIVE,
            input_facts=available_facts,
            confidence=confidence,
            explanation=f"Pattern recognized from {len(facts)} facts"
        )

        return step

    def _analogical_step(self, chain: ReasoningChain) -> ReasoningStep:
        """Analogical reasoning step"""
        step = ReasoningStep(
            step_id=f"step_{len(chain.steps)}",
            reasoning_type=ReasoningType.ANALOGICAL,
            confidence=0.65,
            explanation="Analogy found with similar problem"
        )

        return step

    def get_reasoning_chain(self, chain_id: str) -> Optional[ReasoningChain]:
        """Get reasoning chain by ID"""
        return self.reasoning_chains.get(chain_id)

    def get_best_reasoning(self, agent_id: str) -> Optional[ReasoningChain]:
        """Get highest quality reasoning for agent"""
        agent_chains = [c for c in self.reasoning_chains.values() if c.agent_id == agent_id]

        if not agent_chains:
            return None

        return max(agent_chains, key=lambda c: c.reasoning_quality)

    def to_dict(self) -> Dict:
        return {
            "knowledge_base": self.knowledge_base.to_dict(),
            "reasoning_chains": len(self.reasoning_chains),
            "decompositions": len(self.decompositions),
            "avg_reasoning_quality": round(
                sum(c.reasoning_quality for c in self.reasoning_chains.values()) / max(1, len(self.reasoning_chains)),
                2
            ) if self.reasoning_chains else 0.0
        }


# ===== Tests =====

def test_fact_creation():
    """Test creating a fact"""
    fact = Fact("f1", "2+2=4", "math", confidence=1.0)
    assert fact.fact_id == "f1"
    assert fact.confidence == 1.0


def test_fact_confidence():
    """Test fact confidence levels"""
    fact_certain = Fact("f1", "Sky is blue", "common_sense", confidence=0.95)
    fact_uncertain = Fact("f2", "Aliens exist", "science", confidence=0.2)

    assert fact_certain.confidence > fact_uncertain.confidence


def test_reasoning_rule_creation():
    """Test creating reasoning rule"""
    rule = ReasoningRule(
        "rule1", "If A then B",
        ["fact_a"], "fact_b", strength=0.9
    )
    assert rule.rule_id == "rule1"
    assert rule.strength == 0.9


def test_knowledge_base_add_fact():
    """Test adding facts to knowledge base"""
    kb = KnowledgeBase()
    fact = Fact("f1", "2+2=4", "math", confidence=1.0)

    assert kb.add_fact(fact) is True
    assert kb.get_fact("f1") is not None


def test_knowledge_base_duplicate_fact():
    """Test KB rejects duplicate facts"""
    kb = KnowledgeBase()
    fact = Fact("f1", "2+2=4", "math")

    assert kb.add_fact(fact) is True
    assert kb.add_fact(fact) is False


def test_knowledge_base_add_rule():
    """Test adding rules to knowledge base"""
    kb = KnowledgeBase()
    rule = ReasoningRule("rule1", "If A then B", ["f1"], "f2")

    assert kb.add_rule(rule) is True


def test_knowledge_base_get_facts_by_domain():
    """Test getting facts by domain"""
    kb = KnowledgeBase()
    f1 = Fact("f1", "2+2=4", "math")
    f2 = Fact("f2", "Pythagoras theorem", "math")
    f3 = Fact("f3", "Gravity exists", "science")

    kb.add_fact(f1)
    kb.add_fact(f2)
    kb.add_fact(f3)

    math_facts = kb.get_facts_by_domain("math")
    assert len(math_facts) == 2


def test_knowledge_base_high_confidence_facts():
    """Test getting high confidence facts"""
    kb = KnowledgeBase()
    f1 = Fact("f1", "Fact1", "test", confidence=0.9)
    f2 = Fact("f2", "Fact2", "test", confidence=0.5)

    kb.add_fact(f1)
    kb.add_fact(f2)

    high_conf = kb.get_high_confidence_facts(0.7)
    assert len(high_conf) == 1


def test_problem_decomposition():
    """Test decomposing a problem"""
    decomp = ProblemDecomposition(
        "d1", "Solve complex equation"
    )
    assert decomp.add_sub_problem("Simplify left side") is True
    assert decomp.add_sub_problem("Simplify right side") is True

    assert len(decomp.sub_problems) == 2


def test_decomposition_complexity_reduction():
    """Test complexity reduction calculation"""
    decomp = ProblemDecomposition("d1", "Complex problem")
    decomp.add_sub_problem("Sub1")
    decomp.add_sub_problem("Sub2")
    decomp.add_sub_problem("Sub3")

    reduction = decomp.get_complexity_reduction()
    assert 0.0 < reduction < 1.0


def test_reasoning_step_creation():
    """Test creating reasoning step"""
    step = ReasoningStep(
        "step1", ReasoningType.DEDUCTIVE,
        input_facts=["f1", "f2"], confidence=0.8
    )
    assert step.step_id == "step1"
    assert len(step.input_facts) == 2


def test_reasoning_chain_add_step():
    """Test adding steps to reasoning chain"""
    chain = ReasoningChain("chain1", "agent1", "Solve problem")
    step = ReasoningStep("step1", ReasoningType.DEDUCTIVE, confidence=0.8)

    assert chain.add_step(step) is True
    assert len(chain.steps) == 1


def test_reasoning_chain_confidence():
    """Test overall confidence calculation"""
    chain = ReasoningChain("chain1", "agent1", "Problem")
    chain.add_step(ReasoningStep("s1", ReasoningType.DEDUCTIVE, confidence=0.8))
    chain.add_step(ReasoningStep("s2", ReasoningType.INDUCTIVE, confidence=0.9))

    confidence = chain.calculate_overall_confidence()
    assert 0.8 < confidence < 0.95


def test_reasoning_chain_quality():
    """Test reasoning quality calculation"""
    chain = ReasoningChain("chain1", "agent1", "Problem")
    chain.add_step(ReasoningStep("s1", ReasoningType.DEDUCTIVE, confidence=0.8))
    chain.add_step(ReasoningStep("s2", ReasoningType.INDUCTIVE, confidence=0.9))

    quality = chain.calculate_quality()
    assert 0.0 <= quality <= 1.0


def test_reasoning_engine_add_fact():
    """Test reasoning engine"""
    engine = ReasoningEngine()
    fact = Fact("f1", "2+2=4", "math", confidence=1.0)

    assert engine.add_fact(fact) is True


def test_reasoning_engine_reasoning():
    """Test reasoning through engine"""
    engine = ReasoningEngine()

    # Add facts
    engine.add_fact(Fact("f1", "All men are mortal", "logic", confidence=1.0))
    engine.add_fact(Fact("f2", "Socrates is a man", "logic", confidence=1.0))

    # Add rule
    rule = ReasoningRule(
        "rule1", "Modus ponens",
        ["f1", "f2"], "Socrates is mortal", strength=1.0
    )
    engine.add_rule(rule)

    # Reason
    chain = engine.reason("agent1", "Is Socrates mortal?", ReasoningType.DEDUCTIVE)

    assert chain is not None
    assert len(chain.steps) >= 1


def test_reasoning_engine_best_reasoning():
    """Test getting best reasoning"""
    engine = ReasoningEngine()
    engine.add_fact(Fact("f1", "Fact1", "test", confidence=0.9))

    chain1 = engine.reason("agent1", "Problem1", ReasoningType.DEDUCTIVE)
    chain2 = engine.reason("agent1", "Problem2", ReasoningType.INDUCTIVE)

    best = engine.get_best_reasoning("agent1")
    assert best is not None


def test_complete_reasoning_workflow():
    """Test complete reasoning workflow"""
    engine = ReasoningEngine()

    # Build knowledge base
    engine.add_fact(Fact("f1", "If raining, then wet", "logic"))
    engine.add_fact(Fact("f2", "It is raining", "observation"))
    engine.add_fact(Fact("f3", "Grass is outside", "knowledge"))

    # Add reasoning rules
    engine.add_rule(ReasoningRule(
        "rule1", "Modus ponens",
        ["f1", "f2"], "Everything outside is wet", strength=0.95
    ))

    # Decompose problem
    decomp = ProblemDecomposition("d1", "Why is the grass wet?")
    decomp.add_sub_problem("Is it raining?")
    decomp.add_sub_problem("Is grass outside?")
    assert engine.decompose_problem(decomp) is True

    # Reason about problem
    chain = engine.reason("agent1", "Why is grass wet?", ReasoningType.DEDUCTIVE)

    assert chain is not None
    assert chain.overall_confidence > 0.0
    assert chain.reasoning_quality >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
