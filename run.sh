#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo "🚀 Starting YouTube Style Analyzer..."

# Start Backend
echo "🐍 Starting Backend (FastAPI)..."
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv backend/venv
    source backend/venv/bin/activate
    pip install -r backend/requirements.txt
fi

# Run backend in background
cd backend
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Frontend
echo "⚛️  Starting Frontend (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Application is running!"
echo "📱 Frontend: http://localhost:3100"
echo "🔌 Backend: http://localhost:8000"
echo "Press Ctrl+C to stop."

wait
