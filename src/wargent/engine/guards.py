"""Guard modules: pluggable defensive hooks around the simulated agent.

A guard is a Python module that may define any of these functions:

    filter_segment(segment, ctx)            -> Segment | None
    allow_tool_call(call, ctx)              -> bool
    filter_output(text, ctx)                -> str
    allow_memory_write(entry, source, ctx)  -> bool
    approve_tool_update(old, new, ctx)      -> bool
    accept_delegation(message, ctx)         -> bool

Missing hooks behave permissively.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from wargent.engine.models import GuardContext, Segment, ToolCall


class GuardError(RuntimeError):
    """Raised when a guard module fails to load or raises while running."""


class Guard:
    def __init__(self, module: ModuleType | None = None) -> None:
        self.module = module

    @classmethod
    def from_file(cls, path: Path) -> Guard:
        spec = importlib.util.spec_from_file_location(f"wargent_guard_{abs(hash(str(path)))}", path)
        if spec is None or spec.loader is None:
            raise GuardError(f"cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:
            raise GuardError(f"{path.name}: {type(exc).__name__}: {exc}") from exc
        return cls(module)

    def _call(self, hook: str, default, *args):
        function = getattr(self.module, hook, None) if self.module else None
        if function is None:
            return default
        try:
            return function(*args)
        except Exception as exc:
            raise GuardError(f"{hook}: {type(exc).__name__}: {exc}") from exc

    def filter_segment(self, segment: Segment, ctx: GuardContext) -> Segment | None:
        result = self._call("filter_segment", segment, segment, ctx)
        if result is not None and not isinstance(result, Segment):
            raise GuardError("filter_segment must return a Segment or None")
        return result

    def allow_tool_call(self, call: ToolCall, ctx: GuardContext) -> bool:
        return bool(self._call("allow_tool_call", True, call, ctx))

    def filter_output(self, text: str, ctx: GuardContext) -> str:
        result = self._call("filter_output", text, text, ctx)
        if not isinstance(result, str):
            raise GuardError("filter_output must return a string")
        return result

    def allow_memory_write(self, entry: str, source: str, ctx: GuardContext) -> bool:
        return bool(self._call("allow_memory_write", True, entry, source, ctx))

    def approve_tool_update(self, old: str, new: str, ctx: GuardContext) -> bool:
        return bool(self._call("approve_tool_update", True, old, new, ctx))

    def accept_delegation(self, message: Segment, ctx: GuardContext) -> bool:
        return bool(self._call("accept_delegation", True, message, ctx))
