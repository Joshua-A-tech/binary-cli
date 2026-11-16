import subprocess
from unittest.mock import MagicMock

from binary_cli.tools import (
    Tool,
    ToolRegistry,
    default_registry,
    edit_file,
    list_dir,
    read_file,
    run_command,
    write_file,
)


def test_tool_registry():
    registry = ToolRegistry()
    test_tool = Tool(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object"},
        func=lambda x: f"result: {x}",
    )
    registry.register(test_tool)
    assert registry.get("test_tool") is not None
    assert registry.execute("test_tool", x=42) == "result: 42"
    assert "Error: Tool 'missing' not found" in registry.execute("missing")


def test_default_registry():
    registry = default_registry()
    tool_names = [t.name for t in registry.list_tools()]
    assert "run_command" in tool_names
    assert "read_file" in tool_names
    assert "write_file" in tool_names
    assert "edit_file" in tool_names
    assert "list_dir" in tool_names


def test_read_file_tool(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("line 1\nline 2\nline 3\nline 4", encoding="utf-8")

    out = read_file(str(sample), start_line=2, end_line=3)
    assert "line 2" in out
    assert "line 3" in out
    assert "line 1" not in out
    assert "line 4" not in out

    # Non-existent
    assert "does not exist" in read_file(str(tmp_path / "ghost.txt"))
    # Directory
    assert "is a directory" in read_file(str(tmp_path))


def test_write_file_tool(tmp_path):
    target = tmp_path / "sub" / "output.txt"
    out = write_file(str(target), "Hello World")
    assert "Successfully wrote" in out
    assert target.read_text(encoding="utf-8") == "Hello World"

    # Overwrite = False
    no_overwrite = write_file(str(target), "New content", overwrite=False)
    assert "already exists" in no_overwrite


def test_edit_file_tool(tmp_path):
    doc = tmp_path / "doc.txt"
    doc.write_text("apple banana cherry", encoding="utf-8")

    out = edit_file(str(doc), target="banana", replacement="blueberry")
    assert "Successfully replaced" in out
    assert doc.read_text(encoding="utf-8") == "apple blueberry cherry"

    # Target not found
    fail = edit_file(str(doc), target="grape", replacement="orange")
    assert "target string not found" in fail


def test_list_dir_tool(tmp_path):
    (tmp_path / "file1.txt").write_text("1")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "file2.txt").write_text("2")

    out = list_dir(str(tmp_path))
    assert "file1.txt" in out
    assert "sub/" in out


def test_run_command_tool(monkeypatch):
    # Mock subprocess.run
    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "hello from shell"
    mock_res.stderr = ""
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_res)

    out = run_command("echo test")
    assert "Command succeeded" in out
    assert "hello from shell" in out


def test_run_command_timeout(monkeypatch):
    def timeout_mock(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="sleep 10", timeout=2)

    monkeypatch.setattr("subprocess.run", timeout_mock)
    out = run_command("sleep 10", timeout=2)
    assert "timed out" in out
