---
name: great-evaluator-forge-from-exemplars
lane: agent-engineering
source: canonical-curated
exemplar_of: evaluator-forge-from-exemplars
description: Reference exemplar — the forged rubric GREEN on a real exemplar outscored by 75 over its hollowed twin (and GREEN at a gap exactly at the declared margin), RED (exit 2) on each of the seven planted failures (unweighted dimension, weights summing to 105, unresolvable exemplar path, negative byte-identical to its twin, inverted ranking, unlocalized RED finding, twin-gap below the declared margin)
---

# evaluator-forge-from-exemplars — reference

Canonical asset `evaluator-forge-from-exemplars` (skill). Path:
`capabilities/skills/evaluator-forge-from-exemplars`.

> A rubric earns the right to score by ranking a real exemplar strictly above
> its degraded twin. Forge input: the curated `examples/great/**` file plus
> negatives with their load-bearing specifics and numbers removed. Derived
> output: `version`, `margin`, `dimensions` with weights summing to 100. The
> scoring total is RECOMPUTED by `validate_forge.py` from `met` flags — the
> forge never reports a number the checker cannot reproduce.

## What good looks like

The load-bearing pair — the real exemplar and a hollowed copy of it. The
copy keeps every heading and sentence skeleton; what it loses is the
specifics: JSON record blocks, fixture names, exit-code counts, source ids.

```json
{"kind":"artifact","path":"examples/great/agent-engineering/experience-lesson-records.md","role":"exemplar"}
{"kind":"artifact","path":"capabilities/skills/evaluator-forge-from-exemplars/fixtures/neg_hollowed_lesson_records.md","role":"negative","twin":"examples/great/agent-engineering/experience-lesson-records.md"}
```

The rubric v3 (weights 40/35/25, margin 20) and one localized RED finding —
a node and a check, never an adjective:

```json
{"kind":"finding","path":"capabilities/skills/evaluator-forge-from-exemplars/fixtures/neg_hollowed_lesson_records.md","dimension":"evidence_density","met":false,"finding":"L13-16, L21-25: all counts and ids removed ('several required fields', no fixture names, no arXiv/video id); check: grep -c -E '[0-9]' on the artifact returns near zero"}
```

Recomputed totals: real exemplar **100.00**, hollowed copy **25.00** — gap 75
≥ margin 20. `validate_forge.py rubric_valid.yaml scores_valid.jsonl` →
**exit 0**.

## The ten done-test forms

| rubric | scores | exit | why |
|--------|--------|------|-----|
| `rubric_valid.yaml` | `scores_valid.jsonl` | 0 | twin beats its degraded copy by 75 ≥ margin 20 |
| `rubric_margin_exact.yaml` | `scores_valid.jsonl` | 0 | margin 75, gap 75 — the boundary is GREEN, not a hole |
| `rubric_no_weight.yaml` | `scores_valid.jsonl` | 2 | an unweighted criterion moves no score |
| `rubric_weights_105.yaml` | `scores_valid.jsonl` | 2 | weights sum to 105, not 100 |
| `rubric_valid.yaml` | `scores_missing_path.jsonl` | 2 | a score for a file that does not exist is a score for nothing |
| `rubric_valid.yaml` | `scores_negative_identical.jsonl` | 2 | a "degraded" negative byte-identical to its twin is not degraded |
| `rubric_valid.yaml` | `scores_rank_inverted.jsonl` | 2 | the rubric scores the hollowed copy 100 and the real exemplar 25 — theater |
| `rubric_valid.yaml` | `scores_unlocalized_finding.jsonl` | 2 | a RED finding with no node and no check is an adjective |
| `rubric_margin_90.yaml` | `scores_valid.jsonl` | 2 | gap 75 < declared margin 90 |
| missing rubric file | — | 1 | refusal to judge, not a verdict |

The seven exit-2 fixtures are the regression suite: each is the failure the
forge gate exists to catch, kept so a future edit that stops the gate biting
turns a green red immediately.

## Why the forge was theater before

The RIG delta: `great_example:` pointed at prose an agent read, `quality_floor:
0.6` was a bare threshold with no scoring function, and `hC-04-design-critique`
required weights summing to 100 on a rubric that was selected, never derived
from annotated exemplars. Here the exemplar-plus-degraded-twin ranking is the
done-test itself — a rubric that cannot tell a real exemplar from a
hollowed-out one cannot promote anything.

Provenance: video `LEsKxMfRFjA`; arXiv:2608.13560 (AutoDesign); OSS
`Yaxin9Luo/AutoDesign`.
