import logging
import uuid
from pathlib import Path
from typing import Any

import aiosqlite
from avatar_generator import AvatarGenerator
from llm_client import LLMClient

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self, db_path: str | None = None) -> None:
        if db_path is None:
            self.db_path = str(Path(__file__).parent.parent / "agents.db")
        else:
            self.db_path = db_path
        self.llm_client: LLMClient = LLMClient()
        self.avatar_generator: AvatarGenerator = AvatarGenerator()
        logger.debug(f"AgentService initialized with database at {self.db_path}")

    async def init_db(self) -> None:
        """Initialize database schema."""
        logger.info(f"Initializing database at {self.db_path}")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS agents (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        backstory TEXT,
                        personality TEXT,
                        avatar_url TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                )
                await db.commit()
            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise

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

            # Store in database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT INTO agents (id, name, backstory, personality, avatar_url)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        agent_id,
                        agent_data.name,
                        agent_data.backstory,
                        ",".join(agent_data.personality_traits),
                        avatar_url,
                    ),
                )
                await db.commit()

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
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM agents WHERE id = ?", (agent_id,),
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        logger.info(f"Agent found: {row['name']} (ID: {agent_id})")
                        return {
                            "id": row["id"],
                            "name": row["name"],
                            "backstory": row["backstory"],
                            "personality_traits": row["personality"].split(",")
                            if row["personality"]
                            else [],
                            "avatar_url": row["avatar_url"],
                        }
                    else:
                        logger.warning(f"Agent not found: {agent_id}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching agent {agent_id}: {e}", exc_info=True)
            raise
