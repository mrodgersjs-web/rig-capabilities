# Agent consolidation audit

This is an inventory and adoption plan, not a retirement list. No agent, skill,
prompt, or runtime configuration was removed or replaced during this audit.

## Current inventory

The catalog indexes 1,604 agent entries across Codex, Claude, Hermes, OMP,
Prime, and canonical sources. Normalizing file stems yields 991 role names. Of
those names, 588 occur in multiple sources. The inventory has 124 groups of
byte-identical agent files. The count includes assets that their runtime does
not load, such as OMP JSON agent records. A matching name or hash is a
consolidation candidate, not proof that two runtime contracts behave the same
way. OMP has 123 logical-name collisions between its Markdown agents and JSON
records. Do not treat those JSON records as another 147 live workers. Only 10
entries have `source=canonical`. The catalog parser finds all four quality fields on 2 of the
1,604 entries; this measures metadata completeness, not output quality.

Only `rig-stackwright.md` from the ten canonical agent files appears in OMP
and Prime's direct agent roots. Prime's copy matches. OMP's copy has a
`model:` line in the body rather than in frontmatter, so the loader does not
apply it. OMP's other 162 Markdown profiles have no canonical file owner in
this repo. Import and normalize before considering retirement.

Regenerate these counts with `rig_capabilities.mission.live_assets` and group
agent entries by normalized file stem, source, resolved path, and SHA-256.
Preserve the unnormalized ID and source path in every alias record.

## DAILY and LIBRARY classification

DAILY is the shared coding control path: the runtime's startup rules, the
meta-skill router, the selected specialist skill, Memory OS retrieval, Jev's
logged typed decision, a task contract, and an independent verifier. These
components apply to every coding task. The current `rig-mission` composer
proposes this path for Codex and Claude, but it does not dispatch workers or
certify completion.

LIBRARY is the specialist agent catalog. A specialist loads only when a task
selects its role. Do not put all 1,604 entries into every session. Keep vendor
builtins and unique role contracts accessible until outcome tests prove that a
smaller canonical set covers them. Do not delete a duplicate on a name match.

## Runtime adoption status

| Runtime | Verified now | Missing proof or repair |
| --- | --- | --- |
| Codex | Multi-agent is enabled. The config declares 463 agent roles. A live Python-task composition selected a Codex specialist, meta-skill, Memory OS package, and logged Jev decision. | This was one proposed route. It did not prove every registered agent executes the shared contract or passes a real outcome test. |
| OMP | Live `omp read` loads `when-shipping-code` and `when-building-or-fixing-agents` from its configured skill directories. OMP's user-agent loader reads 163 Markdown files. | Its `includeSkills` allowlist rejects `jev-everywhere`, `jev-system1-cascade`, and `skill-upgrades`. Its live roots contain 110 of 169 canonical skills, with four drifted and 59 missing. The agent directory also has 147 JSON records that the loader ignores. Only 60 of 409 declared `autoloadSkills` references resolve in the current OMP skill inventory; 349 do not. None of the 122 agents that declare skills resolves every declared skill. No all-agent execution receipt exists. |
| Prime Agent | The package list includes the coding fleet. Its direct agent root has one profile, `rig-stackwright.md`. | Its direct skill root has 28 of 169 canonical skills. Four links are broken, including `rig-memory-os`. `prime-agent status --json` reports the default daemon unreachable, so no current coding outcome can pass. |
| Aside | The app and native subagent tool are live. All 15 meta-skill copies currently hash-match canonical files. Memory OS and Jev MCPs are enabled. | Its agent directory has no agent definition files. Of 145 recent sessions, 2 read a `when-*` meta-skill and none called `capabilities_route`. The prompt router is absent, all 26 canonical prompts remain drafts, and six user-skill links are broken. |

Aside usage counts came from 145 local session files with 5,078 tool calls. They
show voluntary use, not a gate. Aside is not a supported runtime in the current
mission composer. Codex and Claude are the only listed routable runtimes.

## Keep and upgrade rule

Do not name a winner from metadata alone. For each overlapping role, retain
the original paths and run the same held-out tasks through the candidates.
Record the input, allowed actions, output artifact, result, latency, cost,
failure mode, and independent verifier. A keeper needs a substrate, telos,
quality profile, work ledger, memory policy, and proof path under
`agent_outcome_evaluation_v0`. Promote one canonical role only after it wins on
real outcomes. Keep old names as aliases with rollback until every runtime
proves the new role loads and completes a task. Do not collapse roles with
different authority or tool boundaries merely because their names match.

## Install plan

1. Make a deterministic overlap report with canonical IDs, aliases, content
   hashes, runtime support, and ownership. Classify exact byte duplicates
   separately from same-name variants. Include each agent's declared skill
   references and whether the runtime resolves them. Do not remove files.
2. Define a small coding DAILY set. Keep specialist roles in LIBRARY. Benchmark
   overlapping specialists before choosing keepers or rewriting prompts.
3. Repair the OMP allowlist. Repair Prime's broken Memory OS link and verify
   its real skill root. Add Aside as a first-class distribution target, then
   connect a mission adapter and prompt router. Use governed installers rather
   than hand-editing home-directory copies.
4. For each runtime, collect a fresh session receipt that binds the startup
   rules, selected meta-skill, specialist skill and agent contract, prompt
   hashes, Memory OS package ID, Jev decision ID, behavior test, independent
   verifier, and completion verdict. A file or config entry alone is not a pass.
5. Change the default route only after a held-out Promptfoo suite and real
   outcome tasks show that the keeper is at least as good as the candidate it
   replaces. Keep a rollback pointer. Never let Jev alone certify DONE.

Direct edits to OMP and Aside home-directory configuration failed the
`rig-repo-guard` placement check. The canonical installer supports OMP and
Codex, but not Aside or Prime Agent as `capability_install` targets. Extend and
verify the governed distribution path before changing those live roots.

## Verification status

This audit is read-only. `rig-agent-standards doctor --format json` passed its
profile and load-document checks. Codex agent counts came from its config and
installed TOMLs. OMP's skill check compared each Markdown frontmatter
`autoloadSkills` name with a fresh `omp read skill://__rig_audit_missing__`
inventory. OMP and Aside checks used their live loaders and local session
traces. Prime has no current live-process proof. No retirement, runtime install,
or all-agent completion claim is authorized by these observations.
