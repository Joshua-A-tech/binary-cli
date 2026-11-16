import pytest

from binary_cli.config import Settings, load_settings


@pytest.fixture(autouse=True)
def isolate_env(monkeypatch):
    monkeypatch.setattr("binary_cli.config.load_dotenv", lambda: None)


def test_settings_default_ollama(monkeypatch):
    monkeypatch.delenv("BINARY_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = Settings()
    assert settings.provider == "ollama"
    assert settings.model == "llama3.2"


def test_settings_openai(monkeypatch):
    monkeypatch.setenv("BINARY_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test12345")
    monkeypatch.setenv("BINARY_OPENAI_MODEL", "gpt-4o")

    settings = load_settings()
    assert settings.provider == "openai"
    assert settings.model == "gpt-4o"
    assert settings.openai_api_key == "sk-test12345"


def test_settings_gemini(monkeypatch):
    monkeypatch.setenv("BINARY_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "ai-test12345")
    monkeypatch.setenv("BINARY_GEMINI_MODEL", "gemini-2.0-flash")

    settings = load_settings()
    assert settings.provider == "gemini"
    assert settings.model == "gemini-2.0-flash"
    assert settings.gemini_api_key == "ai-test12345"


def test_settings_missing_openai_key(monkeypatch):
    monkeypatch.setenv("BINARY_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        load_settings()


def test_settings_missing_gemini_key(monkeypatch):
    monkeypatch.setenv("BINARY_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        load_settings()


def test_settings_invalid_provider(monkeypatch):
    monkeypatch.setenv("BINARY_PROVIDER", "unsupported")

    with pytest.raises(ValueError, match="BINARY_PROVIDER must be one of"):
        load_settings()
