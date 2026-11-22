"""Command-line entry point."""

from __future__ import annotations

import importlib
import pkgutil

import typer

from wargent import __version__, commands

app = typer.Typer(
    name="wargent",
    help="Offline wargame: attack and defend simulated AI agents.",
    no_args_is_help=True,
    add_completion=False,
)


def _show_version(value: bool) -> None:
    if value:
        typer.echo(f"wargent {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_show_version,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """Offline wargame: attack and defend simulated AI agents."""


def _register_commands() -> None:
    for info in sorted(pkgutil.iter_modules(commands.__path__), key=lambda m: m.name):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{commands.__name__}.{info.name}")
        module.register(app)


_register_commands()
