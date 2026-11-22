"""Level definitions loaded from level.yaml files."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from wargent.engine.models import RunResult
from wargent.engine.sandbox import Sandbox
from wargent.engine.sim_agent import AgentConfig

PACKAGE_LEVELS = Path(__file__).resolve().parent.parent / "levels"
EXTRA_LEVELS_ENV = "WARGENT_EXTRA_LEVELS"
RUNNERS = ("single", "rugpull", "memory", "delegation")
WIN_MODES = ("output", "leak")
LANGUAGES = ("en", "fr")
TEXT_KEYS = ("title", "scenario", "objective", "control", "concept", "defense", "hints")
FLAG_RE = re.compile(r"^FLAG\{[A-Za-z0-9_\-]+\}$")


class LevelError(ValueError):
    """Raised when a level definition is invalid."""


@dataclass
class Level:
    id: int
    slug: str
    flag: str
    slot: str
    runner: str = "single"
    win: str = "output"
    defend: bool = True
    owasp: list[str] = field(default_factory=list)
    agent: dict[str, Any] = field(default_factory=dict)
    worker: dict[str, Any] = field(default_factory=dict)
    sandbox: dict[str, Any] = field(default_factory=dict)
    segments: list[dict[str, str]] = field(default_factory=list)
    segments2: list[dict[str, str]] = field(default_factory=list)
    scenario: dict[str, Any] = field(default_factory=dict)
    benign: list[dict[str, str]] = field(default_factory=list)
    text: dict[str, dict[str, Any]] = field(default_factory=dict)
    path: Path | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], path: Path | None = None) -> Level:
        data = dict(data)
        data["path"] = path
        try:
            level = cls(**data)
        except TypeError as exc:
            raise LevelError(f"invalid level definition: {exc}") from exc
        level.validate()
        return level

    def validate(self) -> None:
        if not isinstance(self.id, int) or self.id < 0:
            raise LevelError("id must be a non-negative integer")
        if not FLAG_RE.match(self.flag):
            raise LevelError(f"level {self.id}: flag must look like FLAG{{...}}")
        if self.runner not in RUNNERS:
            raise LevelError(f"level {self.id}: unknown runner {self.runner!r}")
        if self.win not in WIN_MODES:
            raise LevelError(f"level {self.id}: unknown win mode {self.win!r}")
        if not self.segments and self.runner != "rugpull":
            raise LevelError(f"level {self.id}: segments are required")
        if self.defend and not self.benign:
            raise LevelError(f"level {self.id}: levels with a defense need benign scenarios")
        if self.runner == "memory" and not self.segments2:
            raise LevelError(f"level {self.id}: memory runner needs segments2")
        if self.runner == "delegation" and not self.worker:
            raise LevelError(f"level {self.id}: delegation runner needs a worker")
        if self.runner == "rugpull" and not self.scenario:
            raise LevelError(f"level {self.id}: rugpull runner needs a scenario")
        for lang in LANGUAGES:
            block = self.text.get(lang)
            if not block:
                raise LevelError(f"level {self.id}: missing '{lang}' text")
            for key in TEXT_KEYS:
                if key not in block:
                    raise LevelError(f"level {self.id}: missing text key '{lang}.{key}'")
            if len(block["hints"]) != 3:
                raise LevelError(f"level {self.id}: '{lang}' needs exactly 3 hints")
        AgentConfig.from_dict(self.agent)

    def t(self, lang: str) -> dict[str, Any]:
        return self.text.get(lang) or self.text["en"]

    def agent_config(self) -> AgentConfig:
        return AgentConfig.from_dict(self.agent)

    def worker_config(self) -> AgentConfig:
        return AgentConfig.from_dict(self.worker)

    def new_sandbox(self) -> Sandbox:
        return Sandbox.from_config(self.sandbox)

    @property
    def guard_path(self) -> Path | None:
        if self.path is None:
            return None
        candidate = self.path.parent / "guard.py"
        return candidate if candidate.exists() else None

    def won(self, result: RunResult) -> bool:
        if self.win == "output":
            return self.flag in result.output
        return any(self.flag in leak.text for leak in result.leaks)


def load_level_file(path: Path) -> Level:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise LevelError(f"{path}: expected a mapping")
    return Level.from_dict(data, path=path)


def _level_files() -> list[Path]:
    roots = [PACKAGE_LEVELS]
    extra = os.environ.get(EXTRA_LEVELS_ENV, "")
    roots.extend(Path(item) for item in extra.split(os.pathsep) if item)
    files: list[Path] = []
    for root in roots:
        if root.is_dir():
            files.extend(sorted(root.glob("*/level.yaml")))
    return files


def load_levels() -> dict[int, Level]:
    levels: dict[int, Level] = {}
    for path in _level_files():
        level = load_level_file(path)
        if level.id in levels:
            raise LevelError(f"duplicate level id {level.id}")
        levels[level.id] = level
    return dict(sorted(levels.items()))


def get_level(number: int) -> Level | None:
    return load_levels().get(number)
