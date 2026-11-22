"""Progress reset and language selection."""

from __future__ import annotations

from typing import Annotated

import typer

from wargent.commands._common import start
from wargent.engine.defense import user_guard_path
from wargent.engine.levels import load_levels
from wargent.i18n import LANGUAGES, get_language, set_language, t
from wargent.ui import console, print_error, print_ok


def register(app: typer.Typer) -> None:
    @app.command()
    def reset(
        number: Annotated[
            int | None, typer.Argument(help="Level to reset (all if omitted).")
        ] = None,
        yes: Annotated[bool, typer.Option("--yes", help="Confirm without prompting.")] = False,
    ) -> None:
        """Reset progress for one level or for every level."""
        progress = start()
        if not yes:
            print_error(t("reset_need_yes"))
            raise typer.Exit(1)
        progress.reset(number)
        for level_id, level in load_levels().items():
            if number is None or number == level_id:
                user_guard_path(level).unlink(missing_ok=True)
        print_ok(t("reset_done"))

    @app.command()
    def lang(
        code: Annotated[str | None, typer.Argument(help="Language code: en or fr.")] = None,
    ) -> None:
        """Show or set the interface language."""
        progress = start()
        if code is None:
            console.print(t("lang_current", lang=get_language()), markup=False)
            return
        if code not in LANGUAGES:
            print_error(t("lang_invalid"))
            raise typer.Exit(1)
        progress.set_lang(code)
        set_language(code)
        console.print(t("lang_set", lang=code), markup=False)
