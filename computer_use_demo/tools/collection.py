"""Collection classes for managing multiple tools."""

from typing import Any, Sequence

from anthropic.types.beta import BetaToolParam

from .base import (
    BaseAnthropicTool,
    ToolError,
    ToolFailure,
    ToolResult,
)


class ToolCollection:
    """A collection of tools that can be used by the agent."""

    def __init__(self, tools: Sequence[BaseAnthropicTool]):
        """Initialize the tool collection with a list of tools."""
        self.tools = tools
        self.tool_map = {tool.to_params()["name"]: tool for tool in tools}

    def to_params(self) -> list[BetaToolParam]:
        """Convert all tools to their API parameters."""
        return [tool.to_params() for tool in self.tools]

    async def run(self, name: str, tool_input: dict):
        """Run a tool by name with the given input."""
        if name not in self.tool_map:
            raise ValueError(f"Unknown tool: {name}")
        return await self.tool_map[name](**tool_input)
