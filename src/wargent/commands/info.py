"""Commands that display level information."""

from __future__ import annotations

from typing import Annotated

import typer

from wargent.commands._common import require_level, start
from wargent.engine.levels import load_levels
from wargent.i18n import t
from wargent.ui import console, print_banner, print_briefing, print_levels


def register(app: typer.Typer) -> None:
    @app.command("list")
    def list_levels() -> None:
        """List the levels and their status."""
        progress = start()
        levels = load_levels()
        print_banner()
        if not levels:
            console.print(t("no_levels"))
            return
        print_levels(levels, progress)

    @app.command()
    def show(number: Annotated[int, typer.Argument(help="Level number.")]) -> None:
        """Show the briefing of a level."""
        progress = start()
        print_briefing(require_level(number, progress))
