"""Generate docs/<lang>/levels/*.md from the level definitions.

Usage: python scripts/gen_level_docs.py [--check]
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wargent.engine.levels import PACKAGE_LEVELS, load_levels  # noqa: E402

LABELS = {
    "en": {
        "scenario": "Scenario",
        "objective": "Objective",
        "control": "Controlled input",
        "concept": "Concept",
        "defense": "Defense approach",
        "reference": "Reference",
        "hints": "Hints",
        "index": "Levels",
        "level": "Level",
        "title": "Title",
        "note": "Hints are intentionally partial. Solutions are not published.",
    },
    "fr": {
        "scenario": "Scénario",
        "objective": "Objectif",
        "control": "Entrée contrôlée",
        "concept": "Concept",
        "defense": "Approche de défense",
        "reference": "Référence",
        "hints": "Indices",
        "index": "Niveaux",
        "level": "Niveau",
        "title": "Titre",
        "note": "Les indices sont volontairement partiels. Les solutions ne sont pas publiées.",
    },
}


def packaged_levels():
    return [
        level
        for level in load_levels().values()
        if level.path and PACKAGE_LEVELS in level.path.parents
    ]


def render_level(level, lang: str) -> str:
    labels = LABELS[lang]
    block = level.t(lang)
    lines = [f"# {labels['level']} {level.id}: {block['title']}", ""]
    if level.owasp:
        lines += [f"**{labels['reference']}:** " + "; ".join(level.owasp), ""]
    for key in ("scenario", "objective", "control", "concept", "defense"):
        lines += [f"## {labels[key]}", "", str(block[key]).strip(), ""]
    lines += [f"## {labels['hints']}", ""]
    lines += [f"{i}. {str(hint).strip()}" for i, hint in enumerate(block["hints"], start=1)]
    lines += ["", f"_{labels['note']}_", ""]
    return "\n".join(lines)


def render_index(levels, lang: str) -> str:
    labels = LABELS[lang]
    lines = [
        f"# {labels['index']}",
        "",
        f"| {labels['level']} | {labels['title']} |",
        "| --- | --- |",
    ]
    for level in levels:
        title = level.t(lang)["title"]
        lines.append(f"| [{level.id}]({level.id:02d}.md) | {title} |")
    lines.append("")
    return "\n".join(lines)


def expected_files() -> dict[Path, str]:
    """Per-level pages."""
    files: dict[Path, str] = {}
    for lang in LABELS:
        folder = ROOT / "docs" / lang / "levels"
        for level in packaged_levels():
            files[folder / f"{level.id:02d}.md"] = render_level(level, lang)
    return files


def index_files() -> dict[Path, str]:
    """Level index pages, written next to the per-level pages."""
    levels = packaged_levels()
    if not levels:
        return {}
    return {
        ROOT / "docs" / lang / "levels" / "index.md": render_index(levels, lang) for lang in LABELS
    }


def main() -> int:
    files = {**expected_files(), **index_files()}
    if "--check" in sys.argv:
        stale = [
            path
            for path, text in files.items()
            if (not path.exists() and path.name != "index.md")
            or (path.exists() and path.read_text("utf-8") != text)
        ]
        for path in stale:
            print(f"out of date: {path.relative_to(ROOT)}")
        return 1 if stale else 0
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
