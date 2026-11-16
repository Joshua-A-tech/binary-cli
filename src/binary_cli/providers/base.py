from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str


class LLMProvider(ABC):
    @abstractmethod
    def stream(self, messages: list[Message], model: str) -> Iterator[str]:
        """Yield response text chunks."""

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return models visible to this provider."""
