---
name: sk-gate
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. The single gate before anything goes live on community surfaces: claim hygiene, Jev screen, the anti-slop pass, the lane check (minor/client/personal), and the Gate-D request for anything outward. USE WHEN a classroom item, lesson, post, About change or price language is about to go live. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, gate]
outcome: "content-publishing: nothing goes live on community surfaces without a dated gate record naming the claims checked, the Jev verdict or DEFERRED, and the Gate-D request id when one is due"
done_when:
  - grep:capabilities/skills/sk-gate/SKILL.md:content about a minor \(Jacob\) is STOP
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-gate
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "0"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-gate: the pre-publish gate for community surfaces

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: post gate verdict, is this claim supported, is this lane clean. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check post.viral --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `post.viral` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use before every live change to the classroom, About page, community posts, or price language. Not for drafting (any stage drafts freely).

## Procedure

1. **Claim hygiene**: every number, result and comparison gets a receipt or a label (projected / self-report UNVERIFIED). A claim with no receipt is cut.
2. **Lane check**: content about a minor (Jacob) is STOP - never published here; client-lane material (Ideawake/Coby) never inherits this community's voice; personal-brand mascots (Birch, Unit 7, The Coach) stay out.
3. **Jev screen** with `post.viral` (or `atomic.claim` for lessons); record the decision id. DEFERRED blocks the "judged" claim but not the draft.
4. **Anti-slop pass**: no banned words (unlock, empower, synergy, leverage, disrupt, hustle, utilize, iterate, optimize), no hype without mechanism, no fabricated urgency.
5. **Verdict**: SHIP (reversible, in-lane, claims clean) or HOLD-with-reason. Anything outward, priced, or naming a person gets a Gate-D request with the exact payload; only Mike's approval releases it.

## Hands the next stage

`gate-record.md` per item: the claims table (claim / receipt / label), lane verdict, Jev id or DEFERRED, verdict SHIP or HOLD, and the Gate-D request id when one is due.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-gate.md` (local corpus, not republished).

(no laws captured yet for this stage - see data/corpora/skool/BUILD-LOG.md for capture status)

## Where the creators disagree

(none recorded)

## Creator result claims (UNVERIFIED, never repeat as fact)

(none recorded)

## Platform mechanics (Skool's own behavior)

(none recorded)

## RIG application (RIG synthesis, not corpus claims)

The pre-publish gate is RIG doctrine (Gate-D, Jev-first, claim hygiene). Corpus support: creator result claims in this niche are consistently self-reported revenue numbers (see fXiFlwKvB3U creator claims), which is why the gate labels them UNVERIFIED.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/claim-hygiene.md` | the claims table for one item |

## Hard rules

- The gate never publishes; it clears or holds. Publishing is a separate action with its own Gate-D check when outward.
- A Jev DEFERRED is never reported as a pass.
- Minor-lane content is never cleared, under any wording.
- The gate record is dated and kept; a later correction references the original record id.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-gate/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-gate` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
