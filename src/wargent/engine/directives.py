"""Rule-based extraction of instructions from free text.

The simulated agent has no language model. It recognises a small set of imperative
patterns (read a file, reveal a value, send, post, remember, delegate, render an image).
Each pattern produces a Directive made of data sources and a destination (sink).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+|;\s*")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s)\]\"'<>]+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PATH_RE = re.compile(r"(?<![\w:/.~-])/[\w.~%+-]+(?:/[\w.~%+-]*)*")

VERB_RE = re.compile(
    r"\b(read|open|cat|load|fetch|show|print|display|reveal|tell|output|repeat|give|disclose|"
    r"share|leak|say|include|append|attach|send|email|mail|forward|post|publish|comment|pass|"
    r"copy|dump|remember|memorize|memorise|store|save|delegate|ask|render|embed)\b",
    re.I,
)
SECRET_RE = re.compile(
    r"\b(secrets?|passphrases?|passcodes?|passwords?|api[ _-]?keys?|access[ _-]?keys?|"
    r"tokens?|credentials?|flags?|keys?)\b",
    re.I,
)
PROMPT_RE = re.compile(
    r"\b(system (?:prompt|message)|your (?:initial |original )?(?:prompt|instructions))\b", re.I
)
REMEMBER_RE = re.compile(
    r"\b(remember|memori[sz]e|from now on|store (?:this )?in (?:your )?memory|"
    r"save (?:this )?to (?:your )?memory)\b",
    re.I,
)
DELEGATE_RE = re.compile(
    r"\b(delegate|(?:ask|tell|have|instruct) the worker|"
    r"(?:forward|send|pass)\b[^.\n]*\bto the worker)\b",
    re.I,
)
SEND_RE = re.compile(r"\b(send|email|mail|forward)\b", re.I)
POST_RE = re.compile(r"\b(post|publish|comment)\b", re.I)
TOOLARG_RE = re.compile(r"\b(\w+)\s+(?:parameter|argument|param|field)\b", re.I)
OVERRIDE_RE = re.compile(
    r"\b(ignore|disregard|forget)\b[^.\n]{0,30}\b(previous|prior|above|earlier|all)\b"
    r"[^.\n]{0,20}\binstructions?\b",
    re.I,
)
DEBUG_RE = re.compile(r"\b(debug|maintenance|developer|admin)\s+mode\b", re.I)
FILLER = {"the", "a", "an", "this", "that", "its", "your", "my"}


@dataclass(frozen=True)
class Directive:
    sources: tuple[tuple[str, str], ...]
    sink: str
    target: str = ""
    sentence: str = ""


@dataclass(frozen=True)
class Parsed:
    directives: tuple[Directive, ...]
    flags: frozenset[str]
    residue: str


def parse(text: str) -> Parsed:
    flags = set()
    if OVERRIDE_RE.search(text):
        flags.add("override")
    if DEBUG_RE.search(text):
        flags.add("debug")
    directives: list[Directive] = []
    residue: list[str] = []
    for chunk in SENTENCE_SPLIT.split(text):
        sentence = chunk.strip()
        if not sentence:
            continue
        directive = _directive(sentence)
        if directive is None:
            residue.append(sentence)
        else:
            directives.append(directive)
    return Parsed(tuple(directives), frozenset(flags), " ".join(residue))


def _tail(sentence: str, start: int) -> str:
    tail = sentence[start:].strip()
    tail = re.sub(r"^(that\b|:|,)\s*", "", tail, flags=re.I).strip()
    return tail


def _directive(sentence: str) -> Directive | None:
    if not VERB_RE.search(sentence):
        return None
    image = IMAGE_RE.search(sentence)
    work = IMAGE_RE.sub(" ", sentence)
    work = URL_RE.sub(" ", work)
    emails = EMAIL_RE.findall(work)
    work = EMAIL_RE.sub(" ", work)
    paths = [p.rstrip(".,;:)") for p in PATH_RE.findall(work)]
    core = PATH_RE.sub(" ", work)

    match = REMEMBER_RE.search(sentence)
    if match and not image:
        return Directive((), "remember", _tail(sentence, match.end()), sentence)
    match = DELEGATE_RE.search(sentence)
    if match and not image:
        if ":" in sentence:
            target = sentence.split(":", 1)[1].strip()
        else:
            target = _tail(sentence, match.end())
        return Directive((), "delegate", target, sentence)

    sources: list[tuple[str, str]] = [("file", p) for p in paths]
    if SECRET_RE.search(core):
        sources.append(("secret", ""))
    if PROMPT_RE.search(core):
        sources.append(("prompt", ""))

    if image:
        return Directive(tuple(sources), "image", image.group(1), sentence)
    if not sources:
        return None
    if emails and SEND_RE.search(core):
        return Directive(tuple(sources), "email", emails[0], sentence)
    if POST_RE.search(core):
        return Directive(tuple(sources), "post", "", sentence)
    arg = TOOLARG_RE.search(core)
    if arg:
        name = arg.group(1).lower()
        return Directive(tuple(sources), "tool_arg", "note" if name in FILLER else name, sentence)
    return Directive(tuple(sources), "reply", "", sentence)
