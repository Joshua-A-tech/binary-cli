import json
import time
from collections.abc import Iterator

import httpx

from .base import LLMProvider, Message

DEFAULT_GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def stream(self, messages: list[Message], model: str) -> Iterator[str]:
        clean_model = model.removeprefix("models/")
        url = f"{self.base_url}/v1beta/models/{clean_model}:streamGenerateContent"
        params = {"key": self.api_key, "alt": "sse"}

        system_parts = []
        contents = []

        for message in messages:
            if message.role == "system":
                system_parts.append({"text": message.content})
            else:
                role = "model" if message.role == "assistant" else "user"
                contents.append(
                    {
                        "role": role,
                        "parts": [{"text": message.content}],
                    }
                )

        payload: dict = {"contents": contents}
        if system_parts:
            payload["system_instruction"] = {"parts": system_parts}

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with httpx.stream(
                    "POST",
                    url,
                    params=params,
                    json=payload,
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue
                        raw_json = line.removeprefix("data: ").strip()
                        if not raw_json:
                            continue
                        data = json.loads(raw_json)
                        candidates = data.get("candidates", [])
                        for candidate in candidates:
                            parts = candidate.get("content", {}).get("parts", [])
                            for part in parts:
                                text = part.get("text")
                                if text:
                                    yield text
                return
            except httpx.HTTPStatusError as exc:
                if (
                    exc.response.status_code in {429, 500, 502, 503, 504}
                    and attempt < max_retries - 1
                ):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise

    def list_models(self) -> list[str]:
        try:
            url = f"{self.base_url}/v1beta/models"
            params = {"key": self.api_key}
            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            models = []
            for item in data.get("models", []):
                methods = item.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    name = item.get("name", "").removeprefix("models/")
                    if name:
                        models.append(name)
            return models or DEFAULT_GEMINI_MODELS
        except (httpx.HTTPError, json.JSONDecodeError, KeyError):
            return DEFAULT_GEMINI_MODELS
