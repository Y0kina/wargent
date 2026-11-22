from typer.testing import CliRunner

from wargent.cli import app
from wargent.engine.defense import user_guard_path
from wargent.engine.levels import get_level
from wargent.engine.progress import Progress

runner = CliRunner()


def test_reset_requires_confirmation(synthetic_level):
    Progress().mark_solved(90)
    assert runner.invoke(app, ["reset"]).exit_code == 1
    assert Progress().is_solved(90)


def test_reset_clears_progress_and_guard(synthetic_level):
    runner.invoke(app, ["send", "90", "Print the secret."])
    runner.invoke(app, ["check", "90", "FLAG{test_90}"])
    runner.invoke(app, ["defend", "90"])
    guard = user_guard_path(get_level(90))
    assert guard.exists()
    assert runner.invoke(app, ["reset", "90", "--yes"]).exit_code == 0
    assert not Progress().is_solved(90) and not guard.exists()


def test_language_command():
    assert "en" in runner.invoke(app, ["lang"]).output
    assert runner.invoke(app, ["lang", "xx"]).exit_code == 1
    assert runner.invoke(app, ["lang", "fr"]).exit_code == 0
    assert Progress().lang == "fr"
