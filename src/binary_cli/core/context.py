import subprocess
from pathlib import Path


def is_binary_file(path: Path) -> bool:
    """Check if a file appears to be binary by checking the first 1024 bytes for null bytes."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            return b"\0" in chunk
    except OSError:
        return False


def read_file_context(path: Path | str, max_bytes: int = 100_000) -> str:
    """Safely read a file, check for binary format, handle bounds, and format for context."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")
    if is_binary_file(file_path):
        raise ValueError(f"Cannot include binary file '{file_path}' in context.")

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise OSError(f"Could not read file '{file_path}': {exc}") from exc

    truncated = False
    if len(content.encode("utf-8")) > max_bytes:
        content = content[:max_bytes]
        truncated = True

    extension = file_path.suffix.lstrip(".") or "text"
    header = f"### File: `{file_path}`\n```{extension}\n{content}\n```"
    if truncated:
        header += f"\n*(Note: File was truncated to {max_bytes // 1000} KB limit)*"
    return header


def get_git_diff(staged_only: bool = False, max_bytes: int = 200_000) -> str | None:
    """Extract git diff from the working directory."""
    cmd = ["git", "diff", "--staged"] if staged_only else ["git", "diff"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return None
        diff_text = result.stdout.strip()
        if not diff_text:
            return None
        if len(diff_text.encode("utf-8")) > max_bytes:
            diff_text = diff_text[:max_bytes] + "\n...(truncated diff)"
        return f"### Git Diff:\n```diff\n{diff_text}\n```"
    except (FileNotFoundError, OSError):
        return None


def build_context_prompt(
    prompt: str,
    files: list[Path] | None = None,
    include_diff: bool = False,
    staged_only: bool = False,
) -> str:
    """Combine file contexts, git diffs, and the prompt into a structured string."""
    context_sections = []

    if files:
        for file_path in files:
            file_context = read_file_context(file_path)
            context_sections.append(file_context)

    if include_diff:
        diff_context = get_git_diff(staged_only=staged_only)
        if diff_context:
            context_sections.append(diff_context)
        else:
            context_sections.append("### Git Diff:\n*(No changes detected)*")

    if not context_sections:
        return prompt

    full_context = "\n\n".join(context_sections)
    return f"{full_context}\n\n---\n\n**Instructions:**\n{prompt}"
