---
name: tg-quota-gates
description: >
  Sub-skill of tg-free-tier-engineering: the three quota-gate implementations from
  the TubeGuruji corpus — Arcjet token buckets as product quotas, DB counters,
  entitlement flags — plus placement (gate at creation), reset semantics, and the
  upgrade-toast UX.
tags: [rig, doctrine, quotas, arcjet, rate-limiting, tubeguruji]
metadata:
  source: "corpus — ciXiibK7Gds + b_4Z_QpEd2Q (Arcjet token bucket, 86400s refill), saoW6BaNamc (15 msgs/24h), sXRDL-EPtrM (1 itinerary/day), s28yOCBVgGw (3 forms DB counter), zcYM_Gqoph4 (credits<=0 gate placement), 6GKFEqB8LWo (upgrade toast), -h1O73T0jmo (self-resetting 2/day)"
  extracted: "2026-09-25"
  parent: tg-free-tier-engineering
outcome: "Every costly action gated by one explicit mechanism with known reset semantics and an upgrade path — enforced at creation time, verified by attempting the 1-over-limit action."
activation: "Load when implementing any free-tier limit, credits check, or abuse protection on a generation endpoint."
instruction: >
  Choose exactly one gate mechanism per action: edge rate limit when the limit is
  time-windowed, DB counter when it is lifetime/cumulative, entitlement flag when
  it unlocks a surface. Gate at creation, never at consumption. Prove the gate by
  exercising the deny path, not by reading the code.
applies_when:
  env: "Next.js API routes (Arcjet middleware-capable) or app DB"
  runtime: "serverless functions; Arcjet SDK or app database"
  deps: "Arcjet (optional — a DB counter needs nothing extra)"
  params: "limit number + reset window per action; one canonical enforcement point per action"
  budget: "minutes per gate; Arcjet free tier"
  scale: "single app; not a distributed rate-limiting system"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Classify the limit: time-windowed (per day/24h) → Arcjet bucket; cumulative (total forms/files) → DB counter; content tier (which chapters/specialists) → entitlement flag.
  - Time-windowed: configure the Arcjet token bucket with the window as the refill interval — 2/day = 86400s refill (ciXiibK7Gds, -h1O73T0jmo); the deny path returns "too many requests".
  - Cumulative: count the user's rows at creation time and compare (3 forms free, s28yOCBVgGw; 5 files, sxn2GPQjJgc).
  - Entitlement: boolean/plan field switches what renders (membership boolean → Enroll Now vs Buy Membership, _GyIjVgIwtk; paid-only chapters, rdaSPdCkoFQ).
  - Gate at CREATION: check `user.credits <= 0` (or the quota) when the user starts the action, not when they consume output (zcYM_Gqoph4 05:44 — and the creator names the enforcement-surface problem aloud: you must add the condition in every place that creates).
  - Wire the upgrade toast on deny (6GKFEqB8LWo "upgrade to add new file").
  - Verify by exercising the deny path: hit limit+1 and record the rejection.
done_when:
  - "grep:capabilities/skills/tg-quota-gates/SKILL.md:86400"
  - "grep:capabilities/skills/tg-quota-gates/SKILL.md:deny path"
  - "grep:data/corpora/how-to/manifest.jsonl:saoW6BaNamc"
out_of_scope:
  - distributed rate limiting, DDoS protection architecture
  - payment processing itself (Stripe/PayPal integration)
  - quota analytics dashboards
quality_floor: "A gate verified only by code reading is RED — the deny path must be exercised (limit+1 attempt) with the rejection observed."
---

# Quota Gates: three implementations, one rule

## The rule

Gate at creation. The recruiter build checks `user.credits > 0` when the
interviewer creates a session — and the creator says out loud that the check has
to be repeated "at many of the other places" that create, which is the honest name
for the enforcement-surface problem (zcYM_Gqoph4 05:44). Centralize the check in
one creation path per action.

## Implementation 1: Arcjet token bucket (time-windowed limits)

Bucket refill interval IS the quota window: refill 86400s = 2 per day
(ciXiibK7Gds, -h1O73T0jmo: "user can upload only two videos a day and it will
reset next day"). Observed limits: 15 messages/24h (saoW6BaNamc), 1 itinerary/day
(sXRDL-EPtrM). Deny path returns "too many requests" — map that to the upgrade
toast in the UI. Bonus corpus use: Arcjet also does prompt-injection detection on
AI endpoints, integrated by pasting Arcjet's own docs prompt into the coding agent
(-h1O73T0jmo — security integrated via prompt, not hand-coding).

## Implementation 2: DB counter (cumulative limits)

Count rows per user before allowing the next: 3 forms free (s28yOCBVgGw), 5 files
with upgrade prompt on the 6th (sxn2GPQjJgc), 50 MB storage with a live usage
readout (zlZ_7VTfxUs). Lifetime counters don't reset — say so in the UI, or users
read "3 free" as "3 per day".

## Implementation 3: entitlement flag (tiered surfaces)

A membership/plan boolean switches what renders: Enroll Now vs Buy Membership
(_GyIjVgIwtk), free vs paid chapters (rdaSPdCkoFQ), general physician vs
specialists (zjwj21wzs4U), paid-only hard difficulty (HlR15YZM7fg). This gate
sells access to a surface, not capacity — pair it with one of the other two when
capacity also matters.

## Credits are a fourth shape (debit-first)

Credits debit BEFORE generation with instant UI update (lJbIs8_5aqU: one credit =
one deck; bxhDP-e4NDA: one credit = one story), top up via Stripe/PayPal. Credits
are the monetization surface; the three gates above are the free-tier floor. The
corpus pattern debits and does not refund failures — decide your refund policy
deliberately, the corpus did not.

## Verification habit

The corpus demos gates by hitting them (upload #3 rejected, form #4 blocked).
Reproduce that: exercise the deny path and record the rejection message before
calling the gate done.
