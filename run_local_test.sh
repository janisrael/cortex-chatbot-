#!/bin/bash

# Script to run Cortex chatbot locally and test the widget

echo "🚀 Starting Cortex Chatbot for Local Testing..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.deps_installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.deps_installed
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating a basic one..."
    echo "FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env
    echo "PORT=6001" >> .env
    echo "✅ Created .env file with basic configuration"
fi

echo ""
echo "🌐 Starting Flask server on http://localhost:6001"
echo "📄 Test widget at: file://$(pwd)/test_widget_embed.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python app.py



