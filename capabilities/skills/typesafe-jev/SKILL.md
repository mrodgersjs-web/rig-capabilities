---
name: typesafe-jev
description: "Call TypeSafe's Jev (System One) classifier from this machine: the request shapes that actually validate, the live cost and latency, where the gate layer already exists (capabilities_s1gate / rig-s1gate), and the data boundary that decides when a judgment may leave the machine. Use when a task needs a fast typed judgment - classify, rank, route, score, verify a claim - or when an ad-hoc question falls outside the stored rubric packs (28 as of 2026-09-18; call action=list for the live set)."
tags: [rig, jev, typesafe, system-one, classifier, gates]
metadata:
  verified: "2026-09-18, jev-1.13.0, live API from Denver; three primitives in one call, 292ms"
---

# Jev (TypeSafe System One) from this machine

## What it is, and the one thing it is not

A **classifier with a fixed answer set**. It returns calibrated probabilities and
generates **zero text**. It is a gate in front of expensive generation, not a
substitute for it.

**Jev cannot be a model lane in any agent.** It has no chat-completions surface, no
streaming, no tool calling. If asked to "use Jev as the model", route it as a
classifier and say why: `defaultModel` / `modelCategories` in any agent config take
a chat model, and a `POST /v1/systemone` body will not satisfy that contract.

## Three surfaces, in this order

| Need | Use | Cost |
|---|---|---|
| Judge an artifact against a standing RIG bar | MCP `capabilities_s1gate` (`action: check/rank/improve/list/show/stats/recent/review/label/calibrate/selftest`) | `check`/`rank`/`improve` spend a live call; the rest are free |
| Same thing from a shell, hook, or CI | `~/Developer/rig-capabilities/bin/rig-s1gate` — exit codes are the contract: **0 PASS · 1 BLOCK · 2 ESCALATE · 3 config error** | same |
| A question that is **not** in any stored rubric | raw `ask()` from `rig_capabilities.s1gate` | one call, a fraction of a cent |

Prefer the gate over raw calls: the rubrics carry the confidence floors and every
check writes a decision-log row. Go raw only for one-off questions, and say so in
the answer. In Aside the MCP tool is the native path; from any harness the same
handler is one tool call away. See the `s1gate` skill for the six laws and the
rubric packs.

## The request shape that validates (a plain string `criteria` on a noul is a 422)

```jsonc
{"model": "jev-latest",
 "state": "<all context the judgment needs, as one string or JSON>",
 "questions": {
   "is_cold_outreach": {"type": "noul",
                        "instructions": "Is this a first contact with no prior relationship?"},
   "personalisation":  {"type": "score",
                        "instructions": "How specifically does the opener reference the recipient as an individual",
                        "criteria": ["No reference at all", "Generic role reference",
                                     "Names their company or size", "Names an observed fact"]},
   "next_action":      {"type": "choice",
                        "instructions": "What should the sender do next",
                        "criteria": {"send_as_is": "Ready to send",
                                     "tighten_offer": "Offer is vague",
                                     "drop_ask": "Remove the meeting ask",
                                     "needs_prior_context": "Establish context first"}}
 }}
```

- **`noul` takes NO `criteria`** — instructions only. Sending a string criteria
  returns `422 model_attributes_type: Input should be a valid dictionary`. This is
  the single most common wrong-shape call; the vendor line "strings work for simple
  questions" does not apply to noul criteria on `jev-1.13.0`.
- **`score` criteria is an ORDERED LIST** (max 11 levels). **`choice` criteria is a
  DICT** of `id: meaning` (max 255 options).
- Batch independent questions in **one** call — they run in parallel and cannot see
  each other's answers.
- Auth: `Authorization: Bearer <TYPESAFE_API_KEY>`. On this machine the key lives in
  keychain item **`com.rig.env.TYPESAFE_API_KEY`** — read it into an env var inside a
  script, **never print it**. `s1gate._api_key()` already does this, and fails closed
  when the item is missing.

## Measured from Denver, 2026-09-18 (not vendor numbers)

| Measurement | Value |
|---|---|
| Round trip, one call carrying noul + score + choice | 292 ms |
| Range across real gate runs | 202–910 ms |
| Model id answering | `jev-1.13.0` |
| Cost per check | fraction of a cent |

## Reading the answer without lying with it

- **A Score mean can be pure noise.** A live probe returned `score 1.39` with
  `confidence 0.0` on a distribution split `{0: 0.46, 1: 0.11, 2: 0.01, 3: 0.42}` —
  mass at **opposite ends**. Threshold the mean only when the distribution is
  unimodal; bimodal means the question measures two things, so split it.
- **`noul` has no `confidence` field at all.** Missing is not zero. `noul ≈ 0.5`
  means yes and no are equally likely, not "medium intensity".
- **`confidence` summarises distribution concentration** — never permission to act.
- Vendor speed/cost claims are the vendor's own evals. Probe before repeating them.

## Data boundary (a live tension, not a solved problem)

Jev is **hosted**. A `check` sends the artifact to `api.typesafe.ai`. Under
local-first policy that means:

- **Never** send credentials, tokens, client source you don't own, health or
  financial detail, or anything private about Jacob (Lane C). The `nil.jacob` rubric
  scores *content about* him that is already public-facing; it does not authorise
  sending private material, and it is `never_auto` regardless.
- Anything you would not paste into a third-party form does not go into `state`.
- If a judgment is worth making on data that must stay local, the pattern is
  reproducible offline — say that rather than quietly shipping the state out.

## Wiring check (call this before believing "the gate is down")

`capabilities_s1gate` with `{"action": "selftest"}` proves the rule engine and the
fail-closed path with **zero API spend**. `{"action": "list"}` returns every pack
(28 on 2026-09-18, across lanes A/B/C, build, gtm, instagram and a new `job`
lane) and which are `ENFORCING` — as of that date **all are advisory**, so a PASS anywhere
annotates and stops nothing. Every decision lands in
`~/.rig/s1gate/decisions.db`; that file, not a commit message, is the evidence a gate
ran.

## Vendor material

`references/typesafe-vendor-SKILL.md` is TypeSafe's own agent skill, MIT, copied
verbatim (fetched 2026-09-18 from `github.com/typesafe-ai/skills`, main). Keep it
verbatim — to update, replace the whole file. For patterns beyond this page, read
the live index at `https://docs.typesafe.ai/llms.txt`; docs serve Markdown by
appending `.md` to any page path.
