#!/bin/bash
# Automated Environment Setup and Execution
set -e

# Navigate to project directory
cd "$(dirname "$0")"

# Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Execute application
python main.py
