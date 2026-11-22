import pytest

from wargent.engine.guards import Guard, GuardError
from wargent.engine.models import GuardContext, Segment, ToolCall

CTX = GuardContext()


def write(tmp_path, source):
    path = tmp_path / "guard.py"
    path.write_text(source, encoding="utf-8")
    return path


def test_missing_hooks_are_permissive():
    guard = Guard()
    segment = Segment("user", "user", "hi")
    assert guard.filter_segment(segment, CTX) is segment
    assert guard.allow_tool_call(ToolCall("read_file", {}), CTX) is True
    assert guard.filter_output("text", CTX) == "text"
    assert guard.allow_memory_write("e", "user", CTX) is True


def test_guard_from_file_runs_hooks(tmp_path):
    guard = Guard.from_file(
        write(tmp_path, "def filter_output(text, ctx):\n    return text.upper()\n")
    )
    assert guard.filter_output("abc", CTX) == "ABC"


def test_syntax_error_is_reported(tmp_path):
    with pytest.raises(GuardError):
        Guard.from_file(write(tmp_path, "def broken(:\n"))


def test_runtime_error_is_reported(tmp_path):
    guard = Guard.from_file(write(tmp_path, "def filter_output(text, ctx):\n    return 1 / 0\n"))
    with pytest.raises(GuardError):
        guard.filter_output("x", CTX)


def test_wrong_return_type_is_rejected(tmp_path):
    guard = Guard.from_file(write(tmp_path, "def filter_output(text, ctx):\n    return None\n"))
    with pytest.raises(GuardError):
        guard.filter_output("x", CTX)
