---
name: traject-reach
description: "Traject OS sub-skill, stage 5 (reach): HM/recruiter/warm outreach — draft T1-T6 notes, run outreach_lint and JEV outreach gates, and hold every send at Gate-D. NEVER sends. One ask, one nudge; ≤10 DMs/day; never the REPL linkedin global (may be signed in as Coby). DEFER when the classifier is down."
tags: [rig, traject-os, sub-skill, reach, outreach, linkedin]
metadata:
  parent: traject-os
  tier: sub
  stage: reach
  extends: "lv-outreach, lv-engage, aside-job-operator"
outcome: "A batch of outreach drafts (T1 live-role HM, T2 problem-led, T3 referral ask, T4 nudge, T5 warm+live, T6 warm evergreen) that pass outreach_lint and the JEV outreach gates, each held at Gate-D with one ask and at most one nudge — nothing sent without Mike."
activation: "Load when drafting HM/recruiter/warm outreach, seeding follow-ups from an application, or handling a reply."
instruction: "Draft to the Lucy T1-T6 templates, run outreach_lint (BLOCK on O-verified, O-cadence, O-resume, O-claim, O-length, W-recency, W-connected, W-desperate), gate with JEV outreach.first/intro and reply.intent, and hold every send at Gate-D. Assert the signed-in handle is Mike's before any LinkedIn action; never use the REPL linkedin global for Mike."
applies_when:
  env: "LinkedIn and Gmail surfaces; warm-network-log.jsonl and outreach-events.jsonl"
  runtime: "Aside browser; lucy-skills outreach_lint.mjs; JEV jobhunt.hm / jobhunt.warm"
  deps: "outreach_lint; rig-s1gate with outreach.first/outreach.intro/reply.intent/email.outreach"
  params: "recipient, template (T1-T6), role/company, matched reqs with verified numbers"
  budget: "≤10 DMs/day total, ≤10 invites/day & 60/week, spaced 3-10 min (20-10-5 adapted)"
  scale: "one note per recipient; batch drafts, single sends at Gate-D"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - browser.modify
  - gate-d-required:send
flow:
  - Pick the template (T1-T6) and gather verified matched reqs and one outcome.
  - Draft; run outreach_lint; gate with outreach.first/intro and reply.intent.
  - Hold every send at Gate-D; assert the signed-in handle first.
  - Log to outreach-events / warm-network-log; one ask, one nudge, then close the file.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/outreach.first.json"
  - "file:capabilities/harnesses/s1gate/rubrics/reply.intent.json"
out_of_scope:
  - sending any DM, InMail, connection request, or email (Gate-D)
  - using the REPL `linkedin` global for Mike (it may be the client Coby Skonord)
  - claims not in the claims ledger (100+ agents, $35M, $500K, IntOps 5-layer are BANNED)
---

# traject-reach

JEV FIRST: every draft goes to `rig-s1gate check outreach.first` / `outreach.intro` /
`reply.intent` / `email.outreach` BEFORE any frontier call. Classifier down: DEFER.
A required signal passes only above 0.9. A PASS is never permission to send.

Sub-skill of `traject-os`, stage 5. Main skills: `lv-outreach`, `lv-engage`, `aside-job-operator`.
Agent: `traject-outreach-drafter` (wraps outreach_lint + Jev, never sends). Sub-agents:
`traject-recency-checker` (60-day rule). Harness: `traject-outreach-session`.

## Procedure

1. **Pick the template**: T1 live-role HM note (≤5 sentences / 300 chars, "you're hiring
   [title]" never "I applied", 2-3 matched reqs with verified numbers, one outcome, one light
   question), T2 problem-led, T3 warm referral ask, T4 nudge (once after ≥5 business days, then
   go around), T5 warm + live role, T6 warm evergreen.
2. **Lint**: `~/.aside/u/0/skills/user/lucy-skills/scripts/outreach_lint.mjs`. BLOCK on
   O-verified, O-cadence, O-resume (no attachment on touch 1), O-claim (the banned set),
   O-length (>300 char note), W-recency (60-day LinkedIn+Gmail; UNKNOWN never eligible),
   W-connected, W-desperate.
3. **Gate**: `rig-s1gate check outreach.first ... --json` (or `outreach.intro`, `reply.intent`
   for replies). Rewrite-only on ESCALATE; DEFER holds the draft.
4. **Hold at Gate-D**: never send. Assert the signed-in handle is Mike's first; the REPL
   `linkedin` global may be signed in as the client **Coby Skonord** and is never used for
   Mike (TL-08). One ask, one nudge (TL-09), spaced 3-10 min, ≤10 DMs/day.
5. **Log**: outreach-events.jsonl / warm-network-log.jsonl. A draft is not SENT (TL-04).

## Lessons that fire here

- **TL-08** assert the signed-in handle; never the REPL linkedin global for Mike.
- **TL-09** one ask, one nudge, then close the file.
- **TL-04** a local draft is not sent; only a receipt makes it SENT.
