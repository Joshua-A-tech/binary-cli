from unittest.mock import MagicMock

import pytest

from binary_cli.core import context


def test_is_binary_file(tmp_path):
    text_file = tmp_path / "hello.py"
    text_file.write_text("print('hello')", encoding="utf-8")
    assert context.is_binary_file(text_file) is False

    bin_file = tmp_path / "binary.bin"
    bin_file.write_bytes(b"\x00\x01\x02\x03")
    assert context.is_binary_file(bin_file) is True


def test_read_file_context_success(tmp_path):
    code_file = tmp_path / "example.py"
    code_file.write_text("def add(a, b):\n    return a + b", encoding="utf-8")

    result = context.read_file_context(code_file)
    assert f"### File: `{code_file}`" in result
    assert "```py" in result
    assert "def add(a, b):" in result


def test_read_file_context_missing(tmp_path):
    missing_file = tmp_path / "does_not_exist.py"
    with pytest.raises(FileNotFoundError):
        context.read_file_context(missing_file)


def test_read_file_context_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        context.read_file_context(tmp_path)


def test_read_file_context_binary(tmp_path):
    bin_file = tmp_path / "test.bin"
    bin_file.write_bytes(b"\x00\x11")
    with pytest.raises(ValueError, match="Cannot include binary file"):
        context.read_file_context(bin_file)


def test_read_file_context_truncation(tmp_path):
    large_file = tmp_path / "large.txt"
    large_file.write_text("A" * 500, encoding="utf-8")

    result = context.read_file_context(large_file, max_bytes=100)
    assert "truncated" in result
    assert "A" * 100 in result
    assert "A" * 101 not in result


def test_get_git_diff_success(monkeypatch):
    mock_run = MagicMock()
    mock_run.return_value = MagicMock(returncode=0, stdout="diff --git a/file b/file\n+new line")
    monkeypatch.setattr("subprocess.run", mock_run)

    diff = context.get_git_diff()
    assert diff is not None
    assert "### Git Diff:" in diff
    assert "+new line" in diff


def test_get_git_diff_empty(monkeypatch):
    mock_run = MagicMock()
    mock_run.return_value = MagicMock(returncode=0, stdout="")
    monkeypatch.setattr("subprocess.run", mock_run)

    diff = context.get_git_diff()
    assert diff is None


def test_build_context_prompt_with_files(tmp_path):
    file1 = tmp_path / "test.txt"
    file1.write_text("Content 1", encoding="utf-8")

    prompt = context.build_context_prompt("Explain this", files=[file1])
    assert "### File: `" in prompt
    assert "Content 1" in prompt
    assert "**Instructions:**\nExplain this" in prompt


def test_build_context_prompt_without_context():
    prompt = context.build_context_prompt("Simple question")
    assert prompt == "Simple question"
