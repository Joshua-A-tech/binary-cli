from collections.abc import Iterator

import httpx

from .base import LLMProvider, Message


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def stream(self, messages: list[Message], model: str) -> Iterator[str]:
        payload = {
            "model": model,
            "messages": [
                {"role": message.role, "content": message.content} for message in messages
            ],
            "stream": True,
        }
        with httpx.stream(
            "POST", f"{self.base_url}/api/chat", json=payload, timeout=None
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                data = httpx.Response(200, text=line).json()
                if data.get("message", {}).get("content"):
                    yield data["message"]["content"]
                if data.get("done"):
                    break

    def list_models(self) -> list[str]:
        response = httpx.get(f"{self.base_url}/api/tags", timeout=10)
        response.raise_for_status()
        return [item["name"] for item in response.json().get("models", [])]
