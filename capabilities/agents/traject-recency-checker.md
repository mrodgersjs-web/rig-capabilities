---
name: traject-recency-checker
description: "SUB-AGENT: enforces the 60-day recency rule for outreach eligibility — checks LinkedIn + Gmail touch history for the recipient. UNKNOWN is never eligible. A recipient with a touch inside 60 days is held. Parent: traject-outreach-drafter."
allowed-tools: Bash Read Grep Glob
owner: rig-intelligence
domain: business-ops / outreach eligibility
status: Stable
verified_by: jake
verified_on: 2026-09-28
acl: internal
relates_to: traject-outreach-drafter, traject-reach, traject-os
outcome: "eligibility: a per-recipient recency verdict (eligible | held_recent | UNKNOWN-not-eligible) with the last-touch date"
done_when:
  - file:capabilities/agents/traject-recency-checker.md
  - grep:capabilities/agents/traject-recency-checker.md:60-day
quality_floor: 0.8
---

# traject-recency-checker

Parent: `traject-outreach-drafter`. Sub-skill: `traject-reach`. This backs the W-recency lint
rule. Harness: `traject-outreach-session`.

## Procedure

1. Check the recipient's last LinkedIn + Gmail touch (60-day window).
2. Verdict: eligible (no touch in 60 days), held_recent (a touch inside 60 days), or
   UNKNOWN — which is **never eligible** (W-recency: UNKNOWN never eligible).
3. Return the last-touch date so the drafter can pace (one ask, one nudge; 3-10 min spacing).

## Output shape

```json
{"recipient": "...", "recency": "eligible|held_recent|UNKNOWN", "last_touch": "YYYY-MM-DD|NONE"}
```
