import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_generator():
    spec = importlib.util.spec_from_file_location(
        "gen_level_docs", ROOT / "scripts" / "gen_level_docs.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_level_docs_are_up_to_date():
    generator = load_generator()
    for path, text in generator.expected_files().items():
        assert path.exists(), f"missing {path.relative_to(ROOT)}"
        assert path.read_text(encoding="utf-8") == text, f"stale {path.relative_to(ROOT)}"


def test_level_index_is_up_to_date_when_present():
    generator = load_generator()
    for path, text in generator.index_files().items():
        if path.exists():
            assert path.read_text(encoding="utf-8") == text


def test_docs_never_contain_flags():
    generator = load_generator()
    flags = [level.flag for level in generator.packaged_levels()]
    for path in (ROOT / "docs").rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert not any(flag in content for flag in flags)
