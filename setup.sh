#!/bin/bash

# Setup script for Dating Platform Onboarding Agent
# Run this script to set up the project

echo "🚀 Dating Platform Onboarding Agent - Setup"
echo "============================================="
echo ""

# Check Python version
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | awk -F. '{print $2}')
if [ "$PYTHON_MINOR" -lt 10 ] 2>/dev/null; then
    echo "❌ Python $PYTHON_VERSION found, but 3.10+ is required."
    echo "   The code uses 'str | None' union syntax introduced in Python 3.10."
    exit 1
fi
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
    echo "⚠️  Using Ollama by default (no API key needed)."
    echo "    To use Gemini instead, add GEMINI_API_KEY to .env"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "============================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Ollama: ollama serve  (then: ollama pull mistral)"
echo "   Or: add GEMINI_API_KEY to .env and set LLM_PROVIDER=gemini in config.py"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python main.py"
echo ""
echo "For audio input on macOS, you may need:"
echo "  brew install portaudio"
echo "  pip install --upgrade pyaudio"
echo ""
