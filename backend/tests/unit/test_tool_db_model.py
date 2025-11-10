"""Unit tests for ToolDB model."""
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.models.db_models import Base, ToolDB


class TestToolDBModel:
    """Test suite for ToolDB database model."""

    @pytest.fixture
    def session(self) -> Session:
        """Create an in-memory SQLite session for testing."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = Session(engine)
        yield session
        session.close()

    def test_tool_creation(self, session: Session) -> None:
        """Test creating a tool in the database."""
        tool = ToolDB(
            id="tool-123",
            agent_id="agent-456",
            name="move_forward",
            description="Move the agent forward",
            code="@tool(...)\nasync def move_forward(args): ...",
            category="Movement",
        )

        session.add(tool)
        session.commit()

        # Verify tool was created
        retrieved = session.query(ToolDB).filter_by(id="tool-123").first()
        assert retrieved is not None
        assert retrieved.name == "move_forward"
        assert retrieved.agent_id == "agent-456"
        assert retrieved.category == "Movement"

    def test_tool_unique_name(self, session: Session) -> None:
        """Test that tool names must be unique."""
        tool1 = ToolDB(
            id="tool-1",
            agent_id="agent-1",
            name="duplicate_name",
            code="code1",
        )
        tool2 = ToolDB(
            id="tool-2",
            agent_id="agent-2",
            name="duplicate_name",
            code="code2",
        )

        session.add(tool1)
        session.commit()

        # Adding second tool with same name should fail
        session.add(tool2)
        with pytest.raises(Exception):  # IntegrityError
            session.commit()

    def test_tool_created_at_auto_set(self, session: Session) -> None:
        """Test that created_at is automatically set."""
        tool = ToolDB(
            id="tool-789",
            agent_id="agent-123",
            name="test_tool",
            code="code",
        )

        session.add(tool)
        session.commit()

        retrieved = session.query(ToolDB).filter_by(id="tool-789").first()
        assert retrieved is not None
        assert isinstance(retrieved.created_at, datetime)

    def test_tool_optional_fields(self, session: Session) -> None:
        """Test that description and category are optional."""
        tool = ToolDB(
            id="tool-minimal",
            agent_id="agent-123",
            name="minimal_tool",
            code="code",
            # description and category omitted
        )

        session.add(tool)
        session.commit()

        retrieved = session.query(ToolDB).filter_by(id="tool-minimal").first()
        assert retrieved is not None
        assert retrieved.description is None
        assert retrieved.category is None

    def test_tool_repr(self, session: Session) -> None:
        """Test string representation of ToolDB."""
        tool = ToolDB(
            id="tool-repr",
            agent_id="agent-repr",
            name="repr_tool",
            code="code",
        )

        repr_str = repr(tool)
        assert "ToolDB" in repr_str
        assert "tool-repr" in repr_str
        assert "repr_tool" in repr_str
