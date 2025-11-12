"""Test script to deploy an agent using the FastMCP server."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent_deployer import AgentDeployer
from agent_service import AgentService
from world_service import WorldService
from tool_service import ToolService


async def test_deployment():
    """Test deploying an agent with the FastMCP server."""

    # Initialize services
    agent_service = AgentService()
    world_service = WorldService()
    tool_service = ToolService()

    # Create test agent
    agent = await agent_service.create_agent_from_data(
        name="Test Pikachu",
        backstory="A small electric mouse Pokemon",
        personality_traits=["energetic", "loyal", "brave"],
        avatar_url="http://localhost:8000/static/pikachu.png"
    )
    print(f"✅ Created agent: {agent['name']} (ID: {agent['id']})")

    # Create test world
    world_data = {
        "agent_id": agent["id"],
        "name": "Test World",
        "description": "A simple test world",
        "grid": [
            [".", ".", ".", ".", "."],
            [".", "#", ".", "T", "."],
            [".", ".", ".", ".", "."],
            [".", ".", "#", "#", "."],
            [".", ".", ".", ".", "."]
        ],
        "width": 5,
        "height": 5,
        "agent_position": [1, 1],
        "game_type": "grid_navigation"
    }

    world = await world_service.create_world_from_data(world_data)
    print(f"✅ Created world: {world['name']} (ID: {world['id']})")

    # Deploy agent
    deployer = AgentDeployer(tool_service, world_service)

    goal = "Move east one step"
    print(f"\n🚀 Deploying agent with goal: '{goal}'")
    print("=" * 60)

    async for event in deployer.deploy_agent(agent["id"], world["id"], goal):
        event_type = event.event_type
        data = event.data

        if event_type == "system":
            print(f"[SYSTEM] {data.get('text', '')[:100]}")
        elif event_type == "thinking":
            print(f"[THINKING] {data.get('text', '')[:150]}")
        elif event_type == "text":
            print(f"[TEXT] {data.get('text', '')}")
        elif event_type == "tool_call":
            tool_name = data.get('tool_name', '')
            params = data.get('parameters', {})
            print(f"[TOOL CALL] {tool_name}({params})")
        elif event_type == "tool_result":
            tool_name = data.get('tool_name', '')
            result = data.get('result', '')
            success = data.get('success', False)
            print(f"[TOOL RESULT] {tool_name}: {'✅' if success else '❌'} {result[:200]}")
        elif event_type == "world_update":
            print(f"[WORLD UPDATE] {data}")
        elif event_type == "error":
            print(f"[ERROR] {data.get('message', '')}")
        elif event_type == "complete":
            print(f"[COMPLETE] Status: {data.get('status', 'unknown')}")
            print(f"  Goal achieved: {data.get('goal_achieved', False)}")
            print(f"  Steps: {data.get('total_steps', 0)}")
            print(f"  Tools used: {data.get('total_tools_used', 0)}")

    print("=" * 60)
    print("✅ Deployment completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_deployment())
