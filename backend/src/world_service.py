"""Service for world creation and management."""
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from database import async_session_factory
from llm_world_generator import LLMWorldGenerator
from models.db_models import WorldDB
from sqlalchemy import select

logger = logging.getLogger(__name__)


class WorldService:
    """Service for creating and managing 2D grid worlds."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "agents.db"
        self.db_path = str(db_path)
        self.world_generator = LLMWorldGenerator()
        logger.debug(f"WorldService initialized with database at {self.db_path}")

    async def init_db(self):
        """Initialize database schema for worlds.

        Note: This method is now a no-op as database initialization
        is handled by database.init_db(). Kept for backward compatibility.
        """
        logger.info(f"Initializing world database schema at {self.db_path}")
        logger.info("Database schema creation delegated to database.init_db()")

    async def create_world_from_data(
        self,
        agent_id: str,
        world_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a world from pre-defined data (no LLM generation).

        Similar to how default agents work - allows creating starter worlds
        instantly without LLM generation overhead.

        Args:
            agent_id: ID of the agent this world belongs to
            world_data: Pre-defined world data with name, grid, etc.

        Returns:
            dict: Complete world data including generated id
        """
        logger.info(f"Creating default world '{world_data.get('name')}' for agent {agent_id}")

        # Generate unique ID
        world_id = str(uuid.uuid4())

        # Extract data with defaults
        name = world_data.get("name", "Unnamed World")
        description = world_data.get("description", "")
        grid = world_data.get("grid", [["G"] * 10 for _ in range(10)])
        width = world_data.get("width", 10)
        height = world_data.get("height", 10)
        game_type = world_data.get("game_type", "grid")
        agent_position = world_data.get("agent_position", [0, 0])

        # Serialize grid data to JSON
        grid_json = json.dumps(grid)

        # Store in database using SQLAlchemy
        async with async_session_factory() as session:
            db_world = WorldDB(
                id=world_id,
                agent_id=agent_id,
                name=name,
                description=description,
                grid_data=grid_json,
                agent_position_x=agent_position[0],
                agent_position_y=agent_position[1],
                width=width,
                height=height,
                game_type=game_type
            )
            session.add(db_world)
            await session.commit()

        logger.debug(f"Created default world {world_id} without LLM generation")

        # Return complete world data
        return {
            "id": world_id,
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "grid": grid,
            "width": width,
            "height": height,
            "game_type": game_type,
            "agent_position": agent_position,
            "created_at": datetime.now().isoformat()
        }

    async def create_world(self, agent_id: str, description: str) -> dict[str, Any]:
        """Create a new world for an agent.

        Args:
            agent_id: ID of the agent this world belongs to
            description: Natural language description of the desired world

        Returns:
            dict: Complete world data including id, grid, and agent position
        """
        logger.info(f"Creating world for agent {agent_id}: {description[:50]}...")

        # Generate world data using LLM
        world_data = await self.world_generator.generate_world(description)
        logger.debug(f"Generated world: {world_data.name}")

        # Generate unique ID
        world_id = str(uuid.uuid4())

        # Serialize grid data to JSON
        grid_json = json.dumps(world_data.grid)

        # Store in database using SQLAlchemy
        async with async_session_factory() as session:
            db_world = WorldDB(
                id=world_id,
                agent_id=agent_id,
                name=world_data.name,
                description=world_data.description,
                grid_data=grid_json,
                agent_position_x=world_data.agent_start[0],
                agent_position_y=world_data.agent_start[1],
                width=10,  # Width (always 10 for MVP)
                height=10,  # Height (always 10 for MVP)
            )
            session.add(db_world)
            await session.commit()

        # Return complete world data
        return {
            "id": world_id,
            "agent_id": agent_id,
            "name": world_data.name,
            "description": world_data.description,
            "grid": world_data.grid,
            "width": 10,
            "height": 10,
            "game_type": "grid_navigation",  # Default game type for MVP
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
        async with async_session_factory() as session:
            stmt = select(WorldDB).where(WorldDB.id == world_id)
            result = await session.execute(stmt)
            world = result.scalar_one_or_none()

            if world:
                grid_data = json.loads(world.grid_data)
                agent_position = [world.agent_position_x, world.agent_position_y]

                return {
                    "id": world.id,
                    "agent_id": world.agent_id,
                    "name": world.name,
                    "description": world.description,
                    "grid": grid_data,
                    "width": world.width,
                    "height": world.height,
                    "game_type": world.game_type,
                    "agent_position": agent_position,
                    "created_at": world.created_at.isoformat() if world.created_at else None
                }
            return None

    async def get_worlds_by_agent_id(self, agent_id: str) -> list[dict[str, Any]]:
        """Retrieve all worlds for a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            list: List of world data dictionaries
        """
        async with async_session_factory() as session:
            stmt = select(WorldDB).where(WorldDB.agent_id == agent_id).order_by(WorldDB.created_at.desc())
            result = await session.execute(stmt)
            worlds_db = result.scalars().all()

            worlds = []
            for world in worlds_db:
                grid_data = json.loads(world.grid_data)
                agent_position = [world.agent_position_x, world.agent_position_y]

                worlds.append({
                    "id": world.id,
                    "agent_id": world.agent_id,
                    "name": world.name,
                    "description": world.description,
                    "grid": grid_data,
                    "width": world.width,
                    "height": world.height,
                    "game_type": world.game_type,
                    "agent_position": agent_position,
                    "created_at": world.created_at.isoformat() if world.created_at else None
                })
            return worlds
