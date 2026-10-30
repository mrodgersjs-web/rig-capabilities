---
name: rig-top100-agent-evaluation
description: "Score agent output automatically instead of eyeballing it: a fixed eval set, a Brier-calibrated confidence report, the five RIG properties (specific, mechanistic, non-obvious, verifiable, actionable), and deviation engines that flag drift from the last accepted run. Use before an agent ships, when quality is argued rather than measured, or when a model or prompt swap needs a regression verdict."
tags: [rig, top100, agentic-systems, evaluation, calibration, quality-gate]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 10
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-evaluation/SKILL.md
outcome: "A run scored against a versioned eval set with a numeric AntiGenericForce, a calibration curve, per-property subscores, and a PASS/ESCALATE/BLOCK verdict that no agent involved in the work wrote itself."
activation: "Load when an agent output is about to be trusted or shipped, after any model, prompt, or tool change, and whenever someone claims quality improved without numbers."
instruction: "Freeze an eval set with known-good and known-bad examples before scoring anything. Score each output on the five properties plus a confidence, aggregate to a 0-100 gate, and report Brier against outcomes the moment they are knowable. The judge is a different model or a different session from the writer. A PASS needs the gate, calibration within band, and no hard-rule violation; anything else is ESCALATE or BLOCK."
applies_when:
  env: "local eval runner; results stored as JSON or CSV rows with a run id"
  runtime: "LLM-as-judge plus deterministic checks; at least one non-writing judge"
  deps: "versioned eval set, the scoring rubric, a results table with timestamps"
  params: "eval set version, gate thresholds, calibration window, sample size"
  budget: "judge cost at or below 20 percent of the writer's cost"
  scale: "one output at a time, aggregated across a batch for trend"
permissions:
  - fs.read
  - fs.write
  - bash
  - model.judge
flow:
  - Write the eval set first: inputs plus a reference answer, plus adversarial and known-bad cases.
  - Define the rubric as numeric subscores with anchors, not adjectives.
  - Score the five properties and capture the judge's own confidence alongside each subscore.
  - Aggregate to a 0-100 gate with a stated threshold (RIG default 80) and hard rules that cannot be averaged away.
  - Compute Brier on every claim whose outcome is already known; report calibration, not accuracy alone.
  - Run deviation checks against the last accepted run; a large shift needs an explanation, not a shrug.
  - Record verdict, evidence paths, judge model, and eval-set version in the results row.
  - Sample-fail a batch and re-read by hand: the judge drifts too, and it drifts politely.
done_when:
  - "cmd:jq -e '.cases | length >= 10' ${RUN_DIR:-./out/rig-top100-agent-evaluation}/eval-set.json"
  - "cmd:jq -e '.score >= 80 and .verdict == \"PASS\"' ${RUN_DIR:-./out/rig-top100-agent-evaluation}/verdict.json"
  - "cmd:jq -e '.brier <= 0.25 and .n >= 20' ${RUN_DIR:-./out/rig-top100-agent-evaluation}/calibration.json"
  - "grep:SKILL.md:AntiGenericForce"
  - "grep:SKILL.md:judge"
out_of_scope:
  - the writing agent grading its own output
  - a single aggregate number with no per-property subscores
  - tuning the judge to rescue a specific failing run
  - publishing a verdict that its evidence files do not reproduce
---

# Agent Quality Evaluation

## Why this exists

"Looks good" does not scale past the person who wrote it, and an agent that writes and grades
its own work always finds it good. Evaluation only earns trust when the eval set predates the
run, the judge is not the author, and the score decomposes into parts a human can dispute.

## Outcome contract

- Why: Every agent output must pass AntiGenericForce at or above 80
- Baseline: Manual review
- Target: Automated Brier-calibrated eval with a 5-property filter and deviation engines

## Method

### 1. Eval set before run

Cases are versioned and frozen: representative inputs, a reference answer, adversarial edge
cases, and known-bad examples that must score low. A judge that cannot fail a known-bad case
is decoration. Add cases only in a new version, so scores stay comparable.

### 2. The five properties

| Property | What a passing score looks like |
| --- | --- |
| Specific | Names, numbers, paths, dates; nothing that would fit any company |
| Mechanistic | Explains how, with the causal step, not that it happens |
| Non-obvious | Would not be produced by asking a model the question cold |
| Verifiable | Points at evidence a reader could check |
| Actionable | The next move is executable by the named owner |

Each gets a 0-20 anchor-scored subscore. The sum is the AntiGenericForce. Hard rules sit
outside the average: a leaked secret or an invented citation blocks regardless of score.

### 3. Calibration, not just correctness

Every judgment carries a probability. Brier score is mean squared error against the outcome.
Accuracy alone hides an overconfident agent: 90 percent correct at 99 percent stated
confidence is worse than 80 percent at 80 percent. Report the reliability curve, and treat a
rising Brier as a regression even when the pass rate holds.

### 4. Deviation engines

Compare against the last accepted run on structure and behaviour: length, citation density,
tool-call pattern, refusal rate, subscore shape. Composite sigma (structural plus behavioural)
catches an output that scores fine and has changed character.

### 5. Verdicts

`PASS` at or above the gate with calibration in band and no hard violation. `ESCALATE` inside
the noise band, or only one judge above it, or a deviation flag without explanation. `BLOCK`
below the gate, or a hard-rule violation, or missing evidence. Only a failed
Poisson upper-tail merge lets an "improvement" be called real.

## Failure modes

- Author-as-judge, and the sibling case: the judge quietly retuned to pass this run.
- Eval-set overfitting: 100 percent pass, real quality flat for months.
- A strong aggregate hiding a zero on Verifiable.
- Confidence reported after the outcome is known.
- Judge and writer from the same model, same prompt, same failure blind spot.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-evaluation}
r=0
jq -e '.cases | length >= 10' "$RUN_DIR/eval-set.json" >/dev/null || { echo "BLOCK thin eval set"; r=1; }
jq -e '[.cases[] | select(.expected == "low")] | length >= 2' "$RUN_DIR/eval-set.json" >/dev/null || echo "WARN no known-bad cases"
jq -e '.score >= 80 and .verdict == "PASS"' "$RUN_DIR/verdict.json" >/dev/null || { echo "BLOCK gate"; r=1; }
jq -e '.subscores | keys | length >= 5' "$RUN_DIR/verdict.json" >/dev/null || { echo "BLOCK no subscores"; r=1; }
jq -e '.brier <= 0.25 and .n >= 20' "$RUN_DIR/calibration.json" >/dev/null || { echo "BLOCK calibration"; r=1; }
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Rescore a saved known-bad output and confirm it lands below the gate; rescore a known-good one
twice and confirm the variance sits inside the reported noise band. Then verify the verdict
JSON against the raw evidence files it cites. A verdict that cannot be reproduced from its own
artifacts is an opinion, and gets downgraded to ESCALATE.

## Related

`rig-top100-anti-generic-force` (the rubric itself), `rig-top100-brier-calibration`,
`rig-top100-poisson-merge` (is the change real), `rig-top100-composite-sigma` (did behaviour
shift), `rig-top100-agent-observability` (the trace behind the score).
