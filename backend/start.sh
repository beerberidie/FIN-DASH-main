#!/bin/bash
# Start script for FIN-DASH backend

echo "Starting FIN-DASH Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Ensure data directory exists
mkdir -p ../data/backups

# Start the server
echo "Starting FastAPI server on http://localhost:8777"
python app.py

