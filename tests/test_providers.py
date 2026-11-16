from contextlib import contextmanager
from unittest.mock import MagicMock

from binary_cli.providers.base import Message
from binary_cli.providers.gemini_provider import DEFAULT_GEMINI_MODELS, GeminiProvider
from binary_cli.providers.ollama_provider import OllamaProvider
from binary_cli.providers.openai_provider import OpenAIProvider


def test_gemini_provider_stream(monkeypatch):
    provider = GeminiProvider(api_key="fake-key")

    lines = [
        b'data: {"candidates": [{"content": {"parts": [{"text": "Hello "}]}}]}',
        b'data: {"candidates": [{"content": {"parts": [{"text": "Gemini!"}]}}]}',
    ]

    @contextmanager
    def fake_stream(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [line.decode("utf-8") for line in lines]
        yield mock_response

    monkeypatch.setattr("httpx.stream", fake_stream)

    messages = [
        Message(role="system", content="You are helpful."),
        Message(role="user", content="Hi"),
    ]
    chunks = list(provider.stream(messages, model="gemini-1.5-flash"))
    assert "".join(chunks) == "Hello Gemini!"


def test_gemini_provider_list_models(monkeypatch):
    provider = GeminiProvider(api_key="fake-key")

    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "models": [
            {
                "name": "models/gemini-1.5-flash",
                "supportedGenerationMethods": ["generateContent"],
            },
            {
                "name": "models/embedding-001",
                "supportedGenerationMethods": ["embedContent"],
            },
        ]
    }
    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: mock_resp)

    models = provider.list_models()
    assert models == ["gemini-1.5-flash"]


def test_gemini_provider_list_models_fallback(monkeypatch):
    provider = GeminiProvider(api_key="fake-key")

    def raise_err(*args, **kwargs):
        import httpx

        raise httpx.ConnectError("Network down")

    monkeypatch.setattr("httpx.get", raise_err)
    models = provider.list_models()
    assert models == DEFAULT_GEMINI_MODELS


def test_ollama_provider_stream(monkeypatch):
    provider = OllamaProvider(base_url="http://localhost:11434")

    lines = [
        '{"message": {"content": "Hello "}}',
        '{"message": {"content": "from Ollama!"}, "done": true}',
    ]

    @contextmanager
    def fake_stream(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = lines
        yield mock_response

    monkeypatch.setattr("httpx.stream", fake_stream)

    messages = [Message(role="user", content="Hi")]
    chunks = list(provider.stream(messages, model="llama3.2"))
    assert "".join(chunks) == "Hello from Ollama!"


def test_ollama_provider_list_models(monkeypatch):
    provider = OllamaProvider(base_url="http://localhost:11434")

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"models": [{"name": "llama3.2"}, {"name": "mistral"}]}
    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: mock_resp)

    models = provider.list_models()
    assert models == ["llama3.2", "mistral"]


def test_openai_provider_stream(monkeypatch):
    provider = OpenAIProvider(api_key="fake-key")

    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content="Hello "))]
    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content="OpenAI!"))]

    provider.client.chat.completions.create = MagicMock(return_value=[chunk1, chunk2])

    messages = [Message(role="user", content="Hi")]
    chunks = list(provider.stream(messages, model="gpt-4o-mini"))
    assert "".join(chunks) == "Hello OpenAI!"


def test_openai_provider_list_models():
    provider = OpenAIProvider(api_key="fake-key")
    models = provider.list_models()
    assert "gpt-4o-mini" in models
