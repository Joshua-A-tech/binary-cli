from typer.testing import CliRunner

from binary_cli.main import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Binary CLI" in result.stdout


def test_cli_config_show(monkeypatch):
    monkeypatch.setenv("BINARY_PROVIDER", "ollama")
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "Provider: ollama" in result.stdout or "Active Provider: ollama" in result.stdout


def test_cli_config_set(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["config", "set", "BINARY_PROVIDER", "gemini"])
    assert result.exit_code == 0
    assert "Updated BINARY_PROVIDER in .env" in result.stdout

    env_content = (tmp_path / ".env").read_text()
    assert "BINARY_PROVIDER" in env_content
    assert "gemini" in env_content


def test_cli_history_clear(tmp_path, monkeypatch):
    from binary_cli.core import history

    monkeypatch.setattr(history, "data_directory", lambda: tmp_path)
    result = runner.invoke(app, ["history", "--clear"])
    assert result.exit_code == 0
    assert "Cleared" in result.stdout


def test_cli_ask(monkeypatch):
    class FakeSession:
        def __init__(self, provider, model):
            pass

        def send(self, prompt):
            yield "Echo: " + prompt

    monkeypatch.setattr("binary_cli.main.ChatSession", FakeSession)
    monkeypatch.setattr("binary_cli.main.build_provider", lambda settings, p=None: None)

    result = runner.invoke(app, ["ask", "Hello Binary"])
    assert result.exit_code == 0
    assert "Echo: Hello Binary" in result.stdout


def test_cli_ask_with_file(tmp_path, monkeypatch):
    test_file = tmp_path / "hello.py"
    test_file.write_text("print('hi')", encoding="utf-8")

    class FakeSession:
        def __init__(self, provider, model):
            pass

        def send(self, prompt):
            assert "hello.py" in prompt
            assert "print('hi')" in prompt
            yield "File analyzed."

    monkeypatch.setattr("binary_cli.main.ChatSession", FakeSession)
    monkeypatch.setattr("binary_cli.main.build_provider", lambda settings, p=None: None)

    result = runner.invoke(app, ["ask", "Explain", "-f", str(test_file)])
    assert result.exit_code == 0
    assert "File analyzed." in result.stdout


def test_cli_review_no_diff(monkeypatch):
    monkeypatch.setattr("binary_cli.main.get_git_diff", lambda staged_only=False: None)
    result = runner.invoke(app, ["review"])
    assert result.exit_code == 0
    assert "No git changes detected" in result.stdout


def test_cli_review_with_diff(monkeypatch):
    monkeypatch.setattr(
        "binary_cli.main.get_git_diff",
        lambda staged_only=False: "### Git Diff:\n+added code",
    )

    class FakeSession:
        def __init__(self, provider, model):
            pass

        def send(self, prompt):
            assert "+added code" in prompt
            yield "Looks good, no issues."

    monkeypatch.setattr("binary_cli.main.ChatSession", FakeSession)
    monkeypatch.setattr("binary_cli.main.build_provider", lambda settings, p=None: None)

    result = runner.invoke(app, ["review"])
    assert result.exit_code == 0
    assert "Looks good, no issues." in result.stdout


def test_cli_commit_msg(monkeypatch):
    monkeypatch.setattr(
        "binary_cli.main.get_git_diff",
        lambda staged_only=False: "### Git Diff:\n+def fix_bug(): pass",
    )

    class FakeSession:
        def __init__(self, provider, model):
            pass

        def send(self, prompt):
            yield "fix: resolve edge case in calculation"

    monkeypatch.setattr("binary_cli.main.ChatSession", FakeSession)
    monkeypatch.setattr("binary_cli.main.build_provider", lambda settings, p=None: None)

    result = runner.invoke(app, ["commit-msg"])
    assert result.exit_code == 0
    assert "fix: resolve edge case in calculation" in result.stdout
