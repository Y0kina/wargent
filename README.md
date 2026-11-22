# wargent

[![CI](https://github.com/Y0kina/wargent/actions/workflows/ci.yml/badge.svg)](https://github.com/Y0kina/wargent/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/wargent)](https://pypi.org/project/wargent/)
[![Python](https://img.shields.io/pypi/pyversions/wargent)](https://pypi.org/project/wargent/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Offline command-line wargame to learn attacking and defending AI agents, one level at a time.
No API key, no Docker, no network access.

Version française : [README.fr.md](README.fr.md)

## Why

Agents combine instructions, tools and untrusted content, and most of their incidents come from
mixing these up. wargent turns each class of weakness into a short level. The agents are
simulated and deterministic, so every level is reproducible and runs without any setup.

## Install

```bash
pipx install wargent
wargent list
wargent play 0
```

Python 3.10 or later is required. `pip install wargent` works as well.

## Levels

| # | Title |
| --- | --- |
| 0 | Anatomy of an agent |
| 1 | Direct prompt injection |
| 2 | Role confusion |
| 3 | Indirect injection through a document |
| 4 | Hidden text in a web page |
| 5 | Tool description poisoning |
| 6 | Excessive agency |
| 7 | Exfiltration through rendering |
| 8 | Rug pull |
| 9 | Toxic flow between tools |
| 10 | Memory poisoning |
| 11 | Delegation between agents |
| 12 | Final boss |

Each level has three progressive hints and references the OWASP Top 10 for LLM Applications
and the OWASP Top 10 for Agentic Applications. Levels unlock in order.

## Defense mode

After solving a level, `wargent defend N` creates a Python guard that can be edited. `wargent
defend N --run` replays the recorded attack and a set of legitimate inputs. The defense is
accepted when the attack fails and legitimate use still works.

```python
def allow_tool_call(call, ctx):
    return call.name != "send_email"
```

Hooks and their contracts are described in [docs/en/index.md](docs/en/index.md).

## What is simulated

Agents are rule-based programs without a language model. Files, pages, mail, tools and
domains (`*.example.test`) exist only in memory. The engine never executes a command, reads a
real file or opens a network connection on behalf of an agent. Every secret is fictional.

The source code of the agent is readable. Reading it is part of the learning, but it reveals
how each level works.

## Documentation

- [Commands and defense mode](docs/en/index.md)
- [Level descriptions](docs/en/levels/index.md)
- [Add a level](docs/en/add-a-level.md)

## Roadmap

- Optional mode backed by a local model
- Score and completion certificate
- Community levels

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Solutions are never added to the repository.

## Related projects

wargent targets beginners and runs offline. Other labs cover complementary ground:
[DVMCP](https://github.com/harishsg993010/damn-vulnerable-MCP-server),
[DVAA](https://github.com/opena2a-org/damn-vulnerable-ai-agent) and
[OWASP FinBot CTF](https://github.com/GenAI-Security-Project/finbot-ctf).
References: [OWASP GenAI Security Project](https://genai.owasp.org).

## License

[MIT](LICENSE)
