# wargent documentation

- [Levels](levels/index.md)
- [Add a level](add-a-level.md)

## Commands

| Command | Purpose |
| --- | --- |
| `wargent list` | list levels and status |
| `wargent show N` | show the briefing of level N |
| `wargent play N` | interactive session on level N |
| `wargent send N "input"` | send one input and print the outcome |
| `wargent hint N` | reveal the next hint (3 per level) |
| `wargent check N FLAG` | submit a flag |
| `wargent defend N` | prepare the guard of a solved level |
| `wargent defend N --run` | verify the guard against the recorded attack |
| `wargent reset [N] --yes` | reset progress |
| `wargent lang en\|fr` | set the interface language |

Inputs may contain `\n` to insert a line break. `--file PATH` (or `/file PATH` in a session)
sends the content of a local text file.

## Session commands

`/help`, `/info`, `/inspect`, `/hint`, `/file PATH`, `/submit FLAG`, `/quit`.

## Defense mode

After a level is solved, `wargent defend N` creates an editable copy of the level guard in the
user directory and prints its path. The guard is a Python module with optional hooks. Running
`wargent defend N --run` replays the attack recorded during the level and a set of legitimate
inputs. The defense is accepted when the attack fails and the legitimate inputs still work.

| Hook | Purpose |
| --- | --- |
| `filter_segment(segment, ctx)` | inspect or modify context before the agent reads it |
| `allow_tool_call(call, ctx)` | authorise each tool call |
| `filter_output(text, ctx)` | filter the final reply |
| `allow_memory_write(entry, source, ctx)` | authorise memory writes |
| `approve_tool_update(old, new, ctx)` | review changes to a tool description |
| `accept_delegation(message, ctx)` | accept or refuse a request from another agent |

## Files

Progress and guards are stored in `~/.wargent` (override with the `WARGENT_HOME` variable).
`WARGENT_UNLOCK_ALL=1` opens every level. `WARGENT_LANG` forces the language.
