"""Shared test fixtures for unit tests."""
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_api_key():
    """Mock ANTHROPIC_API_KEY environment variable for tests."""
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-api-key"}):
        yield
