"""Local progress storage (JSON file in the user directory)."""

from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path
from typing import Any

UNLOCK_ENV = "WARGENT_UNLOCK_ALL"
HOME_ENV = "WARGENT_HOME"
MAX_HINTS = 3


def home_dir() -> Path:
    override = os.environ.get(HOME_ENV)
    return Path(override) if override else Path.home() / ".wargent"


class Progress:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or home_dir() / "progress.json"
        self.data: dict[str, Any] = {"lang": None, "levels": {}}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and isinstance(loaded.get("levels"), dict):
                self.data = {"lang": loaded.get("lang"), "levels": loaded["levels"]}
        except (OSError, ValueError):
            with contextlib.suppress(OSError):
                self.path.replace(self.path.with_suffix(".bak"))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)

    def _entry(self, number: int) -> dict[str, Any]:
        return self.data["levels"].setdefault(
            str(number), {"solved": False, "defended": False, "hints": 0, "attack": None}
        )

    def is_solved(self, number: int) -> bool:
        return bool(self.data["levels"].get(str(number), {}).get("solved"))

    def is_defended(self, number: int) -> bool:
        return bool(self.data["levels"].get(str(number), {}).get("defended"))

    def is_unlocked(self, number: int) -> bool:
        if number == 0 or os.environ.get(UNLOCK_ENV):
            return True
        return self.is_solved(number - 1)

    def hints_used(self, number: int) -> int:
        return int(self.data["levels"].get(str(number), {}).get("hints", 0))

    def next_hint(self, number: int) -> int:
        entry = self._entry(number)
        entry["hints"] = min(MAX_HINTS, int(entry["hints"]) + 1)
        self.save()
        return int(entry["hints"])

    def attack(self, number: int) -> str | None:
        return self.data["levels"].get(str(number), {}).get("attack")

    def record_attack(self, number: int, text: str) -> None:
        self._entry(number)["attack"] = text
        self.save()

    def mark_solved(self, number: int) -> None:
        self._entry(number)["solved"] = True
        self.save()

    def mark_defended(self, number: int) -> None:
        self._entry(number)["defended"] = True
        self.save()

    def reset(self, number: int | None = None) -> None:
        if number is None:
            self.data["levels"] = {}
        else:
            self.data["levels"].pop(str(number), None)
        self.save()

    @property
    def lang(self) -> str | None:
        return self.data.get("lang")

    def set_lang(self, lang: str) -> None:
        self.data["lang"] = lang
        self.save()
