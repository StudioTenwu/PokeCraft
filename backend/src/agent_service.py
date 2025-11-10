import logging
import uuid
from pathlib import Path
from typing import Any

from avatar_generator import AvatarGenerator
from database import async_session_factory
from llm_client import LLMClient
from models.db_models import AgentDB
from sqlalchemy import select

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self, db_path: str | None = None) -> None:
        # db_path parameter kept for backward compatibility but not used
        # SQLAlchemy engine configuration is now in database.py
        if db_path is None:
            self.db_path = str(Path(__file__).parent.parent / "agents.db")
        else:
            self.db_path = db_path
        self.llm_client: LLMClient = LLMClient()
        self.avatar_generator: AvatarGenerator = AvatarGenerator()
        logger.debug(f"AgentService initialized with database at {self.db_path}")

    async def init_db(self) -> None:
        """Initialize database schema.

        Note: This method is now a no-op as database initialization
        is handled by database.init_db(). Kept for backward compatibility.
        """
        logger.info(f"Initializing database at {self.db_path}")
        logger.info("Database schema creation delegated to database.init_db()")

    async def create_agent(self, description: str) -> dict[str, Any]:
        """Create a new agent with LLM generation and avatar."""
        logger.info(f"Creating agent from description: {description[:50]}...")

        try:
            # Generate agent data using LLM (Agent SDK)
            agent_data = await self.llm_client.generate_agent(description)
            logger.debug(f"LLM generated agent data: name={agent_data.name}")

            # Generate unique ID
            agent_id = str(uuid.uuid4())

            # Generate avatar
            avatar_url = self.avatar_generator.generate_avatar(
                agent_id, agent_data.avatar_prompt,
            )
            logger.info(f"Avatar generated: {avatar_url}")

            # Store in database using SQLAlchemy
            async with async_session_factory() as session:
                db_agent = AgentDB(
                    id=agent_id,
                    name=agent_data.name,
                    backstory=agent_data.backstory,
                    personality=",".join(agent_data.personality_traits),
                    avatar_url=avatar_url,
                )
                session.add(db_agent)
                await session.commit()

            logger.info(
                f"Agent created successfully: {agent_data.name} (ID: {agent_id})",
                extra={"agent_id": agent_id, "agent_name": agent_data.name}
            )

            # Return complete agent data
            return {
                "id": agent_id,
                "name": agent_data.name,
                "backstory": agent_data.backstory,
                "personality_traits": agent_data.personality_traits,
                "avatar_url": avatar_url,
            }
        except Exception as e:
            logger.error(f"Failed to create agent: {e}", exc_info=True)
            raise

    async def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        """Retrieve agent by ID."""
        logger.debug(f"Fetching agent with ID: {agent_id}")

        try:
            async with async_session_factory() as session:
                stmt = select(AgentDB).where(AgentDB.id == agent_id)
                result = await session.execute(stmt)
                agent = result.scalar_one_or_none()

                if agent:
                    logger.info(f"Agent found: {agent.name} (ID: {agent_id})")
                    return {
                        "id": agent.id,
                        "name": agent.name,
                        "backstory": agent.backstory,
                        "personality_traits": agent.personality.split(",")
                        if agent.personality
                        else [],
                        "avatar_url": agent.avatar_url,
                    }
                else:
                    logger.warning(f"Agent not found: {agent_id}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching agent {agent_id}: {e}", exc_info=True)
            raise
