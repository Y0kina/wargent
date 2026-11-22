from wargent.engine.progress import Progress


def test_unlock_rules(monkeypatch):
    progress = Progress()
    assert progress.is_unlocked(0)
    assert not progress.is_unlocked(1)
    progress.mark_solved(0)
    assert progress.is_unlocked(1)
    monkeypatch.setenv("WARGENT_UNLOCK_ALL", "1")
    assert progress.is_unlocked(7)


def test_progress_is_persisted():
    progress = Progress()
    progress.record_attack(3, "payload")
    progress.mark_solved(3)
    reloaded = Progress()
    assert reloaded.is_solved(3) and reloaded.attack(3) == "payload"


def test_hints_are_capped():
    progress = Progress()
    assert [progress.next_hint(1) for _ in range(5)] == [1, 2, 3, 3, 3]


def test_reset_one_and_all():
    progress = Progress()
    progress.mark_solved(0)
    progress.mark_solved(1)
    progress.reset(0)
    assert not progress.is_solved(0) and progress.is_solved(1)
    progress.reset()
    assert not progress.is_solved(1)


def test_corrupt_file_is_backed_up():
    progress = Progress()
    progress.mark_solved(0)
    progress.path.write_text("not json", encoding="utf-8")
    fresh = Progress()
    assert not fresh.is_solved(0)
    assert progress.path.with_suffix(".bak").exists()


def test_language_is_stored():
    progress = Progress()
    progress.set_lang("fr")
    assert Progress().lang == "fr"
