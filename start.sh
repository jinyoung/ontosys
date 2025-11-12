#!/bin/bash

# Event-Storming → Neo4j → VueFlow Startup Script

echo "🚀 Starting Event-Storming System..."

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Docker containers
echo "📦 Starting Docker containers (Neo4j, Redis)..."
docker-compose up -d

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
sleep 5

# Check if backend venv exists
if [ ! -d "backend/.venv" ]; then
    echo "🔧 Setting up backend environment..."
    cd backend
    
    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
    
    uv venv
    source .venv/bin/activate
    uv sync
    cd ..
else
    echo "✅ Backend environment exists"
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "🔧 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
else
    echo "✅ Frontend dependencies installed"
fi

# Start backend in background
echo "🐍 Starting backend server..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend development server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ System started successfully!"
echo ""
echo "📍 Access points:"
echo "   - Frontend:  http://localhost:5173"
echo "   - Backend:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/docs"
echo "   - Neo4j:     http://localhost:7474"
echo ""
echo "📝 Logs:"
echo "   - Backend:   tail -f backend.log"
echo "   - Frontend:  tail -f frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $FRONTEND_PID && docker-compose down"
echo ""



