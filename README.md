# Django DEP 10 & DEP 12 Agent (Unofficial)

An AI Agent that answers questions about Django's governance based on DEP 10 & DEP 12 documents.

**Please note:** This is not official or legal advice.

## Usage

```shell
# Ask about Django governance
just ask "How long are steering council terms?"

# Or use uv directly
uv run src/agent.py ask "How long are steering council terms?"
```

## Available Commands

| Command | Description |
|---------|-------------|
| `just` | List all available commands |
| `just ask "..."` | Ask the DEP agent a question |
| `just debug` | Print the compiled system prompt for debugging |
| `just demo` | Run a demo with a sample question |
| `just bootstrap` | Install pip and uv |
| `just fmt` | Format code |
| `just lint` | Run pre-commit hooks on all files |
| `just lint-autoupdate` | Update pre-commit hooks to latest versions |

## Requirements

- Python 3.12+
- OpenAI API key (set `OPENAI_API_KEY` environment variable)

## Installation

```shell
just bootstrap
```
