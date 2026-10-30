---
name: ss-gate
description: >-
  The single pre-publish gate for Substack issues and Notes: claim hygiene, Jev, the Communications OS score, anti-slop, lane check and the Gate-D request. USE WHEN a draft or Note is about to be shown to Mike as ready, before any schedule or send. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, gate]
outcome: "content-publishing: one verdict per artifact (READY, FIX or DEFERRED) with evidence, and a Gate-D request for anything public"
done_when:
  - grep:capabilities/skills/ss-gate/SKILL.md:Anything about Jacob stops here
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-gate
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "0"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-gate: the pre-publish gate

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: does the artifact pass, which lane is it, is every claim sourced. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check substack.issue --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `substack.issue` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use on every issue and every Note batch before Mike sees it as ready. Not a publishing step: a PASS never sends anything.

## Procedure

1. **Lane check**: RIG publication (rigoperator) only. Anything about Jacob stops here (Lane C: per-post approval, never scheduled). Lane A cast never appears.
2. **Claim sweep**: list every number and named result. Each needs a source line. Creator-corpus numbers are never presented as facts. Cross-check against the other posts on the publication for contradictions (the 134 vs 100+ agents case).
3. **Engine score**: `python3 -m rig_comms score --surface substack --artifact <draft>` must exit 0.
4. **Anti-slop**: run the `anti-slop` skill lint; fix AI tells.
5. **Jev**: `rig-s1gate check substack.issue --file <artifact> --subject "substack <slug> sha256:<hash>" --json`. Record the decision id. DEFERRED if the classifier is down.
6. **Package check**: title, subtitle, cover image, one next step, no em dashes.
7. **Verdict**: READY (all green), FIX (named items), or DEFERRED (Jev down). Then a Gate-D request naming the publication, audience and exact text.

## Hands the next stage

`gate-<slug>.md` with the verdict, the Jev decision id, the rig_comms exit code and the Gate-D request. ss-publish sends only after Mike's yes.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-gate.md` (local corpus, not republished).



## Where the creators disagree

(none recorded)

## Creator result claims (UNVERIFIED, never repeat as fact)

(none recorded)

## Platform mechanics (Substack's own channel)

(none recorded)

## RIG application (RIG synthesis, not corpus claims)

(RIG synthesis.) The gate exists because the 2026-09-28 audit found 9 published posts, 2 with no image, several with unresolved claims (134 vs 100+ agents; an 88%/78% title contradiction; an unlabeled salon case study) and one about a minor. Every one of those would have been caught here.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/claim-sweep.md` | finding and resolving unsourced or contradictory claims |
| `references/gate-d-request.md` | writing the approval request for a public action |

## Hard rules

- A PASS is advisory. Nothing ships without Mike's explicit yes for that item.
- DEFERRED is never upgraded to READY by a frontier model's opinion.
- A contradiction with an already-published post blocks until Mike picks the true figure.
- Content about a minor never passes this gate for automation; it goes to Mike as a draft only.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-gate/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-gate` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
