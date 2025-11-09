"""
Round 44: Community System
Enable players to discover, share, trade tools and agents with other players.
Features: tool library, agent marketplace, leaderboards, community features.
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class PublishStatus(Enum):
    """Status of shared resource"""
    DRAFT = "draft"
    PUBLISHED = "published"
    FEATURED = "featured"
    ARCHIVED = "archived"


class MarketplaceCategory(Enum):
    """Categories for marketplace items"""
    LEARNING_TOOLS = "learning_tools"
    REASONING = "reasoning"
    CREATIVE = "creative"
    UTILITY = "utility"
    CUSTOM = "custom"


@dataclass
class PublishedTool:
    """Tool shared in community library"""
    tool_id: str
    name: str
    description: str
    author_id: str
    reliability: float  # 0.0-1.0
    category: MarketplaceCategory
    download_count: int = 0
    rating: float = 0.5  # 0.0-5.0
    review_count: int = 0
    status: PublishStatus = PublishStatus.PUBLISHED
    created_at: float = 0.0
    tags: List[str] = field(default_factory=list)

    def add_download(self) -> bool:
        """Record download"""
        self.download_count += 1
        return True

    def add_review(self, rating: float) -> bool:
        """Add review and update rating"""
        if not (0.0 <= rating <= 5.0):
            return False

        new_total = (self.rating * self.review_count) + rating
        self.review_count += 1
        self.rating = new_total / self.review_count
        return True

    def to_dict(self) -> Dict:
        return {
            "id": self.tool_id,
            "name": self.name,
            "author": self.author_id,
            "reliability": self.reliability,
            "category": self.category.value,
            "downloads": self.download_count,
            "rating": round(self.rating, 2),
            "reviews": self.review_count,
            "status": self.status.value
        }


@dataclass
class PublishedAgent:
    """Agent shared in marketplace"""
    agent_id: str
    name: str
    description: str
    author_id: str
    personality_traits: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)
    purchase_price: float = 0.0  # Community currency
    times_purchased: int = 0
    rating: float = 0.5  # 0.0-5.0
    review_count: int = 0
    status: PublishStatus = PublishStatus.PUBLISHED
    created_at: float = 0.0

    def purchase(self) -> bool:
        """Record agent purchase"""
        self.times_purchased += 1
        return True

    def add_review(self, rating: float) -> bool:
        """Add review and update rating"""
        if not (0.0 <= rating <= 5.0):
            return False

        new_total = (self.rating * self.review_count) + rating
        self.review_count += 1
        self.rating = new_total / self.review_count
        return True

    def to_dict(self) -> Dict:
        return {
            "id": self.agent_id,
            "name": self.name,
            "author": self.author_id,
            "traits": len(self.personality_traits),
            "expertise": len(self.expertise_areas),
            "price": self.purchase_price,
            "purchases": self.times_purchased,
            "rating": round(self.rating, 2),
            "reviews": self.review_count
        }


@dataclass
class LeaderboardEntry:
    """Entry in community leaderboard"""
    rank: int
    agent_id: str
    player_id: str
    agent_name: str
    metric_type: str  # "expertise", "quests_completed", "relationships", etc.
    metric_value: float
    timestamp: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "rank": self.rank,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "player_id": self.player_id,
            "metric": self.metric_type,
            "value": self.metric_value
        }


class ToolLibrary:
    """Community library for shared tools"""

    def __init__(self):
        self.tools: Dict[str, PublishedTool] = {}
        self.featured_tools: List[str] = []
        self.categories: Dict[str, List[str]] = {}  # category -> tool_ids

    def publish_tool(self, tool: PublishedTool) -> bool:
        """Add tool to library"""
        if tool.tool_id in self.tools:
            return False

        self.tools[tool.tool_id] = tool

        # Add to category
        if tool.category not in self.categories:
            self.categories[tool.category] = []
        self.categories[tool.category].append(tool.tool_id)

        return True

    def get_tool(self, tool_id: str) -> Optional[PublishedTool]:
        """Get tool by ID"""
        return self.tools.get(tool_id)

    def search_tools(self, query: str) -> List[PublishedTool]:
        """Search tools by name/description"""
        results = []
        query_lower = query.lower()
        for tool in self.tools.values():
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower()):
                results.append(tool)
        return results

    def get_category_tools(self, category: MarketplaceCategory) -> List[PublishedTool]:
        """Get all tools in category"""
        if category not in self.categories:
            return []

        tool_ids = self.categories[category]
        return [self.tools[tid] for tid in tool_ids if tid in self.tools]

    def get_trending_tools(self, limit: int = 10) -> List[PublishedTool]:
        """Get most downloaded tools"""
        sorted_tools = sorted(
            self.tools.values(),
            key=lambda t: t.download_count,
            reverse=True
        )
        return sorted_tools[:limit]

    def get_top_rated_tools(self, limit: int = 10) -> List[PublishedTool]:
        """Get highest rated tools"""
        sorted_tools = sorted(
            self.tools.values(),
            key=lambda t: t.rating,
            reverse=True
        )
        return sorted_tools[:limit]

    def feature_tool(self, tool_id: str) -> bool:
        """Feature a tool on marketplace"""
        if tool_id not in self.tools:
            return False

        self.tools[tool_id].status = PublishStatus.FEATURED
        if tool_id not in self.featured_tools:
            self.featured_tools.append(tool_id)
        return True

    def to_dict(self) -> Dict:
        return {
            "total_tools": len(self.tools),
            "featured": len(self.featured_tools),
            "categories": len(self.categories)
        }


class AgentMarketplace:
    """Marketplace for buying/selling/trading agents"""

    def __init__(self):
        self.agents: Dict[str, PublishedAgent] = {}
        self.player_purchases: Dict[str, List[str]] = {}  # player_id -> agent_ids
        self.featured_agents: List[str] = []

    def publish_agent(self, agent: PublishedAgent) -> bool:
        """List agent for sale/trade"""
        if agent.agent_id in self.agents:
            return False

        self.agents[agent.agent_id] = agent
        return True

    def purchase_agent(self, player_id: str, agent_id: str) -> bool:
        """Player purchases agent"""
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]
        if not agent.purchase():
            return False

        if player_id not in self.player_purchases:
            self.player_purchases[player_id] = []
        self.player_purchases[player_id].append(agent_id)

        return True

    def get_player_purchases(self, player_id: str) -> List[PublishedAgent]:
        """Get agents player has purchased"""
        if player_id not in self.player_purchases:
            return []

        agent_ids = self.player_purchases[player_id]
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def get_popular_agents(self, limit: int = 10) -> List[PublishedAgent]:
        """Get most purchased agents"""
        sorted_agents = sorted(
            self.agents.values(),
            key=lambda a: a.times_purchased,
            reverse=True
        )
        return sorted_agents[:limit]

    def feature_agent(self, agent_id: str) -> bool:
        """Feature agent on marketplace"""
        if agent_id not in self.agents:
            return False

        self.agents[agent_id].status = PublishStatus.FEATURED
        if agent_id not in self.featured_agents:
            self.featured_agents.append(agent_id)
        return True

    def to_dict(self) -> Dict:
        return {
            "total_agents": len(self.agents),
            "featured": len(self.featured_agents),
            "total_purchases": sum(len(v) for v in self.player_purchases.values())
        }


class Leaderboard:
    """Track top agents by various metrics"""

    def __init__(self):
        self.entries: Dict[str, List[LeaderboardEntry]] = {}  # metric -> entries

    def add_entry(self, metric_type: str, entry: LeaderboardEntry) -> bool:
        """Add entry to leaderboard"""
        if metric_type not in self.entries:
            self.entries[metric_type] = []

        self.entries[metric_type].append(entry)

        # Keep top 100 by sorting and truncating
        self.entries[metric_type].sort(
            key=lambda e: e.metric_value,
            reverse=True
        )
        self.entries[metric_type] = self.entries[metric_type][:100]

        # Update ranks
        for idx, entry in enumerate(self.entries[metric_type]):
            entry.rank = idx + 1

        return True

    def get_leaderboard(self, metric_type: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top entries for metric"""
        if metric_type not in self.entries:
            return []

        return self.entries[metric_type][:limit]

    def get_agent_rank(self, metric_type: str, agent_id: str) -> Optional[int]:
        """Get agent's rank for metric"""
        if metric_type not in self.entries:
            return None

        for entry in self.entries[metric_type]:
            if entry.agent_id == agent_id:
                return entry.rank

        return None

    def to_dict(self) -> Dict:
        return {
            "metrics": len(self.entries),
            "total_entries": sum(len(v) for v in self.entries.values())
        }


class CommunityManager:
    """Central manager for all community features"""

    def __init__(self):
        self.tool_library = ToolLibrary()
        self.agent_marketplace = AgentMarketplace()
        self.leaderboard = Leaderboard()
        self.player_profiles: Dict[str, Dict] = {}  # player_id -> profile

    def create_player_profile(self, player_id: str, player_name: str) -> bool:
        """Create community profile for player"""
        if player_id in self.player_profiles:
            return False

        self.player_profiles[player_id] = {
            "player_id": player_id,
            "name": player_name,
            "tools_shared": 0,
            "agents_shared": 0,
            "reputation": 0.5,  # 0.0-1.0
            "followers": 0
        }
        return True

    def publish_tool_to_community(self, tool: PublishedTool) -> bool:
        """Publish player's tool"""
        if tool.author_id not in self.player_profiles:
            return False

        if not self.tool_library.publish_tool(tool):
            return False

        self.player_profiles[tool.author_id]["tools_shared"] += 1
        return True

    def publish_agent_to_community(self, agent: PublishedAgent) -> bool:
        """Publish player's agent"""
        if agent.author_id not in self.player_profiles:
            return False

        if not self.agent_marketplace.publish_agent(agent):
            return False

        self.player_profiles[agent.author_id]["agents_shared"] += 1
        return True

    def purchase_agent(self, player_id: str, agent_id: str) -> bool:
        """Player purchases agent"""
        return self.agent_marketplace.purchase_agent(player_id, agent_id)

    def review_tool(self, tool_id: str, rating: float) -> bool:
        """Add review to tool"""
        tool = self.tool_library.get_tool(tool_id)
        if not tool:
            return False

        if not tool.add_review(rating):
            return False

        # Update author reputation
        if tool.author_id in self.player_profiles:
            self.player_profiles[tool.author_id]["reputation"] += 0.01

        return True

    def get_community_stats(self) -> Dict:
        """Get overall community statistics"""
        return {
            "total_players": len(self.player_profiles),
            "tools_shared": self.tool_library.to_dict()["total_tools"],
            "agents_available": self.agent_marketplace.to_dict()["total_agents"],
            "marketplace_data": self.agent_marketplace.to_dict()
        }

    def to_dict(self) -> Dict:
        return {
            "players": len(self.player_profiles),
            "library": self.tool_library.to_dict(),
            "marketplace": self.agent_marketplace.to_dict(),
            "leaderboard": self.leaderboard.to_dict()
        }


# ===== Tests =====

def test_published_tool_creation():
    """Test creating published tool"""
    tool = PublishedTool(
        "tool1", "TextProcessor", "Process text",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    assert tool.tool_id == "tool1"
    assert tool.name == "TextProcessor"


def test_tool_download():
    """Test recording tool download"""
    tool = PublishedTool(
        "tool1", "Tool", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    assert tool.download_count == 0
    assert tool.add_download() is True
    assert tool.download_count == 1


def test_tool_review():
    """Test adding review to tool"""
    tool = PublishedTool(
        "tool1", "Tool", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    assert tool.add_review(4.5) is True
    assert tool.rating == 4.5
    assert tool.review_count == 1


def test_tool_review_multiple():
    """Test multiple reviews update rating correctly"""
    tool = PublishedTool(
        "tool1", "Tool", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    assert tool.add_review(5.0) is True
    assert tool.add_review(3.0) is True
    assert tool.rating == 4.0  # Average of 5 and 3


def test_published_agent_creation():
    """Test creating published agent"""
    agent = PublishedAgent(
        "agent1", "LearningBot", "Helps with learning",
        "player1", purchase_price=100.0
    )
    assert agent.agent_id == "agent1"
    assert agent.name == "LearningBot"
    assert agent.purchase_price == 100.0


def test_agent_purchase():
    """Test agent purchase tracking"""
    agent = PublishedAgent(
        "agent1", "Bot", "Desc",
        "player1", purchase_price=100.0
    )
    assert agent.times_purchased == 0
    assert agent.purchase() is True
    assert agent.times_purchased == 1


def test_tool_library_publish():
    """Test publishing tool to library"""
    library = ToolLibrary()
    tool = PublishedTool(
        "tool1", "Tool", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    assert library.publish_tool(tool) is True
    assert library.get_tool("tool1") is not None


def test_tool_library_duplicate_rejection():
    """Test library rejects duplicate tool"""
    library = ToolLibrary()
    tool = PublishedTool(
        "tool1", "Tool", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    assert library.publish_tool(tool) is True
    assert library.publish_tool(tool) is False


def test_tool_library_search():
    """Test searching tools"""
    library = ToolLibrary()
    tool1 = PublishedTool(
        "tool1", "TextProcessor", "Process text",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    tool2 = PublishedTool(
        "tool2", "Calculator", "Math tool",
        "author2", 0.85, MarketplaceCategory.UTILITY
    )
    library.publish_tool(tool1)
    library.publish_tool(tool2)

    results = library.search_tools("text")
    assert len(results) == 1
    assert results[0].tool_id == "tool1"


def test_tool_library_category():
    """Test getting tools by category"""
    library = ToolLibrary()
    tool1 = PublishedTool(
        "tool1", "Tool1", "Desc",
        "author1", 0.9, MarketplaceCategory.LEARNING_TOOLS
    )
    tool2 = PublishedTool(
        "tool2", "Tool2", "Desc",
        "author2", 0.85, MarketplaceCategory.UTILITY
    )
    library.publish_tool(tool1)
    library.publish_tool(tool2)

    learning = library.get_category_tools(MarketplaceCategory.LEARNING_TOOLS)
    assert len(learning) == 1


def test_tool_library_trending():
    """Test getting trending tools"""
    library = ToolLibrary()
    tool1 = PublishedTool(
        "tool1", "Popular", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    tool2 = PublishedTool(
        "tool2", "Less popular", "Desc",
        "author2", 0.85, MarketplaceCategory.UTILITY
    )
    library.publish_tool(tool1)
    library.publish_tool(tool2)

    tool1.add_download()
    tool1.add_download()
    tool1.add_download()

    trending = library.get_trending_tools(1)
    assert len(trending) == 1
    assert trending[0].tool_id == "tool1"


def test_tool_library_feature():
    """Test featuring tool"""
    library = ToolLibrary()
    tool = PublishedTool(
        "tool1", "Tool", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    library.publish_tool(tool)

    assert library.feature_tool("tool1") is True
    assert tool.status == PublishStatus.FEATURED


def test_agent_marketplace_publish():
    """Test publishing agent to marketplace"""
    marketplace = AgentMarketplace()
    agent = PublishedAgent(
        "agent1", "Bot", "Desc",
        "player1", purchase_price=100.0
    )
    assert marketplace.publish_agent(agent) is True
    assert agent in marketplace.agents.values()


def test_agent_marketplace_purchase():
    """Test purchasing agent"""
    marketplace = AgentMarketplace()
    agent = PublishedAgent(
        "agent1", "Bot", "Desc",
        "player1", purchase_price=100.0
    )
    marketplace.publish_agent(agent)

    assert marketplace.purchase_agent("player2", "agent1") is True
    assert agent.times_purchased == 1
    assert "agent1" in marketplace.player_purchases.get("player2", [])


def test_agent_marketplace_popular():
    """Test getting popular agents"""
    marketplace = AgentMarketplace()
    agent1 = PublishedAgent(
        "agent1", "Popular", "Desc",
        "player1", purchase_price=100.0
    )
    agent2 = PublishedAgent(
        "agent2", "Less popular", "Desc",
        "player2", purchase_price=50.0
    )
    marketplace.publish_agent(agent1)
    marketplace.publish_agent(agent2)

    marketplace.purchase_agent("player3", "agent1")
    marketplace.purchase_agent("player3", "agent1")

    popular = marketplace.get_popular_agents(1)
    assert len(popular) == 1
    assert popular[0].agent_id == "agent1"


def test_leaderboard_entry():
    """Test leaderboard entry"""
    entry = LeaderboardEntry(
        1, "agent1", "player1", "SmartBot",
        "expertise", 0.95
    )
    assert entry.agent_id == "agent1"
    assert entry.metric_value == 0.95


def test_leaderboard_add_entry():
    """Test adding entry to leaderboard"""
    lb = Leaderboard()
    entry = LeaderboardEntry(
        0, "agent1", "player1", "Bot",
        "expertise", 0.95
    )
    assert lb.add_entry("expertise", entry) is True


def test_leaderboard_ranking():
    """Test leaderboard ranking"""
    lb = Leaderboard()
    e1 = LeaderboardEntry(0, "agent1", "p1", "Bot1", "expertise", 0.9)
    e2 = LeaderboardEntry(0, "agent2", "p2", "Bot2", "expertise", 0.95)

    lb.add_entry("expertise", e1)
    lb.add_entry("expertise", e2)

    top = lb.get_leaderboard("expertise", 2)
    assert len(top) == 2
    assert top[0].agent_id == "agent2"  # Highest score first


def test_leaderboard_get_rank():
    """Test getting agent rank"""
    lb = Leaderboard()
    e1 = LeaderboardEntry(0, "agent1", "p1", "Bot1", "expertise", 0.9)
    e2 = LeaderboardEntry(0, "agent2", "p2", "Bot2", "expertise", 0.95)

    lb.add_entry("expertise", e1)
    lb.add_entry("expertise", e2)

    rank = lb.get_agent_rank("expertise", "agent2")
    assert rank == 1


def test_community_manager_player_profile():
    """Test creating player profile"""
    manager = CommunityManager()
    assert manager.create_player_profile("player1", "Alice") is True
    assert "player1" in manager.player_profiles


def test_community_manager_publish_tool():
    """Test publishing tool through manager"""
    manager = CommunityManager()
    manager.create_player_profile("author1", "Bob")

    tool = PublishedTool(
        "tool1", "Tool", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )

    assert manager.publish_tool_to_community(tool) is True


def test_community_manager_publish_agent():
    """Test publishing agent through manager"""
    manager = CommunityManager()
    manager.create_player_profile("player1", "Alice")

    agent = PublishedAgent(
        "agent1", "Bot", "Desc",
        "player1", purchase_price=100.0
    )

    assert manager.publish_agent_to_community(agent) is True


def test_community_manager_review():
    """Test reviewing tool"""
    manager = CommunityManager()
    manager.create_player_profile("author1", "Bob")

    tool = PublishedTool(
        "tool1", "Tool", "Desc",
        "author1", 0.9, MarketplaceCategory.UTILITY
    )
    manager.publish_tool_to_community(tool)

    assert manager.review_tool("tool1", 5.0) is True
    assert tool.rating == 5.0


def test_community_stats():
    """Test getting community statistics"""
    manager = CommunityManager()
    manager.create_player_profile("player1", "Alice")
    manager.create_player_profile("player2", "Bob")

    stats = manager.get_community_stats()
    assert stats["total_players"] == 2


def test_complete_community_workflow():
    """Test complete community workflow"""
    manager = CommunityManager()

    # Players create profiles
    assert manager.create_player_profile("author1", "ToolMaker") is True
    assert manager.create_player_profile("breeder1", "AgentBreeder") is True
    assert manager.create_player_profile("buyer1", "Collector") is True

    # Author publishes tool
    tool = PublishedTool(
        "tool_counter", "Counter", "Counting tool",
        "author1", 0.92, MarketplaceCategory.UTILITY
    )
    assert manager.publish_tool_to_community(tool) is True

    # Breeder publishes agent
    agent = PublishedAgent(
        "agent_smart", "SmartBot", "High capability agent",
        "breeder1", purchase_price=150.0
    )
    agent.personality_traits = ["curious", "analytical"]
    agent.expertise_areas = ["reasoning", "learning"]
    assert manager.publish_agent_to_community(agent) is True

    # Buyer purchases agent
    assert manager.purchase_agent("buyer1", "agent_smart") is True
    assert agent.times_purchased == 1

    # Buyer reviews tool
    assert manager.review_tool("tool_counter", 4.5) is True

    # Check community stats
    stats = manager.get_community_stats()
    assert stats["total_players"] == 3
    assert stats["tools_shared"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
