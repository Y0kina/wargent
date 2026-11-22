"""Interface strings (English and French)."""

from __future__ import annotations

import os
from functools import cache
from importlib import resources

import yaml

LANGUAGES = ("en", "fr")
DEFAULT_LANGUAGE = "en"
_current = DEFAULT_LANGUAGE


def detect_language() -> str:
    """Language from WARGENT_LANG, then from the locale environment."""
    explicit = os.environ.get("WARGENT_LANG", "").lower()
    if explicit in LANGUAGES:
        return explicit
    for name in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(name, "").lower()
        if value.startswith("fr"):
            return "fr"
    return DEFAULT_LANGUAGE


def set_language(lang: str) -> None:
    global _current
    _current = lang if lang in LANGUAGES else DEFAULT_LANGUAGE


def get_language() -> str:
    return _current


@cache
def _load(lang: str) -> dict[str, str]:
    text = resources.files("wargent.i18n").joinpath(f"{lang}.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)


def t(key: str, **values: object) -> str:
    table = _load(_current)
    template = table.get(key) or _load(DEFAULT_LANGUAGE).get(key) or key
    return template.format(**values) if values else template
