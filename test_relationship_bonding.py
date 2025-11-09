"""Round 22: Agent-Player Relationship & Bonding System"""
import pytest
from dataclasses import dataclass

@dataclass
class Relationship:
    player_id: str
    agent_id: str
    bond_level: float = 0.0  # 0.0-1.0
    trust: float = 0.0
    affection: float = 0.0
    interactions: int = 0
    
    def interact_with_agent(self) -> bool:
        self.interactions += 1
        self.bond_level = min(1.0, self.bond_level + 0.05)
        return True
    
    def increase_trust(self, amount: float) -> bool:
        self.trust = min(1.0, self.trust + amount)
        return True
    
    def show_affection(self, amount: float) -> bool:
        self.affection = min(1.0, self.affection + amount)
        return True
    
    def get_bond_status(self) -> str:
        if self.bond_level < 0.3:
            return "stranger"
        elif self.bond_level < 0.6:
            return "friend"
        elif self.bond_level < 0.85:
            return "close_friend"
        else:
            return "best_friend"

class RelationshipManager:
    def __init__(self):
        self.relationships = {}
    
    def create_relationship(self, player_id: str, agent_id: str) -> Relationship:
        rel = Relationship(player_id=player_id, agent_id=agent_id)
        self.relationships[f"{player_id}_{agent_id}"] = rel
        return rel
    
    def get_relationship(self, player_id: str, agent_id: str) -> Relationship:
        return self.relationships.get(f"{player_id}_{agent_id}")
    
    def get_total_bonds(self) -> int:
        return len(self.relationships)

def test_relationship_creation():
    rel = Relationship(player_id="p1", agent_id="a1")
    assert rel.bond_level == 0.0

def test_interaction():
    rel = Relationship(player_id="p1", agent_id="a1")
    assert rel.interact_with_agent() is True
    assert rel.interactions == 1
    assert rel.bond_level > 0.0

def test_trust_building():
    rel = Relationship(player_id="p1", agent_id="a1")
    assert rel.increase_trust(0.3) is True
    assert rel.trust == 0.3

def test_affection():
    rel = Relationship(player_id="p1", agent_id="a1")
    assert rel.show_affection(0.4) is True
    assert rel.affection == 0.4

def test_bond_status():
    rel = Relationship(player_id="p1", agent_id="a1")
    assert rel.get_bond_status() == "stranger"
    rel.bond_level = 0.5
    assert rel.get_bond_status() == "friend"
    rel.bond_level = 0.9
    assert rel.get_bond_status() == "best_friend"

def test_relationship_manager():
    mgr = RelationshipManager()
    rel = mgr.create_relationship("p1", "a1")
    assert mgr.get_relationship("p1", "a1") is not None
    assert mgr.get_total_bonds() == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
