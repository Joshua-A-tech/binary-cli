# Binary CLI

Binary CLI is a modular, terminal-based assistant for chatting with LLMs and, in later releases,
helping developers understand and work with code.

## v0.1.0 scope

- Rich terminal interface
- Google Gemini, OpenAI, and Ollama provider adapters
- Interactive chat and one-shot `ask`
- Streaming output
- SQLite conversation history
- Basic provider/model configuration via CLI or `.env`

Agent execution, automatic file modification, and shell command execution are deliberately
out of scope for v0.1.0.

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
binary config set BINARY_PROVIDER ollama
# or
binary config set BINARY_PROVIDER gemini
binary config set GEMINI_API_KEY your_key_here
```

## Commands

```bash
binary --help
binary chat [--provider gemini|openai|ollama] [--model <name>]
binary ask "Explain recursion in Python" [--provider <name>] [--model <name>]
binary models [--provider <name>]
binary config show
binary config set <KEY> <VALUE>
binary history [--limit 20] [--clear]
```

## Providers

### Google Gemini

Set `GEMINI_API_KEY` in `.env` (or via `binary config set GEMINI_API_KEY <key>`).
Default model: `gemini-1.5-flash`.

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
    history.py
  ui/
    terminal.py
tests/
```

## Safety

Binary CLI v0.1.0 only sends prompts to the configured model and displays responses. It does not
execute model-generated shell commands or modify project files.
