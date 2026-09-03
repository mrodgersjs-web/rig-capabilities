# Great example — iqrsqpi-v11 (reference loop-skill)

What "great" looks like for a v11 loop-skill, shown on the reference implementation.

## A great loop.yaml

- `schema: rig.loop-skill.v11`, `id`, `version`, `doctrine_source` (the prose it encodes).
- Every stage: `id`, `name`, `artifact`, `gate` (≥1 deterministic check), `write_policy`.
- Gates read files and exit codes — never the agent's sentence. A regex gate carries a
  `hint` that tells the agent exactly what to write.
- `closing_loop` names the failing stages and where they reopen; `kill_switch` has all three
  limits; `outward_policy.require_gate_d: true`.

## A great SKILL.md

- Frontmatter: quality contract (`outcome`, `done_when` with a `cmd:python3 bin/rig-loop test <id>`
  line, `great_example`, `quality_floor ≥ 0.7`) and `hooks:` for Claude (PreToolUse with
  `--skill <id>` so the first write auto-activates; Stop).
- Step 0 is `rig-loop activate <id>`; a stage table with artifact · gate · command; the
  closing loop and kill switch stated; a Gate-D section; an **Honesty notes** section that says
  what the engine cannot prove.

## Great tests (tests/cases.json)

- Each gate shown RED on a planted defect and GREEN after the fix.
- Out-of-order advance refused; outward command denied then allowed after `APPROVE <run_id>`.
- Closing loop reaches `escalated` after `max_iterations`; the Stop hook blocks twice then yields.
- A full happy path ends with `seal` and `run_status: done`.

## The session, in practice

```
$ rig-loop activate iqrsqpi-v11 --intent "add rate limiting to /api/send"
[rig-loop] IQRSQPI v11 · run iqrsqpi-v11-2026…-a1b2c3 · mode auto · iteration 1/3 · gate-d not approved
[rig-loop] NOW: stage I1 Intent (1/7) — artifact: ~/.rig/state/loops/runs/…/artifacts/intent.md — gates: file_contains(intent.md); regex(intent.md); regex_absent(intent.md)
… (agent tries to edit src/api.py)
[rig-loop iqrsqpi-v11] WRITE BLOCKED at stage I1 Intent: src/api.py. No code before the goal card. …
$ rig-loop stage I1 pass
$ rig-loop stage Q1 pass
$ rig-loop counter qr_passes --inc   (×2)
$ rig-loop stage R pass
$ rig-loop stage S pass              ← code writes unlock; drift tracked against spec ## Files
$ rig-loop check add "pytest -q tests/test_rate_limit.py"
$ rig-loop plant "remove limiter" --red "pytest -q tests/test_rate_limit.py -k limiter_disabled" --green "pytest -q tests/test_rate_limit.py"
$ rig-loop stage Q2 pass
$ rig-loop seal && rig-loop stage P pass
$ rig-loop gate-d request --action "push feature branch"   # Mike: rig-loop gate-d approve --phrase "APPROVE <run_id>"
$ rig-loop stage I2 pass             → run done; Stop hook allows
```
