---
name: great-hc-04-design-critique-yaml
lane: design-ux
exemplar_of: hC-04-design-critique.yaml
description: "Reference exemplar — a frozen checkout-flow critique that separates reviewer lenses, attaches evidence, and turns every finding into an owned decision."
---

# hC-04 design critique — checkout recovery

## Input

Review `designs/checkout-v3.png` against a 60% usability / 25% accessibility / 15% brand rubric. Use first-time-buyer and accessibility-reviewer lenses. The artifact is immutable during critique; revisions go to `checkout-v4.png`.

## Output

`artifacts/critique/checkout-v3/` contains `FREEZE.txt`, `rubric.yaml`, `findings.md`, annotated captures under `shots/`, and `changelog.md`. The findings table records Nielsen heuristic, screen coordinate, severity, impact rationale, disposition, and owner. Blocker `CHK-04` maps the unannounced payment error to the revised error summary; the changelog schedules a keyboard and screen-reader re-check.

## Acceptance

```console
$ sha256sum designs/checkout-v3.png > artifacts/critique/checkout-v3/FREEZE.txt
$ grep -inE 'make it pop|feels off|more modern|cleaner' artifacts/critique/checkout-v3/findings.md
# expected: no output
$ ./bin/rig-capabilities goal-spec --stem hC-04-design-critique
# expected: verdict OK and the hC-04 gate set served from the canonical harness
```

The rubric weights sum to 100, every concern/fail cites a screen or flow step, each visual finding names an annotated screenshot, and every finding is accepted, revised, or deferred with an owner. `checkout-v4.png` has a different hash and `changelog.md` maps all blocker/major changes back to finding IDs.