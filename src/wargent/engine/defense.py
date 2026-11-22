"""Defense mode: replay a recorded attack against a player-written guard."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from wargent.engine.guards import Guard, GuardError
from wargent.engine.levels import Level
from wargent.engine.progress import home_dir
from wargent.engine.runner import run_level


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class DefenseReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.checks) and all(check.passed for check in self.checks)


def user_guard_path(level: Level) -> Path:
    return home_dir() / "guards" / f"guard_{level.id:02d}.py"


def ensure_user_guard(level: Level) -> Path:
    """Create the editable copy of the level guard when it does not exist yet."""
    target = user_guard_path(level)
    if not target.exists():
        source = level.guard_path
        if source is None:
            raise FileNotFoundError(f"level {level.id} has no guard template")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return target


def verify(level: Level, attack: str, guard: Guard) -> DefenseReport:
    report = DefenseReport()
    try:
        result = run_level(level, guard, attack)
        blocked = not level.won(result)
        report.checks.append(
            Check("attack", blocked, "blocked" if blocked else "the attack still succeeds")
        )
    except GuardError as exc:
        report.checks.append(Check("attack", False, f"guard error: {exc}"))
    for index, scenario in enumerate(level.benign, start=1):
        name = f"legitimate use {index}"
        try:
            result = run_level(level, guard, scenario["input"])
        except GuardError as exc:
            report.checks.append(Check(name, False, f"guard error: {exc}"))
            continue
        expected = scenario["expect"]
        passed = result.contains(expected)
        report.checks.append(Check(name, passed, "" if passed else f"expected {expected!r}"))
    return report
