#!/bin/bash

echo "Setting up Color Display API..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo "Run the service with: python main.py"
echo "Then open your browser to: http://localhost:8000"
