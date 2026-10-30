# Skill and agent quality standard

Status: target standard, not an estate-wide certification. Assessed 2026-09-24.

## The bar

Every **canonical skill and agent**, including a meta- or sub-asset, must pass
two independent axes before promotion:

1. **Specification readiness:** valid loadable format; clear trigger and
   non-trigger; owner, scope, intended outcome, inputs, outputs, tools and
   permissions; a real exemplar; a behavioral done-test that can go red;
   Memory OS read/write policy; source and version identity. For skills,
   validate the Agent Skills frontmatter and progressive-disclosure layout.
   For agents, bind the RIG substrate, telos, quality profile, work ledger,
   memory policy and proof path.
2. **Observed outcome:** more than **0.90** on a pinned, held-out task set for
   that asset, with at least 30 representative cases, including failures,
   non-triggers, and adversarial/permission-boundary cases. A case counts only
   when a deterministic assertion or independent verifier checks the actual
   artifact and trace. Record per-case results, source/config hashes, model,
   tool route, latency/cost, and a reproducible command. Any hard-block
   violation, unrun case, missing trace, or stale source hash blocks promotion.
   Report denominators and failure slices; never average away a safety failure.

`quality_floor` is a declared requirement, **not** an achieved score. Set the
target to at least 0.91, but do not raise a field value to manufacture success.
Jev confidence or `noul` is a classifier output, **not** the asset's outcome
score. Promptfoo assertion scores are useful only if the fixtures and expected
results are independently checked. The RIG profile
`agent_outcome_evaluation_v0` defines agent-specific dimensions and hard
blocks; this >0.90 promotion bar is stricter than its 88/100 “good” bar and
below its 94/100 “excellent” bar.

## Verification stack

- **Code:** parse metadata, validate references, assert hashes/permissions,
  run behavior tests, and count held-out pass/fail results. Code owns the
  promotion decision.
- **Jev:** fast typed triage for ambiguous triggers, vacuous done-tests,
  evidence/claim mismatch, and escalation. Use redacted task state. Store a
  decision ID, rubric/model hash and calibration status. An uncalibrated or
  stale rubric can flag a problem but cannot certify a pass. Failure to reach
  Jev means defer the semantic item.
- **Promptfoo:** compare prompt/agent versions on the same pinned fixtures;
  assert outputs and tool trajectories; track attack blocks, benign false
  positives, indeterminate runs, latency and cost. Keep development fixtures
  separate from held-out fixtures. No live sends, publish, spend or destructive
  actions in tests. Export JSON and run `scripts/check_promptfoo_outcomes.py`
  against the exact asset source. Each case must have unique
  `testCase.metadata.case_id`, `kind` (`representative`, `non_trigger`, or
  `adversarial`), `asset_id`, and `source_sha256`; all three kinds must appear.
  This is a measurement screen, not an independent verifier or promotion gate.
- **Independent verifier:** inspect source-bound artifacts and negative tests,
  then issue a ProofPacket. The builder cannot certify its own change.

The [Agent Skills specification](https://agentskills.io/specification) defines
required `SKILL.md` frontmatter, names, descriptions and progressive
disclosure. Its standard frontmatter permits `name`, `description`,
`license`, `allowed-tools`, and `metadata`; much of this repository's RIG
quality contract currently lives in additional top-level keys. The current
Codex skill validator rejects those keys. Moving them into `metadata` is a
separate compatibility migration: the catalog, quality checks, done-test
runner and cell validator presently read top-level fields. A YAML parse pass
does not equal an Agent Skills conformance pass.

[OpenAI's agent-evaluation guidance](https://developers.openai.com/api/docs/guides/agent-evals)
calls for trace grading to diagnose tool/handoff failures and datasets for
repeatable evaluations. [Promptfoo assertions](https://www.promptfoo.dev/docs/configuration/expected-outputs/)
support deterministic and custom checks; its [guardrail guide](https://www.promptfoo.dev/docs/guides/testing-guardrails/)
calls out attack-block, false-positive, indeterminate, latency and cost
metrics. These sources inform the checks; none establishes a universal 0.90
threshold. That threshold is Mike's RIG promotion requirement.

[Anthropic's agent-evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
supports combining graders rather than trusting one signal, while its
[skills guidance](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
starts with representative-task evaluation before authoring a skill.
[OWASP's excessive-agency guidance](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
motivates explicit functionality, permission and autonomy limits as hard
blocks, not weighted style points.

## Current gap

At the initial 2026-09-24 snapshot, `bin/rig-capabilities quality --weakest 5` reported **200** canonical
skills averaging **38.5/100** and **22** agents averaging **87.5/100** on its
older *field-presence* measure. Only 47 skills and 14 agents are field-complete
there. Its TTL index misses one new agent directory. Presence is not outcome
proof; its `file:` done-test can pass without the claimed behavior. The
read-only, source-scanning `python3 scripts/audit_skill_agent_quality.py
--summary` applies the stricter *RIG field-presence* screen to **201 skills and
23 agents and one nested subskill** and currently finds **20/225 spec-ready on that limited screen**,
**96/201 skills with only permitted top-level Agent Skills keys**, and
**0/225 outcome-verified**. `spec_ready` does not yet assert full Agent
Skills conformance, runtime loading, valid tool grants, or observed behavior.
224 of 225 declare a floor below 0.91 or lack a valid one; 177 lack an existing
exemplar; 146 lack a behavioral `cmd:` or `mcp:` done-test. Two assets lack
valid frontmatter. The count is the top-level canonical repository
inventory, not the much larger installed cross-harness estate. Run the same audit
with `--summary --gate` for an expected nonzero exit until promotion evidence
exists. This is a backlog,
not evidence that every asset is bad. The current script intentionally refuses
to synthesize outcome scores from file metadata. This update also repaired
20 invalid skill YAML frontmatters; the current scan includes 201 top-level
skills and still reports one name/directory mismatch and two frontmatter
failures. The strict
Agent Skills validator still rejects RIG-specific keys, so no universal
loader-compatibility claim follows from that repair.

Jev decision `56196` flagged a file-existence-only quality claim as likely
vacuous (`noul=0.93`), but the `ultra.proof` rubric returned **advisory
ESCALATE**, not enforced BLOCK, because its calibration was stale. Recalibrate
on labeled train/holdout examples before using it as an enforcement gate.
The rubric's old labels graded whole decisions, although its three questions
ask about different defects. That can mislabel a sound done-test as vacuous
merely because the claim or evidence is bad. Jev calibration now requires
`rig-s1gate label <decision-id> good|bad --signal question.attr` for each
multi-question rule; legacy whole-decision certificates on those rubrics are
advisory. MCP-agent labels are excluded from calibration until separately
reviewed. The 2026-09-24 live dry run of `done_test_is_vacuous.noul` has **zero
eligible signal labels**, so `ultra.proof` is still not an enforcement gate.
Do not relabel the historical 63 whole-decision cases wholesale: inspect and
label each question independently, then require a passing holdout and an
independent reviewer before writing a certificate.
The 2026-09-24 offline mission-router Promptfoo run passed 4/4 routing cases,
but the new asset-outcome screen correctly **blocks** it: four cases are below
the 30-case minimum, and those fixtures lack the asset/source binding and
negative-case labels. Routing success is not completion quality.

The configured install-root inventory is larger than the canonical source
catalog. `python3 scripts/audit_installed_skill_agent_estate.py --summary`
observed **5,734 top-level skill/agent entries across 12 roots**, resolving to
**4,804 physical source files** and **3,774 distinct file hashes**. The
remaining entries include 530 physical aliases and 1,560 byte-duplicate
entries; byte identity alone does not prove that whole agent/skill packages
are interchangeable. These are file-presence counts, not runtime
load or quality scores. It found 557 byte-exact canonical installs, 172
same-name byte-drifted installs, 4,605 noncanonical installed entries, and 400
broken symlinks. Broken links split into 238 Claude agent links, 153 Hermes
skill links, 6 Aside skill links, and 3 Prime Agent skill links. The 793
canonical absence cells are asset-by-root comparisons, not a statement that
every asset should load in every runtime. Another 114 top-level entries do not
fit the current top-level skill/agent file scanner and need classification.
One nested `rig-communications-core/references/SKILL.md` is reported
separately in the installed inventory and is now counted as an unverified
subskill in the source-quality audit. Its ownership and load intent remain
unresolved. Same-ID agents in
another file format are marked `FORMAT_VARIANT_UNVERIFIED` and block the
narrow install-integrity gate. That gate does not certify noncanonical assets,
absence cells, unscanned entries, runtime behavior, or outcomes.
The canonical `when-building-or-fixing-agents` pack was then installed with
recoverable backups into all seven configured skill roots and independently
compared file-for-file. The repaired `caveman` and `jev-system1-cascade` packs
were distributed only to their existing configured roots and checked for byte
equality and valid YAML. The current counts are **572 exact-byte installs**
and **157 drifted installs**; broken links and noncanonical counts are
unchanged. This confirms distribution only, not a client load or outcome pass. Do not
overwrite other drifted copies or delete broken links from these counts alone.
Eighteen canonical YouTube skill examples had truncated `cat $G/tran` lines.
Their full transcript filenames were restored from older installed copies,
but the referenced corpus root currently lacks a top-level `transcripts/`
directory. The examples remain unverified and these packs were not distributed.
Jev decision `56438` escalated the estate-wide completion claim as advisory;
stale rubric calibration prevents it from certifying a pass.
An `omp read skill://...` check then returned the current
`when-building-or-fixing-agents`, `jev-everywhere`, `jev-system1-cascade`, and
`skill-upgrades` bodies. This proves the OMP skill read path for those four
names at check time. It does not prove an OMP agent selected or obeyed them.
Resolve ownership, intended load surface, and retained-versus-retired status
first. Every *retained and loadable* physical asset then needs its own source-
bound outcome evidence and client-path load check before promotion.

The central `skill-upgrades` instructions now require source-bound held-out
outcomes and independent verification rather than a field-presence score or
the target's `done_when` alone. Its declared floor is 0.91, not an achieved
score. All seven configured copies match canonical bytes, and OMP can read the
new body. `rig-capabilities test skill-upgrades` passed its infrastructure
regression command after reindexing; this is not a behavioral outcome score.
The strict Agent Skills validator still rejects this pack's RIG-specific
top-level quality fields. Its current OMP read proves only that OMP accepts
this installed copy, not portable specification compliance.
The done-test runner now rejects cached entries when the indexed source hash
differs from the current source. A planted test observed green before source
change, red after change, and green again only after reindexing. The runner
also refuses executable checks from noncanonical indexed
assets or entries lacking a source hash/path, requires an affirmative typed
MCP receipt without contradictory failure flags, restricts `file:`/`grep:`
checks to resolved paths inside the repo root, and treats any skipped
criterion as a failed asset. The `/skill-upgrades` command now points to the
canonical skill workflow and is byte-identical in five configured command
roots; OMP shares the Claude command root. A targeted 12-test runner suite
passes. The wider `tests.test_catalog` suite was red (123 tests, one failure)
because its `done_tests` gate found existing failing assets, including
`rig-build-standard`, `rig-design-harness`, and `rig-deviation-engines`.
That result is a residual, not a reason to loosen the gate. The source estate
grew during this continuation. The 2026-09-24 16:15 UTC audit snapshot counts
**219 top-level skills, 23 agents, and one nested subskill (243 total)**:
20 are spec-ready on the limited screen, 242 lack a valid declared floor of
at least 0.91, and **0/243 are outcome-verified or promotable**. It records
190 missing real exemplars and 158 missing behavioral done-tests. The audit now treats
malformed or overlong exemplar paths as a gap instead of crashing. The
same fail-closed behavior applies to unreadable agent source text. The
same-snapshot installed inventory had 919 asset-by-root absence cells; its 400 broken links
and 157 canonical byte drifts remain. Independent broken-link triage found zero of the 400
links has a matching canonical source. Do not retarget them by name. Forty-two
have live same-ID noncanonical candidates; those require owner and outcome
review before any repair. Jev decision `56525` was advisory ESCALATE on a
narrative proof claim, not certification.
The Jev calibration repair now requires signal-scoped labels for multi-signal
rubrics and binds the signal value, model, and provenance in the evidence hash.
`ultra.proof` has zero eligible signal labels, so it remains advisory. Label
provenance is still self-asserted by local callers: `labelled_by="human"` is
not an authenticated human-review receipt. No Jev calibration may be described
as verified human ground truth until that boundary is implemented and tested.
The source audit now recognizes `owner`, `domain`, and `outcome` when a skill
puts those string fields in specification-compatible `metadata`, and includes
the permitted `compatibility` field in its portable-key screen. This removes
false field-absence findings without claiming a behavioral test passed. The
2026-09-24 recheck still has 20 specification-ready assets and zero
outcome-verified assets. The Jev rubric identity map now includes
`job.opsmd.fit`, `mission.completion`, and `mission.route`; its 49-test group
passes. That validates the map and Jev code, not rubric calibration or agent
outcomes.
The mission router's Promptfoo set has expanded from four to 30 development
cases plus a separate 30-case holdout. Tuning exposed a false-green condition:
the composer could label a packet `candidate` with no child skill. That status
now fails closed, and clear child matches are drawn from the selected
meta-skill's routing table. Tightening the development assertions to check
the selected agent, meta-skill, and child where the intent makes them clear
reduced the current development result to 23/30. Seven routes remain wrong
or unresolved. The earlier holdout passed 26/30 on a different
source version and cannot certify this one. Neither run measured completed
coding work, so the canonical skill and agent outcome count remains zero.
The later strict development run `eval-dOh-2026-09-24T17:00:06` reached
24/30 (80.00%) after three general routing corrections. Six routes still
fail; the earlier holdout is not current-version evidence. A subsequent
canonical audit counted 225 skills, 23 agents, and one subskill (249 assets):
20 spec-ready, zero outcome-verified, zero promotable, and 248 without a
valid declared quality floor of at least 0.91. The changing denominator is
an estate inventory change, not a quality gain.
The latest 2026-09-24 hierarchy reconciliation gives all 230 canonical skills
an explicit planned owner across 16 meta-skills. The proposed schema-v2 graph
has 2,378 unique physical nodes, 2,362 edges, a three-level maximum, zero
orphans, and zero multiple owners. It records 26 physical aliases and 25
shadowed top-level assignments instead of double-counting them. This is only
structural source coverage: `repair_skill_hierarchy.py --audit` still exits
RED because 19 generated routing/manifest files differ from the source graph.
The generator no longer proposes rewriting authored meta-skill instructions,
but applying all 19 generated files would touch concurrently modified routing
tables and has not been done. Current quality audit: 254 assets, 20 spec-ready, zero
outcome-verified and zero promotable. Do not use graph coverage as a proxy for
loaded routes, exercised behavior, or the above-0.90 outcome standard.

## Weekly improvement loop

Inventory canonical changes; ingest only source-attributed official/practitioner
guidance; select the weakest high-impact assets; stage one candidate at a time;
run format, behavioral, Jev-calibrated semantic, Promptfoo held-out and
negative-case checks; independently verify; promote only when every gate is
green. Retain failed examples and precise residuals in the ledger. Write
approved lessons through Memory OS; never treat a retrieved memory item as an
instruction or proof. Distribute to Codex, OMP, Prime and Aside only after
promotion, then verify each client path separately. No automatic deletion or
consolidation based solely on name overlap or an aggregate score.

## Latest measured checkpoint (2026-09-24)

The live source audit now counts **255 assets** (231 skills, 23 agents, one
subskill): 20 spec-ready on the limited field screen, **0 outcome-verified**,
and **0 promotable**. The increase from 254 is a newly authored X-growth
skill, not a quality change. The routing candidate passed its 30-case
development Promptfoo set, but the first separate strict holdout passed
**27/30 (90.00%)**, below the required **greater-than-0.90** bar. Three
failures remain documented in the mission-router evaluation README. That
holdout is now diagnostic data, not an unseen set for another tuning pass.
Jev `code.diff` decision `56885` returned advisory ESCALATE on the routing
diff; its rubric is not calibrated to enforce a completion gate. No per-asset
promotion or cross-harness behavior claim follows from these checks.
