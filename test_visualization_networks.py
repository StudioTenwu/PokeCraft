"""
Round 36: Relationship and Knowledge Visualization

Visualize complex systems of relationships, knowledge, and memory as
interconnected graphs that help players understand agent learning and bonds.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


class NodeType(Enum):
    """Types of nodes in visualization graphs"""
    AGENT = "agent"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    TOPIC = "topic"
    SKILL = "skill"


class EdgeType(Enum):
    """Types of connections between nodes"""
    KNOWS = "knows"  # Agent knows knowledge
    REMEMBERS = "remembers"  # Agent remembers memory
    RELATED = "related"  # Topics are related
    PREREQUISITE = "prerequisite"  # Knowledge prerequisite
    BONDS = "bonds"  # Agent relationship
    COLLABORATES = "collaborates"  # Multi-agent collaboration


class RelationshipStrength(Enum):
    """Visual strength of relationships"""
    WEAK = "weak"  # < 0.3 trust
    MODERATE = "moderate"  # 0.3-0.6 trust
    STRONG = "strong"  # 0.6-0.8 trust
    DEEP = "deep"  # > 0.8 trust


@dataclass
class GraphNode:
    """Node in a visualization graph"""
    node_id: str
    node_type: NodeType
    label: str
    value: float = 0.5  # 0.0-1.0, size/importance
    color: str = "#808080"  # Hex color

    def to_dict(self) -> Dict:
        return {
            "id": self.node_id,
            "type": self.node_type.value,
            "label": self.label,
            "value": self.value,
            "color": self.color
        }


@dataclass
class GraphEdge:
    """Edge connecting two nodes"""
    source: str  # node_id
    target: str  # node_id
    edge_type: EdgeType
    strength: float = 0.5  # 0.0-1.0, importance
    label: str = ""

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.edge_type.value,
            "strength": self.strength,
            "label": self.label
        }


@dataclass
class Graph:
    """Directed graph for visualization"""
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)

    def add_node(self, node: GraphNode) -> bool:
        """Add node to graph"""
        if node.node_id in self.nodes:
            return False
        self.nodes[node.node_id] = node
        return True

    def add_edge(self, edge: GraphEdge) -> bool:
        """Add edge to graph"""
        if edge.source not in self.nodes or edge.target not in self.nodes:
            return False
        self.edges.append(edge)
        return True

    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all connected nodes"""
        neighbors = set()
        for edge in self.edges:
            if edge.source == node_id:
                neighbors.add(edge.target)
            elif edge.target == node_id:
                neighbors.add(edge.source)
        return list(neighbors)

    def get_incoming_edges(self, node_id: str) -> List[GraphEdge]:
        """Get edges pointing to this node"""
        return [e for e in self.edges if e.target == node_id]

    def get_outgoing_edges(self, node_id: str) -> List[GraphEdge]:
        """Get edges from this node"""
        return [e for e in self.edges if e.source == node_id]

    def to_dict(self) -> Dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }


@dataclass
class RelationshipNode:
    """Visual representation of agent relationship"""
    agent_id: str
    agent_name: str
    trust: float  # 0.0-1.0
    shared_goals: int
    interaction_count: int

    def get_relationship_strength(self) -> RelationshipStrength:
        """Determine visual strength from trust"""
        if self.trust > 0.8:
            return RelationshipStrength.DEEP
        elif self.trust > 0.6:
            return RelationshipStrength.STRONG
        elif self.trust > 0.3:
            return RelationshipStrength.MODERATE
        else:
            return RelationshipStrength.WEAK

    def get_color(self) -> str:
        """Color based on relationship strength"""
        strength = self.get_relationship_strength()
        colors = {
            RelationshipStrength.WEAK: "#FFA500",  # Orange
            RelationshipStrength.MODERATE: "#FFD700",  # Gold
            RelationshipStrength.STRONG: "#32CD32",  # Lime green
            RelationshipStrength.DEEP: "#FF1493"  # Deep pink
        }
        return colors.get(strength, "#808080")

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "trust": self.trust,
            "strength": self.get_relationship_strength().value,
            "color": self.get_color()
        }


class RelationshipGraph:
    """Visualize multi-agent relationships"""

    def __init__(self):
        self.relationships: Dict[Tuple[str, str], RelationshipNode] = {}
        self.agent_names: Dict[str, str] = {}

    def register_agent(self, agent_id: str, agent_name: str) -> bool:
        """Register agent for relationship tracking"""
        if agent_id in self.agent_names:
            return False
        self.agent_names[agent_id] = agent_name
        return True

    def add_relationship(self, agent1_id: str, agent2_id: str, trust: float = 0.5) -> bool:
        """Add relationship between agents"""
        if agent1_id not in self.agent_names or agent2_id not in self.agent_names:
            return False

        # Store as undirected (both directions)
        key = tuple(sorted([agent1_id, agent2_id]))
        if key in self.relationships:
            return False

        rel = RelationshipNode(
            agent_id=agent2_id,
            agent_name=self.agent_names[agent2_id],
            trust=trust,
            shared_goals=0,
            interaction_count=0
        )
        self.relationships[key] = rel
        return True

    def update_trust(self, agent1_id: str, agent2_id: str, amount: float) -> bool:
        """Update trust between agents"""
        key = tuple(sorted([agent1_id, agent2_id]))
        if key not in self.relationships:
            return False

        rel = self.relationships[key]
        rel.trust = max(0.0, min(1.0, rel.trust + amount))
        return True

    def add_shared_goal(self, agent1_id: str, agent2_id: str) -> bool:
        """Increase shared goal count"""
        key = tuple(sorted([agent1_id, agent2_id]))
        if key not in self.relationships:
            return False

        self.relationships[key].shared_goals += 1
        return True

    def record_interaction(self, agent1_id: str, agent2_id: str) -> bool:
        """Record interaction between agents"""
        key = tuple(sorted([agent1_id, agent2_id]))
        if key not in self.relationships:
            return False

        self.relationships[key].interaction_count += 1
        return True

    def get_agent_relationships(self, agent_id: str) -> List[RelationshipNode]:
        """Get all relationships for an agent"""
        rels = []
        for (a1, a2), rel in self.relationships.items():
            if a1 == agent_id or a2 == agent_id:
                rels.append(rel)
        return rels

    def get_strongest_bonds(self, agent_id: str, limit: int = 5) -> List[RelationshipNode]:
        """Get strongest relationships for agent"""
        rels = self.get_agent_relationships(agent_id)
        sorted_rels = sorted(rels, key=lambda r: r.trust, reverse=True)
        return sorted_rels[:limit]

    def to_graph(self) -> Graph:
        """Convert to general Graph structure"""
        graph = Graph()

        # Add agent nodes
        for agent_id, agent_name in self.agent_names.items():
            node = GraphNode(
                node_id=agent_id,
                node_type=NodeType.AGENT,
                label=agent_name,
                color="#87CEEB"
            )
            graph.add_node(node)

        # Add relationship edges
        for (a1, a2), rel in self.relationships.items():
            edge = GraphEdge(
                source=a1,
                target=a2,
                edge_type=EdgeType.BONDS,
                strength=rel.trust,
                label=f"Trust: {rel.trust:.2f}"
            )
            graph.add_edge(edge)

        return graph

    def to_dict(self) -> Dict:
        return {
            "agents": len(self.agent_names),
            "relationships": len(self.relationships),
            "bonds": [r.to_dict() for r in self.relationships.values()]
        }


@dataclass
class KnowledgeNode:
    """Visual node for knowledge unit"""
    unit_id: str
    topic: str
    tier: str  # SURFACE, INTERMEDIATE, DEEP, EXPERT
    reliability: float  # 0.0-1.0

    def get_tier_value(self) -> float:
        """Convert tier to numeric value"""
        tiers = {
            "SURFACE": 0.25,
            "INTERMEDIATE": 0.5,
            "DEEP": 0.75,
            "EXPERT": 1.0
        }
        return tiers.get(self.tier, 0.0)

    def get_color(self) -> str:
        """Color based on tier"""
        colors = {
            "SURFACE": "#FFB6C1",  # Light pink
            "INTERMEDIATE": "#FFD700",  # Gold
            "DEEP": "#32CD32",  # Lime green
            "EXPERT": "#FF1493"  # Deep pink
        }
        return colors.get(self.tier, "#808080")

    def to_dict(self) -> Dict:
        return {
            "unit_id": self.unit_id,
            "topic": self.topic,
            "tier": self.tier,
            "reliability": self.reliability,
            "color": self.get_color()
        }


class KnowledgeGraph:
    """Visualize knowledge units and learning structure"""

    def __init__(self):
        self.knowledge_units: Dict[str, KnowledgeNode] = {}
        self.topic_graph: Dict[str, Set[str]] = {}  # topic -> related topics
        self.prerequisites: Dict[str, Set[str]] = {}  # unit_id -> prerequisite unit_ids
        self.agent_knowledge: Dict[str, Set[str]] = {}  # agent_id -> unit_ids

    def add_knowledge_unit(self, unit: KnowledgeNode) -> bool:
        """Add knowledge unit"""
        if unit.unit_id in self.knowledge_units:
            return False
        self.knowledge_units[unit.unit_id] = unit

        # Initialize topic graph
        if unit.topic not in self.topic_graph:
            self.topic_graph[unit.topic] = set()

        # Initialize prerequisites
        if unit.unit_id not in self.prerequisites:
            self.prerequisites[unit.unit_id] = set()

        return True

    def add_prerequisite(self, unit_id: str, prereq_id: str) -> bool:
        """Add prerequisite relationship"""
        if unit_id not in self.knowledge_units or prereq_id not in self.knowledge_units:
            return False
        self.prerequisites[unit_id].add(prereq_id)
        return True

    def relate_topics(self, topic1: str, topic2: str) -> bool:
        """Connect two topics"""
        if topic1 not in self.topic_graph:
            self.topic_graph[topic1] = set()
        if topic2 not in self.topic_graph:
            self.topic_graph[topic2] = set()

        self.topic_graph[topic1].add(topic2)
        self.topic_graph[topic2].add(topic1)
        return True

    def register_agent(self, agent_id: str) -> bool:
        """Register agent for knowledge tracking"""
        if agent_id in self.agent_knowledge:
            return False
        self.agent_knowledge[agent_id] = set()
        return True

    def teach_agent(self, agent_id: str, unit_id: str) -> bool:
        """Mark knowledge as known by agent"""
        if agent_id not in self.agent_knowledge or unit_id not in self.knowledge_units:
            return False
        self.agent_knowledge[agent_id].add(unit_id)
        return True

    def get_agent_expertise(self, agent_id: str) -> Dict[str, float]:
        """Get expertise by topic for agent"""
        if agent_id not in self.agent_knowledge:
            return {}

        expertise = {}
        for unit_id in self.agent_knowledge[agent_id]:
            unit = self.knowledge_units[unit_id]
            tier_value = unit.get_tier_value()

            if unit.topic not in expertise:
                expertise[unit.topic] = tier_value
            else:
                expertise[unit.topic] = max(expertise[unit.topic], tier_value)

        return expertise

    def get_learning_path(self, unit_id: str) -> List[str]:
        """Get prerequisite chain for unit"""
        if unit_id not in self.knowledge_units:
            return []

        path = [unit_id]
        prereqs = self.prerequisites.get(unit_id, set())

        for prereq_id in prereqs:
            path.extend(self.get_learning_path(prereq_id))

        return path

    def to_graph(self) -> Graph:
        """Convert to general Graph structure"""
        graph = Graph()

        # Add knowledge nodes
        for unit_id, unit in self.knowledge_units.items():
            node = GraphNode(
                node_id=unit_id,
                node_type=NodeType.KNOWLEDGE,
                label=f"{unit.topic} ({unit.tier})",
                value=unit.get_tier_value(),
                color=unit.get_color()
            )
            graph.add_node(node)

        # Add prerequisite edges
        for unit_id, prereqs in self.prerequisites.items():
            for prereq_id in prereqs:
                edge = GraphEdge(
                    source=prereq_id,
                    target=unit_id,
                    edge_type=EdgeType.PREREQUISITE,
                    strength=1.0
                )
                if edge.source in graph.nodes and edge.target in graph.nodes:
                    graph.add_edge(edge)

        return graph

    def to_dict(self) -> Dict:
        return {
            "total_units": len(self.knowledge_units),
            "topics": len(self.topic_graph),
            "agents": len(self.agent_knowledge)
        }


@dataclass
class MemoryMarker:
    """Visual marker for a memory"""
    memory_id: str
    experience_type: str  # POSITIVE, NEGATIVE, NEUTRAL
    emotional_charge: float  # -1.0 to 1.0
    timestamp: int = 0  # Order in timeline
    suppressed: bool = False

    def get_color(self) -> str:
        """Color based on emotional charge"""
        if self.suppressed:
            return "#CCCCCC"  # Gray
        elif self.emotional_charge > 0.5:
            return "#FFD700"  # Gold (very positive)
        elif self.emotional_charge > 0:
            return "#90EE90"  # Light green (positive)
        elif self.emotional_charge < -0.5:
            return "#FF0000"  # Red (very negative)
        elif self.emotional_charge < 0:
            return "#FFA500"  # Orange (negative)
        else:
            return "#87CEEB"  # Sky blue (neutral)

    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "type": self.experience_type,
            "charge": self.emotional_charge,
            "color": self.get_color(),
            "suppressed": self.suppressed
        }


class MemoryTimeline:
    """Visualize agent memory as timeline"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.memories: Dict[str, MemoryMarker] = {}
        self.sequence: List[str] = []  # Order of memories
        self.associations: Dict[str, Set[str]] = {}  # memory_id -> related memory_ids

    def add_memory(self, marker: MemoryMarker) -> bool:
        """Add memory to timeline"""
        if marker.memory_id in self.memories:
            return False

        marker.timestamp = len(self.sequence)
        self.memories[marker.memory_id] = marker
        self.sequence.append(marker.memory_id)
        self.associations[marker.memory_id] = set()
        return True

    def associate_memories(self, memory_id1: str, memory_id2: str) -> bool:
        """Link related memories"""
        if memory_id1 not in self.memories or memory_id2 not in self.memories:
            return False

        self.associations[memory_id1].add(memory_id2)
        self.associations[memory_id2].add(memory_id1)
        return True

    def suppress_memory(self, memory_id: str) -> bool:
        """Mark memory as suppressed"""
        if memory_id not in self.memories:
            return False
        self.memories[memory_id].suppressed = True
        return True

    def get_timeline(self) -> List[MemoryMarker]:
        """Get memories in chronological order"""
        return [self.memories[mid] for mid in self.sequence]

    def get_emotional_summary(self) -> float:
        """Average emotional charge of memories"""
        if not self.memories:
            return 0.0
        total = sum(m.emotional_charge for m in self.memories.values())
        return total / len(self.memories)

    def get_positive_ratio(self) -> float:
        """Ratio of positive to total memories"""
        if not self.memories:
            return 0.5
        positive = sum(1 for m in self.memories.values() if m.emotional_charge > 0)
        return positive / len(self.memories)

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "total_memories": len(self.memories),
            "emotional_summary": self.get_emotional_summary(),
            "positive_ratio": self.get_positive_ratio(),
            "timeline": [self.memories[mid].to_dict() for mid in self.sequence]
        }


# ===== Tests =====

def test_graph_node_creation():
    """Test creating graph node"""
    node = GraphNode(
        node_id="n1",
        node_type=NodeType.AGENT,
        label="Agent1",
        value=0.8
    )
    assert node.node_id == "n1"
    assert node.value == 0.8


def test_graph_edge_creation():
    """Test creating graph edge"""
    edge = GraphEdge(
        source="n1",
        target="n2",
        edge_type=EdgeType.BONDS,
        strength=0.7
    )
    assert edge.source == "n1"
    assert edge.strength == 0.7


def test_graph_add_node():
    """Test adding node to graph"""
    graph = Graph()
    node = GraphNode("n1", NodeType.AGENT, "Agent1")
    assert graph.add_node(node) is True


def test_graph_add_edge():
    """Test adding edge to graph"""
    graph = Graph()
    n1 = GraphNode("n1", NodeType.AGENT, "A1")
    n2 = GraphNode("n2", NodeType.AGENT, "A2")
    graph.add_node(n1)
    graph.add_node(n2)

    edge = GraphEdge("n1", "n2", EdgeType.BONDS)
    assert graph.add_edge(edge) is True


def test_graph_neighbors():
    """Test finding connected nodes"""
    graph = Graph()
    n1 = GraphNode("n1", NodeType.AGENT, "A1")
    n2 = GraphNode("n2", NodeType.AGENT, "A2")
    n3 = GraphNode("n3", NodeType.AGENT, "A3")
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    graph.add_edge(GraphEdge("n1", "n2", EdgeType.BONDS))
    graph.add_edge(GraphEdge("n1", "n3", EdgeType.BONDS))

    neighbors = graph.get_neighbors("n1")
    assert len(neighbors) == 2


def test_relationship_node():
    """Test creating relationship node"""
    rel = RelationshipNode(
        agent_id="a2",
        agent_name="Bot2",
        trust=0.7,
        shared_goals=2,
        interaction_count=5
    )
    assert rel.trust == 0.7
    assert rel.get_relationship_strength() == RelationshipStrength.STRONG


def test_relationship_strength_colors():
    """Test relationship strength color mapping"""
    rel_weak = RelationshipNode("a2", "Bot2", 0.2, 0, 0)
    rel_deep = RelationshipNode("a2", "Bot2", 0.9, 5, 20)

    assert rel_weak.get_color() == "#FFA500"  # Orange
    assert rel_deep.get_color() == "#FF1493"  # Deep pink


def test_relationship_graph_creation():
    """Test creating relationship graph"""
    rg = RelationshipGraph()
    assert rg.register_agent("a1", "Agent1") is True
    assert rg.register_agent("a2", "Agent2") is True


def test_add_relationship():
    """Test adding relationship"""
    rg = RelationshipGraph()
    rg.register_agent("a1", "Agent1")
    rg.register_agent("a2", "Agent2")

    assert rg.add_relationship("a1", "a2", 0.6) is True


def test_update_trust():
    """Test updating trust"""
    rg = RelationshipGraph()
    rg.register_agent("a1", "Agent1")
    rg.register_agent("a2", "Agent2")
    rg.add_relationship("a1", "a2", 0.5)

    assert rg.update_trust("a1", "a2", 0.2) is True


def test_strongest_bonds():
    """Test getting strongest relationships"""
    rg = RelationshipGraph()
    rg.register_agent("a1", "A1")
    rg.register_agent("a2", "A2")
    rg.register_agent("a3", "A3")

    rg.add_relationship("a1", "a2", 0.3)
    rg.add_relationship("a1", "a3", 0.8)

    strongest = rg.get_strongest_bonds("a1")
    assert strongest[0].trust == 0.8


def test_knowledge_node_colors():
    """Test knowledge node tier coloring"""
    unit_surface = KnowledgeNode("k1", "math", "SURFACE", 0.5)
    unit_expert = KnowledgeNode("k2", "math", "EXPERT", 0.95)

    assert unit_surface.get_color() == "#FFB6C1"  # Light pink
    assert unit_expert.get_color() == "#FF1493"  # Deep pink


def test_knowledge_graph_creation():
    """Test creating knowledge graph"""
    kg = KnowledgeGraph()
    unit = KnowledgeNode("k1", "python", "INTERMEDIATE", 0.7)
    assert kg.add_knowledge_unit(unit) is True


def test_knowledge_prerequisites():
    """Test prerequisite relationships"""
    kg = KnowledgeGraph()
    kg.add_knowledge_unit(KnowledgeNode("k1", "basics", "SURFACE", 0.5))
    kg.add_knowledge_unit(KnowledgeNode("k2", "advanced", "DEEP", 0.8))

    assert kg.add_prerequisite("k2", "k1") is True


def test_relate_topics():
    """Test relating topics"""
    kg = KnowledgeGraph()
    kg.add_knowledge_unit(KnowledgeNode("k1", "math", "SURFACE", 0.5))
    kg.add_knowledge_unit(KnowledgeNode("k2", "physics", "SURFACE", 0.5))

    assert kg.relate_topics("math", "physics") is True


def test_agent_expertise():
    """Test getting agent expertise"""
    kg = KnowledgeGraph()
    kg.register_agent("a1")

    unit = KnowledgeNode("k1", "python", "DEEP", 0.75)
    kg.add_knowledge_unit(unit)
    kg.teach_agent("a1", "k1")

    expertise = kg.get_agent_expertise("a1")
    assert "python" in expertise


def test_learning_path():
    """Test generating learning path"""
    kg = KnowledgeGraph()
    kg.add_knowledge_unit(KnowledgeNode("k1", "basics", "SURFACE", 0.5))
    kg.add_knowledge_unit(KnowledgeNode("k2", "advanced", "DEEP", 0.8))
    kg.add_knowledge_unit(KnowledgeNode("k3", "expert", "EXPERT", 1.0))

    kg.add_prerequisite("k2", "k1")
    kg.add_prerequisite("k3", "k2")

    path = kg.get_learning_path("k3")
    assert len(path) >= 2


def test_memory_marker_colors():
    """Test memory marker emotional coloring"""
    mem_positive = MemoryMarker("m1", "POSITIVE", 0.8)
    mem_negative = MemoryMarker("m2", "NEGATIVE", -0.7)
    mem_suppressed = MemoryMarker("m3", "POSITIVE", 0.8, suppressed=True)

    assert mem_positive.get_color() == "#FFD700"  # Gold
    assert mem_negative.get_color() == "#FF0000"  # Red
    assert mem_suppressed.get_color() == "#CCCCCC"  # Gray


def test_memory_timeline_creation():
    """Test creating memory timeline"""
    timeline = MemoryTimeline("a1")
    assert timeline.agent_id == "a1"


def test_add_memory_to_timeline():
    """Test adding memory to timeline"""
    timeline = MemoryTimeline("a1")
    marker = MemoryMarker("m1", "POSITIVE", 0.5)

    assert timeline.add_memory(marker) is True


def test_memory_associations():
    """Test associating memories"""
    timeline = MemoryTimeline("a1")
    m1 = MemoryMarker("m1", "POSITIVE", 0.5)
    m2 = MemoryMarker("m2", "POSITIVE", 0.4)

    timeline.add_memory(m1)
    timeline.add_memory(m2)

    assert timeline.associate_memories("m1", "m2") is True


def test_suppress_memory():
    """Test suppressing memory"""
    timeline = MemoryTimeline("a1")
    marker = MemoryMarker("m1", "NEGATIVE", -0.5)
    timeline.add_memory(marker)

    assert timeline.suppress_memory("m1") is True


def test_complete_visualization_workflow():
    """Test complete relationship and knowledge visualization"""
    # Create relationship graph
    rg = RelationshipGraph()
    rg.register_agent("a1", "Explorer")
    rg.register_agent("a2", "Helper")
    rg.add_relationship("a1", "a2", 0.4)
    rg.add_shared_goal("a1", "a2")
    rg.update_trust("a1", "a2", 0.3)

    # Create knowledge graph
    kg = KnowledgeGraph()
    kg.register_agent("a1")
    kg.add_knowledge_unit(KnowledgeNode("k1", "python", "SURFACE", 0.6))
    kg.add_knowledge_unit(KnowledgeNode("k2", "python", "INTERMEDIATE", 0.75))
    kg.add_prerequisite("k2", "k1")
    kg.teach_agent("a1", "k1")
    kg.teach_agent("a1", "k2")

    # Create memory timeline
    timeline = MemoryTimeline("a1")
    timeline.add_memory(MemoryMarker("mem1", "POSITIVE", 0.7))
    timeline.add_memory(MemoryMarker("mem2", "NEGATIVE", -0.4))
    timeline.add_memory(MemoryMarker("mem3", "NEUTRAL", 0.0))

    # Verify complete state
    assert rg.get_strongest_bonds("a1")[0].trust > 0.4
    assert "python" in kg.get_agent_expertise("a1")
    assert timeline.get_emotional_summary() != 0
    assert len(timeline.get_timeline()) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
