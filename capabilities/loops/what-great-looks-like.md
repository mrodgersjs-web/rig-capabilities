# What Great Looks Like — 36H GTM Sprint Loop

**Mission:** `jake-36h-gtm-sprint-2026-07-05`
**Companion to:** `goal-harnesses/36h-gtm-sprint.md`

This is the **quality contract** the harness enforces. "Good" means the artifact moved the mission forward AND the proof was written AND the operator can verify it in under 30 seconds.

---

## THE LOOP (every cycle, every cron, every outcome)

```
1. READ state           → what was last done?
2. RUN work             → produce the artifact
3. WRITE proof          → hash + counters + upgrade-applied
4. CHECK WGLL           → did this meet the quality bar?
5. ADVANCE outcome      → increment counter, stage next
6. REPORT to Telegram   → 4-6 lines, human-readable
```

If step 3 fails → log + skip (don't advance, don't fail).
If step 4 fails → log + alert (depends on severity).
If step 6 fails → still advance, but log warning.

---

## GREAT vs GOOD vs BAD

### GREAT (ship-ready, signed off, in market)
- All WGLL checks pass
- Proof written with cycle number + upgrade applied + next-upgrade noted
- Operator can verify in 30 seconds
- Mike can arm with one keystroke
- Self-evident win (booked call, qualified reply, ready-to-send proposal)

### GOOD (shippable, ready to review, gated)
- Most WGLL checks pass (≥ 80%)
- Proof written but maybe light on detail
- Operator needs to dig to verify
- Mike can arm after reading
- Directionally correct, not yet perfect

### BAD (do not ship)
- Any WGLL check fails
- Proof missing or fabricated
- Blocklist hit
- Gate-D violation
- Voice off, numbers fabricated, sentiment generic
- Output that takes > 5 min to evaluate

---

## PER-OUTCOME GREAT CHECKLIST

### O1 — Pipeline Live
- **Great:** 200+ touches staged, all ICP-scored, all personalized, zero blocklist
- **Good:** 100-200 touches staged, mostly scored, mostly personalized
- **Bad:** < 100 touches, missing ICP scores, or any blocklist hit

### O2 — Calls Booked
- **Great:** 5+ calls on Tue/Thu calendar slots with Calendly links confirmed
- **Good:** 3-5 calls booked but on ad-hoc slots
- **Bad:** 0-2 calls, or calls without Calendly confirmation

### O3 — Contract #1 Signed
- **Great:** Contract signed, deposit received, Stripe confirmed
- **Good:** Verbal commit + contract drafted + Stripe link sent
- **Bad:** No movement on any deal OR new draft created but not sent

### O4 — Google Ads Live
- **Great:** Ads live, ≥1 click, ≥1 conversion tag fire
- **Good:** Ads dormant-built, conversion tag verified, arm bundle ready
- **Bad:** Ads not built OR arm bundle missing OR conversion tag broken

### O5 — Department PAI 5.0
- **Great:** All 8 Studios have atlas entry + 7-layer memory + GBrain query works + doctor PASS
- **Good:** ≥ 6 Studios upgraded, doctor PASS with warnings
- **Bad:** < 6 Studios OR doctor FAIL OR GBrain unreachable

### O6 — Fleet Evidence Atlas
- **Great:** 8 Studio rows, each with corpus + verifier gate + worker allowlist, file committed
- **Good:** 8 Studio rows, file written but not committed
- **Bad:** < 8 rows OR missing verifier gate OR missing worker allowlist

---

## CYCLE NUMBER → UPGRADE MAP

Each cron has a 18-cycle upgrade map (we run 9 cycles in 36h, so half of each map applies). Jake applies ONE upgrade per cycle from this map.

### Lead Engine (Cron #1)
| Cycle | Upgrade |
|---|---|
| 1 | Add firm-size + tech-stack enrichment fields |
| 2 | Add recent-funding signal |
| 3 | Add Apollo sequence templates (3-touch follow-up) |
| 4 | Improve ICP scoring weights (reply history feedback) |
| 5 | Add reply-classification rules |
| 6 | Add warm-intro graph analysis (find connectors) |
| 7 | Add regional CPA network sub-categories |
| 8 | Add DSO vertical sub-categories |
| 9 | Add Law vertical sub-categories |
| 10-18 | Reserved for adaptive upgrades based on reply data |

### Content Engine (Cron #2)
| Cycle | Deviation Engine |
|---|---|
| 1 | RIG-GRAVITON (escape generic AI gravity) |
| 2 | RIG-XRAY (fake understanding check) |
| 3 | RIG-VOLT (emotional voltage without manipulation) |
| 4 | RIG-LOOP (open loops reader must close) |
| 5 | RIG-WITNESS (source-per-claim) |
| 6 | RIG-WELLSPRING (reread payoff) |
| 7 | RIG-SURPRISE (update reader's model) |
| 8 | RIG-FORGE (burn adjectives, leave machinery) |
| 9 | RIG-VISCERA (embodied stakes, felt not described) |

### Reply Closer (Cron #3)
| Cycle | Upgrade |
|---|---|
| 1 | Improve reply classifier accuracy |
| 2 | Add price-objection handler |
| 3 | Add timing-objection handler |
| 4 | Add authority-objection handler |
| 5 | Add 10-Signature closer scoring |
| 6 | Add nurture content variants |
| 7 | Add warm-intro pathway (find connectors) |
| 8 | Add call-prep packet generator |
| 9 | Add post-call follow-up sequence |

### Ads Engine (Cron #4)
| Cycle | Angle |
|---|---|
| 1-3 | Pain-led ("Stop guessing your ICP") |
| 4-6 | Proof-led ("10 contracts in 90 days") |
| 7-9 | Founder-led ("Mike Rodgers built RIG to...") |
| 10-12 | ROI-led ("0.077% of revenue to recover $150K-$500K/yr") |
| 13-15 | Comparison ("Not another Clay clone") |
| 16-18 | Urgency ("Q3 is closing — book before July 31") |

### Pipeline Engine (Cron #5)
| Cycle | Upgrade |
|---|---|
| 1 | Deal scoring model v2 (signal density weight) |
| 2 | Auto-draft proposal templates per vertical |
| 3 | Add competitive displacement signals |
| 4 | Add warm-path scoring (referrals, intros) |
| 5 | Add win/loss capture prompts |
| 6 | Add forecast accuracy tracker |
| 7 | Add overdue-alert escalation |
| 8 | Add daily revenue report auto-format |
| 9 | Add interview-prep packet generator (Julie lane) |

---

## WHAT "FIX ALL ISSUES" MEANS

The harness has three classes of issues:

1. **Self-heal-able** (M1-M4 monitors) — fix automatically, log
   - Cron stall → restart
   - Provider drift → re-pin
   - Blocklist near-miss → quarantine
   - Missing proof → skip cycle

2. **Operator-fixable** (LOW/MEDIUM severity) — log + Telegram + wait for Mike
   - Provider credits exhausted
   - API key rotation needed
   - Stripe not connected
   - Resend key leaked (revoke needed)

3. **Mission-stopping** (HIGH/CRITICAL severity) — log + STOP + immediate alert
   - Unauthorized send (Gate-D violation)
   - Fabricated public claim
   - HED or IdeaWave touch
   - Paid spend without approval
   - Public exposure without Gate-D

Jake monitors 1-2 actively, escalates 3 to operator, halts on 3.

---

*Companion to: `goal-harnesses/36h-gtm-sprint.md`*