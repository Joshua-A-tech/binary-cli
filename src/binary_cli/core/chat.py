from collections.abc import Iterator
from uuid import uuid4

from ..providers.base import LLMProvider, Message
from .history import save_message

SYSTEM_PROMPT = (
    "You are Binary, a helpful command-line AI assistant. "
    "Be accurate, concise, and explain technical concepts clearly."
)


class ChatSession:
    def __init__(self, provider: LLMProvider, model: str):
        self.provider = provider
        self.model = model
        self.conversation_id = str(uuid4())
        self.messages = [Message(role="system", content=SYSTEM_PROMPT)]

    def send(self, prompt: str) -> Iterator[str]:
        user_message = Message(role="user", content=prompt)
        self.messages.append(user_message)
        save_message(self.conversation_id, user_message)

        chunks: list[str] = []
        for chunk in self.provider.stream(self.messages, self.model):
            chunks.append(chunk)
            yield chunk

        answer = "".join(chunks)
        assistant_message = Message(role="assistant", content=answer)
        self.messages.append(assistant_message)
        save_message(self.conversation_id, assistant_message)
