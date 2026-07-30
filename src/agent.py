#!/usr/bin/env -S uv --quiet run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx2",
#     "environs",
#     "pydantic-ai-slim[openai,web]>=2,<3",
#     "rich",
#     "typer",
#     "uvicorn",
# ]
# ///

import time

import httpx2
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

CACHE_MAX_AGE_HOURS: float = env.float("CACHE_MAX_AGE_HOURS", default=24.0)

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


def cache_is_fresh(filename: Path, max_age_hours: float) -> bool:
    """Return True if the cache file exists and is younger than max_age_hours."""
    if not filename.exists() or max_age_hours <= 0:
        return False

    return (time.time() - filename.stat().st_mtime) < (max_age_hours * 3600)


def fetch_and_cache(
    *,
    url: str,
    cache_file: str,
    timeout: float = 10.0,
    max_age_hours: float = CACHE_MAX_AGE_HOURS,
    refresh: bool = False,
):
    filename = Path(cache_file)
    if not refresh and cache_is_fresh(filename, max_age_hours):
        return filename.read_text()

    try:
        response = httpx2.get(f"https://r.jina.ai/{url}", timeout=timeout, follow_redirects=True)
        response.raise_for_status()
    except httpx2.HTTPError as exc:
        if filename.exists():
            console.print(f"[yellow]Could not refresh {filename}: {exc}. Using the cached copy.[/yellow]")
            return filename.read_text()
        raise

    contents = response.text

    filename.write_text(contents)

    return contents


def load_data(*, refresh: bool = False):
    dep_10 = fetch_and_cache(
        url="https://raw.githubusercontent.com/django/deps/refs/heads/main/final/0010-new-governance.rst",
        cache_file="0010-new-governance.rst",
        refresh=refresh,
    )
    dep_12 = fetch_and_cache(
        url="https://raw.githubusercontent.com/django/deps/refs/heads/main/final/0012-steering-council.rst",
        cache_file="0012-steering-council.rst",
        refresh=refresh,
    )
    return {"dep_10": dep_10, "dep_12": dep_12}


def get_agent(*, output_type=Output, refresh: bool = False):
    data = load_data(refresh=refresh)

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
def ask(
    question: str,
    refresh: bool = typer.Option(False, help="Re-fetch the source documents, ignoring the cache."),
):
    """Ask the DEP agent a question."""
    agent = get_agent(refresh=refresh)

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
    refresh: bool = typer.Option(False, help="Re-fetch the source documents, ignoring the cache."),
):
    """Launch the DEP agent as a web chat interface."""
    # output_type=str keeps replies conversational. Pydantic AI v2 rejects None here —
    # it reads it as "no output types provided" and raises UserError.
    agent = get_agent(output_type=str, refresh=refresh)
    web_app = agent.to_web()

    console.print(f"[bold green]Starting web interface at http://{host}:{port}[/bold green]")
    uvicorn.run(web_app, host=host, port=port)


@app.command()
def debug(
    refresh: bool = typer.Option(False, help="Re-fetch the source documents, ignoring the cache."),
):
    """Print the compiled system prompt for debugging."""
    data = load_data(refresh=refresh)

    console.print("[bold cyan]===== SYSTEM PROMPT =====[/bold cyan]\n")
    console.print(SYSTEM_PROMPT)
    console.print("\n[bold cyan]===== INSTRUCTIONS =====[/bold cyan]\n")
    console.print(f"<dep-10>\n\n{data['dep_10']}\n\n</dep-10>")
    console.print(f"\n<dep-12>\n\n{data['dep_12']}\n\n</dep-12>")
    console.print("\n[bold cyan]=========================[/bold cyan]")


if __name__ == "__main__":
    app()
