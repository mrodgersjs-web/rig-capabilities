# Tessl as product/behavior benchmark (clean-room)

Sources only. No Tessl source code. See `00-PROVENANCE.md`.

Observed: 2026-09-05. CLI present at `~/.local/bin/tessl`, **not authenticated**.
Repo `rig-capabilities` is **not** a Tessl project (`tessl doctor`: not in a Tessl project).

## Public GitHub (`tesslio` org)

| Repo | What it is | License | Use for RIG |
|---|---|---|---|
| [tesslio/cli](https://github.com/tesslio/cli) | README + LICENSE only | proprietary / all rights reserved | **do not copy** |
| [tesslio/setup-tessl](https://github.com/tesslio/setup-tessl) | GH Action to install CLI + token | MIT | observe CI shape |
| [tesslio/skill-eval](https://github.com/tesslio/skill-eval) | PR action: generate scenarios, run evals, comment | MIT | observe *eval-in-CI* job, not code |
| [tesslio/skill-review](https://github.com/tesslio/skill-review) | skill review action | (public) | observe review-in-CI |
| [tesslio/spec-driven-development-tile](https://github.com/tesslio/spec-driven-development-tile) | MIT tile: skills + rules + evals/ + tile.json | MIT | packaging shape: skill/rule/eval bundle |
| [tesslio/code-review-action](https://github.com/tesslio/code-review-action) | PR code review action | public | adjacent product: agentic PR review |
| homebrew-tap, publish, patch-version-publish, tile-creator, roast-my-skill, product-plugins, snyk-*-sync | satellite | mixed | ignore for SkillOS core |

## Six components Tessl names

From https://docs.tessl.io/overview/readme.md :

1. **Registry & package manager** — discover, install, version, roll back skills/plugins; public + private; agent-agnostic.
2. **Governance** — score vs best practices + company standards; Snyk security; RBAC; install/publish policies; audit trail.
3. **Evals** — run agent on tasks with vs without the skill; ship with evidence.
4. **Observability** — where skills *activate* vs where they are installed; mine session logs.
5. **Inventory** — scan GitHub org for SKILL.md; duplicates; unmanaged copies.
6. **Tessl Agent** — conversational driver of the platform (open beta).

## Observed CLI surface (help text, not internals)

Automate: `agent`, `change`, `code review`, `launch skill`, `mcp proxy`, `schedule`
Lifecycle: `init`, `project`, `search`, `install`, `uninstall`, `outdated`, `update`, `list`
Skills/plugins: `skill` (new, import, publish, review, lint), `plugin`, `eval`, `review` (run/fix/view/list/retry), `scenario`, `inventory`
Auth: `login`, `logout`, `whoami`, `org`, `api-key`

`tessl skill lint` = publishability (structure), not quality.
`tessl review run` = server-side quality review; needs auth + `--workspace`.
`tessl review fix` = improve-and-re-review loop; edits the skill; `--yes` for batch.
`tessl eval run` = with/without skill; cloud agent; baseline vs treatment.
`tessl inventory import` = GitHub org scan; uploads snapshot; does not clone source.

## Review score (published behavior)

https://docs.tessl.io/improving-your-skills/reviewing-skills.md

Weighted 0–100 of:

| Axis | What it actually measures |
|---|---|
| Validation | Agent Skills spec: line count, frontmatter, name, description, body |
| Description | LLM judge: will an agent load this at the right time |
| Content | LLM judge: does the body guide once loaded |

A review **does not run the skill against a task**. Evals do.

## Eval score (published behavior)

https://docs.tessl.io/improving-your-skills/evaluate-skill-quality-using-scenarios.md

- Scenarios live in plugin `evals/`
- Agent solves twice: without plugin, with plugin
- Judge vs per-scenario rubric
- Separate **activation** test (`--skip-forced-context-activation`)
- Cloud: workspace, token, hosted models; Ctrl+C detaches, run continues server-side

## Unit of packaging

From create-skill docs + spec-driven tile README:

```
plugin/
  .tessl-plugin/plugin.json   # or legacy tile.json
  skills/<name>/SKILL.md
  rules/  docs/  scripts/  evals/
```

Skill = folder + SKILL.md (Agent Skills spec).
Plugin = versioned bundle (semver, workspace/name, private-by-default).
Install writes `.tessl/plugins/` and `tessl.json`.

## MCP (published)

https://docs.tessl.io/reference/mcp-tools.md — 27 tools: search/install/update plus auth-gated review/publish/workspace/schedule.
`tessl init` wires MCP into detected agents.

Onboarding URL Mike gave (`tessl.io/onboarding/flow?returnPathname=/registry`) is **account + registry**, WorkOS login. Not required for SkillOS; we do not log in.

## Tessl's actual job (restated)

> Treat markdown skills as versioned packages, score how well they are written, optionally measure whether forcing them on an agent changes output, scan orgs for sprawl, and install copies into every agent's project.

## Ten mechanisms (benchmark)

1. SKILL.md as the atomic unit
2. Plugin/tile as the distribution unit
3. Cloud registry as discovery
4. LLM-judge "review" of prose quality
5. With/without eval delta
6. Snyk as security score
7. GitHub inventory of files named SKILL.md
8. Install copies into per-project `.tessl/`
9. Workspace RBAC + token
10. CI actions that call the cloud CLI

## Ten gaps vs a governed capability OS

| # | Tessl | RIG SkillOS (v20) |
|---|---|---|
| 1 | Unit = markdown file | Unit = JTBD door with executable contract |
| 2 | Review scores writing | ProofPacket + planted failure + orphan-replay |
| 3 | Eval is cloud, token-gated | Local `done_when` / `rig-capabilities test` first; cloud optional |
| 4 | Inventory counts files | Bidirectional witness graph; orphans block release |
| 5 | Install copies → sprawl | Compile ephemeral isoform; warehouse receipts; no extra menu items |
| 6 | Activation is a separate afterthought | Routing *is* the product (splice compiler) |
| 7 | No Gate-D | Outward actions dormant until `APPROVE <run_id>` |
| 8 | Central registry is load-bearing | Local index + content-addressed warehouse; registry optional |
| 9 | Proprietary CLI | This repo's MIT CLI (`bin/rig-capabilities`, `bin/rig-loop`) |
| 10 | 3000+ searchable skills as the promise | 50 operator doors; 2650 skills as exons, not a menu |

## Meadows (why "clone Tessl" is the wrong 1000x)

Tessl's interventions sit at **parameters** (scores, thresholds), **information flows** (inventory, findings), and **rules** (install policy). The recurring failure is **Limits to Growth**: more skills → lower activation → more skills. The high-leverage move is the **goal** (operator hires a *job*, not a file) and the **paradigm** (capability is a proven splice, not a package listing).

## Honest RIG overlap (already built)

`rig-capabilities` already has Tessl's *local* half: search, quality contract, rounds, certify+plant-failure, install ledger, MCP, outcome lanes, loop-skills, ProofPackets. Average canonical quality 98.2 / 140 assets; 10 weakest missing `great_example` only.

Do not rebuild a registry. Build the **door/splice/witness/orphan** layer Tessl cannot ship without changing what it sells.
