---
name: sk-ads
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Paid traffic for the community: when to spend, what to test, budget caps, and the honest read of whether ads worked. USE WHEN organic growth is proven and scaling is the goal, or when an ad test is being designed. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, ads]
outcome: "content-publishing: a capped, dated ad test with a pre-written success bar and an honest read of members-per-dollar against organic"
done_when:
  - grep:capabilities/skills/sk-ads/SKILL.md:Kill fast\*\*
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-ads
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "0"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-ads: paid acquisition and the spend discipline

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this ad worth spending on, did the test pass, is this audience honest. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check offer.eval --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `offer.eval` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use only after the promise converts organically (sk-growth shows a measured members-per-week rate). Not for organic channels (sk-growth).

## Procedure

1. **Precondition**: organic conversion exists on the current promise. Ads amplify a working message; they do not fix a weak one.
2. **Test design**: one audience, one message, one lead magnet, a written success bar (cost per member vs the band), and a hard spend cap ($300 total was Mike's stated test cap for RIG's first ad test; treat any other cap as needing his yes).
3. **Two-way honesty**: report cost per member, but also 30-day retention of paid-ad members versus organic; cheap members who leave are not growth.
4. **Kill fast**: a test that misses the bar at the cap is killed, not extended "one more week".
5. **Jev**: screen the audience and message with `offer.eval` before spend.

## Hands the next stage

`ad-test-record.md`: audience, message, magnet, success bar, cap, and the honest read (cost/member + retention). sk-measure holds the funnel numbers.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-ads.md` (local corpus, not republished).

(no laws captured yet for this stage - see data/corpora/skool/BUILD-LOG.md for capture status)

## Where the creators disagree

(none recorded)

## Creator result claims (UNVERIFIED, never repeat as fact)

(none recorded)

## Platform mechanics (Skool's own behavior)

(none recorded)

## RIG application (RIG synthesis, not corpus claims)

Paid acquisition is not covered in the captured corpus beyond the $50 validation ad (fXiFlwKvB3U@28:39). RIG procedure carries this stage; corpus laws pending capture from the remaining channel videos (Adam Luke, Ron Medlin, Stephen G. Pope cover paid scaling).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/ad-test-card.md` | designing one capped ad test |

## Hard rules

- Every dollar spent is Gate-D: the cap, the audience and the message appear in the request before spend.
- No exaggerated or unprovable ad claims; ads obey the same receipt rules as any public content.
- Never spend on a promise that has not converted organically.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-ads/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-ads` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
