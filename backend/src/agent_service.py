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
                    personality_traits=agent_data.personality_traits,
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

    async def create_agent_stream(self, description: str):
        """Create agent with streaming progress updates (async generator)."""
        logger.info(f"Creating agent (streaming) from: {description[:50]}...")

        try:
            # Step 1: LLM Start (0%)
            yield {
                "event": "llm_start",
                "data": {"status": "generating", "message": "Dreaming up your companion..."}
            }

            # Generate agent data with LLM
            agent_data = await self.llm_client.generate_agent(description)
            logger.debug(f"LLM generated: {agent_data.name}")

            # Step 2: LLM Complete (33%)
            yield {
                "event": "llm_complete",
                "data": {"name": agent_data.name, "message": f"Meet {agent_data.name}!"}
            }

            # Step 3: Avatar Start (33%)
            agent_id = str(uuid.uuid4())

            yield {
                "event": "avatar_start",
                "data": {"status": "generating", "message": "Hatching your companion..."}
            }

            # Step 4: Stream real avatar generation progress from mflux
            logger.info("Starting avatar generation streaming...")
            async for progress_event in self.avatar_generator.generate_avatar_stream(
                agent_id, agent_data.avatar_prompt
            ):
                logger.debug(f"Received progress_event: {progress_event}")

                if progress_event["type"] == "avatar_progress":
                    # Map mflux progress (25-100) to our scale (33-100)
                    # Formula: 33 + ((progress - 25) * 67/75)
                    mflux_progress = progress_event["progress"]
                    overall_percent = int(33 + ((mflux_progress - 25) * 67 / 75))

                    logger.info(f"🎨 Avatar progress: mflux={mflux_progress}% → overall={overall_percent}% (33-100 scale)")

                    yield {
                        "event": "avatar_progress",
                        "data": {
                            "percent": overall_percent,
                            "message": progress_event.get("message", "Drawing...")
                        }
                    }
                    logger.info(f"✓ Sent avatar_progress SSE event with percent={overall_percent}%")
                elif progress_event["type"] == "avatar_complete":
                    avatar_url = progress_event["avatar_url"]
                    logger.info(f"Avatar generated: {avatar_url}")

                    # Final progress update at 100%
                    yield {
                        "event": "avatar_progress",
                        "data": {
                            "percent": 100,
                            "message": "Avatar complete!"
                        }
                    }

                    # Avatar complete event
                    yield {
                        "event": "avatar_complete",
                        "data": {"avatar_url": avatar_url}
                    }

            # Step 3: Save to database
            yield {
                "event": "progress",
                "data": {"status": "saving", "message": "Saving to Pokédex..."}
            }

            async with async_session_factory() as session:
                db_agent = AgentDB(
                    id=agent_id,
                    name=agent_data.name,
                    backstory=agent_data.backstory,
                    personality_traits=agent_data.personality_traits,
                    avatar_url=avatar_url,
                )
                session.add(db_agent)
                await session.commit()

            logger.info(f"Agent created: {agent_data.name} (ID: {agent_id})")

            # Step 4: Yield complete event
            yield {
                "event": "complete",
                "data": {
                    "agent": {
                        "id": agent_id,
                        "name": agent_data.name,
                        "backstory": agent_data.backstory,
                        "personality_traits": agent_data.personality_traits,
                        "avatar_url": avatar_url,
                    }
                }
            }

        except Exception as e:
            logger.error(f"Failed to create agent (streaming): {e}", exc_info=True)
            yield {
                "event": "error",
                "data": {"message": str(e)}
            }

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
                        "personality_traits": agent.personality_traits or [],
                        "avatar_url": agent.avatar_url,
                    }
                else:
                    logger.warning(f"Agent not found: {agent_id}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching agent {agent_id}: {e}", exc_info=True)
            raise
