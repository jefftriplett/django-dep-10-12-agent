# Django DEP 10 & DEP 12 Agent (Unofficial)

This was an experiment to build an AI Agent that can help answer common questions about Django's governance including DEP 10 & DEP 12.

Please note: It's not official or legal advice.

## Usage

```shell
$ uv run agent.py "How long are steering council terms?"
Answer: The governance documents do not specify a fixed term length for Steering Council members. Instead, members serve until a new election is held under the
conditions set out in the DEPs (for example, triggered by events like the conclusion of a major release series or if a vote of no confidence is raised).

Reasoning: Neither DEP 0012 (which renames the Technical Board to the Steering Council) nor its predecessor, DEP 0010, defines a fixed term length for Steering Council
members. The documents outline conditions under which elections are triggered, meaning that members serve until they are replaced through that process. In short, the
terms are not defined by a set period, but by the occurrence of specific events or renewed elections. This answer is based solely on the current governance documents
and should not be taken as official or legal advice.

Sections:
- DEP 0012 (The Steering Council)
- DEP 0010 (New Governance for the Django project)
```
