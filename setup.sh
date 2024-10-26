#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Starting setup..."

# 1. Install Homebrew if not installed
#if ! command_exists brew; then
#    echo "Homebrew not found. Installing Homebrew..."
#    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
#else
#    echo "Homebrew is already installed."
#fi

# 2. Install System Dependencies
echo "Installing system dependencies..."
brew install cliclick imagemagick

# 3. Install Rust and Cargo if not installed
#if ! command_exists cargo; then
#    echo "Rust and Cargo not found. Installing Rust..."
#    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
#    # Source cargo environment (you may need to restart the terminal)
#    source "$HOME/.cargo/env"
#else
#    echo "Rust and Cargo are already installed."
#fi

# 4. Install Xcode Command Line Tools if not installed
if ! xcode-select -p >/dev/null 2>&1; then
    echo "Installing Xcode Command Line Tools..."
    xcode-select --install
else
    echo "Xcode Command Line Tools are already installed."
fi

# 5. Set Up Python Virtual Environment
if [ ! -d ".venv" ]; then
    echo "Setting up Python virtual environment..."
    python3.12 -m venv .venv
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# 6. Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# 7. Install Python Dependencies
echo "Installing Python dependencies..."
pip install -r dev-requirements.txt

# 8. Install Watchdog (recommended by Streamlit)
echo "Installing Watchdog..."
pip install watchdog

# 9. Install Dependencies for computer_use_demo
COMPUTER_USE_DEMO_DIR="./computer_use_demo"

if [ -d "$COMPUTER_USE_DEMO_DIR" ]; then
    echo "Navigating to computer_use_demo folder..."
    cd "$COMPUTER_USE_DEMO_DIR"
    if [ -f "requirements.txt" ]; then
        echo "Installing dependencies from computer_use_demo/requirements.txt..."
        pip install -r requirements.txt
    else
        echo "requirements.txt not found in computer_use_demo. Skipping..."
    fi
    cd -  # Return to the previous directory
else
    echo "computer_use_demo folder not found. Skipping..."
fi

echo "Setup completed successfully!"

echo "Please ensure you have granted Accessibility permissions to your terminal application and Python interpreter as per the README instructions."