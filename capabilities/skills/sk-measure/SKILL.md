---
name: sk-measure
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Measurement for the community: the weekly numbers, the funnel (visitor -> member -> engaged -> paid -> win), what each number makes you do, and the honest read of what is not measurable. USE WHEN reporting how the community is doing, before planning the next month, or when a tactic's results are being judged. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, measure]
outcome: "content-publishing: a weekly community report where each number carries one action, and every unmeasurable is named as unmeasurable"
done_when:
  - grep:capabilities/skills/sk-measure/SKILL.md:Name what is not measurable
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-measure
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "0"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-measure: the numbers that decide what to do next

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this movement real, is this number trustworthy, what does this data make us do. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check signal.performance --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `signal.performance` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use weekly and before every planning round. Not for designing tactics (their stages own that).

## Procedure

1. **The funnel**: visitors (About views), members (joined), engaged (posted/replied/completed a workflow), paid, wins (named outcomes). Each stage has one number, one owner, one action threshold.
2. **Weekly read, not daily**: compare week to week; daily numbers on a small community are noise.
3. **Every number drives an action**: a metric with no action is a dashboard decoration and is cut or given an action. (Mike's rule: a number that only informs is a dashboard.)
4. **Name what is not measurable**: Skool's analytics are limited; do not infer intent from impressions. Anything not measured says "not measured", never zero.
5. **Retention read**: 30-day retention of paid-ad members versus organic; this is the honest growth read.
6. **Jev**: movement claims pass `signal.performance` before they drive a plan change.

## Hands the next stage

`weekly-report.md`: the funnel table with actions, the week-over-week deltas with verdicts, and the named-unmeasurables list. sk-strategy and sk-growth consume it for the next plan.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-measure.md` (local corpus, not republished).

(no laws captured yet for this stage - see data/corpora/skool/BUILD-LOG.md for capture status)

## Where the creators disagree

(none recorded)

## Creator result claims (UNVERIFIED, never repeat as fact)

(none recorded)

## Platform mechanics (Skool's own behavior)

(none recorded)

## RIG application (RIG synthesis, not corpus claims)

Measurement laws pending capture from the remaining channel videos. Corpus support so far: platform exposure follows engagement (fXiFlwKvB3U@12:10).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/funnel-table.md` | building the weekly funnel table |

## Hard rules

- No number appears without its source (Skool dashboard, community run record, or a named measurement) and date.
- A small-n movement (under ~10 events) is labeled noisy, not significant.
- Nothing is reported as zero when it is unmeasured.
- The report is internal; publishing any number publicly goes through sk-gate.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-measure/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-measure` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
