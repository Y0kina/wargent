"""Shared data types of the simulation engine."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(frozen=True)
class Segment:
    """A piece of text placed in the agent context.

    role: system, user, document, web, email, ticket, tooldesc, memory or agent.
    trusted: when False, the agent treats the text as data and never as instructions.
    """

    role: str
    source: str
    text: str
    trusted: bool = True

    def with_text(self, text: str) -> Segment:
        return replace(self, text=text)


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]
    allowed: bool = True
    output: str = ""


@dataclass(frozen=True)
class Leak:
    """Data observed outside the sandbox (attacker side)."""

    channel: str
    text: str


@dataclass(frozen=True)
class GuardContext:
    """Read-only information handed to guard hooks."""

    secrets: tuple[str, ...] = ()
    history: tuple[ToolCall, ...] = ()
    sensitive_prefixes: tuple[str, ...] = ()
    allowed_domains: tuple[str, ...] = ()


@dataclass
class RunResult:
    output: str = ""
    calls: list[ToolCall] = field(default_factory=list)
    leaks: list[Leak] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)

    def contains(self, needle: str) -> bool:
        """True when the text appears in the reply or in any leaked data."""
        return needle in self.output or any(needle in leak.text for leak in self.leaks)
