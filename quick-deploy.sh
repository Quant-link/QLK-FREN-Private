#!/bin/bash
set -e

echo "🚀 QuantLink FREN Narrator - Quick Deploy Test"
echo "=============================================="
echo "📝 Note: Web interface automatically detects port (dynamic API URL)"
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t quantlink-narrator .

# Run the container in the background
echo "🏃 Starting container..."
CONTAINER_ID=$(docker run -d -p 8000:8000 quantlink-narrator)

echo "📋 Container ID: $CONTAINER_ID"

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Test the health endpoint
echo "🧪 Testing health endpoint..."
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ Health check passed!"
    
    # Test a crypto price endpoint
    echo "🧪 Testing crypto price endpoint..."
    if curl -f "http://localhost:8000/api/crypto/price?crypto=bitcoin" > /dev/null 2>&1; then
        echo "✅ Crypto price endpoint works!"
        echo ""
        echo "🎉 Deployment test successful!"
        echo "🌐 Your API is running at: http://localhost:8000"
        echo "🔍 Health check: http://localhost:8000/api/health"
        echo "💰 Price check: http://localhost:8000/api/crypto/price?crypto=bitcoin"
        echo "🎵 Web interface: http://localhost:8000 (with working audio!)"
        echo ""
        echo "💡 Tip: Change port in Dockerfile - web interface adapts automatically!"
        echo ""
        echo "To stop the container: docker stop $CONTAINER_ID"
        echo "To view logs: docker logs $CONTAINER_ID"
    else
        echo "❌ Crypto price endpoint failed"
        echo "🔍 Checking logs..."
        docker logs $CONTAINER_ID
        docker stop $CONTAINER_ID
        exit 1
    fi
else
    echo "❌ Health check failed"
    echo "🔍 Checking logs..."
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    exit 1
fi 