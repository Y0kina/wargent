# Documentation de wargent

- [Niveaux](levels/index.md)
- [Ajouter un niveau](add-a-level.md)

## Commandes

| Commande | Rôle |
| --- | --- |
| `wargent list` | lister les niveaux et leur statut |
| `wargent show N` | afficher le descriptif du niveau N |
| `wargent play N` | session interactive sur le niveau N |
| `wargent send N "entrée"` | envoyer une entrée et afficher le résultat |
| `wargent hint N` | révéler l'indice suivant (3 par niveau) |
| `wargent check N FLAG` | soumettre un flag |
| `wargent defend N` | préparer le guard d'un niveau résolu |
| `wargent defend N --run` | vérifier le guard face à l'attaque enregistrée |
| `wargent reset [N] --yes` | réinitialiser la progression |
| `wargent lang en\|fr` | choisir la langue de l'interface |

Les entrées peuvent contenir `\n` pour insérer un retour à la ligne. `--file CHEMIN` (ou
`/file CHEMIN` en session) envoie le contenu d'un fichier texte local.

## Commandes de session

`/help`, `/info`, `/inspect`, `/hint`, `/file CHEMIN`, `/submit FLAG`, `/quit`.

## Mode défense

Après la résolution d'un niveau, `wargent defend N` crée une copie modifiable du guard du
niveau dans le dossier utilisateur et affiche son chemin. Le guard est un module Python avec
des hooks facultatifs. `wargent defend N --run` rejoue l'attaque enregistrée pendant le niveau
ainsi qu'un ensemble d'entrées légitimes. La défense est acceptée lorsque l'attaque échoue et
que les entrées légitimes fonctionnent toujours.

| Hook | Rôle |
| --- | --- |
| `filter_segment(segment, ctx)` | inspecter ou modifier le contexte avant lecture par l'agent |
| `allow_tool_call(call, ctx)` | autoriser chaque appel d'outil |
| `filter_output(text, ctx)` | filtrer la réponse finale |
| `allow_memory_write(entry, source, ctx)` | autoriser les écritures en mémoire |
| `approve_tool_update(old, new, ctx)` | examiner les changements d'une description d'outil |
| `accept_delegation(message, ctx)` | accepter ou refuser une demande d'un autre agent |

## Fichiers

La progression et les guards sont stockés dans `~/.wargent` (variable `WARGENT_HOME` pour
changer le dossier). `WARGENT_UNLOCK_ALL=1` ouvre tous les niveaux. `WARGENT_LANG` force la langue.
