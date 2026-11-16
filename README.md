# Binary CLI

Binary CLI is a modular, terminal-based assistant for chatting with LLMs and helping developers
understand and work with code directly from their terminal.

## Features

- **Autonomous Agent Mode (`binary do`)**: ReAct agent that autonomously inspects code, edits files, and executes shell commands to achieve goals
- **Multi-Provider Support**: Google Gemini, OpenAI, and local Ollama adapters
- **Code & File Context**: Attach files (`-f / --file`) and Git diffs (`-d / --diff`) directly to queries
- **Automated Code Review**: Dedicated `binary review` command to inspect working tree or staged changes
- **Conventional Commit Generator**: `binary commit-msg` generates conventional commit messages automatically
- **Interactive Chat & One-Shot Ask**: Real-time streaming output in your terminal
- **SQLite Conversation History**: Automatically persists previous turns and supports history purging
- **CLI & .env Configuration**: Inspect and configure API keys and providers with `binary config show` and `binary config set`

## Requirements

- Python 3.10+
- For Google Gemini: a Gemini API key
- For OpenAI: an OpenAI API key
- For Ollama: Ollama installed and a model downloaded locally

## Install from source

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev,openai]"
cp .env.example .env
```

Select a provider via `.env` or using `binary config set`:

```bash
binary config set BINARY_PROVIDER gemini
binary config set GEMINI_API_KEY your_key_here
# or for local Ollama:
binary config set BINARY_PROVIDER ollama
```

## Commands

```bash
binary --help
binary do "<task>" [--max-steps 15] [--provider <name>] [--model <name>]
binary chat [-f <file>] [-d] [--provider <name>] [--model <name>]
binary ask "<prompt>" [-f <file>] [-d] [--provider <name>] [--model <name>]
binary review [--staged] [--provider <name>] [--model <name>]
binary commit-msg [--staged] [--provider <name>] [--model <name>]
binary models [--provider <name>]
binary config show
binary config set <KEY> <VALUE>
binary history [--limit 20] [--clear]
```

## Autonomous Agent Examples

Execute developer tasks autonomously across your codebase:

```bash
binary do "Inspect tests/ and run pytest to check if all tests pass"
binary do "Create a new utility script fib.py that prints the first 20 fibonacci numbers, and test it"
```

## Code Intelligence Examples

### Ask questions with file context:
```bash
binary ask "Explain the authentication flow in this file" -f src/auth.py
```

### Review local code changes:
```bash
binary review
# or review staged changes only:
binary review --staged
```

### Generate commit messages:
```bash
git add src/
binary commit-msg
```

## Providers

### Google Gemini

Set `GEMINI_API_KEY` in `.env` (or via `binary config set GEMINI_API_KEY <key>`).
Default model: `gemini-2.5-flash`.

### Ollama (Local)

Make sure the Ollama service is running and the model is available:

```bash
ollama pull llama3.2
ollama serve
```

### OpenAI

Set `OPENAI_API_KEY` in `.env`. Default model: `gpt-4o-mini`.

## Project layout

```text
src/binary_cli/
  main.py
  config.py
  providers/
    base.py
    gemini_provider.py
    ollama_provider.py
    openai_provider.py
  core/
    chat.py
    context.py
    history.py
  ui/
    terminal.py
tests/
```

## Safety

Binary CLI v0.2.0 only sends prompts and attached file text to the configured model and displays responses.
It does not execute model-generated shell commands or modify project files without user consent.
