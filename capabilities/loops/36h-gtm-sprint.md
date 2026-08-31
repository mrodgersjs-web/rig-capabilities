---
outcome: revenue-gtm:
done_when:
  - file:capabilities/loops/36h-gtm-sprint.md
  - the loop file parses and declares a termination test
great_example: examples/great/revenue-gtm/36h-gtm-sprint.md.md
quality_floor: 0.6
---

# 36H GTM Sprint Harness — H_36h(G)

**Mission:** `jake-36h-gtm-sprint-2026-07-05`
**Window:** 2026-07-05 16:00 CT → 2026-07-07 04:00 CT
**Owner:** Jake PAI (conductor)
**Operator:** Mike Rodgers
**Mode:** Phase A — I run, self-healing, no clarifying questions unless Gate-D

This harness is a **runtime gate loop**, not a reference. Each gate produces evidence before the sprint advances to its next outcome.

---

## 0. Identity Lock

Jake PAI online. Mission set. Coordinate declared. Every session that touches this sprint must:

- Gate 0.1 ❏ Load `jake-active-goal-2026-07-05.json` and confirm `status == "ACTIVE"`
- Gate 0.2 ❏ State the current outcome in progress (`O1` through `O6`)
- Gate 0.3 ❏ Coordinate: `L4-D1-A3-I1` (product/studio, physical diamond, agent-bounded mode, intent step)

---

## 1. Outcome Gates (the 6 outcomes)

Each outcome has its own micro-harness. The sprint advances only when each gate produces evidence.

### Gate O1 — Pipeline Live (DORMANT)
- ❏ Read `outbound/staged/{date}/*.json` and count `slug` files
- ❏ Each staged packet has `gate_d_approved: false` (Mike arms)
- ❏ Count ≥ 200 by sprint end
- ❏ Zero files in `outbound/staged/{date}/*` matching blocklist (`HED`, `IdeaWake`)
- **Proof:** `wc -l outbound/staged/2026-07-0{5,6,7}/*.json`

### Gate O2 — Calls Booked (DORMANT)
- ❏ Read `outbound/calls/{date}.json` and count call slots
- ❏ Each call has Tue/Thu 10-12 or 14-16 MT slot (Mike's free windows)
- ❏ Count ≥ 5 by sprint end
- **Proof:** `cat outbound/calls/2026-07-0{6,7,8}.json | jq '.calls | length'`

### Gate O3 — Contract #1 Signed (BLOCKED)
- ❏ Read `outbound/contracts/*.json` and confirm signed status
- ❏ Count ≥ 1 with `signed_at` timestamp
- **Proof:** `cat outbound/contracts/*.json`

### Gate O4 — Google Ads Live (DORMANT-BUILT)
- ❏ Read `out/ads/live-arm-bundle.json` — verify all required fields
- ❏ Verify dormant build: 4 ad groups, 20 keywords, 48 negatives
- ❏ Verify LP at `out/ads/lp/cpa/index.html` loads + conversion tag fires
- ❏ Verify `gate_d_approved: false` until Mike arms
- **Proof:** `out/ads/proof-packet.json`

### Gate O5 — Department PAI 5.0 (IN PROGRESS)
- ❏ Run `rig-department-pai doctor --format json` — must return PASS
- ❏ Verify all 8 Studios have evidence atlas entry
- ❏ Verify 7-layer memory wired in each agent's substrate
- ❏ Verify GBrain query path: `curl http://localhost:3131/health` returns 200
- **Proof:** `Department PAI/Fleet Evidence Atlas.md` exists + doctor output

### Gate O6 — Fleet Evidence Atlas Published (IN PROGRESS)
- ❏ `Department PAI/Fleet Evidence Atlas.md` exists with 8 Studio rows
- ❏ Each row has: corpus, verifier gate metric, worker allowlist
- ❏ Layer-0 evidence gate documented
- ❏ File signed + committed to git
- **Proof:** file hash + git log entry

---

## 2. Self-Healing Monitors

The harness runs three monitors that fire on detect-fail. They are NOT blocking — they patch and continue.

### Monitor M1 — Cron Health Watcher (every 15 min)
```
For each of 5 crons:
  if last_run_at > 90 min ago AND state == "scheduled":
    alert: "Cron {name} stalled"
    action: restart + write self-heal log
```

### Monitor M2 — Provider Drift Watcher (every 30 min)
```
For each of 5 crons:
  if cron.provider != "minimax" OR cron.model != "MiniMax-M3":
    alert: "Provider drift on {name}"
    action: re-pin via cronjob action=update
```

### Monitor M3 — Blocklist Watcher (every 30 min)
```
Scan outbound/staged/* for any file referencing:
  - "HED", "Anthony Langeweg", "hed-forge"
  - "IdeaWake"
If found:
  alert: "Blocklist violation in {file}"
  action: quarantine file + write incident log
```

### Monitor M4 — Proof-Writer Watcher (every 60 min)
```
For each of 5 crons:
  if proof_file doesn't exist or is empty:
    alert: "Cron {name} not writing proof"
    action: skip cycle, wait for next
```

---

## 3. What-Good-Looks-Like Loop (WGLL)

This is the **quality contract** for each cron cycle. A cycle is "good" only if it satisfies the WGLL for its stream.

### WGLL-A — Lead Engine (Cron #1)
- ✅ Scraped ≥ 50 leads
- ✅ ICP scored with `predicted_p_reply` field
- ✅ Staged packets in `outbound/staged/{date}/*.json`
- ✅ Zero blocklist prospects
- ✅ `gtm-engine-proof.json` updated with cycle number
- ✅ Upgrade applied (per WGLL-A cycle map)
- **Bad if:** any fabricated company, any missing ICP score, any blocklist hit

### WGLL-B — Content Engine (Cron #2)
- ✅ 3 LinkedIn posts drafted
- ✅ Each post has image (Higgsfield cinematic_studio_2_5 16:9 2K)
- ✅ AntiGenericForce ≥ 80 internal
- ✅ Voice matches Mike (specific numbers, no fabrication)
- ✅ 1 vertical playbook update
- ✅ `content-engine-proof.json` updated
- **Bad if:** text-only post, fabricated number, generic AI voice

### WGLL-C — Reply Closer (Cron #3)
- ✅ Inbox scanned for replies
- ✅ Each reply classified (interested/not_now/wrong_person/unsubscribe)
- ✅ Response drafted for `interested` replies
- ✅ Call slots proposed (Tue/Thu MT windows)
- ✅ Zero HED or IdeaWake replies processed
- ✅ `closer-proof.json` updated
- **Bad if:** auto-send (Gate-D violation), blocklist violation, missing classification

### WGLL-D — Ads Engine (Cron #4)
- ✅ Dormant build verified
- ✅ 1 new ad variant staged (6-angle rotation)
- ✅ Live-arm bundle ready, `gate_d_approved: false`
- ✅ Conversion tag fires on LP
- ✅ Zero HED or IdeaWake copy in variants
- ✅ `ads-proof.json` updated
- **Bad if:** live spend (Gate-D violation), fabricated proof, missing conversion tag

### WGLL-E — Pipeline Engine (Cron #5)
- ✅ 5 live deals scored
- ✅ Next-action packet staged per deal
- ✅ TransPerfect + Cadre AI interview prep packets ready (Julie lane)
- ✅ Daily revenue report written to `Documents/JakeStudio/Daily/{date}-revenue.md`
- ✅ Zero HED or IdeaWake drafts
- ✅ `pipeline-proof.json` updated
- **Bad if:** auto-send, fabricated deal data, missing overdue alerts

---

## 4. Failure Handling

When a gate fails, the harness does NOT halt. It:

1. **Writes the failure to** `/Users/rig128gb/.rig/state/36h-harness-failures.log`
2. **Skips that outcome** and continues to next
3. **Alerts via Telegram** if severity ≥ MEDIUM
4. **Self-heals** if pattern is recognized (provider drift, cron stall, missing proof)

Failure severity:
- **LOW:** missing optional field, slow proof write — log only
- **MEDIUM:** blocklist near-miss, missing cycle upgrade — log + Telegram alert
- **HIGH:** Gate-D violation, fabricated claim, unauthorized send — log + Telegram + immediate Jake escalation
- **CRITICAL:** HED/IdeaWake send, public exposure, paid spend without approval — log + Telegram + STOP all crons + alert Mike

---

## 5. Sprint Closeout

At 2026-07-07 04:00 CT:
1. Write `JULY-36H-HANDOFF-2026-07-07.md` with:
   - Outcomes achieved vs target
   - Cron cycles run + final proof packet hash
   - Calls booked, contracts signed
   - Department PAI 5.0 status
   - Blocklist incidents (if any)
   - What good looked like vs what shipped
2. Seal ProofPacket to `~/.rig/state/36h-goal-proof.json`
3. Telegram final report to Mike
4. Mark goal `status: CLOSED` in active-goal JSON

---

## 6. Operator Override

Mike can:
- `EXTEND` — extend window (default +12h)
- `PAUSE` — halt no kill (all crons skip next cycle, retain state)
- `STOP` — kill all + archive (goal marked STOPPED, no auto-resume)

---

*Signed: Jake PAI, 2026-07-05 16:00 CT*
*Mission: jake-36h-gtm-sprint-2026-07-05*