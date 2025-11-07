"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Agent Engineering Playground API",
    description="Backend API for the interactive agent engineering course",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Agent Engineering Playground API",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_keys_configured": {
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY")),
        }
    }


# Import and include routers (will be added later)
# from .routes import levels, agent, environment
# app.include_router(levels.router, prefix="/api/levels", tags=["levels"])
# app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
# app.include_router(environment.router, prefix="/api/environment", tags=["environment"])
