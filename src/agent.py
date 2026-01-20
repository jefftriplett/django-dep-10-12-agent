#!/usr/bin/env -S uv --quiet run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "environs",
#     "pydantic-ai-slim[openai]",
#     "rich",
#     "typer",
# ]
# ///

import httpx
import typer

from environs import env
from pathlib import Path
from pydantic import BaseModel
from pydantic import Field
from pydantic_ai import Agent
from rich import print


OPENAI_API_KEY: str = env.str("OPENAI_API_KEY")
OPENAI_MODEL_NAME: str = env.str("OPENAI_MODEL_NAME", default="gpt-5-mini")

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


def get_agent():
    dep_10 = fetch_and_cache(
        url="https://raw.githubusercontent.com/django/deps/refs/heads/main/final/0010-new-governance.rst",
        cache_file="0010-new-governance.rst",
    )

    dep_12 = fetch_and_cache(
        url="https://raw.githubusercontent.com/django/deps/refs/heads/main/final/0012-steering-council.rst",
        cache_file="0012-steering-council.rst",
    )

    agent = Agent(
        model=OPENAI_MODEL_NAME,
        output_type=Output,
        system_prompt=SYSTEM_PROMPT,
    )

    @agent.instructions
    def add_dep_10() -> str:
        return f"<dep-10>\n\n{dep_10}\n\n</dep-10>"

    @agent.instructions
    def add_dep_12() -> str:
        return f"<dep-12>\n\n{dep_12}\n\n</dep-12>"

    return agent


def main(question: str, model_name: str = OPENAI_MODEL_NAME):
    agent = get_agent()

    result = agent.run_sync(question)

    print(
        f"[green][bold]Answer:[/bold][/green] {result.output.answer}\n\n"
        f"[yellow][bold]Reasoning:[/bold][/yellow] {result.output.reasoning}\n"
    )

    if result.output.sections:
        print("[yellow][bold]Sections:[/bold][/yellow]")
        for section in result.output.sections:
            print(f"- {section}")


if __name__ == "__main__":
    typer.run(main)
