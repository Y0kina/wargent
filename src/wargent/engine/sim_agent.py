"""Deterministic simulated agent.

The agent has no model. It reproduces common weaknesses of real agents with explicit rules:
it obeys instructions found in the roles it trusts, applies naive confidentiality checks,
extracts hidden text from pages, and calls tools without further validation unless a guard
hook says otherwise.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

from wargent.engine.directives import Directive, Parsed, parse
from wargent.engine.guards import Guard
from wargent.engine.models import GuardContext, RunResult, Segment, ToolCall
from wargent.engine.sandbox import Sandbox

COMMENT_RE = re.compile(r"<!--(.*?)-->", re.S)
TAG_RE = re.compile(r"<[^>]+>")
HIDDEN_RE = re.compile(
    r"<(\w+)\b[^>]*(?:display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0|\bhidden\b)"
    r"[^>]*>.*?</\1>",
    re.I | re.S,
)
ROLE_TAG_RE = re.compile(
    r"^\s*(?:\[(?:system|developer)\]|<(?:system|developer)>|(?:system|developer)\s*:)\s*", re.I
)
PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")


def visible_text(html: str) -> str:
    """Text a person sees when the page is rendered."""
    text = COMMENT_RE.sub(" ", html)
    text = HIDDEN_RE.sub(" ", text)
    return _squash(TAG_RE.sub(" ", text))


def agent_text(html: str) -> str:
    """Text the agent extracts: comments and hidden elements are kept."""
    text = COMMENT_RE.sub(lambda m: f" {m.group(1)} ", html)
    return _squash(TAG_RE.sub(" ", text))


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_role_tags(segment: Segment) -> list[Segment]:
    """Re-label lines that start with a role tag as system-level text."""
    parts: list[Segment] = []
    buffer: list[str] = []
    for line in segment.text.splitlines():
        match = ROLE_TAG_RE.match(line)
        if match:
            if buffer:
                parts.append(segment.with_text("\n".join(buffer)))
                buffer = []
            parts.append(Segment("system", "role-tag", line[match.end() :]))
        else:
            buffer.append(line)
    if buffer:
        parts.append(segment.with_text("\n".join(buffer)))
    return parts


@dataclass
class AgentConfig:
    name: str = "assistant"
    system_prompt: str = ""
    secrets: dict[str, str] = field(default_factory=dict)
    tools: tuple[str, ...] = ()
    obey_roles: tuple[str, ...] = ("user",)
    exempt_roles: tuple[str, ...] = ("system", "agent")
    confidential: bool = False
    refuse_words: tuple[str, ...] = ()
    refusal: str = "I can't share that."
    role_tags: bool = False
    gist_roles: tuple[str, ...] = ("document", "web", "email", "ticket", "memory")
    reply: str = ""
    fallback: str = "How can I help?"
    task_call: dict[str, Any] | None = None
    sensitive_prefixes: tuple[str, ...] = ()
    allowed_domains: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentConfig:
        data = dict(data)
        for key in (
            "tools",
            "obey_roles",
            "exempt_roles",
            "refuse_words",
            "gist_roles",
            "sensitive_prefixes",
            "allowed_domains",
        ):
            if key in data:
                data[key] = tuple(data[key])
        return cls(**data)


class SimAgent:
    def __init__(
        self,
        config: AgentConfig,
        sandbox: Sandbox,
        guard: Guard,
        memory: list[str] | None = None,
        delegate: Callable[[str], str] | None = None,
    ) -> None:
        self.cfg = config
        self.sandbox = sandbox
        self.guard = guard
        self.memory = memory if memory is not None else []
        self.delegate = delegate
        self.calls: list[ToolCall] = []
        self.trace: list[str] = []
        self.extra_args: dict[str, str] = {}

    def context(self) -> GuardContext:
        return GuardContext(
            secrets=tuple(self.cfg.secrets.values()),
            history=tuple(call for call in self.calls if call.allowed),
            sensitive_prefixes=self.cfg.sensitive_prefixes,
            allowed_domains=self.cfg.allowed_domains,
        )

    def run(self, segments: list[Segment]) -> RunResult:
        parts: list[str] = []
        gist: list[str] = []
        self.extra_args = {}
        privileged = False
        for segment in self._prepare(segments):
            parsed = parse(segment.text)
            if segment.role == "system" and "debug" in parsed.flags:
                privileged = True
            if segment.role in self.cfg.gist_roles and parsed.residue:
                gist.append(parsed.residue)
            if not segment.trusted:
                self.trace.append(f"{segment.role} '{segment.source}': treated as data")
                continue
            if segment.role not in self.cfg.obey_roles and segment.role != "system":
                continue
            for directive in parsed.directives:
                parts.extend(self._execute(directive, segment, parsed, privileged))

        result = ""
        if self.cfg.task_call:
            args = {**self.cfg.task_call.get("args", {}), **self.extra_args}
            output = self._tool(self.cfg.task_call["tool"], args)
            result = output if output is not None else "(unavailable)"

        gist_text = " ".join(gist)[:200]
        base = self.cfg.reply.format(gist=gist_text, result=result) if self.cfg.reply else ""
        if ("{gist}" in self.cfg.reply and not gist_text) or (
            "{result}" in self.cfg.reply and not result
        ):
            base = ""
        lines = [line for line in [base, *parts] if line]
        output_text = "\n".join(lines) or self.cfg.fallback
        return RunResult(output=output_text, calls=self.calls, trace=self.trace)

    def _prepare(self, segments: list[Segment]) -> list[Segment]:
        prepared: list[Segment] = []
        for segment in segments:
            filtered = self.guard.filter_segment(segment, self.context())
            if filtered is None:
                self.trace.append(f"{segment.role} '{segment.source}': dropped by guard")
                continue
            segment = filtered
            if segment.role == "web":
                self.trace.append(f"page as displayed: {visible_text(segment.text)!r}")
                segment = segment.with_text(agent_text(segment.text))
                self.trace.append(f"page as extracted: {segment.text!r}")
            if self.cfg.role_tags and segment.role == "user":
                prepared.extend(split_role_tags(segment))
            else:
                prepared.append(segment)
        return prepared

    def _refuses(self, segment: Segment, parsed: Parsed, privileged: bool) -> bool:
        cfg = self.cfg
        if not cfg.confidential or privileged or segment.role in cfg.exempt_roles:
            return False
        if cfg.refuse_words:
            if "override" in parsed.flags:
                return False
            lowered = segment.text.lower()
            return any(word in lowered for word in cfg.refuse_words)
        return True

    def _execute(
        self, directive: Directive, segment: Segment, parsed: Parsed, privileged: bool
    ) -> list[str]:
        data: list[str] = []
        for kind, value in directive.sources:
            if kind == "file":
                output = self._tool("read_file", {"path": value})
                if output is not None:
                    data.append(output)
            elif kind in ("secret", "prompt"):
                if self._refuses(segment, parsed, privileged):
                    self.trace.append("request refused by the confidentiality rule")
                    return [self.cfg.refusal]
                if kind == "prompt":
                    data.append(self.cfg.system_prompt)
                else:
                    data.append(next(iter(self.cfg.secrets.values()), "(no secret available)"))
        body = "\n".join(data)
        return self._deliver(directive, segment, body)

    def _deliver(self, directive: Directive, segment: Segment, body: str) -> list[str]:
        sink = directive.sink
        if sink == "reply":
            return [body] if body else []
        if sink == "email":
            self._tool("send_email", {"to": directive.target, "body": body})
        elif sink == "post":
            self._tool("post_comment", {"text": body})
        elif sink == "tool_arg":
            self.extra_args[directive.target] = body
        elif sink == "image":
            return [f"![image]({self._expand(directive.target, body)})"]
        elif sink == "remember":
            if self.guard.allow_memory_write(directive.target, segment.role, self.context()):
                self.memory.append(directive.target)
                self.trace.append(f"memory write accepted from {segment.role}")
            else:
                self.trace.append(f"memory write rejected from {segment.role}")
        elif sink == "delegate":
            if self.delegate is None:
                self.trace.append("no worker available")
            else:
                return [self.delegate(directive.target)]
        return []

    def _expand(self, template: str, data: str) -> str:
        secrets = self.cfg.secrets

        def substitute(match: re.Match[str]) -> str:
            name = match.group(1)
            if name == "data":
                return quote(data, safe="")
            if name in secrets:
                return quote(secrets[name], safe="")
            if name == "secret" and secrets:
                return quote(next(iter(secrets.values())), safe="")
            return match.group(0)

        return PLACEHOLDER_RE.sub(substitute, template)

    def _tool(self, name: str, args: dict[str, Any]) -> str | None:
        label = f"{name}({', '.join(f'{k}={str(v)[:40]!r}' for k, v in args.items())})"
        if name not in self.cfg.tools:
            self.trace.append(f"tool unavailable: {label}")
            return None
        call = ToolCall(name, dict(args))
        if not self.guard.allow_tool_call(call, self.context()):
            call.allowed = False
            self.calls.append(call)
            self.trace.append(f"tool call blocked: {label}")
            return None
        call.output = self.sandbox.execute(name, args)
        self.calls.append(call)
        self.trace.append(f"tool call: {label}")
        return call.output
