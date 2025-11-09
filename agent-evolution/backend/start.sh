#!/bin/bash

# Start script for Agent Evolution Prototype Backend

echo "Starting Agent Evolution Backend..."
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and add your ANTHROPIC_API_KEY"
    exit 1
fi

# Check if ANTHROPIC_API_KEY is set
source .env
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" == "sk-ant-YOUR-KEY-HERE" ]; then
    echo "ERROR: ANTHROPIC_API_KEY is not configured in .env file!"
    echo "Please add your API key from https://console.anthropic.com/"
    exit 1
fi

# Use Python 3.11 (required for claude-agent-sdk)
PYTHON="/opt/homebrew/opt/python@3.11/bin/python3.11"

# Check if requirements are installed
if ! $PYTHON -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    $PYTHON -m pip install -r requirements.txt
    echo ""
fi

# Start the server
echo "Starting FastAPI server on port 8001..."
echo "API Docs will be available at: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
$PYTHON -m uvicorn src.api.main:app --reload --port 8001 --host 0.0.0.0
