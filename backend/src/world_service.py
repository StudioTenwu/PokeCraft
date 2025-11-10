"""Service for world creation and management."""
import aiosqlite
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from llm_world_generator import LLMWorldGenerator


class WorldService:
    """Service for creating and managing 2D grid worlds."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "agents.db"
        self.db_path = str(db_path)
        self.world_generator = LLMWorldGenerator()

    async def init_db(self):
        """Initialize database schema for worlds."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS worlds (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    grid_data TEXT NOT NULL,
                    agent_position_x INTEGER NOT NULL,
                    agent_position_y INTEGER NOT NULL,
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def create_world(self, agent_id: str, description: str) -> dict[str, Any]:
        """Create a new world for an agent.

        Args:
            agent_id: ID of the agent this world belongs to
            description: Natural language description of the desired world

        Returns:
            dict: Complete world data including id, grid, and agent position
        """
        # Generate world data using LLM
        world_data = await self.world_generator.generate_world(description)

        # Generate unique ID
        world_id = str(uuid.uuid4())

        # Serialize grid data to JSON
        grid_json = json.dumps(world_data.grid)

        # Store in database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO worlds (id, agent_id, name, description, grid_data, agent_position_x, agent_position_y, width, height)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    world_id,
                    agent_id,
                    world_data.name,
                    world_data.description,
                    grid_json,
                    world_data.agent_start[0],
                    world_data.agent_start[1],
                    10,  # Width (always 10 for MVP)
                    10,  # Height (always 10 for MVP)
                )
            )
            await db.commit()

        # Return complete world data
        return {
            "id": world_id,
            "agent_id": agent_id,
            "name": world_data.name,
            "description": world_data.description,
            "grid": world_data.grid,
            "width": 10,
            "height": 10,
            "agent_position": world_data.agent_start,
            "created_at": datetime.now().isoformat()
        }

    async def get_world(self, world_id: str) -> dict[str, Any] | None:
        """Retrieve world by ID.

        Args:
            world_id: Unique world identifier

        Returns:
            dict: World data or None if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM worlds WHERE id = ?", (world_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    grid_data = json.loads(row["grid_data"])
                    agent_position = [row["agent_position_x"], row["agent_position_y"]]

                    return {
                        "id": row["id"],
                        "agent_id": row["agent_id"],
                        "name": row["name"],
                        "description": row["description"],
                        "grid": grid_data,
                        "width": row["width"],
                        "height": row["height"],
                        "agent_position": agent_position,
                        "created_at": row["created_at"]
                    }
                return None

    async def get_worlds_by_agent_id(self, agent_id: str) -> list[dict[str, Any]]:
        """Retrieve all worlds for a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            list: List of world data dictionaries
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM worlds WHERE agent_id = ? ORDER BY created_at DESC",
                (agent_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                worlds = []
                for row in rows:
                    grid_data = json.loads(row["grid_data"])
                    agent_position = [row["agent_position_x"], row["agent_position_y"]]

                    worlds.append({
                        "id": row["id"],
                        "agent_id": row["agent_id"],
                        "name": row["name"],
                        "description": row["description"],
                        "grid": grid_data,
                        "width": row["width"],
                        "height": row["height"],
                        "agent_position": agent_position,
                        "created_at": row["created_at"]
                    })
                return worlds
