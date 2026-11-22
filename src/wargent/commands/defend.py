"""Defense mode command."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.table import Table
from rich.text import Text

from wargent.commands._common import require_level, start
from wargent.engine.defense import ensure_user_guard, verify
from wargent.engine.guards import Guard, GuardError
from wargent.i18n import t
from wargent.ui import console, print_error, print_ok


def register(app: typer.Typer) -> None:
    @app.command()
    def defend(
        number: Annotated[int, typer.Argument(help="Level number.")],
        run: Annotated[bool, typer.Option("--run", help="Verify the guard.")] = False,
    ) -> None:
        """Prepare the guard of a solved level, or verify it with --run."""
        progress = start()
        level = require_level(number, progress)
        if not level.defend:
            print_error(t("defend_none", n=number))
            raise typer.Exit(1)
        if not progress.is_solved(number):
            print_error(t("defend_need_solve", n=number))
            raise typer.Exit(1)
        path = ensure_user_guard(level)
        if not run:
            console.print(t("defend_prepared", path=path), markup=False)
            console.print(t("defend_contract"))
            console.print(t("defend_howto", n=number), markup=False)
            return
        attack = progress.attack(number)
        if attack is None:
            print_error(t("defend_need_attack", n=number))
            raise typer.Exit(1)
        try:
            guard = Guard.from_file(path)
        except GuardError as exc:
            print_error(t("defend_load_error", error=exc))
            raise typer.Exit(1) from exc
        report = verify(level, attack, guard)
        table = Table(title=t("defend_title", n=number))
        table.add_column("check")
        table.add_column("result")
        for item in report.checks:
            name = t("defend_attack_label") if item.name == "attack" else item.name
            detail = item.detail
            if item.name == "attack":
                detail = t("defend_blocked") if item.passed else t("defend_passes")
            mark = Text("pass" if item.passed else "fail", style="green" if item.passed else "red")
            cell = Text.assemble(mark, f"  {detail}" if detail else "")
            table.add_row(name, cell)
        console.print(table)
        if report.ok:
            progress.mark_defended(number)
            print_ok(t("defend_success", n=number))
        else:
            print_error(t("defend_failure"))
            raise typer.Exit(1)
