from typing import Any

from rich.panel import Panel

from ..providers.base import LLMProvider, StepResponse
from ..tools import ToolRegistry, default_registry
from ..ui.terminal import console

AGENT_SYSTEM_PROMPT = """You are Binary Agent, an autonomous software engineering assistant modeled after Google Antigravity.
You solve developer tasks methodically and safely by calling available tools.

Guidelines:
1. Always explore and read relevant files or directory listings before making changes.
2. Formulate explicit, focused tool calls to inspect, write, or execute code.
3. After editing or writing code, run tests or verify execution using `run_command` whenever applicable.
4. When you have achieved the user's goal, conclude with a clear, concise final summary of your solution.
"""


class AgentSession:
    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        registry: ToolRegistry | None = None,
    ):
        self.provider = provider
        self.model = model
        self.registry = registry or default_registry()
        self.messages: list[dict[str, Any]] = []

    def run(self, goal: str, max_steps: int = 15) -> str:
        self.messages.append(
            {
                "role": "user",
                "parts": [{"text": goal}],
            }
        )

        step_count = 0
        final_answer = ""

        while step_count < max_steps:
            step_count += 1
            with console.status(
                f"[bold cyan]Binary Agent thinking (Step {step_count}/{max_steps})...[/bold cyan]"
            ):
                response: StepResponse = self.provider.chat_step(
                    messages=self.messages,
                    model=self.model,
                    system_instruction=AGENT_SYSTEM_PROMPT,
                    tools=self.registry.list_tools(),
                )

            if response.content:
                console.print(
                    Panel(
                        response.content,
                        title="[bold cyan]Agent Reasoning[/bold cyan]",
                        border_style="cyan",
                    )
                )
                final_answer = response.content

            if not response.has_tool_calls():
                return final_answer or "Task completed."

            model_parts = []
            if response.content:
                model_parts.append({"text": response.content})
            for tool_call in response.tool_calls:
                model_parts.append(
                    {
                        "functionCall": {
                            "name": tool_call.name,
                            "args": tool_call.args,
                        }
                    }
                )
            self.messages.append(
                {
                    "role": "model",
                    "parts": model_parts,
                }
            )

            for tool_call in response.tool_calls:
                console.print(
                    f"[bold yellow]⚙ Executing Tool:[/bold yellow] [bold white]{tool_call.name}[/bold white]([dim]{tool_call.args}[/dim])"
                )
                result_str = self.registry.execute(tool_call.name, **tool_call.args)

                preview = result_str[:400] + ("..." if len(result_str) > 400 else "")
                console.print(
                    Panel(
                        preview,
                        title=f"[dim]Output: {tool_call.name}[/dim]",
                        border_style="dim",
                    )
                )

                self.messages.append(
                    {
                        "role": "function",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": tool_call.name,
                                    "response": {"output": result_str},
                                }
                            }
                        ],
                    }
                )

        return f"Agent reached maximum limit of {max_steps} steps."
