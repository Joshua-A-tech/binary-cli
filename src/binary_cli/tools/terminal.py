import subprocess

from .base import Tool


def run_command(command: str, timeout: int = 30) -> str:
    """Execute a shell command with a timeout, capturing stdout, stderr, and exit code."""
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output_parts = []
        if proc.stdout:
            output_parts.append(proc.stdout.strip())
        if proc.stderr:
            output_parts.append(f"[stderr]\n{proc.stderr.strip()}")
        output_str = "\n".join(output_parts) or "(No output)"
        status = "succeeded" if proc.returncode == 0 else f"exited with code {proc.returncode}"
        return f"Command {status}:\n{output_str}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as exc:  # noqa: BLE001
        return f"Error executing command: {exc}"


RUN_COMMAND_TOOL = Tool(
    name="run_command",
    description="Run a non-interactive shell command in the workspace and view its stdout, stderr, and exit code.",
    parameters={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The exact shell command to execute."},
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds before terminating (default 30).",
            },
        },
        "required": ["command"],
    },
    func=run_command,
)
