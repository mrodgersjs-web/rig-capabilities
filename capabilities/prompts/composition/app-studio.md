# App Studio prompt composition - draft v1

The App Studio family in this library: 1 meta prompt, 15 main prompts (11 stage + 4 role),
29 sub-prompts. Every entry is a draft with `score: null`; nothing here is calibrated.
Registry entries carry `tier`, `parent`, `stage`, `audience`, `lessons` and a `jev` block
(rubric `app.prompt`, decision id, verdict) on top of the standard fields.

## Tiers

| tier | ids | owns |
|---|---|---|
| meta | `app-studio-meta` | the 11-stage machine, roles, composition, JEV-first, evidence contract, Gate-D, stop rules |
| main, stage | `app-studio-<stage>` for the 11 stages | what the stage decides, its done_when, its output gate, its sub-prompts |
| main, role | `app-studio-builder`, `app-studio-verifier`, `app-studio-ui-judge`, `app-studio-lesson-filer` | the agent's contract and its role sub-prompts |
| sub | `app-sub-*` | one parameterized fragment, owned by exactly one main prompt (its `parent`) |

A main prompt lists its sub-prompts on its `sub-prompts owned:` line; the meta prompt lists every
main prompt on its `main prompts:` line. `capabilities/skills/app-studio/scripts/validate_hierarchy.py`
(V9) checks both, plus registry, frontmatter and hierarchy agreement.

## Composition order (a builder prompt)

1. `app-studio-meta`
2. the role prompt for the audience (`app-studio-builder` for a bench builder)
3. the stage prompts that fire for the task, in stage order
4. the sub-prompts owned by those stages (and by the role prompt) whose firing rule matches the task

Only prompts whose `audience` is the composed role (or `all`) are included, so conductor-only
fragments such as `app-sub-acceptance-checks` never reach a builder. Hidden acceptance checks are
never read by the composer: the bench renderer drops the task's `acceptance` array before anything
else runs.

Firing rules for stages and sub-prompts live with the consumer, not here:
`~/Desktop/Projects/rig-app-studio/bench/prompt-rules.json` (read by `bench/render_prompt.py`).

## Variables

`{{TASK_ID}} {{OUTCOME}} {{SOURCE}} {{FEATURES}} {{CONTRACT}} {{STACK}} {{SERVE}} {{PORT_LO}}
{{PORT_HI}} {{OUT_OF_SCOPE}} {{DOCTRINE_ROOT}} {{FIRED_STAGES}} {{SKIPPED_STAGES}}
{{FIRED_LESSONS}} {{DATA_DIR}} {{PROVIDER}} {{FALLBACK}} {{QUOTA}}` are filled by the composer.
Role-only variables (`{{TASK_JSON}} {{APP_DIR}} {{RUN_DIR}} {{PORT}} {{SCREENS_DIR}} {{SPEC_MD}}
{{BRIEF}} {{LEDGER}} {{FAILURE_EVIDENCE}} {{TARGET}} {{RUNNER_PATHS}}`) belong to verifier, judge
and filer compositions. A composer must refuse to emit a prompt with an unfilled variable.

## Attribution

Each composition writes `.app-studio/prompt.json`: task id, mode (`library` or `legacy`), the ordered
prompt list with `id`, `version`, `content_sha256` and bytes, fired and skipped stages, fired
lessons, and the sha256 of the composed text. A score row is attributable to prompt versions only
through that file.

## Gates

- Library gate: every prompt passes `rig-s1gate check app.prompt` with contract_stated,
  evidence_done, lessons_actionable and stop_rules above 0.9 before it is filed. Decision ids are in
  each registry entry's `jev` block. `app.prompt` is advisory and uncalibrated.
- Output gates: each stage record goes to `app.stage-gate` plus the stage's sub rubric.

## Lessons

Lessons are carried as named imperatives: LA ids from
`capabilities/skills/app-studio/references/lessons.jsonl`, TG ids (TubeGuruji, with video ids) and
BENCH ids (App Bench evidence) from `capabilities/skills/app-studio/references/prompts.md`.

## Filing and versions

File family prompts with `~/Desktop/Projects/rig-app-studio/bench/prompt-file.py` (`new` or
`version`), not `tools/ingest.mjs`: the filer gates on `app.prompt` and keeps the family fields V9
reads. Nothing changes in place: a changed prompt is a new version, and a ledger edit to a lesson a
prompt carries forces one (V9 fails stale LA text).

## Seam: channel-derived sub-prompts

Lessons from the ten build channels enter through
`capabilities/prompts/composition/app-studio-channel-lessons.md`: classify, index row, prompt
text, hierarchy row, firing rule, gates.
