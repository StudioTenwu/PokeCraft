#!/usr/bin/env python3
"""Quick integration test for tool-action architecture."""
import asyncio
import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

async def test_integration():
    """Test the full tool→action→game engine flow."""
    from world_service import WorldService
    from tool_service import ToolService
    from agent_deployer import AgentDeployer
    from action_registry import get_action_set_for_game, create_game_engine
    from database import init_db

    print("🔧 Initializing services...")
    await init_db()

    world_service = WorldService(db_path=":memory:")
    tool_service = ToolService(db_path="sqlite+aiosqlite:///:memory:", world_service=world_service)

    await world_service.init_db()
    await tool_service.init_db()

    # 1. Create a test world
    print("\n🌍 Creating test world...")
    world = await world_service.create_world(
        agent_id="test-agent-123",
        description="A simple 10x10 grid with a goal at (5,5)"
    )
    print(f"   ✅ World created: {world['id']}")
    print(f"   - Name: {world['name']}")
    print(f"   - Game type: {world['game_type']}")
    print(f"   - Agent position: {world['agent_position']}")

    # 2. Verify game_type is returned
    assert "game_type" in world, "game_type missing from world!"
    assert world["game_type"] == "grid_navigation", f"Expected grid_navigation, got {world['game_type']}"
    print("   ✅ game_type correctly included in response")

    # 3. Test game engine initialization
    print("\n⚙️  Testing game engine initialization...")
    action_set = get_action_set_for_game(world["game_type"])
    print(f"   - Action set loaded: {len(action_set.actions)} actions")
    print(f"   - Available actions: {', '.join([a.action_id for a in action_set.actions])}")

    game_engine = create_game_engine(
        world["game_type"],
        world["id"],
        action_set,
        world
    )
    print(f"   ✅ Game engine initialized: {game_engine.__class__.__name__}")

    # 4. Test action execution
    print("\n🎮 Testing action execution...")

    # Test move action
    result = game_engine.execute_action("move", {"direction": "south", "steps": 1})
    print(f"   - Move south result: {result.success}")
    print(f"   - Message: {result.message}")
    print(f"   - State delta: {result.state_delta}")

    assert result.success, "Move action should succeed"
    assert "agent_position" in result.state_delta, "Should return agent_position delta"
    print("   ✅ Action execution working correctly")

    # 5. Test invalid action
    print("\n❌ Testing invalid action handling...")
    result = game_engine.execute_action("fly", {"height": 100})
    assert not result.success, "Invalid action should fail"
    print(f"   - Error message: {result.error}")
    print("   ✅ Invalid actions properly rejected")

    # 6. Test tool service integration
    print("\n🔨 Testing tool service with game context...")
    # Note: This would require mocking the LLM, so we'll just verify the service is wired up
    assert tool_service.world_service is not None, "ToolService should have world_service"
    print("   ✅ ToolService correctly wired to WorldService")

    print("\n" + "="*60)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("="*60)
    print("\nThe tool-action architecture is fully integrated:")
    print("  ✓ Worlds return game_type")
    print("  ✓ Game engines initialize from world data")
    print("  ✓ Actions execute and return state deltas")
    print("  ✓ Invalid actions are properly rejected")
    print("  ✓ ToolService has access to game context")

if __name__ == "__main__":
    asyncio.run(test_integration())
