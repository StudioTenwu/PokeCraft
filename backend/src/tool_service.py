"""Service for managing custom tools."""
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models.db_models import Base, ToolDB
from tool_generator import ToolGenerator
from tool_registry import append_tool_to_file

logger = logging.getLogger(__name__)


class ToolService:
    """Service for creating, retrieving, and deleting custom tools."""

    def __init__(self, db_path: str = "sqlite+aiosqlite:///agents.db") -> None:
        """
        Initialize the ToolService.

        Args:
            db_path: Path to SQLite database (async URL)
        """
        self.db_path = db_path
        self.engine = create_async_engine(self.db_path, echo=False)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.tool_generator = ToolGenerator()

    async def init_db(self) -> None:
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tool database initialized")

    async def create_tool(self, agent_id: str, description: str) -> dict[str, Any]:
        """
        Create a new custom tool for an agent.

        Args:
            agent_id: ID of the agent this tool is for
            description: Natural language description of the tool

        Returns:
            Dictionary with tool_name, code, explanation, and tool_id
        """
        logger.info(f"Creating tool for agent {agent_id}: {description[:50]}...")

        # Generate tool code using LLM
        tool_code_obj = await self.tool_generator.generate_tool(description, agent_id)

        # Append tool to tools.py file
        append_tool_to_file(tool_code_obj.code)

        # Save to database
        tool_id = str(uuid.uuid4())
        tool_db = ToolDB(
            id=tool_id,
            agent_id=agent_id,
            name=tool_code_obj.tool_name,
            description=description,
            code=tool_code_obj.code,
            category=None,  # Could be inferred from description in future
        )

        async with self.session_factory() as session:
            session.add(tool_db)
            await session.commit()
            await session.refresh(tool_db)

        logger.info(f"Tool created: {tool_code_obj.tool_name} (ID: {tool_id})")

        return {
            "tool_name": tool_code_obj.tool_name,
            "code": tool_code_obj.code,
            "explanation": tool_code_obj.explanation,
            "tool_id": tool_id,
        }

    async def get_agent_tools(self, agent_id: str) -> list[dict[str, Any]]:
        """
        Get all tools for a specific agent.

        Args:
            agent_id: ID of the agent

        Returns:
            List of tool dictionaries
        """
        logger.info(f"Fetching tools for agent {agent_id}")

        async with self.session_factory() as session:
            result = await session.execute(
                select(ToolDB).where(ToolDB.agent_id == agent_id).order_by(ToolDB.created_at.desc())
            )
            tools = result.scalars().all()

            return [
                {
                    "id": tool.id,
                    "agent_id": tool.agent_id,
                    "name": tool.name,
                    "description": tool.description,
                    "code": tool.code,
                    "category": tool.category,
                    "created_at": tool.created_at.isoformat(),
                }
                for tool in tools
            ]

    async def delete_tool(self, tool_name: str) -> bool:
        """
        Delete a tool by name.

        Args:
            tool_name: Name of the tool to delete

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting tool: {tool_name}")

        async with self.session_factory() as session:
            result = await session.execute(select(ToolDB).where(ToolDB.name == tool_name))
            tool = result.scalar_one_or_none()

            if not tool:
                logger.warning(f"Tool not found: {tool_name}")
                return False

            await session.delete(tool)
            await session.commit()

        logger.info(f"Tool deleted: {tool_name}")
        return True
