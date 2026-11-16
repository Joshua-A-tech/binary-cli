from collections.abc import Iterator

from openai import OpenAI

from .base import LLMProvider, Message


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def stream(self, messages: list[Message], model: str) -> Iterator[str]:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            stream=True,
        )
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def list_models(self) -> list[str]:
        # Keep this deterministic in v0.1; users can set any model supported by their account.
        return ["gpt-4o-mini", "gpt-4o"]
