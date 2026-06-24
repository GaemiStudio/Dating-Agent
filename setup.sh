#!/bin/bash

# Setup script for Dating Platform Onboarding Agent
# Run this script to set up the project

echo "🚀 Dating Platform Onboarding Agent - Setup"
echo "============================================="
echo ""

# Check Python version
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip &> /dev/null

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Create .env from example
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OpenAI API key"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "============================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python main.py"
echo ""
echo "For audio input on macOS, you may need:"
echo "  brew install portaudio"
echo "  pip install --upgrade pyaudio"
echo ""
