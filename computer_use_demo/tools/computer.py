import asyncio
import base64
import os
import shlex
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict
from uuid import uuid4

from AppKit import NSScreen, NSEvent
from anthropic.types.beta import BetaToolComputerUse20241022Param
from PIL import Image

from .base import BaseAnthropicTool, ToolError, ToolResult
from .run import run

OUTPUT_DIR = "/tmp/outputs"

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50
SHELL_SCREENSHOT_DELAY = 2.0

Action = Literal[
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "screenshot",
    "cursor_position",
]


class Resolution(TypedDict):
    width: int
    height: int


MAX_SCALING_TARGETS: dict[str, Resolution] = {
    "XGA": Resolution(width=1024, height=768),  # 4:3
    "WXGA": Resolution(width=1280, height=800),  # 16:10
    "FWXGA": Resolution(width=1366, height=768),  # ~16:9
}


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


class ScreenInfo(TypedDict):
    display_id: int
    width: int
    height: int
    description: str
    origin_x: int  # Position relative to main screen
    origin_y: int  # Position relative to main screen
    scale_factor: float


class ComputerTool(BaseAnthropicTool):
    """
    A tool that allows the agent to interact with the screen, keyboard, and mouse of the current computer.
    Adapted for macOS using 'cliclick' and 'screencapture'.
    """

    name: Literal["computer"] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"
    width: int
    height: int
    display_id: int  # Changed from display_num
    scale_factor: float

    _scaling_enabled = True

    @property
    def options(self) -> ComputerToolOptions:
        width, height = self.scale_coordinates(
            ScalingSource.COMPUTER, self.width, self.height
        )
        return {
            "display_width_px": width,
            "display_height_px": height,
            "display_number": self.display_id,  # Changed from display_num
        }

    def to_params(self) -> BetaToolComputerUse20241022Param:
        return {"name": self.name, "type": self.api_type, **self.options}

    def __init__(self, display_id: int = 0):
        super().__init__()
        
        # Store the display ID
        self.display_id = display_id
        
        # Get the selected screen
        screens = NSScreen.screens()
        if display_id >= len(screens):
            self.display_id = 0  # Fall back to main display
        
        selected_screen = screens[self.display_id]
        frame = selected_screen.frame()
        
        # Get scale factor for selected screen
        self.scale_factor = float(selected_screen.backingScaleFactor())
        
        # Get logical screen dimensions and position
        self.width = int(frame.size.width)
        self.height = int(frame.size.height)
        self.origin_x = int(frame.origin.x)
        
        # Calculate Y origin in global positioning terms from the top-left corner of the main screen
        # (it's returned based on its bottom-left corner relative to the main screen's bottom-left corner)
        main_screen = NSScreen.mainScreen()
        main_height = main_screen.frame().size.height
        self.origin_y = int(main_height - frame.origin.y - frame.size.height)

        print(f"DEBUG: screen {self.display_id} {self.width} x {self.height} @ {self.origin_x}, {self.origin_y}")
        
        # Path to cliclick
        self.cliclick = "cliclick"

    def get_screen_scale_factor(self) -> float:
        """Get the screen's scaling factor using NSScreen."""
        main_screen = NSScreen.mainScreen()
        return float(main_screen.backingScaleFactor())

    def get_screen_size(self) -> tuple[int, int]:
        """Get the logical screen size."""
        main_screen = NSScreen.mainScreen()
        frame = main_screen.frame()
        return int(frame.size.width), int(frame.size.height)

    def image_dimensions(self, path: Path) -> tuple[int, int]:
        """Get the dimensions of an image."""
        img = Image.open(path)
        return img.width, img.height

    async def __call__(
        self,
        *,
        action: Action,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        **kwargs,
    ):
        if action in ("mouse_move", "left_click_drag"):
            if coordinate is None:
                raise ToolError(f"coordinate is required for {action}")
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
                raise ToolError(f"{coordinate} must be a tuple of length 2")
            if not all(isinstance(i, int) and i >= 0 for i in coordinate):
                raise ToolError(f"{coordinate} must be a tuple of non-negative ints")
            
            print(f"DEBUG: Input coordinate: {coordinate}")

            # 1. Input coordinates are in logical pixels for the target screen
            x, y = coordinate[0], coordinate[1]
            
            # 2. Add screen origin offset for X
            x += self.origin_x
            y += self.origin_y
            
            print(f"DEBUG: Final coordinates after offset: {x}, {y}")

            if action == "mouse_move":
                return await self.shell(f"{self.cliclick} -e300 m:{x},{y}")
            elif action == "left_click_drag":
                current_x, current_y = self.get_mouse_position()
                command = f"{self.cliclick} -e800 dd:{current_x},{current_y} du:{x},{y}"
                return await self.shell(command)

        if action in ("key", "type"):
            if text is None:
                raise ToolError(f"text is required for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")
            if not isinstance(text, str):
                raise ToolError(output=f"{text} must be a string")

            if action == "key":
                key_sequence = self.map_keys(text)
                return await self.shell(f"{self.cliclick} kp:{key_sequence}")
            elif action == "type":
                results: list[ToolResult] = []
                for chunk in chunks(text, TYPING_GROUP_SIZE):
                    cmd = f"{self.cliclick} -w {TYPING_DELAY_MS} t:{shlex.quote(chunk)}"
                    results.append(await self.shell(cmd, take_screenshot=False))
                screenshot_base64 = (await self.screenshot()).base64_image
                return ToolResult(
                    output="".join(result.output or "" for result in results),
                    error="".join(result.error or "" for result in results),
                    base64_image=screenshot_base64,
                )

        if action in (
            "left_click",
            "right_click",
            "double_click",
            "middle_click",
            "screenshot",
            "cursor_position",
        ):
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")

            if action == "screenshot":
                return await self.screenshot()
            elif action == "cursor_position":
                x, y = self.get_mouse_position()
                x, y = self.scale_coordinates(ScalingSource.COMPUTER, x, y)
                return ToolResult(output=f"X={x},Y={y}")
            else:
                click_arg = {
                    "left_click": "c:.",
                    "right_click": "rc:.",
                    "middle_click": "mc:.",
                    "double_click": "dc:.",
                }[action]
                return await self.shell(f"{self.cliclick} {click_arg}")

        raise ToolError(f"Invalid action: {action}")

    async def screenshot(self):
        """Take a screenshot and scale it to logical resolution."""
        output_dir = Path(OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"screenshot_{uuid4().hex}.png"
        resized_path = output_dir / f"screenshot_{uuid4().hex}_resized.png"

        # Take screenshot at native resolution
        screenshot_cmd = f"screencapture -C -D {self.display_id + 1} -x {path}"
        result = await self.shell(screenshot_cmd, take_screenshot=False)
        img_width, img_height = self.image_dimensions(path)
        print(f"DEBUG: initial image {path} {img_width} x {img_height}")
        
        if path.exists():
            # Scale down to logical resolution if needed using ImageMagick
            if img_width != self.width or img_height != self.height:
                convert_cmd = f"convert {path} -resize {self.width}x{self.height} {resized_path}"
                print(f"DEBUG: converting image with cmd {convert_cmd}")
                await run(convert_cmd)
                path = resized_path
                img_width, img_height = self.image_dimensions(resized_path)
                print(f"DEBUG: converted image {resized_path} {img_width} x {img_height}")
            
            return result.replace(
                base64_image=base64.b64encode(path.read_bytes()).decode()
            )
        raise ToolError(f"Failed to take screenshot: {result.error}")

    async def shell(self, command: str, take_screenshot=True) -> ToolResult:
        """Run a shell command and return the output, error, and optionally a screenshot."""
        _, stdout, stderr = await run(command)
        base64_image = None

        if take_screenshot:
            await asyncio.sleep(SHELL_SCREENSHOT_DELAY)
            base64_image = (await self.screenshot()).base64_image

        return ToolResult(output=stdout, error=stderr, base64_image=base64_image)

    def scale_coordinates(self, source: ScalingSource, x: int, y: int) -> tuple[int, int]:
        """Scale coordinates to a target maximum resolution."""
        if not self._scaling_enabled:
            return x, y
        ratio = self.width / self.height
        target_dimension = None
        for dimension in MAX_SCALING_TARGETS.values():
            if abs(dimension["width"] / dimension["height"] - ratio) < 0.02:
                if dimension["width"] < self.width:
                    target_dimension = dimension
                break
        if target_dimension is None:
            return x, y
        
        x_scaling_factor = target_dimension["width"] / self.width
        y_scaling_factor = target_dimension["height"] / self.height
        
        if source == ScalingSource.API:
            if x > self.width or y > self.height:
                raise ToolError(f"Coordinates {x}, {y} are out of bounds")
            return round(x / x_scaling_factor), round(y / y_scaling_factor)
        return round(x * x_scaling_factor), round(y * y_scaling_factor)

    def get_mouse_position(self) -> tuple[int, int]:
        """Get current mouse position in logical coordinates."""
        loc = NSEvent.mouseLocation()
        # Convert to logical coordinates
        x = int(loc.x)
        y = int(self.height - loc.y)
        return x, y

    def map_keys(self, text: str) -> str:
        """Map text to cliclick key codes if necessary."""
        if text.lower() == "enter":
            return "return"
        return text

    @staticmethod
    def get_available_screens() -> list[ScreenInfo]:
        """Get information about all available screens."""
        screens = []
        main_screen = NSScreen.mainScreen()
        main_height = main_screen.frame().size.height
        
        for i, screen in enumerate(NSScreen.screens()):
            frame = screen.frame()
            scale = screen.backingScaleFactor()
            # Get logical dimensions
            width = int(frame.size.width)
            height = int(frame.size.height)
            # Calculate position relative to main screen
            origin_x = int(frame.origin.x)
            # Y origin is main screen height minus (current screen Y origin + current screen height)
            origin_y = int(main_height - (frame.origin.y + frame.size.height))
            
            description = f"Display {i} ({width}x{height} @ {origin_x},{origin_y})"
            screens.append(ScreenInfo(
                display_id=i,
                width=width,
                height=height,
                description=description,
                origin_x=origin_x,
                origin_y=origin_y,
                scale_factor=float(scale)
            ))
        return screens

