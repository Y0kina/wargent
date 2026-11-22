from typer.testing import CliRunner

from wargent.cli import app

runner = CliRunner()


def test_list_shows_synthetic_level(synthetic_level):
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Synthetic level" in result.output


def test_show_unknown_level():
    result = runner.invoke(app, ["show", "999"])
    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_show_briefing(synthetic_level):
    result = runner.invoke(app, ["show", "90"])
    assert result.exit_code == 0
    assert "Objective text." in result.output


def test_locked_level_is_refused(synthetic_level, monkeypatch):
    monkeypatch.delenv("WARGENT_UNLOCK_ALL")
    result = runner.invoke(app, ["show", "90"])
    assert result.exit_code == 1
    assert "locked" in result.output
