# Add a level

A level lives in `src/wargent/levels/level_NN/` and contains two files: `level.yaml` and
`guard.py`. During development, a level can also be placed in any directory listed in the
`WARGENT_EXTRA_LEVELS` environment variable.

## level.yaml

| Key | Meaning |
| --- | --- |
| `id`, `slug` | level number and short name |
| `flag` | value of the form `FLAG{...}` |
| `slot` | where the player input is placed (informative label) |
| `runner` | `single`, `rugpull`, `memory` or `delegation` |
| `win` | `output` (flag in the reply) or `leak` (flag observed outside the sandbox) |
| `defend` | `true` when the level has a defense exercise |
| `owasp` | references to the OWASP LLM and Agentic Top 10 |
| `agent` | configuration of the simulated agent (see below) |
| `worker` | second agent, `delegation` runner only |
| `sandbox` | fake files, pages and external tools |
| `segments` | context given to the agent; `{{input}}` marks the player input |
| `segments2` | second session, `memory` runner only |
| `scenario` | tool description, tasks and swap point, `rugpull` runner only |
| `benign` | legitimate inputs with an expected substring |
| `text` | `en` and `fr` blocks: title, scenario, objective, control, concept, defense, 3 hints |

### Agent configuration

`system_prompt`, `secrets`, `tools`, `obey_roles` (roles whose instructions are executed),
`exempt_roles` (roles not subject to the confidentiality rule), `confidential`, `refuse_words`,
`role_tags`, `reply`, `fallback`, `task_call`, `sensitive_prefixes`, `allowed_domains`.

The agent recognises a fixed set of imperative patterns: read a file, reveal a value, send mail,
post a comment, render an image, remember, delegate. They are defined in
`src/wargent/engine/directives.py`.

## guard.py

The guard is the vulnerable baseline. It defines the hooks relevant to the level and documents
their contract in the module docstring. The player edits a copy in defense mode.

## Requirements

- Both languages are complete and each level has exactly three hints.
- At least one `benign` scenario exercises the capability the attack abuses, so that blocking
  everything does not count as a defense.
- The level is fully simulated. No real command, file, network access or exploit.
- No solution or payload is committed.

## Checks

```bash
python scripts/gen_level_docs.py
python -m pytest
```
