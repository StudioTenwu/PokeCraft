"""FastAPI backend for the Agent Evolution demo."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import json

from tools import TOOL_DEFINITIONS
from custom_handler import get_stage_handler

load_dotenv()

app = FastAPI(title="Agent Evolution API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5190", "http://127.0.0.1:5190"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str | List[Dict[str, Any]]


class AgentConfig(BaseModel):
    systemPrompt: str | None = None
    tools: List[str] | None = None
    executableTools: List[str] | None = None
    maxTurns: int | None = None
    chainingStrategy: str | None = None


class ChatRequest(BaseModel):
    messages: List[Message]
    stage: int
    config: AgentConfig | None = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Agent Evolution API"}


@app.get("/api/tools")
async def get_tools():
    """Get available tool definitions."""
    return {"tools": TOOL_DEFINITIONS}


@app.get("/api/stages")
async def get_stages():
    """Get information about all stages."""
    return {
        "stages": [
            {
                "id": 1,
                "name": "Basic Chat",
                "description": "Simple conversation loop with message history",
                "capabilities": ["Chat", "Remember context"],
                "key_activity": {
                    "title": "Plan a Birthday Party",
                    "prompt": "I'm planning a birthday party for my friend. Can you help me think through what I need to organize?"
                }
            },
            {
                "id": 2,
                "name": "Tool Recognition",
                "description": "Agent understands available tools",
                "capabilities": ["Chat", "Recognize tools", "Explain tool usage"],
                "key_activity": {
                    "title": "Find Party Ideas Online",
                    "prompt": "Can you search the web for creative birthday party ideas and themes?"
                }
            },
            {
                "id": 3,
                "name": "Tool Execution",
                "description": "Agent executes tools and processes results",
                "capabilities": ["Chat", "Execute tools", "Process results"],
                "key_activity": {
                    "title": "Save Party Plan",
                    "prompt": "Search for birthday party ideas and save the best ones to a file called party_ideas.txt"
                }
            },
            {
                "id": 4,
                "name": "Multi-Tool Composition",
                "description": "Agent chains multiple tools intelligently",
                "capabilities": ["Chat", "Chain tools", "Complex reasoning", "Multi-step tasks"],
                "key_activity": {
                    "title": "Complete Party Research",
                    "prompt": "Research birthday party ideas, create a comprehensive party plan document with themes, activities, and budget considerations, then organize it into sections"
                }
            }
        ]
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Stream chat responses based on the current stage."""

    # Validate stage
    if request.stage not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Invalid stage. Must be 1, 2, 3, or 4.")

    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    # Convert messages to the format expected by the API
    messages = []
    for msg in request.messages:
        if isinstance(msg.content, str):
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        else:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

    # Convert config to dict if provided
    config_dict = None
    if request.config:
        config_dict = request.config.model_dump()

    # Get the appropriate stage handler with custom config
    handler = get_stage_handler(api_key, request.stage, config_dict)

    async def event_stream():
        """Stream events to the client."""
        try:
            async for event in handler.process_message(messages, request.stage):
                yield f"data: {event}\n"
        except Exception as e:
            error_event = json.dumps({
                "type": "error",
                "error": str(e)
            })
            yield f"data: {error_event}\n"
        finally:
            # Send done event
            done_event = json.dumps({
                "type": "done"
            })
            yield f"data: {done_event}\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
