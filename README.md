
# Computer Use Demo for macOS

---

## ⚠️ **DANGER WARNING**

**This project enables an AI assistant to control your computer, including executing commands, moving the mouse, typing, and more. Running this code can be very dangerous. Neither I nor Anthropic take any liability for any damage to your computer, data loss, security breaches, or any other harm that may result from using this software. Use it at your own risk. Proceed only if you fully understand the implications and are willing to accept all responsibility.**

---

This project is adapted from the [Anthropic Quickstarts](https://github.com/anthropics/anthropic-quickstarts), specifically the `computer-use-demo`, modified to run on macOS systems.

This demo showcases an AI assistant capable of controlling a computer through natural language commands. The assistant can perform tasks like moving the mouse, typing text, taking screenshots, and executing bash commands.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Features

- **Natural Language Interaction**: Control your computer using natural language commands through an AI assistant.
- **Mouse and Keyboard Control**: Move the mouse, click, and type text.
- **Screenshot Capabilities**: Capture screenshots and share them within the conversation.
- **File Editing**: Open, read, and write to files on your system.
- **Bash Commands**: Execute bash commands directly from the assistant.

## Prerequisites

- **macOS**: This demo is designed for macOS systems.
- **Python 3.11 or Later**: Ensure you have Python 3.11 or a newer version installed.
- **Anthropic API Key**: Obtain an API key from [Anthropic](https://www.anthropic.com/).


<div>
  <a href="https://www.loom.com/share/1aad71b5bb9248ff84b88cf85b123762">
    <p>Finder - computer - 23 October 2024 - Watch Video</p>
  </a>
  <a href="https://www.loom.com/share/1aad71b5bb9248ff84b88cf85b123762">
    <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/1aad71b5bb9248ff84b88cf85b123762-86c3144f3c85df1a-full-play.gif" alt="Loom Video Thumbnail">
  </a>
</div>


## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/newideas99/Anthropic-Computer-Use-MacOS.git
cd Anthropic-Computer-Use-MacOS
```

### 2. Run the Setup Script

Make the `setup.sh` script executable if it isn't already:

```bash
chmod +x setup.sh
```

Run the setup script:

```bash
./setup.sh
```

**Note:** The script will:
- Install Homebrew if not already installed.
- Install system dependencies (cliclick, imagemagick).
- Install Rust and Cargo if not already installed.
- Install Xcode Command Line Tools if not already installed.
- Set up a Python virtual environment.
- Upgrade pip and install Python dependencies.
- Install watchdog for Streamlit performance improvements.

### 3. Grant Accessibility Permissions

Some functionalities require accessibility permissions.

- Go to **System Preferences > Security & Privacy > Privacy** tab.
- Select **Accessibility** from the left pane.
- Click the lock icon to make changes and authenticate.
- Click the "+" button and add your terminal application (e.g., Terminal, iTerm).
- Also, add the Python executable located in your virtual environment:

```bash
/path/to/computer-use-demo-mac/.venv/bin/python
```

**Important:** Ensure both your terminal application and the Python interpreter have accessibility permissions.

## Configuration

### 1. Set Up the Anthropic API Key

- Obtain your API key from Anthropic.
- Create a file named `.env` in the project root directory and add your API key:

```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Alternatively, you can export the API key as an environment variable in your shell:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### 2. (Optional) Configure the System Prompt

You can customize the system prompt by editing the `SYSTEM_PROMPT` in `computer_use_demo/loop.py`:

```python
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilizing a macOS system with internet access.
* You can install applications using Homebrew.
* Use `curl` instead of `wget`.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>
"""
```

## Running the Application

Activate your virtual environment if you haven't already:

```bash
source .venv/bin/activate
```

Run the Streamlit application:

```bash
streamlit run app.py
```

This will start the application and provide you with a local URL (e.g., http://localhost:8501) to access the interface in your browser.

## Usage

1. **Access the Application**: Open the provided local URL in your web browser.
2. **Enter Your API Key**: If not set via environment variable or `.env` file, enter your Anthropic API key in the sidebar.
3. **Interact with the Assistant**: Use the chat interface to send commands to the assistant.
   - **Examples of Commands**:
     - "Open a new browser window and navigate to example.com."
     - "Take a screenshot of the current screen."
     - "Type 'Hello, World!' into the text editor."
     - "Run the command `ls -la` in the terminal."
4. **View Results**: The assistant's responses and any outputs (e.g., screenshots, command outputs) will appear in the chat interface.

## Troubleshooting

### Common Issues and Solutions

1. **Permission Denied Errors**
   - **Symptom**: Errors related to permissions when installing packages or running commands.
   - **Solution**: Ensure you have the necessary permissions. Run commands with `sudo` if required, but use caution.

2. **ModuleNotFoundError**
   - **Symptom**: Python cannot find a module when running the application.
   - **Solution**: Ensure that your virtual environment is activated and that all dependencies are installed.

3. **ValueError in `get_screen_size`**
   - **Symptom**: Error related to screen resolution parsing.
   - **Solution**: The `get_screen_size` method in `computer.py` has been updated to handle macOS output. Ensure you have the latest code.

4. **Accessibility Permissions Not Working**
   - **Symptom**: The assistant cannot control the mouse or keyboard.
   - **Solution**: Double-check that you have granted accessibility permissions to your terminal and Python applications.

5. **Streamlit Warnings About Watchdog**
   - **Symptom**: Streamlit recommends installing the `Watchdog` module for better performance.
   - **Solution**: The `setup.sh` script installs Watchdog. If you still see warnings, ensure it's installed in your virtual environment:

   ```bash
   pip install watchdog
   ```

## Acknowledgments

- Original code by Anthropic.
- Adapted for macOS by Jacob Ferrari-Shaikh (https://github.com/newideas99/).

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Disclaimer:** This project is for educational purposes. Be extremely cautious when granting applications accessibility permissions, and ensure you understand the implications of allowing an AI assistant to control your computer. Neither I nor Anthropic take any liability for any damage to your computer, data loss, security breaches, or any other harm that may result from using this software. Use it at your own risk.

**Important Note:** By using this software, you acknowledge that running code which allows an AI to control your computer can pose significant risks, including unintended execution of commands, data corruption, or exposure of sensitive information. Ensure that you run this software in a controlled environment, such as a virtual machine or a non-critical system, and understand all the potential consequences.

**Stay Safe:** Always monitor the assistant's actions carefully. Do not provide sensitive information or access to critical systems.
