#!/bin/bash

# CV Optimizer ATS - Quick Start Script
# This script sets up and runs the application

echo "=========================================="
echo "CV Optimizer for ATS - Startup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo ""
    echo "Please create a .env file with your DeepSeek API key:"
    echo "  1. Copy: cp .env.example .env"
    echo "  2. Edit: nano .env"
    echo "  3. Add your DeepSeek API key"
    echo ""
    echo "Get your API key at: https://platform.deepseek.com/api_keys"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '#' | xargs)

# Check if API key is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ DEEPSEEK_API_KEY is not set in .env file"
    exit 1
fi

echo "✅ Configuration loaded"

# Run the app
echo ""
echo "=========================================="
echo "Starting CV Optimizer..."
echo "=========================================="
echo ""
echo "Opening browser at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
