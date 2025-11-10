from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import sys
import json
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent_service import AgentService

app = FastAPI(title="AICraft - Pokémon Edition API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Initialize service
agent_service = AgentService()

class AgentCreateRequest(BaseModel):
    description: str

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await agent_service.init_db()
    print("✅ Database initialized")
    print("🚀 AICraft API running on http://localhost:8000")

@app.get("/")
async def root():
    return {
        "message": "AICraft - Pokémon Edition API",
        "version": "1.0",
        "endpoints": {
            "create_agent": "POST /api/agents/create",
            "get_agent": "GET /api/agents/{agent_id}"
        }
    }

@app.post("/api/agents/create")
async def create_agent(request: AgentCreateRequest):
    """Create a new AI agent."""
    try:
        agent = await agent_service.create_agent(request.description)
        return agent
    except Exception as e:
        print(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/create/stream")
async def create_agent_stream(request: AgentCreateRequest):
    """Create a new AI agent with real-time progress streaming via SSE."""

    async def event_generator():
        """Generator that yields SSE-formatted events."""
        try:
            async for event in agent_service.create_agent_stream(request.description):
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
            "X-Accel-Buffering": "no"  # Disable buffering for nginx
        }
    )

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent by ID."""
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
