#!/bin/bash
# Wrapper script to start the bot with virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to bot directory
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the bot
python3 main.py

