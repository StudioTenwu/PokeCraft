"""Tests for AgentDB model personality traits serialization."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.db_models import Base, AgentDB


class TestAgentDBPersonalityTraits:
    """Test personality traits storage and retrieval."""

    @pytest.fixture
    def db_session(self):
        """Create an in-memory SQLite database for testing."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_personality_traits_stored_as_json(self, db_session):
        """Personality traits should be stored as JSON, not comma-separated string."""
        agent = AgentDB(
            id="test-123",
            name="Test Agent",
            backstory="A test",
            personality_traits=["brave", "curious", "friendly"],
            avatar_url="http://test.com/avatar.png"
        )
        db_session.add(agent)
        db_session.commit()

        # Retrieve and verify
        retrieved = db_session.query(AgentDB).filter_by(id="test-123").first()
        assert retrieved is not None
        assert retrieved.personality_traits == ["brave", "curious", "friendly"]
        assert isinstance(retrieved.personality_traits, list)

    def test_empty_personality_traits(self, db_session):
        """Empty personality traits should be handled as empty list."""
        agent = AgentDB(
            id="test-456",
            name="Minimalist Agent",
            backstory="Simple",
            personality_traits=[],
            avatar_url="http://test.com/avatar.png"
        )
        db_session.add(agent)
        db_session.commit()

        retrieved = db_session.query(AgentDB).filter_by(id="test-456").first()
        assert retrieved.personality_traits == []
        assert isinstance(retrieved.personality_traits, list)

    def test_personality_traits_with_special_characters(self, db_session):
        """Personality traits with commas and quotes should be preserved."""
        traits = ["brave, fearless", "curious\"smart", "kind"]
        agent = AgentDB(
            id="test-789",
            name="Complex Agent",
            backstory="Complex",
            personality_traits=traits,
            avatar_url="http://test.com/avatar.png"
        )
        db_session.add(agent)
        db_session.commit()

        retrieved = db_session.query(AgentDB).filter_by(id="test-789").first()
        assert retrieved.personality_traits == traits
