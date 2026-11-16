from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()


def banner(version: str) -> None:
    console.print(
        Panel(
            Text(f"BINARY CLI  v{version}\nYour AI assistant in the terminal", justify="center"),
            border_style="bright_blue",
        )
    )


def stream_to_terminal(chunks) -> str:
    output = []
    for chunk in chunks:
        console.print(chunk, end="")
        output.append(chunk)
    console.print()
    return "".join(output)


def ask_prompt() -> str:
    return Prompt.ask("[bold cyan]You[/bold cyan]")
