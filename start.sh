#!/bin/bash

echo "🚀 Starting AI Interviewer Application..."
echo ""

# Check if Python and Node.js are installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Python and Node.js are installed"
echo ""

# Start backend in background
echo "🔧 Starting Backend Server..."
cd backend
./start.sh &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 5

# Start frontend in background
echo "🎨 Starting Frontend Server..."
cd frontend
./start.sh &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 AI Interviewer is starting up!"
echo ""
echo "📱 Frontend: http://localhost:3015"
echo "🔌 Backend:  http://localhost:8015"
echo "📚 API Docs: http://localhost:8015/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait