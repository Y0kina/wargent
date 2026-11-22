"""Checks applied to every level shipped in the package."""

import pytest

from wargent.engine.levels import PACKAGE_LEVELS, load_levels
from wargent.engine.runner import default_guard, run_level

LEVELS = [
    level for level in load_levels().values() if level.path and PACKAGE_LEVELS in level.path.parents
]


def test_levels_are_numbered_without_gaps():
    ids = sorted(level.id for level in LEVELS)
    assert ids == list(range(len(ids)))


def test_flags_are_unique():
    flags = [level.flag for level in LEVELS]
    assert len(flags) == len(set(flags))


@pytest.mark.parametrize("level", LEVELS, ids=lambda level: f"level{level.id}")
class TestEachLevel:
    def test_directory_content(self, level):
        names = {item.name for item in level.path.parent.iterdir()}
        assert names <= {"level.yaml", "guard.py", "__pycache__"}
        assert level.guard_path is not None

    def test_directory_name_matches_id(self, level):
        assert level.path.parent.name == f"level_{level.id:02d}"

    def test_guard_loads(self, level):
        default_guard(level)

    def test_flag_is_reachable_only_through_the_level(self, level):
        for block in level.text.values():
            assert level.flag not in str(block)

    def test_benign_scenarios_pass_on_default_guard(self, level):
        guard = default_guard(level)
        for scenario in level.benign:
            result = run_level(level, guard, scenario["input"])
            assert result.contains(scenario["expect"])
            assert not level.won(result)

    def test_benign_scenarios_do_not_win(self, level):
        guard = default_guard(level)
        for scenario in level.benign:
            assert not level.won(run_level(level, guard, scenario["input"]))

    def test_empty_input_does_not_win(self, level):
        assert not level.won(run_level(level, default_guard(level), ""))

    def test_guard_hooks_match_declared_defense(self, level):
        hooks = ("filter_segment", "allow_tool_call", "filter_output")
        guard = default_guard(level)
        defined = [hook for hook in hooks if hasattr(guard.module, hook)]
        if level.defend and level.id not in (10, 11, 8):
            assert defined
