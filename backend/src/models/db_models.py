"""SQLAlchemy ORM models for database tables."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class AgentDB(Base):
    """ORM model for agents table."""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    backstory: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality_traits: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationship to worlds
    worlds: Mapped[list["WorldDB"]] = relationship(
        "WorldDB",
        back_populates="agent",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of AgentDB."""
        return f"<AgentDB(id={self.id}, name={self.name})>"


class WorldDB(Base):
    """ORM model for worlds table."""

    __tablename__ = "worlds"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    grid_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON stored as text
    agent_position_x: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_position_y: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationship to agent
    agent: Mapped["AgentDB"] = relationship("AgentDB", back_populates="worlds")

    def __repr__(self) -> str:
        """String representation of WorldDB."""
        return f"<WorldDB(id={self.id}, name={self.name}, agent_id={self.agent_id})>"


class ToolDB(Base):
    """ORM model for tools table."""

    __tablename__ = "tools"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # Movement, Perception, Interaction
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of ToolDB."""
        return f"<ToolDB(id={self.id}, name={self.name}, agent_id={self.agent_id})>"
