set dotenv-load := false

export JUST_UNSTABLE := "true"

# List all available commands
@_default:
    just --list

# Process with the Django DEP agent
@agent *ARGS:
    uv --quiet run agent.py "{{ ARGS }}"

# Ask the DEP agent a question
@ask *ARGS:
    just agent "{{ ARGS }}"

# Install pip and uv package management tools
@bootstrap *ARGS:
    pip install --upgrade pip uv

# Run a demo with a sample question
@demo:
    just ask "How long are steering council terms?"

# Format code using just's built-in formatter
@fmt:
    just --fmt

# Run pre-commit checks on files
@lint *ARGS="--all-files":
    uv --quiet tool run --with pre-commit-uv pre-commit run {{ ARGS }}
