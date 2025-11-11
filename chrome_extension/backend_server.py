#!/usr/bin/env python3
"""
Standalone backend server for AICraft Chrome Extension.
Uses Claude Agent SDK to provide real AI chat responses.

Usage:
    python backend_server.py

Then the Chrome extension can connect to http://localhost:8080/chat
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock
from typing import Optional
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="AICraft Extension Backend")

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Chrome extension
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory chat history storage (per agent)
# Structure: { "agent_id": [ {"role": "user", "content": "..."}, ... ] }
chat_histories: dict[str, list[dict[str, str]]] = {}

# In-memory pending agents queue (for agent export/import)
# Structure: [ {"id": "...", "name": "...", "avatar_url": "...", ...}, ... ]
pending_agents: list[dict] = []


class AgentData(BaseModel):
    id: str
    name: str
    backstory: str
    personality_traits: list[str]


class ChatRequest(BaseModel):
    message: str
    agent_data: AgentData
    clear_history: Optional[bool] = False  # Optional flag to clear history


@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat messages using Claude Agent SDK with conversation history."""
    try:
        agent_id = request.agent_data.id

        # Clear history if requested (e.g., when switching agents)
        if request.clear_history:
            if agent_id in chat_histories:
                chat_histories[agent_id] = []
            logger.info(f"Cleared history for agent: {agent_id}")
            return {"response": ""}  # Early return, don't process message

        # Initialize chat history for new agent
        if agent_id not in chat_histories:
            chat_histories[agent_id] = []

        # Get conversation history for this agent
        history = chat_histories[agent_id]

        # Build system prompt from agent data
        personality_str = ", ".join(request.agent_data.personality_traits)
        system_prompt = f"""{request.agent_data.backstory}

Personality traits: {personality_str}

You are {request.agent_data.name}. Respond in character, keeping your responses concise and friendly (2-3 sentences max).

Previous conversation context:
{format_history(history)}"""

        # Configure Claude Agent SDK
        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            model="haiku",  # Use Haiku model for fast, cost-effective responses
            permission_mode='bypassPermissions',
            max_turns=1,
        )

        # Query Claude with current message
        response_text = ""
        async for message in query(prompt=request.message, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text

        if not response_text:
            response_text = f"Pika pika! I'm {request.agent_data.name}!"

        # Add to chat history (keep last 10 exchanges to avoid token limits)
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": response_text})

        # Trim history to last 10 exchanges (20 messages)
        if len(history) > 20:
            history = history[-20:]
            chat_histories[agent_id] = history

        return {"response": response_text}

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def format_history(history: list[dict[str, str]]) -> str:
    """Format chat history for system prompt."""
    if not history:
        return "No previous conversation."

    formatted = []
    for msg in history[-10:]:  # Only include last 5 exchanges
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted.append(f"{role}: {msg['content']}")

    return "\n".join(formatted)


@app.post("/agents/queue")
async def queue_agent(agent_data: dict):
    """Queue an agent for loading into the extension.

    Called by AICraft frontend to send agent data to extension.
    Extension will poll /agents/pending to fetch queued agents.
    """
    # Validate agent data
    required_fields = ['id', 'name', 'avatar_url', 'backstory', 'personality_traits']
    for field in required_fields:
        if field not in agent_data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

    # Add to pending queue
    pending_agents.append(agent_data)
    logger.info(f"Queued agent for export: {agent_data['name']} (id: {agent_data['id']})")

    return {
        "status": "queued",
        "agent_id": agent_data['id'],
        "agent_name": agent_data['name']
    }


@app.get("/agents/pending")
async def get_pending_agents():
    """Get list of pending agents waiting to be loaded into extension.

    Extension polls this endpoint to fetch new agents.
    Returns and clears the pending queue.
    """
    global pending_agents

    agents = pending_agents.copy()
    pending_agents.clear()  # Clear after fetching

    if agents:
        logger.info(f"Returning {len(agents)} pending agent(s) to extension")

    return {"agents": agents, "count": len(agents)}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AICraft Extension Backend"}


if __name__ == "__main__":
    print("🎮 Starting AICraft Extension Backend Server...")
    print("📡 Extension can connect to: http://localhost:8080/chat")
    print("💡 Press Ctrl+C to stop\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
