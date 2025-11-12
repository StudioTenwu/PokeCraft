"""Simple test script for FastMCP deployment using existing agent and world."""
import asyncio
import os
import sys
from pathlib import Path

# Set API key
os.environ["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY", "")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent_deployer import AgentDeployer
from agent_service import AgentService
from world_service import WorldService
from tool_service import ToolService


async def test_simple_deployment():
    """Test deploying an agent with the FastMCP server using existing data."""

    # Initialize services
    agent_service = AgentService()
    world_service = WorldService()
    tool_service = ToolService()

    # Get existing agent (or create a simple one)
    agent_id = "test-pikachu"
    agent = await agent_service.get_agent(agent_id)

    if not agent:
        # Create test agent
        agent = await agent_service.create_agent_from_data(
            name="Test Pikachu",
            backstory="A small electric mouse Pokemon",
            personality_traits=["energetic", "loyal", "brave"],
            avatar_url="http://localhost:8000/static/pikachu.png"
        )
        agent_id = agent["id"]
        print(f"✅ Created agent: {agent['name']} (ID: {agent_id})")
    else:
        print(f"✅ Using existing agent: {agent['name']} (ID: {agent_id})")

    # Get existing world (or create a simple one)
    worlds = await world_service.get_agent_worlds(agent_id)

    if not worlds:
        # Create simple test world using the service's create method
        from models.world import WorldData
        world_data = WorldData(
            agent_id=agent_id,
            name="Test World",
            description="A simple test world",
            grid=[
                [".", ".", ".", ".", "."],
                [".", "#", ".", "T", "."],
                [".", ".", ".", ".", "."],
                [".", ".", "#", "#", "."],
                [".", ".", ".", ".", "."]
            ],
            width=5,
            height=5,
            agent_position=[1, 1],
            game_type="grid_navigation"
        )
        world = await world_service._create_world_internal(world_data)
        world_id = world["id"]
        print(f"✅ Created world: {world['name']} (ID: {world_id})")
    else:
        world = worlds[0]
        world_id = world["id"]
        print(f"✅ Using existing world: {world['name']} (ID: {world_id})")

    # Deploy agent
    deployer = AgentDeployer(tool_service, world_service)

    goal = "Move east one step"
    print(f"\n🚀 Deploying agent with goal: '{goal}'")
    print("=" * 60)

    event_count = 0
    tool_calls = 0
    tool_results = 0

    async for event in deployer.deploy_agent(agent_id, world_id, goal):
        event_count += 1
        event_type = event.event_type
        data = event.data

        if event_type == "system":
            text = data.get('text', '')
            print(f"[SYSTEM] {text[:150]}...")
        elif event_type == "thinking":
            print(f"[THINKING] {data.get('text', '')[:150]}...")
        elif event_type == "text":
            print(f"[TEXT] {data.get('text', '')}")
        elif event_type == "tool_call":
            tool_calls += 1
            tool_name = data.get('tool_name', '')
            params = data.get('parameters', {})
            print(f"[TOOL CALL #{tool_calls}] {tool_name}({params})")
        elif event_type == "tool_result":
            tool_results += 1
            tool_name = data.get('tool_name', '')
            result = data.get('result', '')
            success = data.get('success', False)
            print(f"[TOOL RESULT #{tool_results}] {tool_name}: {'✅' if success else '❌'}")
            if len(str(result)) < 300:
                print(f"  Result: {result}")
            else:
                print(f"  Result: {str(result)[:300]}...")
        elif event_type == "world_update":
            print(f"[WORLD UPDATE] {data}")
        elif event_type == "error":
            print(f"[ERROR] {data.get('message', '')}")
        elif event_type == "complete":
            print(f"\n[COMPLETE] Status: {data.get('status', 'unknown')}")
            print(f"  Goal achieved: {data.get('goal_achieved', False)}")
            print(f"  Steps: {data.get('total_steps', 0)}")
            print(f"  Tools used: {data.get('total_tools_used', 0)}")

    print("=" * 60)
    print(f"✅ Deployment completed!")
    print(f"   Total events: {event_count}")
    print(f"   Tool calls: {tool_calls}")
    print(f"   Tool results: {tool_results}")

    if tool_results == 0 and tool_calls > 0:
        print("❌ ISSUE: Tool calls were made but NO tool results received!")
        print("   This indicates the MCP server is not properly connected.")
        return False
    elif tool_results > 0:
        print("✅ SUCCESS: Tools are working correctly with FastMCP server!")
        return True
    else:
        print("⚠️  WARNING: No tools were called during deployment.")
        return True


if __name__ == "__main__":
    success = asyncio.run(test_simple_deployment())
    sys.exit(0 if success else 1)
