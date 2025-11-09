"""Main FastAPI application with agent evolution endpoints."""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
from typing import Optional

from agent_handler import create_agent_handler
from stages import get_all_stages_info, get_stage_config, validate_stage

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Agent Engineering Playground API",
    description="Backend API for the interactive agent engineering course",
    version="0.1.0",
)

# CORS configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=False,  # Must be False when allow_origins=*
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    stage: int
    model: Optional[str] = "claude-sonnet-4-5-20250929"


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    tool_calls: list
    stage: int
    max_turns: int


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Agent Engineering Playground API",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "api_keys_configured": {
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY")),
        }
    }


@app.get("/api/stages")
async def get_stages():
    """Get information about all available stages.

    Returns:
        List of stage configurations with metadata
    """
    try:
        stages = get_all_stages_info()
        return {
            "success": True,
            "stages": stages,
            "total_stages": len(stages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stages/{stage_id}")
async def get_stage_detail(stage_id: int):
    """Get detailed information about a specific stage.

    Args:
        stage_id: Stage number (1-4)

    Returns:
        Detailed stage configuration
    """
    if not validate_stage(stage_id):
        raise HTTPException(
            status_code=404,
            detail=f"Stage {stage_id} not found. Valid stages are 1-4."
        )

    try:
        config = get_stage_config(stage_id)
        return {
            "success": True,
            "stage": stage_id,
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat requests with the agent.

    This endpoint supports both regular JSON responses and streaming.

    Args:
        request: ChatRequest with message, stage, and optional model

    Returns:
        ChatResponse with agent's reply and metadata
    """
    # Validate stage
    if not validate_stage(request.stage):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage: {request.stage}. Must be 1-4."
        )

    # Claude Agent SDK handles authentication automatically
    # No need to check ANTHROPIC_API_KEY explicitly

    try:
        # Create agent handler for the requested stage
        handler = create_agent_handler(request.stage, request.model)

        # Process the message
        result = await handler.chat(request.message)

        return {
            "success": True,
            **result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Handle streaming chat requests with the agent.

    Uses Server-Sent Events (SSE) to stream the response.

    Args:
        request: ChatRequest with message, stage, and optional model

    Returns:
        StreamingResponse with SSE events
    """
    # Validate stage
    if not validate_stage(request.stage):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage: {request.stage}. Must be 1-4."
        )

    # Claude Agent SDK handles authentication automatically
    # No need to check ANTHROPIC_API_KEY explicitly

    async def event_generator():
        """Generate SSE events from agent response."""
        try:
            handler = create_agent_handler(request.stage, request.model)

            # Stream responses
            async for chunk in handler.process_message(request.message):
                # Format as SSE
                event_data = json.dumps(chunk)
                yield f"data: {event_data}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            error_data = json.dumps({
                "type": "error",
                "error": str(e)
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/models")
async def get_available_models():
    """Get list of available Claude models.

    Returns:
        List of supported model IDs
    """
    return {
        "success": True,
        "models": [
            {
                "id": "claude-sonnet-4-5-20250929",
                "name": "Claude Sonnet 4.5",
                "description": "Latest Claude Sonnet model (recommended)"
            },
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "description": "Previous generation Sonnet"
            },
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "description": "Most capable Claude 3 model"
            }
        ],
        "default": "claude-sonnet-4-5-20250929"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
