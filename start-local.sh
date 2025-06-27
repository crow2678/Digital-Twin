#!/bin/bash

echo "🚀 Starting Digital Twin Voice Intelligence Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check main web app
if curl -s http://localhost:80/health > /dev/null; then
    echo "✅ Web App: Running on http://localhost:80"
else
    echo "❌ Web App: Failed to start"
fi

# Check Whisper service
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Whisper Service: Running on http://localhost:8001"
else
    echo "❌ Whisper Service: Failed to start"
fi

# Check Collaboration API
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Collaboration API: Running on http://localhost:8002"
else
    echo "❌ Collaboration API: Failed to start"
fi

# Check Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Running"
else
    echo "❌ Redis: Failed to start"
fi

# Check PostgreSQL
if docker-compose exec postgres pg_isready -U admin > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Running"
else
    echo "❌ PostgreSQL: Failed to start"
fi

echo ""
echo "🎉 Digital Twin Voice Intelligence Platform is ready!"
echo ""
echo "📱 Access the application:"
echo "   Main Dashboard: http://localhost:80"
echo "   Direct Web App: http://localhost:8080"
echo "   Whisper API: http://localhost:8001"
echo "   Collaboration API: http://localhost:8002"
echo ""
echo "🎙️ Voice Features:"
echo "   • Click the floating microphone button to start voice recording"
echo "   • Real-time transcription with Whisper AI"
echo "   • Automatic action item detection"
echo "   • Meeting intelligence and collaboration insights"
echo ""
echo "📊 Monitor with:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop with:"
echo "   docker-compose down"