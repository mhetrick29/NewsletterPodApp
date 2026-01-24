#!/bin/bash

# Newsletter Podcast Agent - Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting Newsletter Podcast Agent..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Run this script from the newsletter-podcast-agent root directory"
    exit 1
fi

# Check for credentials
if [ ! -f "parsers/credentials.json" ]; then
    echo "⚠️  Warning: credentials.json not found in parsers/"
    echo "   You'll need to add your Google OAuth credentials before extraction works"
    echo ""
fi

# Start backend
echo "📦 Starting backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and start backend
source venv/bin/activate
pip install -q -r requirements.txt

echo "✅ Backend starting on http://localhost:8000"
python main.py &
BACKEND_PID=$!

cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo ""
echo "🎨 Starting frontend server..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

echo "✅ Frontend starting on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✨ Both servers started!"
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Keep script running
wait
