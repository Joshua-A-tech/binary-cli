import os
from pathlib import Path

from .base import Tool


def read_file(path: str, start_line: int | None = None, end_line: int | None = None) -> str:
    """Read contents of a text file, optionally specifying line numbers (1-indexed)."""
    file_path = Path(path)
    if not file_path.exists():
        return f"Error: File '{path}' does not exist."
    if file_path.is_dir():
        return f"Error: Path '{path}' is a directory, not a file."

    try:
        lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return f"Error reading file '{path}': {exc}"

    total_lines = len(lines)
    start = max(1, start_line) if start_line is not None else 1
    end = min(total_lines, end_line) if end_line is not None else total_lines

    if start > total_lines:
        return f"Error: start_line ({start}) exceeds total line count ({total_lines})."

    selected_lines = lines[start - 1 : end]
    formatted = [f"{i:4d}: {line}" for i, line in enumerate(selected_lines, start=start)]
    return "\n".join(formatted)


def write_file(path: str, content: str, overwrite: bool = True) -> str:
    """Create or overwrite a file with the given content."""
    file_path = Path(path)
    if file_path.exists() and not overwrite:
        return f"Error: File '{path}' already exists and overwrite is set to False."

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content.encode('utf-8'))} bytes to '{path}'."
    except OSError as exc:
        return f"Error writing file '{path}': {exc}"


def edit_file(path: str, target: str, replacement: str) -> str:
    """Replace an exact matching block of text in an existing file."""
    file_path = Path(path)
    if not file_path.exists():
        return f"Error: File '{path}' does not exist."

    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"Error reading file '{path}': {exc}"

    if target not in content:
        return (
            f"Error: target string not found in '{path}'. Please ensure exact whitespace matching."
        )

    count = content.count(target)
    new_content = content.replace(target, replacement, 1)

    try:
        file_path.write_text(new_content, encoding="utf-8")
        return f"Successfully replaced 1 occurrence in '{path}' (remaining matches: {count - 1})."
    except OSError as exc:
        return f"Error writing changes to '{path}': {exc}"


def list_dir(path: str = ".", max_depth: int = 2) -> str:
    """List files and directories up to a maximum depth."""
    root_path = Path(path)
    if not root_path.exists():
        return f"Error: Directory '{path}' does not exist."
    if not root_path.is_dir():
        return f"Error: Path '{path}' is not a directory."

    entries = []
    prefix_len = len(root_path.parts)
    for root, dirs, files in os.walk(root_path):
        current_depth = len(Path(root).parts) - prefix_len
        if current_depth >= max_depth:
            dirs.clear()
            continue

        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in {"node_modules", "__pycache__", "venv"}
        ]
        for f in files:
            if not f.startswith("."):
                rel_path = Path(root, f).relative_to(root_path)
                entries.append(str(rel_path))
        for d in dirs:
            rel_path = Path(root, d).relative_to(root_path)
            entries.append(f"{rel_path}/")

    if not entries:
        return f"Directory '{path}' is empty."
    return "\n".join(sorted(entries)[:100])


READ_FILE_TOOL = Tool(
    name="read_file",
    description="Read the contents of a file with line numbers. You can specify start_line and end_line.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path of the file to read."},
            "start_line": {"type": "integer", "description": "Optional start line (1-indexed)."},
            "end_line": {"type": "integer", "description": "Optional end line (inclusive)."},
        },
        "required": ["path"],
    },
    func=read_file,
)

WRITE_FILE_TOOL = Tool(
    name="write_file",
    description="Create a new file or overwrite an existing file with the provided content.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path of the file to write."},
            "content": {"type": "string", "description": "Full text content to write."},
            "overwrite": {
                "type": "boolean",
                "description": "Whether to overwrite if file exists (default True).",
            },
        },
        "required": ["path", "content"],
    },
    func=write_file,
)

EDIT_FILE_TOOL = Tool(
    name="edit_file",
    description="Replace an exact matching block of text in an existing file with new content.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Relative path of the file to modify."},
            "target": {"type": "string", "description": "Exact text block to replace."},
            "replacement": {"type": "string", "description": "New replacement text block."},
        },
        "required": ["path", "target", "replacement"],
    },
    func=edit_file,
)

LIST_DIR_TOOL = Tool(
    name="list_dir",
    description="List files and subdirectories in a directory up to a depth limit.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path (default '.')."},
            "max_depth": {"type": "integer", "description": "Max folder depth to traverse."},
        },
    },
    func=list_dir,
)
