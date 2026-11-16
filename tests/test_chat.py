from binary_cli.core.chat import ChatSession
from binary_cli.providers.base import LLMProvider


class FakeProvider(LLMProvider):
    def stream(self, messages, model):
        yield "Hello"
        yield " from Binary"

    def list_models(self):
        return ["fake-model"]


def test_chat_streams_response():
    session = ChatSession(FakeProvider(), "fake-model")
    assert "".join(session.send("Hi")) == "Hello from Binary"
    assert session.messages[-1].content == "Hello from Binary"
