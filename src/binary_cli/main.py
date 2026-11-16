from pathlib import Path

import typer
from dotenv import set_key
from rich import box
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .config import Settings, load_settings
from .core.chat import ChatSession
from .core.history import clear_history, recent_messages
from .providers.gemini_provider import GeminiProvider
from .providers.ollama_provider import OllamaProvider
from .providers.openai_provider import OpenAIProvider
from .ui.terminal import ask_prompt, banner, console, stream_to_terminal

app = typer.Typer(
    name="binary",
    help="Binary CLI — a modular LLM assistant for your terminal.",
    no_args_is_help=False,
)
config_app = typer.Typer(help="Manage Binary CLI configuration.")
app.add_typer(config_app, name="config")


def build_provider(settings: Settings, provider_override: str | None = None):
    provider = (provider_override or settings.provider).lower()
    if provider == "openai":
        key = settings.openai_api_key
        if not key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider.")
        return OpenAIProvider(key)
    if provider == "gemini":
        key = settings.gemini_api_key
        if not key:
            raise ValueError("GEMINI_API_KEY is required for Gemini provider.")
        return GeminiProvider(key)
    if provider == "ollama":
        return OllamaProvider(settings.ollama_base_url)
    raise ValueError(f"Unknown provider '{provider}'. Must be openai, gemini, or ollama.")


def resolve_model(settings: Settings, provider: str, model_override: str | None = None) -> str:
    if model_override:
        return model_override
    if provider == "openai":
        return settings.openai_model
    if provider == "gemini":
        return settings.gemini_model
    return settings.ollama_model


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        chat()


@app.command()
def chat(
    provider: str | None = typer.Option(
        None, "--provider", "-p", help="Provider to use (openai, gemini, ollama)."
    ),
    model: str | None = typer.Option(None, "--model", "-m", help="Model name to use."),
):
    """Start an interactive chat session."""
    try:
        settings = load_settings()
        active_provider_name = provider or settings.provider
        active_model = resolve_model(settings, active_provider_name, model)
        provider_instance = build_provider(settings, active_provider_name)
    except Exception as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        raise typer.Exit(1)

    banner(__version__)
    console.print(f"[dim]Provider: {active_provider_name} | Model: {active_model}[/dim]")
    console.print("[dim]Type /exit to quit. Type /clear to clear this session.[/dim]\n")
    session = ChatSession(provider_instance, active_model)

    while True:
        try:
            prompt = ask_prompt()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not prompt.strip():
            continue
        if prompt.strip().lower() in {"/exit", "/quit"}:
            console.print("[dim]Goodbye.[/dim]")
            break
        if prompt.strip().lower() == "/clear":
            session = ChatSession(provider_instance, active_model)
            console.print("[dim]Started a fresh conversation.[/dim]")
            continue

        console.print("[bold green]Binary[/bold green] ", end="")
        try:
            stream_to_terminal(session.send(prompt))
        except Exception as exc:
            console.print(f"\n[bold red]Request failed:[/bold red] {exc}")


@app.command()
def ask(
    prompt: str = typer.Argument(..., help="Question or instruction for the model."),
    provider: str | None = typer.Option(
        None, "--provider", "-p", help="Provider to use (openai, gemini, ollama)."
    ),
    model: str | None = typer.Option(None, "--model", "-m", help="Model name to use."),
):
    """Send a single prompt to the configured model."""
    try:
        settings = load_settings()
        active_provider_name = provider or settings.provider
        active_model = resolve_model(settings, active_provider_name, model)
        provider_instance = build_provider(settings, active_provider_name)
        session = ChatSession(provider_instance, active_model)
        console.print("[bold green]Binary[/bold green] ", end="")
        stream_to_terminal(session.send(prompt))
    except Exception as exc:
        console.print(f"[bold red]Request failed:[/bold red] {exc}")
        raise typer.Exit(1)


@app.command()
def models(
    provider: str | None = typer.Option(
        None, "--provider", "-p", help="Provider to query (openai, gemini, ollama)."
    ),
):
    """List models available from the configured provider."""
    try:
        settings = load_settings()
        active_provider = provider or settings.provider
        provider_instance = build_provider(settings, active_provider)
        names = provider_instance.list_models()
    except Exception as exc:
        console.print(f"[bold red]Could not list models:[/bold red] {exc}")
        raise typer.Exit(1)

    table = Table(title=f"Available {active_provider} models", box=box.ROUNDED)
    table.add_column("Model", style="cyan")
    for name in names:
        table.add_row(name)
    console.print(table)


@config_app.command("show")
def config_show():
    """Show non-secret configuration values."""
    try:
        settings = load_settings(validate_keys=False)
    except Exception as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        raise typer.Exit(1)

    openai_status = "configured" if settings.openai_api_key else "not configured"
    gemini_status = "configured" if settings.gemini_api_key else "not configured"

    active_provider_display = settings.provider
    if (settings.provider == "openai" and not settings.openai_api_key) or (
        settings.provider == "gemini" and not settings.gemini_api_key
    ):
        active_provider_display += " [yellow](API key missing)[/yellow]"

    console.print(
        Panel(
            f"Active Provider: [cyan]{active_provider_display}[/cyan]\n"
            f"Active Model: [cyan]{settings.model}[/cyan]\n"
            f"Ollama URL: {settings.ollama_base_url}\n"
            f"OpenAI API key: {openai_status} (model: {settings.openai_model})\n"
            f"Gemini API key: {gemini_status} (model: {settings.gemini_model})",
            title="Binary configuration",
        )
    )


@config_app.command("set")
def config_set(
    key: str = typer.Argument(
        ...,
        help="Config key (e.g. BINARY_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY, BINARY_GEMINI_MODEL).",
    ),
    value: str = typer.Argument(..., help="Value to set."),
):
    """Set a configuration variable in the local .env file."""
    env_path = Path(".env")
    if not env_path.exists():
        env_path.touch()
    set_key(dotenv_path=env_path, key_to_set=key.upper(), value_to_set=value)
    console.print(f"[bold green]Updated[/bold green] {key.upper()} in .env")


@app.command()
def history(
    limit: int = typer.Option(20, min=1, max=100, help="Number of recent messages."),
    clear: bool = typer.Option(
        False, "--clear", "-c", help="Clear all stored conversation history."
    ),
):
    """Show or clear recent saved messages."""
    if clear:
        deleted = clear_history()
        console.print(f"[bold green]Cleared {deleted} stored messages.[/bold green]")
        return

    rows = recent_messages(limit)
    if not rows:
        console.print("[dim]No saved conversations yet.[/dim]")
        return
    table = Table(title="Recent conversation history", box=box.SIMPLE)
    table.add_column("Conversation", style="dim", max_width=10)
    table.add_column("Role", style="cyan")
    table.add_column("Message")
    for conversation_id, role, content in rows:
        table.add_row(conversation_id[:8], role, content.replace("\n", " ")[:120])
    console.print(table)


if __name__ == "__main__":
    app()
