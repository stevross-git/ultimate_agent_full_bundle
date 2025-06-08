#!/bin/bash

echo "🔧 Setting up virtual environment..."

# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Running the Enhanced Node Server..."
python enhanced_remote_node_v345.py


