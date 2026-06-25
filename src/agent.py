#!/usr/bin/env -S uv --quiet run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "environs",
#     "pydantic-ai-slim[openai]>=2,<3",
#     "pydantic-ai-slim[web]>=2,<3",
#     "rich",
#     "typer",
#     "uvicorn",
# ]
# ///

import httpx
import typer
import uvicorn

from environs import env
from pathlib import Path
from pydantic import BaseModel
from pydantic import Field
from pydantic_ai import Agent
from rich.console import Console

console = Console()

OPENAI_API_KEY: str = env.str("OPENAI_API_KEY")
OPENAI_MODEL_NAME: str = env.str("OPENAI_MODEL_NAME", default="openai:gpt-5.4-nano")

SYSTEM_PROMPT = """
<system_context>

You are a Django Software Foundation expert on Django Enhanced Proposals (DEPs).

</system_context>

<behavior_guidelines>

- Please answer all questions using Django's governance.
- Please warn the user that this not official or legal advice.

</behavior_guidelines>
"""


class Output(BaseModel):
    answer: str = Field(description="The answer to our question")
    reasoning: str = Field(description="The reasoning and support for our answer based on our source material")
    sections: list[str] = Field(description="Sections to reference")


def fetch_and_cache(
    *,
    url: str,
    cache_file: str,
    timeout: float = 10.0,
):
    filename = Path(cache_file)
    if filename.exists():
        return filename.read_text()

    response = httpx.get(f"https://r.jina.ai/{url}", timeout=timeout)
    response.raise_for_status()

    contents = response.text

    Path(cache_file).write_text(contents)

    return contents


def load_data():
    dep_10 = fetch_and_cache(
        url="https://raw.githubusercontent.com/django/deps/refs/heads/main/final/0010-new-governance.rst",
        cache_file="0010-new-governance.rst",
    )
    dep_12 = fetch_and_cache(
        url="https://raw.githubusercontent.com/django/deps/refs/heads/main/final/0012-steering-council.rst",
        cache_file="0012-steering-council.rst",
    )
    return {"dep_10": dep_10, "dep_12": dep_12}


def get_agent(*, output_type=Output):
    data = load_data()

    agent = Agent(
        model=OPENAI_MODEL_NAME,
        output_type=output_type,
        system_prompt=SYSTEM_PROMPT,
    )

    @agent.instructions
    def add_dep_10() -> str:
        return f"<dep-10>\n\n{data['dep_10']}\n\n</dep-10>"

    @agent.instructions
    def add_dep_12() -> str:
        return f"<dep-12>\n\n{data['dep_12']}\n\n</dep-12>"

    return agent


app = typer.Typer(
    help="Django DEP Agent - Ask questions about Django governance",
    no_args_is_help=True,
)


@app.command()
def ask(question: str):
    """Ask the DEP agent a question."""
    agent = get_agent()

    result = agent.run_sync(question)

    console.print(
        f"[green][bold]Answer:[/bold][/green] {result.output.answer}\n\n"
        f"[yellow][bold]Reasoning:[/bold][/yellow] {result.output.reasoning}\n"
    )

    if result.output.sections:
        console.print("[yellow][bold]Sections:[/bold][/yellow]")
        for section in result.output.sections:
            console.print(f"- {section}")


@app.command()
def web(
    host: str = "127.0.0.1",
    port: int = 8080,
):
    """Launch the DEP agent as a web chat interface."""
    agent = get_agent(output_type=None)
    web_app = agent.to_web()

    console.print(f"[bold green]Starting web interface at http://{host}:{port}[/bold green]")
    uvicorn.run(web_app, host=host, port=port)


@app.command()
def debug():
    """Print the compiled system prompt for debugging."""
    data = load_data()

    console.print("[bold cyan]===== SYSTEM PROMPT =====[/bold cyan]\n")
    console.print(SYSTEM_PROMPT)
    console.print("\n[bold cyan]===== INSTRUCTIONS =====[/bold cyan]\n")
    console.print(f"<dep-10>\n\n{data['dep_10']}\n\n</dep-10>")
    console.print(f"\n<dep-12>\n\n{data['dep_12']}\n\n</dep-12>")
    console.print("\n[bold cyan]=========================[/bold cyan]")


if __name__ == "__main__":
    app()
