"""Integration tests for static file serving."""
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_avatar_file():
    """Create a test avatar file for testing static serving."""
    static_dir = Path(__file__).parent.parent.parent / "static" / "avatars"
    static_dir.mkdir(parents=True, exist_ok=True)

    test_file = static_dir / "test_avatar.png"
    # Create a minimal PNG file (1x1 transparent pixel)
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    test_file.write_bytes(png_data)

    yield test_file

    # Cleanup
    if test_file.exists():
        test_file.unlink()


def test_static_files_accessible(client, test_avatar_file):
    """Test that static files can be accessed via /static route."""
    response = client.get("/static/avatars/test_avatar.png")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers["content-type"].startswith("image/"), \
        f"Expected image content-type, got {response.headers['content-type']}"
    logger.info("✓ Static file accessible via /static route")


def test_cors_headers_on_static_files(client, test_avatar_file):
    """Test that CORS headers are present on static file responses."""
    response = client.get(
        "/static/avatars/test_avatar.png",
        headers={"Origin": "http://localhost:5173"}
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers, \
        "CORS header 'access-control-allow-origin' missing"
    logger.info("✓ CORS headers present on static files")


def test_missing_static_file_returns_404(client):
    """Test that requesting non-existent file returns 404."""
    response = client.get("/static/avatars/nonexistent.png")

    assert response.status_code == 404, \
        f"Expected 404 for missing file, got {response.status_code}"
    logger.info("✓ Missing files return 404")


@pytest.mark.asyncio
async def test_avatar_url_in_agent_response():
    """Test that agent response includes FULL URL format (not relative path).

    Per instructions: avatar_url should be http://localhost:8000/static/avatars/{id}.png
    NOT just /static/avatars/{id}.png

    Mock subprocess to simulate successful mflux generation so we can test the file path.
    """
    from unittest.mock import AsyncMock, patch, MagicMock
    from src.models.agent import AgentData
    from src.agent_service import AgentService
    from pathlib import Path

    # Mock only the LLM (expensive to call)
    mock_agent_data = AgentData(
        name="Test Agent",
        backstory="A test backstory",
        personality_traits=["friendly", "curious"],
        avatar_prompt="test prompt"
    )

    # Mock subprocess to simulate successful mflux run
    mock_subprocess_result = MagicMock()
    mock_subprocess_result.returncode = 0
    mock_subprocess_result.stderr = ""

    with patch("src.agent_service.LLMClient") as mock_llm, \
         patch("src.avatar_generator.subprocess.run", return_value=mock_subprocess_result):

        mock_llm.return_value.generate_agent = AsyncMock(return_value=mock_agent_data)

        # Create a real PNG file in the output directory to simulate mflux output
        service = AgentService(db_path=":memory:")
        await service.init_db()

        # We need to create a file before calling create_agent
        # Let's patch the AvatarGenerator to create a test file
        static_dir = Path(__file__).parent.parent.parent / "static" / "avatars"
        static_dir.mkdir(parents=True, exist_ok=True)

        # Patch Path.exists to return True for any avatar file
        original_exists = Path.exists
        def mock_exists(self):
            if str(self).endswith(".png") and "static/avatars" in str(self):
                # Create the file if it doesn't exist
                self.parent.mkdir(parents=True, exist_ok=True)
                if not original_exists(self):
                    # Create minimal PNG
                    png_data = (
                        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
                        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
                        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
                    )
                    self.write_bytes(png_data)
                return True
            return original_exists(self)

        with patch.object(Path, 'exists', mock_exists):
            result = await service.create_agent("A test agent")

    assert "avatar_url" in result, "avatar_url field missing from response"

    avatar_url = result["avatar_url"]
    assert avatar_url, "avatar_url should not be empty"

    # Test the REQUIREMENT: Must return FULL URL when it's a static file
    # Expected: http://localhost:8000/static/avatars/{id}.png
    # Currently returns: /static/avatars/{id}.png (WRONG!)
    if not avatar_url.startswith("data:"):
        # This is a static file - must be full URL
        assert avatar_url.startswith("http://localhost:8000/static/avatars/"), \
            f"avatar_url must be full URL like http://localhost:8000/static/avatars/{{id}}.png, got: {avatar_url}"
        assert avatar_url.endswith(".png"), \
            f"avatar_url should end with .png, got: {avatar_url}"
        logger.info(f"✓ Agent response has FULL URL: {avatar_url}")
    else:
        logger.info(f"✓ Agent response has fallback data URI: {avatar_url[:50]}...")


def test_static_directory_exists():
    """Test that the static/avatars directory exists."""
    static_dir = Path(__file__).parent.parent.parent / "static" / "avatars"

    assert static_dir.exists(), f"Static avatars directory should exist at {static_dir}"
    assert static_dir.is_dir(), f"Static avatars path should be a directory"

    logger.info(f"✓ Static directory exists at {static_dir}")
