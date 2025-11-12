"""Standalone FastMCP server for AICraft game tools.

This MCP server can be run independently and connected to Claude Code.
It provides game tools for Pokemon-themed AI agents.

Usage:
    uv run fastmcp run game_tools_mcp_server.py
"""
from typing import Any
from fastmcp import FastMCP
from state_manager import state_manager

# Create FastMCP server instance
mcp = FastMCP("AICraft Game Tools")


@mcp.tool()
def move_direction(direction: str, steps: int = 1) -> str:
    """Move the agent in a cardinal direction (north, south, east, or west) for a specified number of steps.

    Args:
        direction: The direction to move (north, south, east, or west)
        steps: Number of steps to move (default: 1)

    Returns:
        A message about the move. Call observe_world() to see the actual result!
    """
    # Validate direction
    valid_directions = ['north', 'south', 'east', 'west']
    if direction.lower() not in valid_directions:
        return f"Invalid direction '{direction}'. Please use: north, south, east, or west."

    # Validate steps
    if steps < 1:
        return "Steps must be at least 1."

    direction_lower = direction.lower()

    return f"Moving {direction_lower} {steps} step{'s' if steps > 1 else ''}. Call observe_world() to see your new position!"


@mcp.tool()
def observe_world(world_id: str) -> str:
    """Get current world state, your position, and surroundings. Call this after every action to see what happened.

    Args:
        world_id: The ID of the world to observe

    Returns:
        A formatted view of the world showing your position and surroundings
    """
    world = state_manager.get_world(world_id)
    if not world:
        return f"Error: World {world_id} not found"

    # Format world state for agent
    position = world.get("agent_position", [0, 0])
    width = world.get("width", 10)
    height = world.get("height", 10)
    grid = world.get("grid", [])

    # Create 5x5 view around agent
    x, y = position
    view_lines = []
    for dy in range(-2, 3):
        row = []
        for dx in range(-2, 3):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                cell = grid[ny][nx] if grid else "."
                if dx == 0 and dy == 0:
                    cell = "A"  # Agent marker
                row.append(cell)
            else:
                row.append("#")  # Out of bounds
        view_lines.append("".join(row))

    grid_view = "\n".join(view_lines)

    result_text = f"""🗺️ WORLD STATE 🗺️

Current Position: [{x}, {y}]
World Size: {width}x{height}

5x5 View (A = You):
{grid_view}

Legend:
. = empty/path
# = boundary/obstacle/wall
W = water
T = treasure
G = grass
A = your position
"""

    return result_text


@mcp.tool()
def move_in_s_shape(size: int = 2) -> str:
    """Move Pixelmon in an S-shaped pattern on the grid. Perfect for exploring in a curvy snake pattern!

    Args:
        size: Size of the S pattern (1-3, default: 2)

    Returns:
        A message about starting the S-pattern movement
    """
    # Validate size
    if size < 1:
        size = 1
    elif size > 3:
        size = 3

    total_distance = size * 4
    return f"🐍 Pixelmon is moving in a cool S-shape! Starting by going right {size} steps. The S pattern will cover about {total_distance} spaces total!"


@mcp.tool()
def pixelmon_smiley_dance() -> str:
    """Makes Pixelmon dance in a smiley face pattern! Pixelmon will move around to trace a happy face shape on the grid.

    Returns:
        A message about Pixelmon's dance move
    """
    import random

    dance_moves = ["north", "east", "east", "south", "south", "west", "west", "north"]
    direction = random.choice(dance_moves)

    emojis = ["😊", "😄", "🎉", "✨", "💃", "🕺"]
    random_emoji = random.choice(emojis)

    messages = [
        f"Pixelmon is dancing in a smiley face pattern! {random_emoji}",
        f"Watch Pixelmon groove and move! Dancing {direction}! {random_emoji}",
        f"Pixelmon's happy dance continues! Spinning {direction}! {random_emoji}",
        f"Pixelmon dances joyfully in a smile shape! Moving {direction}! {random_emoji}",
    ]

    return random.choice(messages)


@mcp.tool()
def celebrate_pixelmon_birth(turns: int = 1) -> str:
    """Celebrate the birth of a new Pixelmon by waiting and watching the special moment.

    Args:
        turns: Number of turns to celebrate (default: 1)

    Returns:
        A celebratory message
    """
    return f"🎉 A new Pixelmon is born! Celebrating this magical moment for {turns} turn(s). Welcome to the world, little Pixelmon! 🥚✨"


if __name__ == "__main__":
    # Run as standalone MCP server with stdio transport
    mcp.run(transport="stdio")
