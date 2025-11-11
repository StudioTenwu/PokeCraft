import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent_service import AgentService
from config import Config
from database import init_db
from logging_config import setup_logging
from models.tool import ToolCreateRequest, ToolCreateResponse, ToolResponse
from tool_service import ToolService
from world_service import WorldService

# Initialize logging
setup_logging(
    level=Config.LOG_LEVEL,
    log_dir=Config.LOG_DIR,
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    # Startup: Initialize database schema
    logger.info("Initializing database schema...")
    await init_db()

    # Initialize services
    logger.info("Initializing services...")

    agent_service = AgentService()
    world_service = WorldService()
    tool_service = ToolService(world_service=world_service)

    await agent_service.init_db()
    await world_service.init_db()
    await tool_service.init_db()

    # Store in app.state for dependency injection
    app.state.agent_service = agent_service
    app.state.world_service = world_service
    app.state.tool_service = tool_service

    logger.info("Database initialized")
    logger.info("AICraft API running on http://localhost:8000")

    yield  # Application runs here

    # Shutdown: Cleanup resources (if needed in future)
    logger.info("Shutting down services...")
    # Future: Close database connections, cleanup resources

# Create app with lifespan
app = FastAPI(
    title="AICraft - Pokemon Edition API",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

class AgentCreateRequest(BaseModel):
    description: str

class WorldCreateRequest(BaseModel):
    agent_id: str
    description: str

@app.get("/")
async def root():
    return {
        "message": "AICraft - Pokemon Edition API",
        "version": "1.0",
        "endpoints": {
            "create_agent": "POST /api/agents/create",
            "get_agent": "GET /api/agents/{agent_id}",
            "create_world": "POST /api/worlds/create",
            "get_world": "GET /api/worlds/{world_id}",
            "get_worlds_by_agent": "GET /api/worlds/agent/{agent_id}",
            "get_world_actions": "GET /api/actions/{world_id}",
            "create_tool": "POST /api/tools/create",
            "get_agent_tools": "GET /api/tools/agent/{agent_id}",
            "delete_tool": "DELETE /api/tools/{tool_name}",
            "deploy_agent": "GET /api/agents/deploy (SSE stream)",
        },
    }

@app.post("/api/agents/create")
async def create_agent(request: AgentCreateRequest, req: Request):
    """Create a new AI agent."""
    try:
        agent = await req.app.state.agent_service.create_agent(request.description)
        return agent
    except Exception as e:
        logger.error(f"Error creating agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/create/stream")
async def create_agent_stream(description: str, req: Request):
    """Create a new AI agent with real-time progress streaming via SSE."""

    async def event_generator():
        """Generator that yields SSE-formatted events."""
        try:
            async for event in req.app.state.agent_service.create_agent_stream(description):
                event_name = event.get("event", "message")
                event_data = event.get("data", {})

                # Format as SSE: event: name\ndata: json\n\n
                sse_message = f"event: {event_name}\ndata: {json.dumps(event_data)}\n\n"
                yield sse_message

                # Small delay to ensure client receives message
                await asyncio.sleep(0.01)

        except Exception as e:
            # Send error event
            error_event = f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
            yield error_event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering for nginx
        },
    )

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str, req: Request):
    """Get agent by ID."""
    agent = await req.app.state.agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.get("/health")
async def health():
    return {"status": "healthy"}

# World endpoints
@app.post("/api/worlds/create")
async def create_world(request: WorldCreateRequest, req: Request):
    """Create a new world for an agent."""
    try:
        world = await req.app.state.world_service.create_world(request.agent_id, request.description)
        return world
    except Exception as e:
        logger.error(f"Error creating world: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/actions/{world_id}")
async def get_world_actions(world_id: str, req: Request):
    """Get available actions for a world's game type."""
    # Fetch world
    world = await req.app.state.world_service.get_world(world_id)
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    # Get action set for game type
    from action_registry import get_action_set_for_game
    action_set = get_action_set_for_game(world["game_type"])

    if not action_set:
        raise HTTPException(status_code=500, detail=f"No action set found for game type: {world['game_type']}")

    # Group actions by category
    grouped_actions: dict[str, list[dict[str, Any]]] = {
        "Movement": [],
        "Perception": [],
        "Interaction": []
    }

    for action in action_set.actions:
        category = action.category or "Interaction"
        if category not in grouped_actions:
            grouped_actions[category] = []

        grouped_actions[category].append({
            "action_id": action.action_id,
            "name": action.name,
            "description": action.description,
            "parameters": [
                {"name": p.name, "type": p.type, "description": p.description}
                for p in action.parameters
            ]
        })

    return {
        "world": {
            "id": world["id"],
            "name": world["name"],
            "width": world.get("width", 10),
            "height": world.get("height", 10),
            "game_type": world["game_type"]
        },
        "actions": grouped_actions
    }

@app.get("/api/worlds/{world_id}")
async def get_world(world_id: str, req: Request):
    """Get world by ID."""
    world = await req.app.state.world_service.get_world(world_id)
    if not world:
        raise HTTPException(status_code=404, detail="World not found")
    return world

@app.get("/api/worlds/agent/{agent_id}")
async def get_worlds_by_agent(agent_id: str, req: Request):
    """Get all worlds for a specific agent."""
    worlds = await req.app.state.world_service.get_worlds_by_agent_id(agent_id)
    return worlds

# Tool endpoints
@app.post("/api/tools/create")
async def create_tool(request: ToolCreateRequest, req: Request):
    """Create a new custom tool for an agent."""
    try:
        result = await req.app.state.tool_service.create_tool(
            request.agent_id,
            request.world_id,
            request.description
        )
        return ToolCreateResponse(**result)
    except Exception as e:
        logger.error(f"Error creating tool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools/agent/{agent_id}")
async def get_agent_tools(agent_id: str, req: Request):
    """Get all tools for a specific agent."""
    try:
        tools = await req.app.state.tool_service.get_agent_tools(agent_id)
        return [ToolResponse(**tool) for tool in tools]
    except Exception as e:
        logger.error(f"Error fetching tools: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tools/{tool_name}")
async def delete_tool(tool_name: str, req: Request):
    """Delete a tool by name."""
    try:
        success = await req.app.state.tool_service.delete_tool(tool_name)
        if not success:
            raise HTTPException(status_code=404, detail="Tool not found")
        return {"message": f"Tool {tool_name} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/deploy")
async def deploy_agent(agent_id: str, world_id: str, goal: str, req: Request):
    """Deploy an agent in a world with SSE streaming.

    Args:
        agent_id: UUID of the agent to deploy
        world_id: UUID of the world to deploy in
        goal: Mission goal for the agent
    """

    async def event_generator():
        """Generator that yields SSE-formatted events."""
        # Import here to avoid circular dependencies
        from agent_deployer import AgentDeployer

        deployer = AgentDeployer(
            req.app.state.tool_service, req.app.state.world_service
        )

        async for event in deployer.deploy_agent(
            agent_id, world_id, goal
        ):
            # Convert DeploymentEvent to SSE format
            sse_message = f"event: {event.event_type}\ndata: {json.dumps(event.data)}\n\n"
            yield sse_message

            # Small delay to ensure client receives message
            await asyncio.sleep(0.01)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
