# Django DEP 10 & DEP 12 Agent (Unofficial)

An AI Agent that answers questions about Django's governance based on DEP 10 & DEP 12 documents.

**Please note:** This is not official or legal advice.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

```shell
# Install required tools
pip install --upgrade pip uv
```

## Usage

```shell
# Using uv directly
$ uv run src/agent.py "How long are steering council terms?"

# Using just command
$ just ask "How long are steering council terms?"

# Quick demo with sample question
$ just demo
```

### Example Output

```
Answer: The governance documents do not specify a fixed term length for Steering Council members. Instead, members serve until a new election is held under the
conditions set out in the DEPs (for example, triggered by events like the conclusion of a major release series or if a vote of no confidence is raised).

Reasoning: Neither DEP 0012 (which renames the Technical Board to the Steering Council) nor its predecessor, DEP 0010, defines a fixed term length for Steering Council
members. The documents outline conditions under which elections are triggered, meaning that members serve until they are replaced through that process. In short, the
terms are not defined by a set period, but by the occurrence of specific events or renewed elections.

Sections:
- DEP 0012 (The Steering Council)
- DEP 0010 (New Governance for the Django project)
```
