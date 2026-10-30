---
name: rig-top100-agent-self-improve
description: "Close the loop from failure to capability: mine run logs for weaknesses, turn a repeated one into a skill or a fix, gate the change with the same eval that could refute it, and keep only what measurably improved. Use when the same class of task fails repeatedly, when a fleet is re-learning what it already knows, or when an agent has been 'getting better' without any numbers moving."
tags: [rig, top100, agentic-systems, self-improvement, skill-acquisition, eval-gate]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 20
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-self-improve/SKILL.md
outcome: "A dated backlog of observed weaknesses, one change per weakness, and a merged change that beat the baseline on a frozen eval set by a margin that clears the noise gate; failures that did not improve stay visible."
activation: "Load on a schedule over recent runs, after any eval regression, when a fix has been applied twice to the same symptom, and before crediting an agent with improvement."
instruction: "Start from evidence, not ambition: cluster failures and friction from the trace and verdict logs, rank by cost times frequency, and pick one. Write the smallest change that could plausibly fix it, run the frozen eval set before and after, and require a Poisson-merge-cleared margin to adopt. Add the change as a skill or a rule with a done-test; never let the agent edit its own judge. Keep a rollback and record what did not work."
applies_when:
  env: "the repo holding skills and prompts, plus the trace and verdict logs to mine"
  deps: "frozen eval set, the eval runner, version control, the deviation engines"
  runtime: "an analysis pass by a model, deterministic scoring, and a human check on the chosen weakness"
  params: "lookback window, weakness clustering rule, adoption margin, candidate cap per cycle"
  budget: "one to three changes per cycle; more means the weaknesses are too small"
  scale: "a single agent's prompt to a fleet's shared skill set"
permissions:
  - fs.read
  - fs.write
  - bash
  - model.judge
flow:
  - Pull the last cycle's verdicts, rejects, retries, and redos from the trace store, not from impressions.
  - Cluster into weakness classes and rank by frequency times cost, with outward-error risk weighted up.
  - Pick one class; write the smallest change that could plausibly move it.
  - Run the frozen eval set on baseline and candidate, same version, same seeds where possible.
  - Require the improvement to clear the noise gate before adopting; inside the band is no change.
  - Ship the change as a skill or rule with a done-test, so the new capability is verifiable later.
  - Confirm the writer did not edit the judge, and that hard floors did not move.
  - Record the attempt either way, including the negative results, and keep the rollback path.
done_when:
  - "cmd:jq -e '.weaknesses | length >= 1 and (.[0].frequency > 0 and .[0].cost > 0)' ${RUN_DIR:-./out/rig-top100-agent-self-improve}/backlog.json"
  - "cmd:jq -e '(.baseline.score) as $b | (.candidate.score - $b) >= .min_delta' ${RUN_DIR:-./out/rig-top100-agent-self-improve}/comparison.json"
  - "cmd:jq -e '.eval_set_version_before == .eval_set_version_after' ${RUN_DIR:-./out/rig-top100-agent-self-improve}/comparison.json"
  - "cmd:jq -es -e 'all(.[]; .verdict != null)' ${RUN_DIR:-./out/rig-top100-agent-self-improve}/attempts.jsonl"
  - "grep:SKILL.md:noise gate"
out_of_scope:
  - an agent rewriting its own scoring rubric or gate to pass
  - 'vibes-based improvement' with no before-and-after numbers
  - adding capability while silently relaxing a hard floor
  - five changes at once, after which nothing is attributable
---

# Self-Improvement Loop

## Why this exists

An agent fleet that only executes accumulates the same mistakes. The loop that fixes this is
not "reflect and try harder"; it is evidence to weakness to minimal change to a gated
adoption. Without the gate, self-improvement drifts into self-grading, and every change looks
like progress while the numbers hold flat.

## Outcome contract

- Why: RIG must get 1000x better, not 10 percent better
- Baseline: Static capabilities
- Target: Automated weakness detection, practice loops, and skill upgrades with quality gates

## Method

### 1. Mine evidence, not ambition

Sources: failed eval verdicts, guardrail rejects, retries and redos, tasks needing a human
rescue, cost outliers, and questions the agent had to re-ask. Cluster them, then rank by
frequency times cost, weighted up for outward errors. Impressions of weakness are exactly how
an agent optimises the loudest complaint instead of the biggest leak.

### 2. One class, one minimal change

Pick the top class and write the smallest change that could plausibly move it: a rule, a skill,
a prompt section, a tool. A broad rewrite destroys attribution, so it is not allowed as a
first move. Two failed attempts on the same symptom means the diagnosis is wrong, not the fix.

### 3. Gate with the eval that could refute it

Same frozen eval set before and after, same version, same cases. The improvement must clear the
noise gate (Poisson upper-tail), or it is a measurement. Track subscores so a candidate that
gains on Specific and loses on Verifiable is visible as a trade, not hidden in an aggregate.

### 4. New capability, new skill, new test

Adopt by writing the capability down with a done-test, so a month later someone can check the
agent still has it. A behaviour change that lives only in a prompt rewrite is a capability
nobody can audit or move between agents.

### 5. The judge stays fixed

The agent may edit its skills; it may not edit the rubric, the eval set, or its own gate to
accommodate this run. Judge changes are a separate, human-approved commit. Hard floors do not
move in a self-improvement cycle, and if one appears to have moved, that is the finding.

## Failure modes

- Rubric creep, and eval-set overfitting to the agent's own outputs.
- Change stacking, so nothing is attributable and a regression hides behind a win.
- Improving a metric nobody uses while client-facing quality slides.
- Silent floor relaxation dressed up as a capability gain.
- Negative results discarded, so the same failed idea is retried next quarter.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-self-improve}
r=0
jq -e '.weaknesses | length >= 1' "$RUN_DIR/backlog.json" >/dev/null || { echo "BLOCK no evidence-based backlog"; r=1; }
jq -e '.eval_set_version_before == .eval_set_version_after' "$RUN_DIR/comparison.json" >/dev/null || { echo "BLOCK eval set changed mid-cycle"; r=1; }
jq -e '((.candidate.score - .baseline.score) >= .min_delta)' "$RUN_DIR/comparison.json" >/dev/null || echo "WARN improvement inside noise band: do not adopt"
jq -es -e 'all(.[]; .verdict != null)' "$RUN_DIR/attempts.jsonl" >/dev/null || { echo "BLOCK unrecorded attempt"; r=1; }
git -C "${REPO:-.}" diff --name-only HEAD~1 2>/dev/null | grep -q 'eval' && echo "WARN eval touched this cycle: needs separate human approval"
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Re-run the frozen eval three times on the adopted artifact and confirm the gain survives the
variance. Then check the next cycle's logs for the weakness class: if it recurs at the same
rate, the change did not bite and the class gets reopened rather than closed. Finally confirm
the judge's own files are unchanged in the adoption diff.

## Related

`rig-top100-agent-evaluation` (the gate), `rig-top100-poisson-merge` (is it real),
`rig-top100-agent-skills` (adopting as a skill), `rig-top100-agent-observability` (what gets
mined), `rig-top100-agent-memory` (what was learned and what failed).
