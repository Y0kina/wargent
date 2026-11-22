from wargent import i18n


def test_both_languages_define_the_same_keys():
    assert set(i18n._load("en")) == set(i18n._load("fr"))


def test_translation_and_fallback():
    i18n.set_language("fr")
    assert "niveau" in i18n.t("level_unknown", n=1).lower()
    assert i18n.t("missing-key") == "missing-key"
    i18n.set_language("en")
    assert i18n.t("level_unknown", n=1) == "Level 1 does not exist."


def test_detect_language(monkeypatch):
    monkeypatch.setenv("WARGENT_LANG", "")
    monkeypatch.setenv("LC_ALL", "fr_FR.UTF-8")
    assert i18n.detect_language() == "fr"
    monkeypatch.setenv("LC_ALL", "en_US.UTF-8")
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    assert i18n.detect_language() == "en"
