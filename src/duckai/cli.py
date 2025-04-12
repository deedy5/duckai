from __future__ import annotations

import importlib.metadata
import logging
from pathlib import Path
from typing import Any

import click
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from .duckai import DuckAI
from .utils import _expand_proxy_tb_alias, json_dumps, json_loads

logger = logging.getLogger(__name__)
console = Console()

CHAT_MODEL_CHOICES = {f"{i}": k for i, k in enumerate(DuckAI._chat_models, start=1)}
CHAT_MODEL_CHOICES_PROMPT = (
    "DuckAI chat. Choose a model:\n"
    + "\n".join([f"[{key}]: {value}" for key, value in CHAT_MODEL_CHOICES.items()])
    + "\n"
)


def _save_json(jsonfile: Path | str, data: Any) -> None:
    with open(jsonfile, "w", encoding="utf-8") as file:
        file.write(json_dumps(data))


@click.group(chain=True)
def cli() -> None:
    """duckai CLI tool"""
    pass


def safe_entry_point() -> None:
    try:
        cli()
    except Exception as ex:
        click.echo(f"{type(ex).__name__}: {ex}")


@cli.command()
def version() -> str:
    version = importlib.metadata.version("duckai")
    print(version)
    return version


@cli.command()
@click.option("-l", "--load", is_flag=True, default=False, help="load the last conversation from the json cache")
@click.option("-p", "--proxy", help="the proxy to send requests, example: socks5://127.0.0.1:9150")
@click.option("-t", "--timeout", default=30, help="timeout value for the HTTP client")
@click.option("-v", "--verify", default=True, help="verify SSL when making the request")
@click.option(
    "-m",
    "--model",
    prompt=CHAT_MODEL_CHOICES_PROMPT,
    type=click.Choice([k for k in CHAT_MODEL_CHOICES]),
    show_choices=False,
    default="1",
)
def chat(load: bool, proxy: str | None, timeout: float, verify: bool, model: str) -> None:
    """CLI function to perform an interactive AI chat using DuckDuckGo API."""
    client = DuckAI(proxy=_expand_proxy_tb_alias(proxy), verify=verify)
    model = CHAT_MODEL_CHOICES[model]

    cache_file = "duckai_chat.json"
    if load and Path(cache_file).exists():
        with open(cache_file) as f:
            cache = json_loads(f.read())
            client._chat_vqd = cache.get("vqd", None)
            client._chat_vqd_hash = cache.get("vqd_hash", None)
            client._chat_messages = cache.get("messages", [])
            client._chat_tokens_count = cache.get("tokens", 0)

    while True:
        user_input = prompt(
            message=HTML("""<b><style fg="ansired">@you: </style></b>"""),
            multiline=True,
        )
        if user_input.strip():
            output_buffer = ""
            with Live(Markdown(output_buffer), console=console) as live:
                for chunk in client.chat_yield(keywords=user_input, model=model, timeout=timeout):
                    top_message = f"""`@AI[{model=} tokens={client._chat_tokens_count}]:`"""
                    output_buffer += chunk
                    result = f"{top_message}\n\n{output_buffer}"
                    live.update(Markdown(result))
            cache = {
                "vqd": client._chat_vqd,
                "vqd_hash": client._chat_vqd_hash,
                "tokens": client._chat_tokens_count,
                "messages": client._chat_messages,
            }
            _save_json(cache_file, cache)


if __name__ == "__main__":
    cli(prog_name="duckai")
