# Canonical estate vs Tessl review

Tessl CLI is authenticated (`rodgemd1`, workspace `rodgemd1`) and Snyk CLI is
authenticated (`rodgemd1`) as an explicitly requested, separate task. Neither
vendors CLI source into the tree; provenance still denies `tesslio/cli`. The
SkillOS DAG (v5+) does not depend on either.

Tracked sanitized evidence: `review-summary-2026-09-05.md`.
Full per-run JSON (untracked working evidence): `.context/tessl-review-batch/`,
`.context/snyk-code-review.json`.

Tessl axes: https://docs.tessl.io/improving-your-skills/reviewing-skills.md

## Tessl `review run` — 140 canonical assets, 2026-09-05

| axis | result |
|---|---|
| Canonical denominator | 140 (skill 29, harness 67, loop 16, command 13, hook 13, agent 1, data 1) |
| Review records | 280 (security + quality per asset), all terminal |
| Supported (skill) | 29 assets → 58 attempts, **58 completed, 0 failed** |
| Unsupported (non-skill) | 111 assets → 222 explicit `unsupported` records (Tessl reviews SKILL.md bundles only; harnesses/loops/hooks/commands/agents/data are not converted to skills) |
| Quality score (29 completed) | min 66, max 99, mean 85.86 |
| Security findings | 2 accepted MEDIUM `W011` (`iqrsqpi-v20`, `semgrep`) — inherent third-party-content exposure; each carries a treat-content-as-data rule; both verdicts `pass` |
| Hash binding | every supported review labelled with its row's live catalog SHA (`Repo._sha_dir`), re-run after edits so no record binds a stale hash |

12 supported quality reviews initially failed on malformed `outcome:` YAML
(compact-mapping scalars); the frontmatter was repaired and re-run to pass. The
four W011 security skills gained explicit untrusted-content handling; `rig-office-docs`
and `semgrep-rule-creator` cleared, the two above are accepted with reason.

## Snyk — local CLI, 2026-09-05

| scan | result |
|---|---|
| `snyk code test --org=rodgemd1` (SAST) | scan completed, **272 findings: 0 high, 26 medium, 246 low** — untriaged, not a clearance |
| `snyk test` (open-source deps) | no supported manifests (stdlib-only `pyproject.toml`) |

Snyk Code was enabled in the org UI (Free plan, no billing) and the setting
persisted across reload before the scan ran.

## Catalog hygiene — current

| gate | result |
|---|---|
| Quality-contract fields | 140/140 specified |
| Exemplars (`great_example`) | 140 declared / 140 resolved / **0 dangling** |
| Executable `done_when` | canonical unrunnable count **0** (prose rows converted to `cmd:`/`file:`/`grep:`; the three remaining hook rows are `cmd:python3 scripts/hook_fires.py <hook>` with real deny/allow fixtures) |
| Secret sweep | no AKIA/sk-/PEM/TESSL_TOKEN assignments in this session's edits |

## Store gate (unchanged, red)

`skillos check --stores` stays red: 143/4993 restorable (140 blob + 3 network-verified
recipe). External harness roots have no license-cleared blob or verified git recipe;
SkillOS v6+ remains gated behind a green store gate. This review task does not touch
that gate.
