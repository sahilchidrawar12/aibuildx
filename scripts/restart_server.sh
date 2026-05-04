#!/bin/bash
# Force restart server with clean Python cache

echo "🧹 Cleaning Python bytecode cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

echo "🔄 Killing existing Python processes..."
pkill -f "python.*app.py" 2>/dev/null
sleep 2

echo "🚀 Starting server with clean state..."
source /Users/sahil/Documents/aibuildx/path/to/venv/bin/activate
python app.py
