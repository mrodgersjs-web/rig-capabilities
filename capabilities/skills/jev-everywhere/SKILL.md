---
name: jev-everywhere
description: "JEV FIRST, and it is a mandate: every typed judgment (semantic triage, routing, classification, verification, ranking, screening, gating) goes to Jev, TypeSafe's System One, BEFORE any frontier LLM call, on every surface: coding agents, programs, and the Aside browser. Use at the start of any agent session (read the mission, inventory its decisions, route each to code -> Jev -> System 2 -> human) and whenever typed decisions are being wired into a program, hook, or browser lane. Carries the situation matrix (what good and bad use look like per decision class), per-surface embedding instructions, expectations in real numbers, and the evidence standard for claiming \"Jev was used\"."
tags: [rig, jev, typesafe, system-one, s1gate, doctrine, routing, embedding, session-protocol]
metadata:
  verified: "2026-09-23: rig-s1gate selftest 6/6 rule-engine checks, 71 rubrics loadable; this surface scored by the doctrine.surface rubric, bar: every required noul strictly above 0.9"
done_when:
  - grep:capabilities/skills/jev-everywhere/SKILL.md:JEV FIRST, BEFORE ANY FRONTIER CALL
  - grep:capabilities/skills/jev-everywhere/SKILL.md:Rule 2.{1,3}FAIL CLOSED
  - grep:capabilities/skills/jev-everywhere/references/decision-criteria.md:(?i)jev
---

# Jev Everywhere: session protocol + embedding kit

Load status: ALWAYS-LOADED. The two rules below are carried in the always-loaded instruction
surfaces (the AGENTS.md first section at session start; the CLAUDE.md / AGENTS.md JEV_EVERYWHERE
blocks; the cursor alwaysApply rule), so this text reaches the agent before any task begins. It is
not a deep reference an agent must already know about.

## Rule 1, a mandate and not a preference: JEV FIRST, BEFORE ANY FRONTIER CALL

An agent whose only context is this excerpt sends semantic triage, routing, and classification to
the rig-s1gate Jev path before any frontier LLM call. When the fast classifier is unavailable:
defer, never guess a verdict locally.

This changes your routing. From the moment the mission is known, no typed judgment is
made by your own prose, and no typed judgment goes to a frontier LLM before Jev. Any
decision expressible as a typed choice, probability, or score over bounded text is a
System-1 decision and goes to Jev first (100-200 ms, a fraction of a cent, decision
logged). A frontier model is the escalation tier, never the default tier.

Self-test for a typed judgment: if you are about to write a paragraph deciding between
named options, scoring a bounded artifact, or sorting items into fixed buckets, STOP.
That is a Jev question. The route is live now:
`python3 capabilities/hooks/redact_state.py < state.txt | bin/rig-s1gate check <rubric> --stdin --subject <kind:id> --json`
(exit 0 PASS / 1 BLOCK / 2 ESCALATE / 3 config), or MCP `capabilities_s1gate`, or
`rig_capabilities.s1gate.ask` from Python. Use it before you reason around it.

## Rule 2: FAIL CLOSED

Jev unreachable, timed out, or unparseable: DEFER the item and leave it untouched, or
ESCALATE into the human / System-2 queue. Never guess a verdict locally, never let a
prose model stand in for a typed answer, never treat silence or a missing field as
consent, and never send unredacted state (redact first: hooks/redact_state.py).

## The session protocol (run once the mission is known, re-run when it changes)

**Step 0. Mission line.** One line: what this session must accomplish and what it
must not touch. If scope shifts mid-session (an interjection restates the goal),
re-run Steps 1-2 for the new scope before doing more work.

**Step 1. Decision inventory.** List the decisions the mission will force: triage,
routing, verification, ranking, screening, extraction, gate transitions, lane
assignment. Name each one before it happens, not after.

**Step 2. Route each decision. First match wins:**

- **a. CODE.** A deterministic rule can decide it (schema, type, threshold, allow
  list, arithmetic, an equality pass). Code decides. Cheapest, reproducible, free.
- **b. JEV.** All three of the Jev-fit test hold:
  1. the judgment's state is bounded text (fits one string, no live browsing),
  2. the answer set is fixed: `noul` / `choice` / `score`,
  3. the answer is consumed by code (a threshold, a route, a lock, an ordering),
     not narrated to a human as prose.
- **c. SYSTEM 2 (frontier LLM).** Generation, long-horizon planning, wide context,
  open-ended synthesis. The escalation tier. Jev's job includes deciding what
  deserves one: screen first, send only the shortlist.
- **d. HUMAN (Gate-D).** Outward, paid, destructive, public, credential-changing,
  or content about a minor (Lane C, `never_auto`). No machine verdict authorizes
  these; a clean PASS is evidence, not permission.

**Step 3. Batch the calls.** Independent questions go in ONE request (they run in
parallel and cannot see each other's answers). One call can carry noul + score +
choice together. Prefer `noul` for anything binary: cheapest, and no mean to misread.

**Step 4. Consume in three bands.** act / proceed-with-caution / do-not-act, with
thresholds scaled to the stakes of the action, not fixed globally. Policy lives in
code: routes, budgets, locks, spend caps. Jev supplies typed answers only.

**Step 5. Close the session.** Label the decisions that were right
(`rig-s1gate label <id> good|bad`, this is the calibration corpus), run the
done-gate on the deliverable, and report decision-log ids as the evidence of every
"Jev judged X" claim.

## What good looks like / what bad looks like (summary)

Full matrix per situation: `references/decision-criteria.md`.

| Axis | Good | Bad |
|---|---|---|
| Routing | typed question names the work type, code applies the route | a frontier model deliberates routing in prose |
| Screening | one batched call over N items, code maps answers to actions | one LLM call per item in a bulk loop |
| Verification | per-claim verdict bound to cited evidence | "this looks right" narration |
| Ranking | score/choice per candidate, ordering computed in code | ranking paragraphs nobody can threshold |
| Extraction | typed fields out of prose via `choice`/`noul` | regex over a model's prose |
| Gate transition | rubric check consumed by a hook's exit code | a gate that annotates and nobody reads |
| Score reading | threshold only unimodal means, with a confidence floor | threshold a bimodal mean (it is noise) |
| Provider down | defer the item, retry next tick, escalate queue | silent local fallback verdict |
| Secrets | redact before state leaves the machine | raw dump to the classifier |
| Authority | PASS means "the measured bar was met" | PASS read as permission to send, spend, deploy |
| Embedding claim | a logged request carrying typed questions and a parsed answer coming back | a README promise that Jev is used |

## Expectations (measured, not vendor claims)

**Hosted JEV only, effective 2026-09-30.** Use
`https://api.typesafe.ai/v1/systemone` with `jev-latest`. Redact secrets through
`capabilities/hooks/redact_state.py` before sending state. That helper removes known secret
patterns; it does not sanitize health, financial, contact, family, or client details.
If private details remain, or safe redaction is unavailable, defer the item.
Provider failure also defers. Do not install, start, restart, or fall back to OpenJev or Laya.
The retired local experiments in `references/embedding.md` section 4 are historical evidence,
not operating instructions. Hosted verifier agreement with a hosted router is not an
independent calibration label.

- Round trip 202-910 ms from Denver on `jev-1.13.0`; a 3-primitive call measured 292 ms.
- Fraction of a cent per call. External measurements: 253 questions in one call for
  $0.0012 at 915 ms; 4 questions per alert at p50 418 ms, $0.04 per 1,000 alerts.
  Counter-evidence exists: for one-character answers with per-question repeated
  criteria, Jev measured 6.6-12.7x an LLM's token cost. Batch, and compare before
  assuming a cost win.
- Budgets: `TYPESAFE_DAILY_BUDGET_USD` (default 1.00) and `TYPESAFE_DAILY_MAX_CALLS`
  (default 300) from `~/.rig-secrets/typesafe.env`. Over budget degrades to shadow
  (log only), never to error and never to a guessed verdict.
- Uncalibrated rubrics are advisory: they annotate and cannot BLOCK. Only
  `rig-s1gate calibrate` on labelled decisions flips one to enforcing.

## Evidence standard for "Jev was used"

A claim binds to the decision-log row id in `~/.rig/s1gate/decisions.db` (state
hash, answers, verdict, latency) or, for a raw `ask()` call, the request/response
pair. Borrowing the outside world's adopter test from awesome-jev: look for a real
request carrying typed questions and a parsed answer coming back. A config entry, a
skill file, or a README sentence is not embedding.

## Surfaces

`references/embedding.md`: coding agents (instruction blocks, stage-gate hook,
skill-routing pattern), programs (the three call routes and the request-shape traps),
Aside (the browser lane situations and the data boundary).
`references/external-comparables.md`: how other people built the same thing, and the
adopter checklist worth stealing.

## Scope and sources

This extends the Jev System-1 Cascade Doctrine v1.0 (2026-09-20) with the session
layer: how an agent that has just learned its mission decides which of its own
decisions are Jev-shaped and routes them, plus criteria for good and bad use in each
situation. It does not restate doctrine. Read `s1gate` for the six laws and rubric
packs, `typesafe-jev` for request shapes, measured cost and the data boundary,
`jev-lane` for the tool map, `jev-system1-cascade` for building a new judgment
surface.
