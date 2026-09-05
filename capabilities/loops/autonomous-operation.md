---
outcome: agent-engineering:
done_when:
  - file:capabilities/loops/autonomous-operation.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/autonomous-operation.md
great_example: examples/great/agent-engineering/autonomous-operation.md.md
quality_floor: 0.6
---

# Autonomous Operation Harness — H_auto(D,G,B,E,H,I)

**Session type:** unattended multi-day operation holding standing send authority
**Created:** 2026-08-10 · **First governed run:** Ralph LinkedIn 5-day (2026-08-10 → 2026-08-15)

Distinct from `36h-gtm-sprint.md` (outcome gates, human driving) and `ops-harness.md`
(attended operations). This governs sessions where **no human is in the loop between gates**
and the system holds authority to affect real people. The failure modes are different:
a sprint that stalls is visible; a daemon that dies silently is not.

---

## 0. Identity Lock

**Startup phrase:** "Autonomous operation online. Grant verified. Kill switch armed."

**RIG coordinate:** L4-D2-A2-P (operation layer, execution diamond, deterministic-with-bounded-
agentic-edge, Produce step). Escalates to A3 only for content synthesis; A4 forbidden — an
unattended session may never take an irreversible action outside its declared grant.

**Harness tuple:** `H_auto(D, G, B, E, H, I)`
- **D** — Daemon: the heartbeat that proves liveness
- **G** — Grant: time-boxed, class-scoped, budget-capped authority
- **B** — Binding: per-batch content digest that the grant may never bypass
- **E** — Evidence: append-only telemetry, zero-baseline honest
- **H** — Healers: named, idempotent, no-op when their condition is absent
- **I** — Improvement: proposes diffs, never writes production

**Identity gates**

| | Requirement |
|---|---|
| 0.1 ❏ | Startup sequence run; harness loaded before any outbound capability is touched |
| 0.2 ❏ | Coordinate stated and BMS mode declared (A4 forbidden for unattended runs) |
| 0.3 ❏ | Harness tuple declared with all six components resolved to real paths |
| 0.4 ❏ | Governing grant located, parsed, and its expiry computed — never assumed |

---

## 1. Capability Gates

Each gate exists because this failure actually happened, here, in this system.

### Liveness

**Gate 1.1 ❏ Daemon proves it is ticking, not merely "started."**
Proof: ≥2 consecutive entries in the cycle ledger with timestamps matching the declared
cadence ±20%. A PID is not liveness.
*Origin: LinkedIn Studio Daemon showed "started" while dead since 2026-06-22, 11/11 runs
failed, 100% failure rate, nobody noticed for seven weeks.*
Tier: **halt**

**Gate 1.2 ❏ Daemon survives worker death.**
Proof: kill the process, observe supervisor restart, confirm the next tick lands and the
cycle counter continues rather than resets.
Tier: **halt**

### Authority

**Gate 2.1 ❏ Kill switch demonstrably halts, not just documented.**
Proof: remove the kill file, run a tick, observe HALT with reason; restore, observe OK.
Both directions required — a switch that stays halted after restore is broken the other way.
Tier: **stop**

**Gate 2.2 ❏ Grant expiry is computed from data, never hardcoded.**
Proof: backdate the grant expiry, observe DENY; restore, observe ALLOW. A grant whose renewal
requires a code edit will lock the operator out at the worst moment.
Tier: **stop**

**Gate 2.3 ❏ Standing grant supplies budget only — it never bypasses content binding.**
Proof: attempt an outbound with a valid grant but an unreviewed payload digest; observe refusal.
*Origin: 2026-07-03 — fabricated content reached real LinkedIn prospects. The audit is explicit
that this was unreviewed CONTENT, not a missing class permission.*
Tier: **stop**

### Content safety

**Gate 3.1 ❏ Placeholder and fabrication guards refuse even operator-approved payloads.**
Proof: approve a payload containing an unresolved template token; observe refusal despite approval.
Tier: **stop**

**Gate 3.2 ❏ Blocklist quarantines rather than filters.**
Proof: submit a payload containing a blocklist term; observe QUARANTINE and a written audit
record — not a silent drop, not a scrubbed send.
Tier: **stop**

### Resource integrity

**Gate 4.1 ❏ No provider-credit dependency in the unattended path.**
Proof: enumerate every scheduled job's provider; assert each resolves to a free local endpoint
or carries an explicit funded-and-verified note.
*Origin: HTTP 402 "requires more credits" silently killed 29 of 42 scheduled jobs.*
Tier: **halt**

**Gate 4.2 ❏ One scheduler of record per job class.**
Proof: enumerate all schedulers (cron, launchd, hub, engine-native) and show no job class is
driven by two of them.
*Origin: four overlapping scheduling systems ran LinkedIn automation simultaneously.*
Tier: **degrade**

**Gate 4.3 ❏ Dead-provider paths quarantine instead of retrying.**
Proof: a known-down provider produces at most one alert per day and zero retry attempts.
*Origin: Postiz workspace de-auth with 69 queued posts — a retry loop would have burned all 69.*
Tier: **halt**

### Truthfulness

**Gate 5.1 ❏ Baseline is measured, never assumed.**
Proof: read the actual telemetry ledger and state the real starting number, including zero.
*Origin: the engagement ledger records zero successful outbound actions all-time; any report
implying prior history is fabricated.*
Tier: **halt**

**Gate 5.2 ❏ Every claimed action resolves to a ledger row.**
Proof: reported counts equal ledger counts. A number in a report with no row behind it is a
fabrication, regardless of intent.
Tier: **stop**

### Learning

**Gate 6.1 ❏ Self-improvement proposes diffs; it never writes production.**
Proof: improvement output lands in a candidate directory; production prompt files show no
modification timestamp from the loop.
Tier: **stop**

**Gate 6.2 ❏ Healers are idempotent and no-op when their condition is absent.**
Proof: run every healer twice against a clean system; observe zero mutations both times.
Tier: **degrade**

---

## 2. Definition of Done

A governed autonomous run is complete when:

- [ ] All applicable gates passed with evidence recorded, or explicitly degraded with reason
- [ ] Primary objective achieved and expressed as a verifiable artifact, not a narrative
- [ ] Telemetry ledger reconciles: reported numbers equal ledger rows (Gate 5.2)
- [ ] Zero gate violations of `stop` tier across the whole window
- [ ] Grant expired or was revoked cleanly; no outbound capability outlived its authority
- [ ] One improvement entry written to `~/.hermes/jake/improvements.log`
- [ ] Identity closure: coordinate, verdict, and next safe action stated

---

## 3. Failure Protocol

| Tier | Gates | Behaviour |
|---|---|---|
| **stop** | 2.1, 2.2, 2.3, 3.1, 3.2, 5.2, 6.1 | Immediate full halt of all outbound. Requires operator approval to resume. These are the gates whose failure reaches real people or falsifies the record. |
| **halt** | 1.1, 1.2, 4.1, 4.3, 5.1 | Halt the affected branch, write a BlockerPacket, continue independent branches. Resume when evidence is produced. |
| **degrade** | 4.2, 6.2 | Continue with the degradation logged and surfaced in the next operator report. Never silently. |

**Error budget:** three consecutive failed cycles on any branch escalates that branch to `halt`
and emits a BlockerPacket. Independent branches keep running — a failure must not take the fleet.

**Escalation:** any `stop` tier failure pages the operator and writes to the alert directory. An
unattended session may not clear its own `stop`.

---

## 4. Self-Improvement Loop

**Log:** `~/.hermes/jake/improvements.log` — one entry per governed run.

Entry format: run id · window · gates passed/degraded/failed · one thing that broke ·
one thing that worked · the gate this suggests adding or removing.

**Pattern extraction:** every 5 entries, extract recurring failures and write a pattern note.

**Harness update trigger:** the same gate fails 3+ times across runs → the gate is wrong, not the
operator. Rewrite it. A gate that fires constantly is either miscalibrated or guarding the wrong
property; either way the harness is at fault and must change.

**Gate retirement:** a gate that has never fired in 10 runs is a candidate for removal. Gates earn
their place by catching real failures; a gate that catches nothing is bloat that trains people to
skim.

---

## 5. Final Rule

```
No gate evidence, no progress.
No ledger row, no claimed action.
The grant funds the budget; it never buys the content check.
An unattended session may never clear its own stop.
No improvement entry, no session complete.
Every autonomous operation session leaves the system stronger than it found it.
```

---

**Governs loops:** GL-OF (operating fleet), GL-SH (self-healing), GL-RI (runtime integrity),
GL-GG (governance gates), GL-CB (compounding builds).
**Coordinate space:** L4–L6 × D2 × A1–A3 × IQRSQPI(P, I2).
