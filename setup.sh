#!/bin/bash

# Newsletter Podcast Agent - Setup Script
# Run this once to set up the development environment

echo "🔧 Setting up Newsletter Podcast Agent..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $(python3 --version) found"

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Node.js $(node --version) found"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete"
cd ..
echo ""

# Frontend setup
echo "🎨 Setting up frontend..."
cd frontend

echo "Installing npm dependencies..."
npm install

echo "✅ Frontend setup complete"
cd ..
echo ""

# Credentials check
echo "🔐 Checking for Google OAuth credentials..."
if [ ! -f "parsers/credentials.json" ]; then
    echo ""
    echo "⚠️  credentials.json not found!"
    echo ""
    echo "To complete setup, you need to:"
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Create a project and enable Gmail API"
    echo "3. Create OAuth 2.0 credentials (Desktop app)"
    echo "4. Download credentials.json"
    echo "5. Place it in the parsers/ directory"
    echo ""
    echo "See README.md for detailed instructions."
else
    echo "✅ credentials.json found"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure credentials.json is in parsers/ (if not already)"
echo "2. In Gmail, create a label called 'newsletters' and apply it to your newsletters"
echo "3. Run ./start.sh to start both servers"
echo "4. Open http://localhost:5173 in your browser"
echo "5. Click 'Extract Newsletters' to begin"
echo ""
