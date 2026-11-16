from .base import Tool, ToolRegistry
from .filesystem import (
    EDIT_FILE_TOOL,
    LIST_DIR_TOOL,
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    edit_file,
    list_dir,
    read_file,
    write_file,
)
from .terminal import RUN_COMMAND_TOOL, run_command


def default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(RUN_COMMAND_TOOL)
    registry.register(READ_FILE_TOOL)
    registry.register(WRITE_FILE_TOOL)
    registry.register(EDIT_FILE_TOOL)
    registry.register(LIST_DIR_TOOL)
    return registry


__all__ = [
    "EDIT_FILE_TOOL",
    "LIST_DIR_TOOL",
    "READ_FILE_TOOL",
    "RUN_COMMAND_TOOL",
    "WRITE_FILE_TOOL",
    "Tool",
    "ToolRegistry",
    "default_registry",
    "edit_file",
    "list_dir",
    "read_file",
    "run_command",
    "write_file",
]
