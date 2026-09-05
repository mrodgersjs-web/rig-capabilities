---
outcome: revenue-gtm:
done_when:
  - file:capabilities/loops/gtm-harness.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/gtm-harness.md
great_example: examples/great/revenue-gtm/gtm-harness.md.md
quality_floor: 0.6
---

# GTM Goal Harness — H_gtm(GL-GG)

Governs GL-GG (go-to-market/growth) loops.
This is a runtime gate loop. Each gate must produce evidence before the session
may advance to outreach, publishing, or spending. No gate evidence, no progress.

## 0. Identity Lock

The session starts as Jake RIG Agent executing a GTM task. Before any message
is drafted, campaign launched, or spend authorized, identity must be locked.

Gate 0.1 ❏ Session declared as GL-GG in first 3 lines.
Gate 0.2 ❏ RIG procedures loaded — `~/.hermes/jake/rig-operating-procedures.md`
   read or cited by line range.
Gate 0.3 ❏ Coordinate stated: `L{level}-D{diamond}-A{mode}-{step}`.
Gate 0.4 ❏ GTM objective stated as measurable outcome.
   Proof: "This session will produce: <X> <deliverable> targeting <Y> ICP,
   measured by <Z> KPI." Not "do some outreach" — a specific, measurable goal.

## 1. ICP Verification

### 1.1 Target Fit
Gate ICP.1 ❏ Every outreach target matches the Ideal Customer Profile.
   Proof: for each target, show ICP score. Minimum ICP score: 70/100.
   Scoring: industry match (+20), size match (+15), role match (+15),
   tech stack match (+10), trigger event (+15), geography match (+10),
   budget signal (+15).
Gate ICP.2 ❏ No duplicates, blocklist hits, or existing contacts targeted.
   Proof: cross-reference target list against:
   - Existing CRM contacts (Twenty CRM at localhost:3000)
   - Blocklist (`~/.rig/blocklist.txt` or equivalent)
   - Previous outreach in last 90 days
   Zero hits required.
Gate ICP.3 ❏ Target list has minimum density.
   Proof: at least 10 qualified targets per batch. If < 10, flag as
   "thin list" and widen ICP criteria explicitly before proceeding.

### 1.2 Personalization
Gate PR.1 ❏ Every message contains at least 2 personalization signals.
   Proof: each message references something specific to the target —
   recent company news, mutual connection, specific pain point from
   their role/industry, content they published, or trigger event.
   Generic {first_name} + {company_name} tokens don't count.
Gate PR.2 ❏ Personalization is verifiable.
   Proof: each personalization signal can be traced to a source —
   LinkedIn post, company blog, Crunchbase, news article. Not fabricated.

## 2. Message Quality

### 2.1 Anti-Generic Score
Gate MQ.1 ❏ Anti-generic score >= 85 for every outbound message.
   Proof: run through AntiGenericForce scorer or manual equivalent.
   Scoring: +15 per specific pain point, +10 per relevant data point,
   +10 per personalization signal, +10 per clear CTA, +10 per
   social proof element, +15 per "this is clearly about ME" factor,
   +15 per unique angle.
   -20 per generic opener ("I hope this finds you well"),
   -15 per generic value prop, -10 per template feel, -10 per
   unsubstantiated claim.
Gate MQ.2 ❏ Subject lines (email) or opening lines (DM) are specific.
   Proof: subject/opening line contains a specific reference to the
   target, not a generic hook. Test: strip the name — does the line
   still work for this specific person?
Gate MQ.3 ❏ CTA is clear and low-friction.
   Proof: every message has exactly one CTA. CTA is specific
   ("15-min call Tuesday or Thursday?" not "let me know if interested").
   CTA commitment level is appropriate for the touch number (touch 1 =
   low commitment, touch 3+ = higher).

### 2.2 Voice Consistency
Gate VC.1 ❏ Message matches the brand voice.
   Proof: message reads like it was written by a human who understands
   the recipient's world, not like an AI template. Voice check: would
   Mike send this? Would a thoughtful peer send this?
Gate VC.2 ❏ No AI-isms.
   Proof: zero instances of "I hope this email finds you well,"
   "leverage," "synergy," "circle back," "touch base," "per my last
   email," "I wanted to reach out," "just following up" (unless
   it's genuinely a follow-up), "game-changer," "revolutionize."

## 3. Channel Fit

### 3.1 Channel Selection
Gate CF.1 ❏ Channel matches the message type and audience.
   Proof: state why this channel (email, LinkedIn DM, LinkedIn comment,
   Twitter DM, phone, ad) is the right one for this message to this
   audience. Not "because it's what we have" — a real reason.
Gate CF.2 ❏ Channel cadence is appropriate.
   Proof: no more than 3 touches per channel per 30-day window.
   No more than 5 total touches across all channels per 30-day window.
   Touch spacing: minimum 3 days between touches to same person.

### 3.2 Timing
Gate TM.1 ❏ Outreach timing is appropriate.
   Proof: not sent on weekends (unless B2C and weekend is peak),
   not sent during known holidays, not sent at 2am local time of
   recipient. For email: Tuesday-Thursday, 8-10am or 1-3pm recipient
   timezone preferred.
Gate TM.2 ❏ No campaign fatigue signals.
   Proof: check open/reply rates of recent campaigns. If open rate
   < 15% or reply rate < 2%, pause and diagnose before sending more.

## 4. Gate-D for Outward Actions

Gate D.1 ❏ No message sent externally without typed APPROVE + run_id.
   Proof: every send (email, DM, comment, ad) requires explicit approval.
   Outbound messages are prepared as artifacts and gated before send.
   This is the hardest gate. Violation = immediate halt.
Gate D.2 ❏ No paid spend authorized without explicit approval.
   Proof: ad budgets, tool subscriptions, paid placements — all require
   Mike's approval with amount stated. "I'll spend up to $X" is not
   approval. "Approved: $X for Y" is.
Gate D.3 ❏ No public brand representation without approval.
   Proof: any content that represents RIG publicly (social posts, comments,
   reviews, forum replies) requires Gate-D approval. Drafts can be
   prepared; sends cannot happen.

## 5. Performance Tracking

### 5.1 KPI Definition
Gate KPI.1 ❏ Every campaign has defined KPIs before launch.
   Proof: "This campaign targets: X replies, Y meetings booked,
   Z pipeline generated, measured over N days." Not vanity metrics —
   leading indicators tied to revenue.
Gate KPI.2 ❏ Baseline established.
   Proof: current performance metrics documented before campaign starts.
   "Current reply rate: X%. Target: Y%." So improvement is measurable.

### 5.2 Attribution
Gate AT.1 ❏ Each touch is tagged for attribution.
   Proof: UTM parameters, unique reply addresses, or CRM tags that
   trace outcomes back to this specific campaign.
Gate AT.2 ❏ Results feed back into the system.
   Proof: after campaign completes, outcomes recorded in
   `~/.rig/departments/gtm/` or equivalent. What worked, what didn't,
   what to change next time.

## 6. Proof Requirements

Every GTM session produces a ProofPacket:

```json
{
  "schema_version": "rig.gtm.v1",
  "run_id": "<uuid>",
  "loop": "GL-GG",
  "objective": "...",
  "targets_count": 15,
  "avg_icp_score": 78,
  "avg_anti_generic": 87,
  "channel": "linkedin_dm | email | comment | ad",
  "touches_prepared": 15,
  "touches_sent": 0,
  "gates": {
    "identity_lock": {"pass": true, "evidence": "..."},
    "icp_verification": {"pass": true, "score": 78, "blocklist_hits": 0},
    "personalization": {"pass": true, "signals_per_message": 2.3},
    "anti_generic": {"pass": true, "score": 87},
    "message_quality": {"pass": true, "evidence": "..."},
    "channel_fit": {"pass": true, "evidence": "..."},
    "gate_d": {"pass": true, "evidence": "all sends gated"},
    "performance_tracking": {"pass": true, "kpis_defined": true}
  },
  "verdict": "PASS | FAIL",
  "proof_hash": "sha256:..."
}
```

## 7. Definition of Done

A GTM session is done when:
1. All applicable gates in §0–§5 passed.
2. Every message scored >= 85 anti-generic.
3. Every target verified against ICP and blocklist.
4. Gate-D enforced — zero sends without approval.
5. KPIs defined and baselines recorded.
6. ProofPacket written.
7. One improvement entry to `~/.hermes/jake/improvements.log`.
8. Identity closure: coordinate, verdict, touches prepared/sent,
   KPI targets, next safe action.

## 8. What Happens When a Gate Fails

| Gate | On Failure |
|------|-----------|
| 0.1–0.4 (Identity) | HALT. No outreach without locked scope and measurable goal. |
| ICP.1–ICP.3 (ICP) | Block. Remove non-ICP targets. Recount. No outreach to bad-fit. |
| PR.1–PR.2 (Personalization) | Block. Rewrite with real personalization signals. |
| MQ.1–MQ.3 (Message Quality) | Block. Rewrite until anti-generic >= 85. Generic = wasted touch. |
| VC.1–VC.2 (Voice) | Warn. Flag AI-isms. Fix before send but don't halt prep. |
| CF.1–CF.2 (Channel) | Block. Wrong channel = wrong audience = wasted effort. |
| TM.1–TM.2 (Timing) | Warn. Reschedule if needed but allow prep to continue. |
| D.1–D.3 (Gate-D) | HALT IMMEDIATELY. Unauthorized send = emergency. Assess damage. |
| KPI.1–KPI.2 (Performance) | Block. Define KPIs before campaign. No measurement = no learning. |
| AT.1–AT.2 (Attribution) | Warn. Add tags before send. Missing attribution = blind spots. |

## 9. Self-Improvement Loop

After each GTM session, append to `~/.hermes/jake/improvements.log`:

```text
[YYYY-MM-DD HH:MM] GTM session: GL-GG
  gates passed: <count>/<total>
  gates failed/skipped: <which>
  targets processed: <count>
  avg ICP score: <score>
  avg anti-generic: <score>
  channel: <channel>
  touches prepared: <count>
  touches sent: <count>
  capability gap: <what was missing>
  improvement: <what to add or change>
```

Every 5 entries: extract pattern. If anti-generic consistently < 90,
update message templates. If ICP scores drift, tighten ICP criteria.
If same gate fails 3+ times, update this harness.

## 10. Final Rule

```text
No ICP fit, no outreach.
No personalization, no send.
No Gate-D approval, no external action.
Every GTM session leaves the pipeline stronger than it found it.
```

---

*Companion to: hermes-conductor.md, doer-checker-validator.md*
*Governs: GL-GG (go-to-market/growth)*

## What Great Looks Like (WGLL)

Amazing GTM output from this harness:

- **ICP is specific** — named persona, named pain, named trigger event
- **Messaging passes the "so what" test** — every claim has a proof point
- **Sequences are multi-channel** — email + LinkedIn + ads, not just one touch
- **Metrics are leading indicators** — open rates, reply rates, meeting rates (not vanity)
- **A/B tests are pre-registered** — hypothesis, variant, success metric, sample size before launch
- **Pipeline stages are defined** — MQL → SQL → Opportunity → Closed with clear criteria
- **Anti-generic score ≥ 85** — no "synergize your workflow" language

