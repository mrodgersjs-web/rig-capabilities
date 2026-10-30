---
name: "gate-subject-required"
description: "Every quality-gate call must carry a non-empty subject that identifies the artifact judged (id plus hash). An empty subject makes calibration impossible forever. Use whenever calling a Jev/s1gate rubric, logging a decision, or adding any new gate. Trigger on: 'run the gate', 'score this', 'check the rubric', 'calibrate', 's1gate'."
when_to_use: "At every gate call, and before designing any new gate or rubric."
version: "1.0.0"
status: "active"
outcome: "agent-engineering: zero gate decisions with empty or self-referential subject; calibration becomes possible"
done_when:
  - "cmd:sqlite3 ~/.rig/s1gate/decisions.db \"select count(*) from decisions where trim(coalesce(subject,''))=''\""
quality_floor: "0.8"
---

# Gate subject required

**Rule: a gate decision that does not name what it judged cannot be calibrated, ever.**

## The check

Pass `--subject <artifact-id>:<sha256-prefix>` on every gate call. The subject must be:

- **non-empty**
- **the artifact**, not the rubric name (`code.diff` as the subject of a `code.diff` call is
  self-referential and worthless)
- **stable across re-runs** of the same artifact, so labels can join to it

```bash
SUBJECT="$(basename "$FILE"):$(shasum -a 256 "$FILE" | cut -c1-12)"
rig-s1gate check <rubric> --file "$FILE" --subject "$SUBJECT" --json
```

Reject, and do not log, any call whose subject is empty or equals the rubric name.

## Why this exists

Calibration for the Jev rubrics has been REFUSED for weeks on one ground: nothing to
inspect. The scale of it is larger than anyone assumed - **28,567 of 91,008 decisions** in
`~/.rig/s1gate/decisions.db` have no subject at all, and some callers pass the rubric name
as the subject.

The consequence is concrete: `advisory_until_calibrated` is true, so every verdict is
downgraded and no gate enforces anything. Your standing bar of ">0.9 everywhere" is
unreachable on some axes (`claims_match_diff` clears 0.9 in only 4 of 283 decisions) because
the gate has never been shown right or wrong on a labelled example.

Fifty labelled decisions - real outcomes, joined to real subjects - is what moves the first
rubric from advisory to enforcing. That is a 20-minute task that has been deferred for weeks
because the labels had nothing to attach to.

## Hard rules

- No subject, no decision record. Skip the call rather than log a blank.
- An empty result from the count check above means the DB path changed, not that the
  problem is solved. Run it against a known-non-empty query first.
