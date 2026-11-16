from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..tools.base import Tool


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass
class StepResponse:
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)

    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class LLMProvider(ABC):
    @abstractmethod
    def stream(self, messages: list[Message], model: str) -> Iterator[str]:
        """Yield response text chunks."""

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return models visible to this provider."""

    def chat_step(
        self,
        messages: list[dict[str, Any]],
        model: str,
        system_instruction: str | None = None,
        tools: list["Tool"] | None = None,
    ) -> StepResponse:
        """Execute a single agent turn with optional tool calling."""
        raise NotImplementedError(
            f"Autonomous tool calling is not supported on {self.__class__.__name__} yet."
        )
