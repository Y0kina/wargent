# Contributing

Documentation is available in English (`docs/en`) and French (`docs/fr`).
La documentation existe en anglais (`docs/en`) et en français (`docs/fr`).

## Development setup

```bash
git clone https://github.com/Y0kina/wargent.git
cd wargent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Checks

```bash
ruff check .
ruff format --check .
python scripts/gen_level_docs.py --check
python -m pytest
```

All four commands must pass before a pull request is opened.

## Conventions

- Commit messages are short, in English and factual (`add level 3 indirect injection`).
- Code comments are brief and explain intent.
- Interface strings live in `src/wargent/i18n`. Every key exists in both languages.
- Level texts exist in both `en` and `fr`.

## Contributing a level

A level is a folder `src/wargent/levels/level_NN/` with `level.yaml` and `guard.py`. The guide
`docs/en/add-a-level.md` describes the format. A level proposal is welcome as an issue first.

Rules:

- Everything is simulated. No real exploit, malware, credential or network access.
- Solutions, payloads and walkthroughs are never added to the repository. Hints stay partial.
- Each level provides legitimate-use scenarios (`benign`) that a correct defense must keep working.
- After a change to a level, regenerate the docs with `python scripts/gen_level_docs.py`.

## Pull requests

Keep a pull request focused on one change. Describe the behaviour that changes and add tests.
