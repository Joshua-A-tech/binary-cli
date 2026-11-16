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
