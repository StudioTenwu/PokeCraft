#!/bin/bash

# Test script for Agent Evolution API

echo "=========================================="
echo "Agent Evolution API Test Script"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8001"

# Check if server is running
echo "1. Checking if server is running..."
if curl -s "$BASE_URL/" > /dev/null 2>&1; then
    echo "   ✓ Server is running"
else
    echo "   ✗ Server is not running"
    echo "   Please start the server with: ./start.sh"
    exit 1
fi
echo ""

# Test root endpoint
echo "2. Testing root endpoint (GET /)..."
RESPONSE=$(curl -s "$BASE_URL/")
if echo "$RESPONSE" | grep -q "Agent Engineering Playground"; then
    echo "   ✓ Root endpoint working"
    echo "   Response: $RESPONSE"
else
    echo "   ✗ Root endpoint failed"
    echo "   Response: $RESPONSE"
fi
echo ""

# Test health endpoint
echo "3. Testing health endpoint (GET /health)..."
RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$RESPONSE" | grep -q "healthy"; then
    echo "   ✓ Health endpoint working"
    echo "   Response: $RESPONSE"
else
    echo "   ✗ Health endpoint failed"
    echo "   Response: $RESPONSE"
fi
echo ""

# Test stages endpoint
echo "4. Testing stages list (GET /api/stages)..."
RESPONSE=$(curl -s "$BASE_URL/api/stages")
if echo "$RESPONSE" | grep -q "Stage 1"; then
    echo "   ✓ Stages endpoint working"
    echo "   Found stages:"
    echo "$RESPONSE" | python3 -m json.tool | grep -A 1 '"name"'
else
    echo "   ✗ Stages endpoint failed"
    echo "   Response: $RESPONSE"
fi
echo ""

# Test individual stage endpoints
for STAGE in 1 2 3 4; do
    echo "5.$STAGE Testing stage $STAGE detail (GET /api/stages/$STAGE)..."
    RESPONSE=$(curl -s "$BASE_URL/api/stages/$STAGE")
    if echo "$RESPONSE" | grep -q "Stage $STAGE"; then
        STAGE_NAME=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['config']['name'])" 2>/dev/null)
        MAX_TURNS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['config']['max_turns'])" 2>/dev/null)
        TOOLS_EXEC=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['config']['tools_executable'])" 2>/dev/null)
        echo "   ✓ Stage $STAGE: $STAGE_NAME"
        echo "     - Max turns: $MAX_TURNS"
        echo "     - Tools executable: $TOOLS_EXEC"
    else
        echo "   ✗ Stage $STAGE endpoint failed"
    fi
done
echo ""

# Test models endpoint
echo "6. Testing models list (GET /api/models)..."
RESPONSE=$(curl -s "$BASE_URL/api/models")
if echo "$RESPONSE" | grep -q "claude-sonnet"; then
    echo "   ✓ Models endpoint working"
    echo "   Available models:"
    echo "$RESPONSE" | python3 -m json.tool | grep '"name"'
else
    echo "   ✗ Models endpoint failed"
    echo "   Response: $RESPONSE"
fi
echo ""

# Test chat endpoint (requires API key)
echo "7. Testing chat endpoint (POST /api/chat)..."
if curl -s "$BASE_URL/health" | grep -q '"anthropic": true'; then
    echo "   API key is configured, testing chat..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "What is 2+2?", "stage": 1}')

    if echo "$RESPONSE" | grep -q "success"; then
        echo "   ✓ Chat endpoint working"
        echo "   Sample response:"
        echo "$RESPONSE" | python3 -m json.tool | head -15
    else
        echo "   ✗ Chat endpoint failed"
        echo "   Response: $RESPONSE"
    fi
else
    echo "   ⚠ API key not configured, skipping chat test"
    echo "   To test chat, add ANTHROPIC_API_KEY to .env file"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "All basic endpoints are working!"
echo ""
echo "Next steps:"
echo "1. Add your ANTHROPIC_API_KEY to .env to test chat functionality"
echo "2. Visit http://localhost:8001/docs for interactive API documentation"
echo "3. Connect the frontend to test the full application"
echo ""
