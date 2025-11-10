import aiosqlite
import uuid
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator
from llm_client import LLMClient
from avatar_generator import AvatarGenerator

class AgentService:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "agents.db"
        self.db_path = str(db_path)
        self.llm_client = LLMClient()
        self.avatar_generator = AvatarGenerator()

    async def init_db(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    backstory TEXT,
                    personality TEXT,
                    avatar_url TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def create_agent(self, description: str) -> dict:
        """Create a new agent with LLM generation and avatar."""
        # Generate agent data using LLM (Agent SDK)
        agent_data = await self.llm_client.generate_agent(description)

        # Generate unique ID
        agent_id = str(uuid.uuid4())

        # Generate avatar
        avatar_url = self.avatar_generator.generate_avatar(
            agent_id,
            agent_data.get("avatar_prompt", "cute AI companion")
        )

        # Store in database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO agents (id, name, backstory, personality, avatar_url)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    agent_id,
                    agent_data["name"],
                    agent_data["backstory"],
                    ",".join(agent_data["personality_traits"]),
                    avatar_url
                )
            )
            await db.commit()

        # Return complete agent data
        return {
            "id": agent_id,
            "name": agent_data["name"],
            "backstory": agent_data["backstory"],
            "personality_traits": agent_data["personality_traits"],
            "avatar_url": avatar_url
        }

    async def get_agent(self, agent_id: str) -> dict:
        """Retrieve agent by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM agents WHERE id = ?", (agent_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "id": row["id"],
                        "name": row["name"],
                        "backstory": row["backstory"],
                        "personality_traits": row["personality"].split(",") if row["personality"] else [],
                        "avatar_url": row["avatar_url"]
                    }
                return None

    async def create_agent_stream(self, description: str) -> AsyncGenerator[dict, None]:
        """
        Create a new agent with real-time progress streaming.

        Yields SSE-compatible events:
        - llm_start: LLM generation started
        - llm_complete: LLM generation complete with agent data
        - avatar_start: Avatar generation started
        - avatar_progress: Avatar generation progress updates
        - avatar_complete: Avatar generation complete with URL
        - complete: Agent creation complete with full data
        - error: Error occurred during creation
        """
        try:
            # Step 1: Generate agent data using LLM
            yield {
                "event": "llm_start",
                "data": {"message": "Dreaming up your companion..."}
            }

            agent_data = await self.llm_client.generate_agent(description)

            yield {
                "event": "llm_complete",
                "data": {
                    "name": agent_data.name,
                    "backstory": agent_data.backstory,
                    "personality_traits": agent_data.personality_traits
                }
            }

            # Step 2: Generate avatar with progress streaming
            agent_id = str(uuid.uuid4())

            yield {
                "event": "avatar_start",
                "data": {"message": "Hatching your companion..."}
            }

            # Stream avatar generation progress
            avatar_url = None
            for progress_update in self.avatar_generator.generate_avatar_stream(
                agent_id,
                agent_data.avatar_prompt
            ):
                if progress_update.get("type") == "complete":
                    # Final yield with avatar URL
                    avatar_url = progress_update["avatar_url"]
                else:
                    # This is a progress update
                    yield {
                        "event": "avatar_progress",
                        "data": progress_update
                    }

            # If no avatar URL from generator, use fallback
            if avatar_url is None:
                avatar_url = self.avatar_generator._get_fallback_avatar()

            yield {
                "event": "avatar_complete",
                "data": {"avatar_url": avatar_url}
            }

            # Step 3: Save to database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT INTO agents (id, name, backstory, personality, avatar_url)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        agent_id,
                        agent_data.name,
                        agent_data.backstory,
                        ",".join(agent_data.personality_traits),
                        avatar_url
                    )
                )
                await db.commit()

            # Step 4: Return complete agent
            complete_agent = {
                "id": agent_id,
                "name": agent_data.name,
                "backstory": agent_data.backstory,
                "personality_traits": agent_data.personality_traits,
                "avatar_url": avatar_url
            }

            yield {
                "event": "complete",
                "data": {"agent": complete_agent}
            }

        except Exception as e:
            print(f"Error in create_agent_stream: {e}")
            yield {
                "event": "error",
                "data": {"message": str(e)}
            }
