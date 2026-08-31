---
outcome: agent-engineering:
done_when:
  - file:capabilities/loops/doer-checker-validator.md
  - the loop file parses and declares a termination test
great_example: examples/great/agent-engineering/doer-checker-validator.md.md
quality_floor: 0.6
---

# 3-Tier Quality Gate Architecture — DOER / CHECKER / VALIDATOR

**Owner:** Jake PAI
**Date:** 2026-07-05
**Status:** DESIGN — building 5+ cron jobs to enforce

After every build cycle, no artifact ships until **three independent agents** each inspect it. This is the **maker-never-grades doctrine** applied as a fleet, not a single verifier.

---

## THE THREE ROLES

### 🛠️ DOER — the builder
- Produces artifacts (code, scrapes, posts, proposals, designs)
- Runs on the build cron lane
- Writes proof of what it did (hashes, gates passed)
- **Does NOT grade itself**

### 🔍 CHECKER — the spec inspector
- Reads the Doer's proof
- Runs the **mechanical / syntactic** checks: did the file exist? does it parse? does it lint? does it import? does the schema match?
- Fast, deterministic, no LLM in the loop (or minimal LLM)
- Returns PASS/FAIL with concrete errors
- **Independent of the Doer** — runs in its own context window

### ⚖️ VALIDATOR — the semantic / business-judgment inspector
- Reads the Checker's PASS report + the Doer's proof
- Runs the **semantic** checks: does the code do what it claims? does the post match Mike's voice? does the GTM lead match ICP? does the price change violate guardrails?
- Slower, often LLM-backed
- Returns PASS/WEAK/FAIL/CRITICAL with citations
- **Independent of both Doer and Checker** — separate context, separate model if needed

---

## THE FIVE+ CRON JOBS (each enforces a different slice)

| Cron | Role | Cadence | What it inspects | Independent of |
|---|---|---|---|---|
| **1. Code Syntax Checker** | CHECKER | every 30m | All code in `~/.rig/departments/**/workers/` + `~/.rig/dept-meta-harness/` | Doer, Validator |
| **2. Doctype & Schema Validator** | CHECKER | every 60m | Every `pai.json` + `contract.yaml` matches the schema registry | Doer, Validator |
| **3. Business Rules Validator** | VALIDATOR | every 60m | Blocklist, tier, gate_d_required, fabrications across all dept outputs | Doer, Checker |
| **4. AntiGenericForce Scorer** | VALIDATOR | every 4h | All public-facing artifacts score ≥ 85 | Doer, Checker |
| **5. Drift Watchdog** | VALIDATOR | every 30m | Provider drift, model drift, schedule drift, output drift | Doer, Checker |
| **6. Substrate Integrity Checker** | CHECKER | every 4h | Each dept's 5GB target on track, scraper output byte count | Doer |
| **7. End-to-End Pipeline Validator** | VALIDATOR | every 6h | Full pipeline test: scrape → entity → pattern → L7 → verifier → dashboard | Doer, Checker |

That's **7 cron jobs** enforcing the doer / checker / validator separation — **exceeds your "at least 5" ask.**

---

## SEPARATION OF CONCERNS

```
DOER layer:    5 GTM crons + 8 scraper crons + 1 monitor (already running)
CHECKER layer: 3 new crons (syntax, schema, substrate)
VALIDATOR layer: 4 new crons (business rules, AntiGeneric, drift, e2e)
```

**No cron is both a builder and a grader.** Each is a separate context with separate model assignments:

| Cron | Model assignment |
|---|---|
| Doers (existing 14 crons) | minimax/MiniMax-M3 or fleet nodes |
| Checkers (3 new) | rig-128gb-local ornith:35b (fast, local, cheap) |
| Validators (4 new) | rig-256gb-lan rig-256gb-strategy (deeper reasoning) |

---

## DOER → CHECKER → VALIDATOR FLOW

```
Doer cron runs cycle:
  produces artifact (file, JSON, MD)
  writes proof to /Users/rig128gb/.rig/state/{dept}-proof.json

Checker cron runs (after Doer, 15-60m later):
  reads /Users/rig128gb/.rig/state/{dept}-proof.json
  runs mechanical checks on the artifact
  writes /Users/rig128gb/.rig/state/{dept}-checker-{cycle}.json
  returns PASS / FAIL with error list
  if FAIL → returns artifact to Doer with retry instructions

Validator cron runs (after Checker, 1-6h later):
  reads Checker PASS + Doer proof
  runs semantic checks (business rules, voice, ICP, etc)
  writes /Users/rig128gb/.rig/state/{dept}-validator-{cycle}.json
  returns PASS / WEAK / FAIL / CRITICAL
  if FAIL → escalates to Jake-direct + Mike (Telegram)
  if CRITICAL → STOP all depts that touch this artifact
```

---

## FAILURE HANDLING

| Verdict | Action |
|---|---|
| PASS | Log + continue |
| WEAK | Log + flag in next Doer cycle as known-issue to address |
| FAIL | Re-spawn Doer cycle, increment `retry_count` |
| FAIL × 3 in 24h | Escalate to Jake-direct + Mike Telegram |
| CRITICAL | STOP all depts that touched artifact + Telegram + require Mike APPROVE to resume |

---

## PROOF PACKET SHAPE

Each cycle produces one ProofPacket per layer:

```json
{
  "schema_version": "rig.proof.v1",
  "run_id": "<uuid>",
  "cycle": <int>,
  "artifact_path": "...",
  "artifact_hash": "sha256:...",
  "doer": {
    "cron_id": "...",
    "ran_at": "<iso>",
    "claimed_outputs": ["..."],
    "self_report": "..."
  },
  "checker": {
    "cron_id": "...",
    "ran_at": "<iso>",
    "mechanical_checks": [
      {"name": "file_exists", "pass": true},
      {"name": "imports_ok", "pass": true},
      {"name": "schema_valid", "pass": true},
      {"name": "blocklist_clean", "pass": true}
    ],
    "verdict": "PASS | FAIL",
    "errors": []
  },
  "validator": {
    "cron_id": "...",
    "ran_at": "<iso>",
    "semantic_checks": [
      {"name": "voice_match", "score": 0.92, "pass": true},
      {"name": "icp_fit",     "score": 0.85, "pass": true},
      {"name": "fabrication", "pass": true}
    ],
    "verdict": "PASS | WEAK | FAIL | CRITICAL",
    "citations": ["..."]
  },
  "verdict": "PASS | WEAK | FAIL | CRITICAL",
  "proof_hash": "sha256:..."
}
```

---

## SELF-HEALING MONITOR (existing, 15m cron)

The monitor cron watches all of this and self-heals:
- If Checker FAIL × 3 → auto-rebuild substrate, retry
- If Validator CRITICAL → halt dept + telegram Mike
- If any cron drifts off schedule → restart
- If proof file empty > 2h → skip cycle, log

---

## DELIVERABLE

7 new cron jobs (3 checkers + 4 validators) wired into the 36h sprint, each pinned to a different node + model so they can't accidentally use the same context as the Doer.

---

*Signed: Jake PAI, 2026-07-05*
*Companion to: 36h-gtm-sprint.md, what-great-looks-like.md*