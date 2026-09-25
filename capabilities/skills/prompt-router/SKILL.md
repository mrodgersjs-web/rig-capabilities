---
name: prompt-router
description: Select a stored RIG prompt and compose it with the matching skill, memory, and doctrine for a natural-language job.
metadata:
  activation: The operator states a job to be done in plain language and wants the stored prompt that already does it, plus the system around it, instead of a blank chat turn.
  instruction: >-
    Turn one stated job into an assembled prompt pack: the best stored prompt from
    capabilities/prompts, the when-* skill route governing the work, the memory
    pages it must respect, and the governing doctrine. Never author a fresh prompt
    when a stored one earns its place.
  applies_when:
    env: any local agent runtime on Mike's machine (Aside, OMP/Orca, Codex, Claude)
    runtime: local-first; the deterministic ranker needs Node >= 18 and no network
    deps: node, capabilities/prompts/registry.json, optional bin/rig-s1gate and the rig-capabilities MCP
    params: one natural-language job statement; optional --top N and --json
    budget: one routing turn; a model call happens only to break a scored tie through JEV
    scale: one job to one pack; bulk corpus mining runs offline into the gitignored dump/
  permissions:
    - fs.read: capabilities/prompts/** (registry, ledger, prompt bodies, tools)
    - fs.read: ~/.codex/commands, ~/.codex/prompts, ~/.rig/universal-commands, ~/.omp/commands
    - fs.read: local session stores (~/.aside/u/0/sessions, ~/.codex/archived_sessions, ~/.codex/thread_history_1.sqlite, ~/.claude/projects)
    - fs.write: capabilities/prompts/dump/** (gitignored staging only)
    - fs.write: capabilities/prompts/ledger.jsonl (append-only pull log)
    - fs.write: capabilities/skills/prompt-router/references/routing.md (generated, never hand-edited)
    - exec: node tools/route.mjs, node tools/pull.mjs, node tools/ingest.mjs, node tools/list.mjs, node tools/mine_sessions.mjs
    - mcp.read: rig-capabilities.capabilities_route, rig-capabilities.capabilities_context_pack
    - exec: bin/rig-s1gate rank|check (advisory only)
    - deny: network writes, git push, publish, send, deploy, spend, credential reads
  flow:
    - 1 JEV FIRST: the routing judgment is a typed JEV decision, not a local guess - generate candidates with node tools/route.mjs (lexical, offline, scores reported) and put the pick through bin/rig-s1gate rank before any choice is presented; when no rubric covers the kind or the gate errors, DEFER to the operator with the named candidates and their scores
    - 2 CODE EVIDENCE: the deterministic ranker supplies the candidate list and scores so the JEV rank judges real candidates; run node tools/route.mjs --selftest after any trigger or registry change (fixture intents with expected picks, exit 1 on a wrong top-1)
    - 3 COMPOSE: assemble the pack - prompt body verbatim, the when-* meta-skill route plus exactly one child skill, the lane memory pages and named pre-checks, and the governing doctrine for the action class
    - 4 DELIVER: copy-paste pack with header PROMPT <id> v<version> [status] | SKILL <when-*>/<child> | PROVENANCE <src>, and the line unvalidated draft attached whenever score is null
    - 5 LOG: append one pull entry to ledger.jsonl and re-read it to confirm the append landed
  done_when:
    - a pack is delivered naming prompt id, version, status (draft or calibrated) and provenance
    - the skill route, memory pages and doctrine it composes are each named
    - an unmatched job reports NO_STORED_PROMPT with the nearest three candidates and their scores instead of an invented prompt
    - one pull entry is appended to ledger.jsonl and confirmed by re-read
    - no raw session text appears in the pack and nothing leaves the local machine
  out_of_scope:
    - calibrating prompts (AutoPrompt runs are promote.mjs territory; ingest only ever files drafts)
    - editing, exporting, deleting or re-syncing session stores
    - publishing, git push, sending, deploying, purchasing or signing anything
    - authoring a new prompt while a stored prompt fits the job
    - content about a minor (routes to its own lane skills first; never auto-scheduled)
---

# prompt-router

The "I just tell it what to do" layer over the prompt estate. One stated job in, one
assembled pack out: the prompt that already does that job, and the system that keeps
the work governed.

Run the `node tools/*.mjs` commands below from
`/Users/rig128gb/Developer/rig-capabilities/capabilities/prompts/`. Installed skill
copies contain this router, not the prompt registry or its tools.

FINDABILITY (load this skill, do not reinvent it): this is the router for
`capabilities/prompts/`. It is named from three places an agent already reads: the
`capabilities/prompts/README.md` Routing section, the capability index
(`capabilities_search` for "prompt router"), and `references/routing.md` generated from
the registry. If you are about to author a prompt for a stated job, stop and route first.

## Hierarchy

1. **Meta-skill (this file)** - routes only, holds no prompt content.
2. **`references/routing.md`** - category to prompt-id table, generated from `registry.json`
   by `node tools/route.mjs --write-routing`. Never hand-edited; the registry owns it.
3. **Prompt entries** - `capabilities/prompts/prompts/<id>/prompt.md`, each with YAML
   frontmatter carrying version, status, score, model_target and provenance.

## Routing contract (binding)

- MUST rank from the registry before authoring anything. Search before authoring is the
  library doctrine and it is not optional here.
- MUST report the prompt's `status` verbatim. `draft` (score null) is not `calibrated`,
  and a draft is never described as proven.
- MUST resolve the routing judgment through JEV (`rig-s1gate rank`) before presenting a
  pick. The ranker generates candidates and evidence; JEV decides. When the kind is absent
  or the gate errors: defer to the operator with the named candidates. Never guess a verdict
  locally, and never present an unscored pick as settled.
- MUST NOT emit raw session text into a pack. Mined prompts are distilled templates;
  session transcripts stay local and unexported.
- MUST NOT present a third-party prompt as first-party. Provenance and license travel with
  every prompt, and an unlicensed prompt is offered as a pattern, not as reusable text.
- MUST route content about a minor to its own lane skills first; that lane is never
  auto-scheduled and never inherits a commercial call to action.
- MUST log one `pull` entry in `ledger.jsonl` when a pack is delivered from a stored prompt.

## How to route

1. Classify the job's kind (research, code, writing, ops, planning, verification, gtm, job).
2. `node tools/route.mjs "<the job as stated>" --json` from `capabilities/prompts/`.
   Lexical ranker over registry fields (id, task, domain, category, triggers). Deterministic,
   offline, no model. It reports scores so a weak match is visible rather than implied.
3. Read the winning `prompts/<id>/prompt.md`. Check `status`, `score`, `model_target`.
4. Compose the pack:
   - **prompt body** - verbatim, unmodified. If it needs slots filled, say which.
   - **skill route** - the `when-*` meta-skill for the lane (see the JTBD filing system),
     then exactly one child skill.
   - **memory pages** - the lane's project page and its named pre-checks.
   - **doctrine** - the governing loop for the action class (proof, gate-d, phase).
5. Deliver the pack in copy-paste form, with a header line:
   `PROMPT <id> v<version> [status] | SKILL <when-*>/<child> | PROVENANCE <src>`.
6. `node tools/pull.mjs <id>` to ledger the pull (or append by hand if pull is unavailable).

## Composition rules

- One prompt per pack unless the job is explicitly two jobs. Two jobs get two packs.
- A prompt with `score: null` ships with the line "unvalidated draft" attached.
- When the ranker's top score is below 2.0, the honest answer is NO_STORED_PROMPT; show the
  nearest three with scores and offer to draft a new one as `status: draft`.
- When a stored prompt is third-party (license field not `first-party`), quote it as a
  pattern with its source URL and rewrite before use rather than pasting it wholesale.

## Honesty rules

- A pack is assembled evidence: every member names where it came from.
- Routing quality is measured, not asserted. If `rig-s1gate label` outcomes show bad picks,
  the trigger words are wrong; fix the registry entry, not the verdict.
- This skill routes and assembles. It does not send, publish, push, buy, or sign.
