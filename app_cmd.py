"""
Command-line interface for the Claude Computer Use Demo
"""

import asyncio
import base64
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import cast, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from anthropic.types import TextBlock
from anthropic.types.beta import BetaMessage, BetaTextBlock, BetaToolUseBlock
from rich.console import Console
from rich.markdown import Markdown

from computer_use_demo.loop import (
    PROVIDER_TO_DEFAULT_MODEL_NAME,
    APIProvider,
    sampling_loop,
)
from computer_use_demo.tools import ToolResult
from app import (
    CONFIG_DIR,
    Sender,
    load_from_storage,
    save_to_storage,
)

console = Console()

class ChatState:
    def __init__(self):
        self.messages = []
        self.tools = {}
        self.responses = {}
        
        # Load config
        self.api_key = load_from_storage("api_key") or os.getenv("ANTHROPIC_API_KEY", "")
        self.provider = cast(APIProvider, 
            load_from_storage("provider") 
            or os.getenv("API_PROVIDER", "anthropic") 
            or APIProvider.ANTHROPIC
        )
        self.model = load_from_storage("model") or PROVIDER_TO_DEFAULT_MODEL_NAME[
            cast(APIProvider, self.provider)
        ]
        
        stored_n = load_from_storage("only_n_most_recent_images")
        self.only_n_most_recent_images = int(stored_n) if stored_n else 10
        
        self.custom_system_prompt = load_from_storage("system_prompt") or ""
        
        stored_hide = load_from_storage("hide_images")
        self.hide_images = stored_hide.lower() == "true" if stored_hide else False
        
        self.selected_display = int(load_from_storage("selected_display") or 0)

def setup_multiline_prompt():
    kb = KeyBindings()
    
    @kb.add('enter')  # Regular enter to submit
    def _(event):
        event.current_buffer.validate_and_handle()
    
    @kb.add(Keys.ShiftEnter)  # Use the Keys enum for shift+enter
    def _(event):
        event.current_buffer.insert_text('\n')
    
    session = PromptSession(
        message='You: ',
        key_bindings=kb,
        enable_history_search=True,
    )
    return session

def render_message(
    sender: Sender,
    message: str | BetaTextBlock | BetaToolUseBlock | ToolResult,
    hide_images: bool = False
):
    """Render a message to the terminal"""
    prefix = f"[{sender.value}] "
    
    is_tool_result = not isinstance(message, str) and (
        isinstance(message, ToolResult)
        or message.__class__.__name__ == "ToolResult"
        or message.__class__.__name__ == "CLIResult"
    )
    
    if is_tool_result:
        message = cast(ToolResult, message)
        if message.output:
            console.print(f"{prefix}Output:", style="bold blue")
            if message.__class__.__name__ == "CLIResult":
                console.print(message.output)
            else:
                console.print(Markdown(message.output))
                
        if message.error:
            console.print(f"{prefix}Error:", style="bold red")
            console.print(message.error)
            
        if message.base64_image and not hide_images:
            # Save image to temp file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(base64.b64decode(message.base64_image))
                console.print(f"{prefix}Image saved to: {tmp.name}")
                
    elif isinstance(message, (BetaTextBlock, TextBlock)):
        console.print(f"{prefix}{message.text}")
        
    elif isinstance(message, (BetaToolUseBlock)):
        console.print(f"{prefix}Using tool: {message.name}")
        console.print(f"Input: {message.input}")
        
    else:
        console.print(f"{prefix}{message}")
    
    console.print("─" * 80)

async def main():
    state = ChatState()
    session = setup_multiline_prompt()
    
    console.print("Claude Computer Use Demo (CLI Version)")
    console.print("Press Shift+Enter for newline, Enter to submit")
    console.print("Ctrl+C to exit")
    console.print("─" * 80)
    
    while True:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None, session.prompt
            )
            
            if not user_input.strip():
                continue
                
            # Add user message to state
            state.messages.append({
                "role": Sender.USER,
                "content": [TextBlock(type="text", text=user_input)]
            })
            
            def tool_callback(output: ToolResult, tool_id: str) -> None:
                state.tools.update({tool_id: output})
                render_message(Sender.TOOL, output, state.hide_images)

            # Run the agent loop
            state.messages = await sampling_loop(
                system_prompt_suffix=state.custom_system_prompt,
                model=state.model,
                provider=state.provider,
                messages=state.messages,
                output_callback=lambda msg: render_message(Sender.BOT, msg),
                tool_output_callback=tool_callback,  # Use the properly typed callback
                api_response_callback=lambda response: state.responses.update({
                    datetime.now().isoformat(): response
                }),
                api_key=state.api_key,
                only_n_most_recent_images=state.only_n_most_recent_images,
                display_id=state.selected_display,
            )
            
        except KeyboardInterrupt:
            console.print("\nGoodbye!")
            break
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")

if __name__ == "__main__":
    asyncio.run(main())
