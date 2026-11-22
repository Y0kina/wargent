"""Terminal rendering helpers."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from wargent.engine.levels import Level
from wargent.engine.models import RunResult
from wargent.i18n import get_language, t

console = Console()

BANNER = r"""
 __      ____ _ _ __ __ _  ___ _ __ | |_
 \ \ /\ / / _` | '__/ _` |/ _ \ '_ \| __|
  \ V  V / (_| | | | (_| |  __/ | | | |_
   \_/\_/ \__,_|_|  \__, |\___|_| |_|\__|
                    |___/
"""


def print_banner() -> None:
    console.print(Text(BANNER, style="bold cyan"))
    console.print(Text(t("tagline"), style="dim"))


def print_error(message: str) -> None:
    console.print(Text(message, style="bold red"))


def print_ok(message: str) -> None:
    console.print(Text(message, style="bold green"))


def print_levels(levels: dict[int, Level], progress) -> None:
    table = Table(title=t("list_title"))
    table.add_column(t("col_level"), justify="right")
    table.add_column(t("col_title"))
    table.add_column(t("col_status"))
    lang = get_language()
    for number, level in levels.items():
        if progress.is_defended(number):
            status = Text(t("status_defended"), style="green")
        elif progress.is_solved(number):
            status = Text(t("status_solved"), style="green")
        elif progress.is_unlocked(number):
            status = Text(t("status_open"), style="yellow")
        else:
            status = Text(t("status_locked"), style="dim")
        table.add_row(str(number), level.t(lang)["title"], status)
    console.print(table)


def print_briefing(level: Level) -> None:
    block = level.t(get_language())
    body = Text()
    for label, key in (
        ("label_scenario", "scenario"),
        ("label_objective", "objective"),
        ("label_control", "control"),
    ):
        body.append(f"{t(label)}\n", style="bold")
        body.append(f"{str(block[key]).strip()}\n\n")
    if level.owasp:
        body.append(f"{t('label_owasp')}: ", style="bold")
        body.append(", ".join(level.owasp))
    console.print(Panel(body, title=f"{level.id} - {block['title']}", border_style="cyan"))


def print_inspect(level: Level) -> None:
    cfg = level.agent_config()
    prompt = cfg.system_prompt
    for value in cfg.secrets.values():
        prompt = prompt.replace(value, "[hidden]")
    body = Text()
    body.append(f"{t('inspect_prompt')}\n", style="bold")
    body.append(f"{prompt.strip() or '-'}\n\n")
    body.append(f"{t('inspect_tools')}\n", style="bold")
    body.append(f"{', '.join(cfg.tools) or '-'}\n\n")
    body.append(f"{t('inspect_context')}\n", style="bold")
    for segment in level.segments:
        if "{{input}}" in segment["text"]:
            continue
        body.append(f"[{segment['role']}] {segment['text']}\n")
    body.append("\n" + t("inspect_slot", slot=level.slot), style="dim")
    console.print(Panel(body, border_style="blue"))


def print_result(level: Level, result: RunResult, won: bool) -> None:
    console.print(Panel(Text(result.output), title=t("panel_reply"), border_style="green"))
    if result.calls:
        table = Table(title=t("panel_calls"))
        table.add_column("tool")
        table.add_column("arguments")
        table.add_column("status")
        for call in result.calls:
            status = t("call_allowed") if call.allowed else t("call_blocked")
            args = ", ".join(f"{k}={str(v)[:60]!r}" for k, v in call.args.items())
            table.add_row(call.name, args, status, style=None if call.allowed else "red")
        console.print(table)
    if result.leaks:
        body = Text()
        for leak in result.leaks:
            body.append(f"{leak.channel}: ", style="bold")
            body.append(f"{leak.text}\n")
        console.print(Panel(body, title=t("panel_outside"), border_style="red"))
    if result.trace:
        console.print(Panel(Text("\n".join(result.trace)), title=t("panel_trace"), style="dim"))
    if won:
        print_ok(t("flag_seen", n=level.id))
    else:
        console.print(Text(t("no_flag"), style="dim"))
