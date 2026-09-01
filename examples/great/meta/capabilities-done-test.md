# Great example — capabilities-done-test

Run: `test semgrep`

| check | form | ok | detail |
|---|---|---|---|
| SKILL.md exists | file | Y | capabilities/skills/semgrep/SKILL.md |
| run-scans.sh exists | file | Y | capabilities/skills/semgrep/scripts/run-scans.sh |

pass=True with both checks quoted. The second check used to be `grep:...:Semgrep` — which passed even when the skill's body was deleted (frontmatter carried the word). V22's plant-failure replaced it with an external file check. This example is the lesson: a done-test earns its green by being able to say no.
