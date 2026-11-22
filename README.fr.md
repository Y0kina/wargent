# wargent

[![CI](https://github.com/Y0kina/wargent/actions/workflows/ci.yml/badge.svg)](https://github.com/Y0kina/wargent/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/wargent)](https://pypi.org/project/wargent/)
[![Python](https://img.shields.io/pypi/pyversions/wargent)](https://pypi.org/project/wargent/)
[![Licence : MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

Wargame en ligne de commande, hors ligne, pour apprendre à attaquer et défendre des agents IA,
niveau par niveau. Sans clé API, sans Docker, sans accès réseau.

English version: [README.md](README.md)

## Pourquoi

Les agents combinent instructions, outils et contenu non fiable, et la plupart de leurs
incidents viennent de la confusion entre ces éléments. wargent transforme chaque classe de
faille en un court niveau. Les agents sont simulés et déterministes : chaque niveau est
reproductible et fonctionne sans configuration.

## Installation

```bash
pipx install wargent
wargent list
wargent play 0
```

Python 3.10 ou supérieur est requis. `pip install wargent` fonctionne aussi.

## Niveaux

| # | Titre |
| --- | --- |
| 0 | Anatomie d'un agent |
| 1 | Injection de prompt directe |
| 2 | Confusion de rôles |
| 3 | Injection indirecte par document |
| 4 | Texte caché dans une page web |
| 5 | Empoisonnement de description d'outil |
| 6 | Excès de pouvoir |
| 7 | Exfiltration par le rendu |
| 8 | Rug pull |
| 9 | Flux toxique entre outils |
| 10 | Empoisonnement de la mémoire |
| 11 | Délégation entre agents |
| 12 | Boss final |

Chaque niveau propose trois indices progressifs et renvoie au Top 10 OWASP pour les applications
LLM et au Top 10 OWASP pour les applications agentiques. Les niveaux se déverrouillent dans l'ordre.

## Mode défense

Une fois un niveau résolu, `wargent defend N` crée un guard Python modifiable. `wargent defend N
--run` rejoue l'attaque enregistrée et un ensemble d'entrées légitimes. La défense est acceptée
lorsque l'attaque échoue et que l'usage légitime fonctionne toujours.

```python
def allow_tool_call(call, ctx):
    return call.name != "send_email"
```

Les hooks et leurs contrats sont décrits dans [docs/fr/index.md](docs/fr/index.md).

## Ce qui est simulé

Les agents sont des programmes à règles, sans modèle de langage. Les fichiers, pages, mails,
outils et domaines (`*.example.test`) n'existent qu'en mémoire. Le moteur n'exécute jamais de
commande, ne lit aucun fichier réel et n'ouvre aucune connexion réseau pour le compte d'un
agent. Tous les secrets sont fictifs.

Le code source de l'agent est lisible. Le lire fait partie de l'apprentissage, mais révèle le
fonctionnement de chaque niveau.

## Documentation

- [Commandes et mode défense](docs/fr/index.md)
- [Descriptif des niveaux](docs/fr/levels/index.md)
- [Ajouter un niveau](docs/fr/add-a-level.md)

## Feuille de route

- Mode optionnel reposant sur un modèle local
- Score et certificat de fin
- Niveaux communautaires

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md). Les solutions ne sont jamais ajoutées au dépôt.

## Projets voisins

wargent s'adresse aux débutants et fonctionne hors ligne. D'autres labs couvrent un terrain
complémentaire :
[DVMCP](https://github.com/harishsg993010/damn-vulnerable-MCP-server),
[DVAA](https://github.com/opena2a-org/damn-vulnerable-ai-agent) et
[OWASP FinBot CTF](https://github.com/GenAI-Security-Project/finbot-ctf).
Références : [OWASP GenAI Security Project](https://genai.owasp.org).

## Licence

[MIT](LICENSE)
