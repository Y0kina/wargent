"""Helpers shared by command modules."""

from __future__ import annotations

import os

import typer

from wargent.engine.levels import Level, LevelError, get_level
from wargent.engine.progress import Progress
from wargent.i18n import LANGUAGES, detect_language, set_language, t
from wargent.ui import print_error


def start() -> Progress:
    """Load progress and select the interface language."""
    progress = Progress()
    explicit = os.environ.get("WARGENT_LANG", "").lower()
    if explicit in LANGUAGES:
        set_language(explicit)
    else:
        set_language(progress.lang or detect_language())
    return progress


def require_level(number: int, progress: Progress, enforce_lock: bool = True) -> Level:
    try:
        level = get_level(number)
    except LevelError as exc:
        print_error(str(exc))
        raise typer.Exit(1) from exc
    if level is None:
        print_error(t("level_unknown", n=number))
        raise typer.Exit(1)
    if enforce_lock and not progress.is_unlocked(number):
        print_error(t("level_locked", n=number, prev=number - 1))
        raise typer.Exit(1)
    return level
