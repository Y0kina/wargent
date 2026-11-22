import copy

import pytest
import yaml

from conftest import make_level_dict
from wargent.engine.levels import Level, LevelError, load_level_file, load_levels


def test_valid_level_loads():
    level = Level.from_dict(make_level_dict())
    assert level.id == 90 and level.t("fr")["title"] == "Synthetic level"


def test_unknown_language_falls_back_to_english():
    level = Level.from_dict(make_level_dict())
    assert level.t("de") is level.text["en"]


@pytest.mark.parametrize(
    "change",
    [
        {"flag": "not-a-flag"},
        {"runner": "unknown"},
        {"win": "never"},
        {"segments": []},
        {"benign": []},
        {"extra_field": 1},
    ],
)
def test_invalid_definitions_are_rejected(change):
    data = {**make_level_dict(), **change}
    with pytest.raises(LevelError):
        Level.from_dict(data)


def test_hints_must_be_three():
    data = copy.deepcopy(make_level_dict())
    data["text"]["en"]["hints"] = ["only one"]
    with pytest.raises(LevelError):
        Level.from_dict(data)


def test_missing_language_block_is_rejected():
    data = copy.deepcopy(make_level_dict())
    del data["text"]["fr"]
    with pytest.raises(LevelError):
        Level.from_dict(data)


def test_load_level_file_and_guard_path(tmp_path):
    folder = tmp_path / "level_90"
    folder.mkdir()
    (folder / "level.yaml").write_text(yaml.safe_dump(make_level_dict()), encoding="utf-8")
    level = load_level_file(folder / "level.yaml")
    assert level.guard_path is None
    (folder / "guard.py").write_text("", encoding="utf-8")
    assert level.guard_path == folder / "guard.py"


def test_extra_levels_are_discovered(synthetic_level):
    assert synthetic_level in load_levels()
