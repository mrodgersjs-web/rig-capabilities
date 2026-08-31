---
outcome: business-ops:
done_when:
  - file:capabilities/loops/co-unemployment-filing.md
  - the loop file parses and declares a termination test
great_example: examples/great/business-ops/co-unemployment-filing.md.md
quality_floor: 0.6
---

# Goal Harness: Colorado Unemployment Weekly Filing

**Harness ID:** `co-unemployment-filing`
**Type:** Personal Life / Automation
**Schedule:** Saturday 10pm MT (weekly)
**Owner:** Mike Rodgers
**Cron Job:** `96ee485f1dde`

---

## Intent

File Colorado unemployment weekly certification automatically every Saturday evening, using Safari automation via osascript.

## Gates

| # | Gate | Pass Condition | Evidence |
|---|------|---------------|----------|
| G1 | Session Valid | Safari logged into MyUI+ (RODGERS visible) | Page text contains "RODGERS" |
| G2 | RESEA Complete | Not on RESEA enrollment pages | Page title ≠ "Career Information" / "Career Skills" / etc. |
| G3 | Form Filled | All radio buttons answered correctly | JS verification of checked states |
| G4 | Work Search Entered | Required number of work-search activities saved | `hdnWorkSearchContactCount` ≥ `hdnWrkSrchNoOfJobContReqNum` |
| G5 | Submitted | Confirmation page shown | Page contains `W-` confirmation number |
| G6 | Confirmation Captured | Confirmation number extracted and saved | Written to `safari_session.json` |

## Failure Modes

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Session expired | "RODGERS" not in page text | Alert: "Re-login to MyUI+ via Safari" |
| RESEA blocking | Page title matches RESEA pages | Fill RESEA pages via JS, alert if Save stuck |
| Already filed | "Submitted" in certification history | Report existing confirmation, exit 0 |
| Form structure changed | Expected elements not found | Alert with page text for manual review |
| Save button stuck | Page doesn't advance after Save | Alert: "Manual click needed in Safari" |

## BMS Mode

- **A3** (Agent Bounded) — Safari automation via osascript, JS injection, deterministic field mapping
- Escalates to **A4** (human override) when: RESEA Save stuck, form structure changed, MFA required

## IQRSQPI Trace

| Step | Implementation |
|------|---------------|
| **I1** Intent | File weekly unemployment certification |
| **Q1** Question | Is the Safari session valid? Is RESEA complete? What week are we filing? |
| **R** Research | Check page state via osascript JS, read hidden field counts |
| **S** Solution | `file_weekly_safari.py` — navigate, fill, submit |
| **Q2** Quality | Verify confirmation number extracted, session file updated |
| **P** Proof | Confirmation number in `safari_session.json` + Telegram delivery |
| **I2** Integrate | Cron fires Saturday 10pm, delivers via Telegram |

## Deviation Engines Applied

| Engine | Application |
|--------|------------|
| RIG-ANCHOR (15) | Every claim tied to confirmation number |
| RIG-LUMEN (37) | Causal chain: login → navigate → fill → submit → confirm |
| RIG-SHIELD (36) | Human stays decision-maker for RESEA completion |

## Files

| File | Purpose |
|------|---------|
| `scripts/file_weekly_safari.py` | Main cron script |
| `scripts/file_weekly.py` | Legacy CloakBrowser (broken) |
| `session/safari_session.json` | Session state + filing history |
| `session/claim_info.json` | Cached claim details |

## Cron Configuration

```yaml
job_id: 96ee485f1dde
name: Colorado Unemployment Weekly Filing (Saturday 10pm)
schedule: "0 22 * * 6"
deliver: telegram
enabled_toolsets: [terminal]
model: rig-96gb-daily:latest
provider: rig-96gb-lan
```

## Improvement Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-12 | Initial build | First filing completed manually |
| 2026-07-12 | Switched from CloakBrowser to Safari | ID.me reCAPTCHA blocks headless browsers |
| 2026-07-12 | Schedule changed from Sunday 6am to Saturday 10pm | Catch filing window earlier |
| 2026-07-12 | Added RESEA flow handling | System requires RESEA before weekly cert |
