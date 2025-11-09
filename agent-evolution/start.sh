#!/bin/bash

# Start script for Agent Evolution application

echo "🚀 Starting Agent Evolution Application..."
echo ""

# Check if backend .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env not found"
    echo "Please create backend/.env with your ANTHROPIC_API_KEY"
    exit 1
fi

# Start backend
echo "📡 Starting backend server on port 8001..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Start frontend
echo "🎨 Starting frontend server on port 5190..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

echo ""
echo "✅ Application started successfully!"
echo ""
echo "Frontend: http://localhost:5190"
echo "Backend:  http://localhost:8001"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop both servers, run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Opening browser..."

# Open browser
open http://localhost:5190

# Wait for user to press Ctrl+C
wait
