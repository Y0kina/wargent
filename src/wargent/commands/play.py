"""Commands to play a level: play, send, hint and check."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from wargent.commands._common import require_level, start
from wargent.engine.levels import Level, get_level
from wargent.engine.progress import MAX_HINTS, Progress
from wargent.engine.runner import default_guard, run_level
from wargent.i18n import get_language, t
from wargent.ui import (
    console,
    print_briefing,
    print_error,
    print_inspect,
    print_ok,
    print_result,
)


def submit_flag(level: Level, progress: Progress, flag: str) -> bool:
    if flag.strip() == level.flag:
        progress.mark_solved(level.id)
        print_ok(t("check_ok", n=level.id))
        if get_level(level.id + 1) is not None:
            console.print(t("unlocked_next", next=level.id + 1))
        if level.defend:
            console.print(t("defend_available", n=level.id))
        return True
    print_error(t("check_bad"))
    return False


def show_hint(level: Level, progress: Progress) -> None:
    if progress.hints_used(level.id) >= MAX_HINTS:
        index = MAX_HINTS
        console.print(t("hints_done"))
    else:
        index = progress.next_hint(level.id)
    hint = level.t(get_language())["hints"][index - 1]
    console.print(f"[bold]{t('hint_title', i=index)}[/bold]")
    console.print(str(hint).strip(), markup=False)


def attack(level: Level, progress: Progress, payload: str) -> None:
    result = run_level(level, default_guard(level), payload)
    won = level.won(result)
    if won:
        progress.record_attack(level.id, payload)
    print_result(level, result, won)


def _read_payload_file(path: str) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        print_error(t("file_missing", path=path))
        return None


def _command(line: str, level: Level, progress: Progress) -> bool:
    """Handle a slash command. Returns True when the session must end."""
    name, _, argument = line.partition(" ")
    argument = argument.strip()
    if name in ("/quit", "/exit"):
        return True
    if name == "/help":
        console.print(t("repl_help"), markup=False)
    elif name == "/info":
        print_briefing(level)
    elif name == "/inspect":
        print_inspect(level)
    elif name == "/hint":
        show_hint(level, progress)
    elif name == "/submit":
        submit_flag(level, progress, argument)
    elif name == "/file":
        payload = _read_payload_file(argument)
        if payload is not None:
            attack(level, progress, payload)
    else:
        console.print(t("repl_unknown"))
    return False


def register(app: typer.Typer) -> None:
    @app.command()
    def play(number: Annotated[int, typer.Argument(help="Level number.")]) -> None:
        """Open an interactive session on a level."""
        progress = start()
        level = require_level(number, progress)
        print_briefing(level)
        console.print(t("repl_intro"), markup=False)
        while True:
            try:
                line = input(f"wargent[{level.id}]> ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print()
                break
            if not line:
                continue
            if line.startswith("/"):
                if _command(line, level, progress):
                    break
                continue
            attack(level, progress, line.replace("\\n", "\n"))

    @app.command()
    def send(
        number: Annotated[int, typer.Argument(help="Level number.")],
        message: Annotated[str, typer.Argument(help="Input to send.")] = "",
        file: Annotated[
            str | None, typer.Option("--file", help="Read the input from a file.")
        ] = None,
    ) -> None:
        """Send one input to a level and print the outcome."""
        progress = start()
        level = require_level(number, progress)
        payload = message.replace("\\n", "\n")
        if file is not None:
            loaded = _read_payload_file(file)
            if loaded is None:
                raise typer.Exit(1)
            payload = loaded
        attack(level, progress, payload)

    @app.command()
    def hint(number: Annotated[int, typer.Argument(help="Level number.")]) -> None:
        """Reveal the next hint of a level."""
        progress = start()
        show_hint(require_level(number, progress), progress)

    @app.command()
    def check(
        number: Annotated[int, typer.Argument(help="Level number.")],
        flag: Annotated[str, typer.Argument(help="Flag to verify.")],
    ) -> None:
        """Verify a flag and mark the level as solved."""
        progress = start()
        level = require_level(number, progress)
        if not submit_flag(level, progress, flag):
            raise typer.Exit(1)
