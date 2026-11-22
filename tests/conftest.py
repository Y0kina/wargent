import pytest
import yaml


def make_level_dict(number: int = 90) -> dict:
    flag = f"FLAG{{test_{number}}}"
    text = {
        "title": "Synthetic level",
        "scenario": "Scenario text.",
        "objective": "Objective text.",
        "control": "Control text.",
        "concept": "Concept text.",
        "defense": "Defense text.",
        "hints": ["first", "second", "third"],
    }
    return {
        "id": number,
        "slug": "synthetic",
        "flag": flag,
        "slot": "user_message",
        "win": "output",
        "defend": True,
        "owasp": ["LLM01:2025 Prompt Injection"],
        "agent": {
            "name": "Test agent",
            "system_prompt": "You hold a secret.",
            "secrets": {"secret": flag},
            "confidential": False,
            "obey_roles": ["user"],
        },
        "segments": [{"role": "user", "text": "{{input}}"}],
        "benign": [{"input": "Hello there", "expect": "help"}],
        "text": {"en": dict(text), "fr": dict(text)},
    }


GUARD_SOURCE = '''"""Synthetic guard."""


def filter_output(text, ctx):
    return text
'''


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("WARGENT_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("WARGENT_LANG", "en")
    monkeypatch.delenv("WARGENT_EXTRA_LEVELS", raising=False)
    monkeypatch.delenv("WARGENT_UNLOCK_ALL", raising=False)


@pytest.fixture
def synthetic_level(tmp_path, monkeypatch):
    """Install a synthetic level 90 through the extra-levels directory."""
    root = tmp_path / "extra"
    folder = root / "level_90"
    folder.mkdir(parents=True)
    (folder / "level.yaml").write_text(yaml.safe_dump(make_level_dict(90)), encoding="utf-8")
    (folder / "guard.py").write_text(GUARD_SOURCE, encoding="utf-8")
    monkeypatch.setenv("WARGENT_EXTRA_LEVELS", str(root))
    monkeypatch.setenv("WARGENT_UNLOCK_ALL", "1")
    return 90
