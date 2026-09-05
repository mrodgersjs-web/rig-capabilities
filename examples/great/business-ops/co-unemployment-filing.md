---
name: great-co-unemployment-filing
lane: business-ops
source: canonical-curated
exemplar_of: co-unemployment-filing
description: "Reference exemplar for a weekly Colorado certification flow that proves session identity, required work-search entries, submission confirmation, and bounded human escalation."
---

# Colorado weekly certification: successful governed run

## Input

At the Saturday 10pm MT cron window, use the authenticated Safari session for the owner. Confirm the page contains `RODGERS`, detect whether RESEA blocks the weekly form, read the hidden required-contact count, and fill exactly the required work-search activities. Escalate rather than guessing if MFA appears, the form structure changes, or RESEA Save does not advance.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/co-unemployment-filing.md
```

## Output

The contract validator exits cleanly. During an authorized filing run, `file_weekly_safari.py` follows login → navigate → fill → submit → confirm. JavaScript verification shows every radio state selected and `hdnWorkSearchContactCount` at least `hdnWrkSrchNoOfJobContReqNum`. A confirmation page supplies a `W-` number, which is written to `session/safari_session.json` and included in the delivery record. An already-filed week returns the existing confirmation instead of duplicating a claim.

## Acceptance

- The termination command exits 0.
- A successful run has one captured `W-` confirmation and updated session history.
- Expired login, stuck RESEA, changed form, or MFA produces an explicit manual-review alert and no fabricated confirmation.
- The Saturday schedule remains `0 22 * * 6 (America/Denver)`; human override is required for every A4 condition.
