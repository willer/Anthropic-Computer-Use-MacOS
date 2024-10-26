#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Starting server..."
streamlit run app.py
