# Ajouter un niveau

Un niveau se trouve dans `src/wargent/levels/level_NN/` et contient deux fichiers :
`level.yaml` et `guard.py`. Pendant le développement, un niveau peut aussi être placé dans un
dossier listé dans la variable d'environnement `WARGENT_EXTRA_LEVELS`.

## level.yaml

| Clé | Signification |
| --- | --- |
| `id`, `slug` | numéro et nom court du niveau |
| `flag` | valeur de la forme `FLAG{...}` |
| `slot` | emplacement de l'entrée du joueur (libellé informatif) |
| `runner` | `single`, `rugpull`, `memory` ou `delegation` |
| `win` | `output` (flag dans la réponse) ou `leak` (flag observé hors du bac à sable) |
| `defend` | `true` si le niveau a un exercice de défense |
| `owasp` | références au Top 10 OWASP LLM et Agentic |
| `agent` | configuration de l'agent simulé (voir ci-dessous) |
| `worker` | second agent, runner `delegation` uniquement |
| `sandbox` | faux fichiers, pages et outils externes |
| `segments` | contexte donné à l'agent ; `{{input}}` marque l'entrée du joueur |
| `segments2` | seconde session, runner `memory` uniquement |
| `scenario` | description d'outil, tâches et point de bascule, runner `rugpull` uniquement |
| `benign` | entrées légitimes avec une sous-chaîne attendue |
| `text` | blocs `en` et `fr` : title, scenario, objective, control, concept, defense, 3 hints |

### Configuration de l'agent

`system_prompt`, `secrets`, `tools`, `obey_roles` (rôles dont les instructions sont exécutées),
`exempt_roles` (rôles non soumis à la règle de confidentialité), `confidential`, `refuse_words`,
`role_tags`, `reply`, `fallback`, `task_call`, `sensitive_prefixes`, `allowed_domains`.

L'agent reconnaît un ensemble fixe de motifs impératifs : lire un fichier, révéler une valeur,
envoyer un mail, publier un commentaire, afficher une image, retenir, déléguer. Ils sont définis
dans `src/wargent/engine/directives.py`.

## guard.py

Le guard est la base vulnérable. Il définit les hooks pertinents pour le niveau et documente leur
contrat dans la docstring du module. Le joueur modifie une copie en mode défense.

## Exigences

- Les deux langues sont complètes et chaque niveau a exactement trois indices.
- Au moins un scénario `benign` exerce la capacité exploitée par l'attaque, afin que tout bloquer
  ne compte pas comme une défense.
- Le niveau est entièrement simulé. Aucune commande, aucun fichier réel, aucun accès réseau, aucun exploit.
- Aucune solution ni aucun payload n'est commité.

## Vérifications

```bash
python scripts/gen_level_docs.py
python -m pytest
```
