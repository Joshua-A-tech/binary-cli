from binary_cli.core.agent import AgentSession
from binary_cli.providers.base import LLMProvider, StepResponse, ToolCall
from binary_cli.tools import Tool, ToolRegistry, write_file


class FakeAgentProvider(LLMProvider):
    def __init__(self, responses: list[StepResponse]):
        self.responses = list(responses)
        self.calls = []

    def stream(self, messages, model):
        yield "not used"

    def list_models(self):
        return ["fake-model"]

    def chat_step(self, messages, model, system_instruction=None, tools=None):
        self.calls.append(messages)
        if self.responses:
            return self.responses.pop(0)
        return StepResponse(content="Final default answer.")


def test_agent_session_executes_tool_and_completes(tmp_path):
    target_file = tmp_path / "result.txt"

    step1 = StepResponse(
        content="I will write the file.",
        tool_calls=[
            ToolCall(
                id="call-1",
                name="write_file",
                args={"path": str(target_file), "content": "agent output"},
            )
        ],
    )
    step2 = StepResponse(content="I have written the file successfully.")

    provider = FakeAgentProvider([step1, step2])

    registry = ToolRegistry()
    registry.register(
        Tool(
            name="write_file",
            description="Write a file",
            parameters={"type": "object"},
            func=write_file,
        )
    )

    agent = AgentSession(provider=provider, model="fake-model", registry=registry)
    result = agent.run("Create the file", max_steps=5)

    assert result == "I have written the file successfully."
    assert target_file.read_text(encoding="utf-8") == "agent output"
    assert len(provider.calls) == 2


def test_agent_session_max_steps():
    # Provider always asks for tool call
    step = StepResponse(
        content="Looping...",
        tool_calls=[ToolCall(id="c", name="noop", args={})],
    )
    provider = FakeAgentProvider([step, step, step, step])

    registry = ToolRegistry()
    registry.register(Tool(name="noop", description="", parameters={}, func=lambda: "ok"))

    agent = AgentSession(provider=provider, model="fake-model", registry=registry)
    res = agent.run("infinite", max_steps=2)
    assert "reached maximum limit" in res
