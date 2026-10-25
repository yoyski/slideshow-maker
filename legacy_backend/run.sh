#!/bin/bash

# Voice Slideshow Maker - macOS/Linux startup script

echo "========================================"
echo "Voice Slideshow Maker"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo ""
echo "Starting application..."
echo "Open your browser to: http://localhost:5000"
echo ""

python app.py
