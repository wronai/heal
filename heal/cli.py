#!/usr/bin/env python3
"""
CLI module for heal package - LLM-powered shell error fixing.
"""

import os
import sys
import subprocess
from pathlib import Path
import click

from dotenv import load_dotenv, set_key
from litellm import completion

CONFIG_DIR = Path.home() / ".heal"
ENV_PATH = CONFIG_DIR / ".env"


def ensure_config():
    """Ensure configuration exists and prompt for missing values."""
    CONFIG_DIR.mkdir(exist_ok=True)

    if not ENV_PATH.exists():
        ENV_PATH.touch()

    load_dotenv(ENV_PATH)

    api_key = os.getenv("HEAL_API_KEY")
    model = os.getenv("HEAL_MODEL")

    if not api_key:
        api_key = click.prompt("Enter API key", type=str).strip()
        set_key(ENV_PATH, "HEAL_API_KEY", api_key)

    if not model:
        model = click.prompt("Enter model (e.g. gpt-4o-mini, gpt-4.1, etc)", type=str, default="gpt-4o-mini").strip()
        set_key(ENV_PATH, "HEAL_MODEL", model)

    os.environ["HEAL_API_KEY"] = api_key
    os.environ["HEAL_MODEL"] = model


def last_shell_command():
    """Get the last shell command from history."""
    try:
        out = subprocess.check_output(
            ["bash", "-lc", "fc -ln -1"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        return out.strip()
    except Exception:
        return ""


def read_stdin():
    """Read from stdin if not a TTY."""
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read()


def get_last_output():
    """Read the last captured output from shell hook."""
    output_file = CONFIG_DIR / "last_output.txt"
    if output_file.exists():
        return output_file.read_text()
    return ""


def call_llm(model, api_key, prompt):
    """Call the LLM with the given prompt."""
    # litellm uses standard envs
    os.environ["OPENAI_API_KEY"] = api_key

    try:
        resp = completion(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error calling LLM: {e}"


@click.group()
def main():
    """Heal - LLM-powered shell error fixing."""
    pass


@main.command()
@click.option('--model', help='Override the model')
@click.option('--api-key', help='Override the API key')
def fix(model, api_key):
    """Fix shell errors using LLM."""
    ensure_config()

    if model:
        os.environ["HEAL_MODEL"] = model
    if api_key:
        os.environ["HEAL_API_KEY"] = api_key

    model = os.environ["HEAL_MODEL"]
    api_key = os.environ["HEAL_API_KEY"]

    last_cmd = last_shell_command()
    error_output = read_stdin() or get_last_output()

    if not error_output:
        click.echo("No error input detected on stdin or from shell hook.")
        click.echo("Tip: run your command like:")
        click.echo("  your_command 2>&1 | heal fix")
        click.echo("  # Or install shell hook with: heal install")
        return

    prompt = f"""
You are a CLI assistant that helps fix shell errors and command failures.

The user executed this command:
{last_cmd}

And got this output / error:
{error_output}

The user is currently in this directory: {os.getcwd()}

Your task:
- Explain briefly what went wrong
- Propose concrete shell commands or file edits to fix it
- Be concise and practical
- Focus on the most likely solution

If there's no obvious error, suggest debugging steps.
"""

    response = call_llm(model, api_key, prompt)
    click.echo(response)


@main.command()
def install():
    """Install shell hook for automatic error capture."""
    shell_hook_path = CONFIG_DIR / "heal.bash"
    
    # Create the shell hook
    hook_content = '''# Heal shell hook for automatic command capture
__heal_cmd=""
__heal_out="$HOME/.heal/last_output.txt"

mkdir -p "$HOME/.heal"

preexec_heal() {
  __heal_cmd="$1"
  exec 3>&1 4>&2
  exec > >(tee "$__heal_out") 2>&1
}

precmd_heal() {
  exec 1>&3 2>&4
  exec 3>&- 4>&-
}

trap 'preexec_heal "$BASH_COMMAND"' DEBUG
PROMPT_COMMAND="precmd_heal"
'''
    
    shell_hook_path.write_text(hook_content)
    
    click.echo("Shell hook installed successfully!")
    click.echo()
    click.echo("Add this line to your ~/.bashrc:")
    click.echo(f"  source {shell_hook_path}")
    click.echo()
    click.echo("Then restart your shell or run:")
    click.echo("  source ~/.bashrc")
    click.echo()
    click.echo("After installation, you can simply run:")
    click.echo("  your_command")
    click.echo("  heal fix")


@main.command()
def uninstall():
    """Remove shell hook and configuration."""
    shell_hook_path = CONFIG_DIR / "heal.bash"
    output_file = CONFIG_DIR / "last_output.txt"
    
    if shell_hook_path.exists():
        shell_hook_path.unlink()
        click.echo("Shell hook removed.")
    
    if output_file.exists():
        output_file.unlink()
        click.echo("Output cache cleared.")
    
    click.echo("Remember to remove the source line from your ~/.bashrc")


if __name__ == "__main__":
    main()
