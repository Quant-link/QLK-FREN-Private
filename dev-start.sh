#!/bin/bash
# Development startup script for QuantLink FREN Narrator

set -e

echo "🚀 Starting QuantLink FREN Narrator Development Environment"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Build frontend for production
echo "🏗️  Building frontend..."
cd frontend
npm run build
cd ..

# Move built frontend to static directory
echo "📁 Setting up static files..."
rm -rf static
mv frontend/dist static

echo "✅ Setup complete!"
echo ""
echo "🌐 Starting Flask development server..."
echo "Frontend will be served at: http://localhost:5000"
echo "API endpoints available at: http://localhost:5000/api/"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the Flask development server
python web_api.py --host 0.0.0.0 --port 5000 --debug 