---
name: great-hd-10-competitive-intel-yaml
lane: research-intel
exemplar_of: hD-10-competitive-intel.yaml
description: "Reference exemplar — public-only competitor snapshots that represent rivals at full strength, separate fact from inference, and produce sourced internal battlecards with refresh triggers."
---

# hD-10 competitive intel — workflow platforms

## Input

Compare three named workflow platforms for a live enterprise evaluation. Lock the competitor set before collection; use official docs and pricing pages for capabilities, permitted G2/Capterra exports for review themes, and public methods only.

## Output

`artifacts/compintel/workflow-2026-09/` contains the locked competitor set, per-domain robots/ToS posture, source-bearing feature cells, hashed live pricing snapshots, review themes with counts/date ranges, prior-run diff, two-sided positioning deltas, uncertainty tags, one five-section battlecard per competitor, and refresh schedule. Every battlecard frontmatter remains `distribution: internal`.

## Acceptance

```console
$ jq '[.. | .source_url? // empty] | length >= 20' artifacts/compintel/workflow-2026-09/feature_matrix.json
# expected: true
$ python3 scripts/compintel_diff.py --prev artifacts/compintel/prev/ --cur artifacts/compintel/workflow-2026-09/ --out diff.md
# expected: exit 0, or a documented first-run skip
$ python3 scripts/strawman_lint.py artifacts/compintel/workflow-2026-09/deltas.md
$ python3 scripts/battlecard_lint.py artifacts/compintel/workflow-2026-09/battlecards/
# expected: both exit 0
```

Each pricing value traces to a verified local snapshot; no review theme has fewer than five reviews. Weaknesses cite reviews or changelogs, not assumptions, and each comparison cites both competitor and internal evidence. External distribution has no approval record and therefore does not occur; `./bin/rig-capabilities goal-spec --stem hD-10-competitive-intel` returns verdict OK.