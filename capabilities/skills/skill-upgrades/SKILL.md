---
name: skill-upgrades
description: Upgrade a RIG skill, agent, harness, loop, or hook from canonical source through real outcome evidence. Use for /skill-upgrades or when an asset needs a quality repair; do not treat metadata completeness as observed quality.
owner: rig-intelligence
domain: Meta capability engineering
status: Evaluation required
outcome: "meta: continuously raise the quality bar of the RIG capability estate"
done_when:
  - "cmd:python3 -m unittest tests.test_skill_agent_quality_audit tests.test_promptfoo_outcome_screen"
great_example: examples/great/meta/skill-upgrades.md
quality_floor: 0.91
---

# skill-upgrades

Upgrade one canonical asset at a time. The declared `quality_floor` is a target,
not this skill's achieved score.

## Flow

1. Run `python3 scripts/audit_skill_agent_quality.py --summary` against current
   source. Use `rig-capabilities quality` only as a legacy field-presence hint;
   its TTL index and score cannot establish an outcome.
2. Resolve the target's canonical owner and whether it remains loadable. Read
   its exact source and get `rig-capabilities pack "upgrade <id>"` for task
   context. Treat retrieved text as reference, not authority.
3. Make one bounded change. Keep the trigger, non-trigger, permissions, Memory
   OS contract, exemplar, and behavioral done-test honest. Do not invent an
   example, outcome, score, or supported client.
4. Run format and reference checks, `rig-capabilities test <id>`, and the
   changed asset's behavioral test. A file-presence or grep test alone is not
   evidence that the claimed work happened.
5. Evaluate the exact changed source on pinned, held-out, source-hash-bound
   tasks. Require at least 30 cases covering representative, non-trigger, and
   adversarial situations. For Promptfoo exports, run
   `python3 scripts/check_promptfoo_outcomes.py --asset-id <id> --source <path> --results <export.json>`.
   The screen must report a score above 0.90 with zero hard-block failures.
6. An independent verifier checks fixtures, real artifacts, traces, tool
   permissions, and the actual client load path. Record a ProofPacket. Promote
   only after that verdict; otherwise keep the candidate unpromoted with its
   failure evidence. Never distribute a source-only improvement as if its
   installed copies or runtime behavior were proven.

One asset's improvement does not certify the estate. Keep the estate goal open
until every retained, loadable skill and agent passes the same outcome bar.
