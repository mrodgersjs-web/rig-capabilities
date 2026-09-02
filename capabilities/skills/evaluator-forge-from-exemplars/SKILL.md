---
name: evaluator-forge-from-exemplars
description: >-
  Use when a harness needs a scorer for an asset it already calls "great".
  Feed the curated exemplar plus N degraded negatives (copies with their
  load-bearing specifics and numbers removed) and derive a versioned rubric:
  named dimensions with weights summing to 100 and a declared twin-gap margin.
  A scoring record is only trusted if the rubric ranks the real exemplar
  strictly above its degraded twin by at least the margin — a rubric that
  cannot tell a real exemplar from a hollowed-out one is self-scoring theater.
  Every RED finding must be localized to a named artifact node and the check
  that goes RED, never an adjective. validate_forge.py enforces every
  clause: exit 2 on an unweighted dimension, weights not summing to 100, an
  unresolvable exemplar path, a non-degraded negative, an unlocalized RED
  finding, or a failed ranking.
allowed-tools: Bash Read Write
owner: rig-intelligence
domain: Agent evaluation / rubric derivation
status: Draft
outcome: >-
  agent-engineering: a forged rubric earns its promotion decision by ranking a
  real exemplar above its degraded twin, so `quality_floor` becomes a scoring
  function that can go red, not a bare threshold
done_when:
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_valid.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_valid.jsonl; test $? -eq 0
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_margin_exact.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_valid.jsonl; test $? -eq 0
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_no_weight.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_valid.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_weights_105.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_valid.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_valid.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_missing_path.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_valid.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_negative_identical.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_valid.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_rank_inverted.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_valid.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_unlocalized_finding.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py capabilities/skills/evaluator-forge-from-exemplars/fixtures/rubric_margin_90.yaml capabilities/skills/evaluator-forge-from-exemplars/fixtures/scores_valid.jsonl; rc=$?; test $rc -eq 2
  - file:capabilities/skills/evaluator-forge-from-exemplars/validate_forge.py
great_example: examples/great/agent-engineering/evaluator-forge-from-exemplars.md
quality_floor: 0.6
---

# evaluator-forge-from-exemplars

THE LAW: **a rubric earns the right to score by ranking a real exemplar above
its degraded twin.** The forge input is not an opinion of what "great" means —
it is the asset's curated exemplar (`examples/great/<lane>/<id>.md`) plus N
degraded negatives built from it. If the derived dimensions cannot tell the
real file from the hollowed-out copy, the rubric scores adjectives, not
specifics, and the forge is theater.

The source names the loop: a meta-harness optimizes its own design by scoring
candidates against derived criteria, and the scorer's output is the reward the
outer loop acts on (arXiv:2608.13560 AutoDesign; video `LEsKxMfRFjA`; OSS
`Yaxin9Luo/AutoDesign`).

The RIG delta this closes: RIG owns all three inputs and none of the
derivation. `great_example:` points at prose an agent reads; `quality_floor:
0.6` is a bare threshold with no scoring function behind it;
`hC-04-design-critique` gate 1.2 *requires* weights summing to 100 but the
rubric is selected, never derived from annotated exemplars, and gate 2.4 bans
vague phrasing in copy without forcing a finding to name its patch target.

## The rubric: versioned, weighted, margin-declared

`rubric` (strict YAML subset): `version`, `margin`, and `dimensions` where each
dimension has a `name` and a numeric `weight`; weights MUST sum to 100. A
dimension with no weight moves no score and is exit 2; an unversioned rubric is
exit 2 because a promotion decision must cite a version plus hash, not a vibe.

## The scoring record: recomputed, never trusted

`scores.jsonl`: `artifact` rows (role `exemplar` or `negative`; each negative
names its `twin`), then one `finding` row per artifact × dimension with `met`.
The checker RECOMPUTES every total from the weights — the forge never reports
a number the checker cannot derive. Three structural laws, each exit 2:

- every artifact path MUST resolve — a score for a file that does not exist is
  a score for nothing;
- a negative MUST differ from its twin — "degraded" that is byte-identical is
  not degraded, and a forge trained on identical pairs learns nothing;
- a RED finding MUST be localized — name the artifact node and the check that
  goes RED (`L13-16: all counts removed; grep -c -E '[0-9]' returns ~0`).

## The load-bearing test: twin-gap

For every negative: `total(twin) − total(negative) >= margin`. Equality with
the twin, an inverted ranking, or a gap below the declared margin is exit 2 —
this is the difference between a rubric that measures the asset and a rubric
that measures itself. The margin is declared in the rubric (here 20 of 100),
tested at the exact boundary (GREEN at gap == margin) and past it
(`rubric_margin_90.yaml`: a gap of 75 under a margin of 90 is exit 2).

Re-forge whenever the exemplar set changes; the version+hash is what
promotion cites. Risk: the scorer inherits the corpus's blind spots — pair
every declared dimension with the adversarial-verification loop (plant a
defect, prove the rubric goes red on it).

## Done-tests

Nine `done_when` forms: two GREEN (valid forge; gap exactly at the declared
margin) and seven RED at exit 2 — unweighted dimension, weights summing to
105, unresolvable exemplar path, negative identical to its twin, inverted
ranking, unlocalized RED finding, and a twin-gap below the declared margin.
Each RED fixture is a permanent regression case.

## Provenance

Source video `LEsKxMfRFjA`; paper arXiv:2608.13560 (*AutoDesign:
Meta-Harness Optimization for Long-Horizon Agentic Design*); implementation
`Yaxin9Luo/AutoDesign`. No creator text is reproduced; the mechanism is
re-derived as an enforceable rubric contract.
