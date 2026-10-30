# Jev practice review and RIG decision map

Date: 2026-09-23. These are public primary-source examples, not independent
proof that their claimed outcomes generalize to RIG. `Jeff` and `JET` in the
request are interpreted as Jev/System One.

## Observed approaches

| Source | Working pattern worth testing | Evidence limit |
| --- | --- | --- |
| [TypeSafe tool-router example](https://github.com/TypeSafeAI/typesafe-playground/blob/main/docs/tool-router.md) | Policy filters graph edges before Jev chooses the next edge; a deterministic single-edge path skips the model. | Demo mocks execution. |
| [TypeSafe router](https://github.com/TypeSafeAI/typesafe-router) | Closed candidate set, typed choice, confidence/fallback policy, separate authorization and executor. | Demo/library, not RIG production evidence. |
| [OpenJev](https://github.com/razorback16/openjev/blob/main/README.md) | Loopback `/v1/systemone` accepts batched noul/choice/score questions; no generated prose. | Our observed local mission choice took about 2 seconds end-to-end, not a verified sub-200 ms route. Local probability calibration is unproven here. |
| [pi-jev](https://github.com/TheoOliveira/pi-jev) | Agent tool selection uses an opt-in semantic gate; model output does not execute the tool. | Third-party project claims, not RIG live behavior. |
| [Jev Agent Skill Router](https://github.com/GodsBoy/jev-agent-skill-router) | Confidence-aware skill choice and a no-match option; synthetic evaluation compared to lexical search. | Small synthetic benchmark is not proof on Mike's real requests. |
| [Skillbox](https://github.com/kitze/skillbox) | Optional Jev recommendation over versioned, scoped skills. | Recommendation is distinct from authorization. |
| [Jev research pipeline](https://github.com/shimo4228/jev-research-pipeline) | Deterministic collection, Jev relevance screening, generative synthesis. | Pilot; source screening is not factual verification. |

## RIG decision inventory

Order for every interaction: code eligibility/permission filters → Jev on a
bounded shortlist if semantic judgment is needed → System 2 for generation or
complex reasoning → independent deterministic/outcome verifier → human Gate-D
for outward or irreversible acts. Candidate ID and version are always bound to
the current catalog before model selection. A model never sees a candidate it
is not allowed to propose.

| Surface | Code owns | Jev can answer (typed) | System 2 / verifier owns |
| --- | --- | --- | --- |
| NL mission | Scope, runtime support, candidate shortlist, ties | Meta-lane choice, no-match, urgency class | Plan, work, actual completion receipt |
| Agents/subagents | Catalog provenance, grants, one-writer lease, verifier independence | Rank eligible agents or choose no-match | Agent execution and independent review |
| Skills/subskills | Canonical ownership, parent route, file hash, required reads | Choose among allowed children; confidence/abstain | Follow skill instructions; test outcome |
| Prompts | Version, status, source, fixture split, promotion lock | Choose a prompt challenger or relevance screen | Generate/edit; Promptfoo plus real task outcomes determine promotion |
| Tools/MCP | Allowlist, parameters, auth, side-effect class, rate/cost ceilings | Rank permitted read tools; classify whether a tool is needed | Actual call, postcondition, audit, approval |
| Automation | Schedule, idempotency, state machine, retry/kill switch | Triage new items, relevance, anomaly/priority | Perform bounded work; verify state; human outward approval |
| Research/knowledge | Source allowlist, recency, data boundary | Relevance and candidate prioritization | Read actual source, citation and claim check |
| Quality/completion | Gate schema, hashes, tests, execution receipts | Advisory semantic quality or unsupported-claim screen | Deterministic gates and independent real-world evidence |

This matrix covers every asset *by kind* as a routing policy. The current
catalog query returns 1,604 agent entries, 2,293 skill entries, and 26 prompt
registry entries (all 26 draft). It does not mean every entry has been individually
smoked or calibrated. Current wiring only performs a local shadow meta-lane
choice via `mission.route`; agent, child-skill, prompt, tool, and automation
choices in the matrix are staged requirements, not implemented gates.

## Calibration and weekly update contract

1. Collect actual requests and expected lane/agent/skill/prompt/tool choices
   with source and privacy labels. Keep training, tuning, and held-out cases
   separate. Include no-match, prompt injection, conflicting choices, missing
   Memory OS, local Jev outage, and irreversible-action examples.
2. Run the deterministic route and Jev in shadow on the same eligible shortlist.
   Log decision ID, model revision, confidence, latency, disagreement, and
   later outcome label; do not store raw private state previews.
3. Measure false accept, miss, abstention, p50/p95 wall time, total cost, and
   task outcome against lexical-only and System-2 baselines. Local OpenJev
   confidence must not be called calibrated without this evidence.
4. Stage weekly primary-source deltas and candidate changes. Promptfoo tests
   routing invariants now; add an independent artifact/outcome dataset before
   any champion prompt/agent promotion. Source publication and synthetic
   benchmarks are leads, not acceptance tests.
5. Promote only a version-pinned winner after human review of failures and
   independent proof. Rollback pointer stays available. No weekly job sends,
   publishes, deploys, installs, or changes credentials automatically.

## Current proof and residuals

Local OpenJev `/v1/models` returned `openjev-0.1`. The `mission.route` rubric
returned `when-shipping-code` for a Python parser task with logged decision
55059 at 2,041 ms and decision 55060 at 1,956 ms. These two observations prove
the call path only; they do not establish routing accuracy or cost superiority.
The mission packet remains `candidate`, with `execution.authorized=false` and
a draft prompt block. Memory OS package status was `ok` in the live smoke.
An earlier internal completion probe reran `tests.test_completion_gate` with
exit 0 and logged Jev decision 55073. Independent review then found that the
agent-controlled command and mutable rubric could yield false DONE. The CLI
now only prechecks artifact hashes; it executes no tests without a trusted
controller contract, and this adapter cannot return DONE. Decision 55073 is
historical path evidence, not current completion certification.
Other harness runtimes, dynamic asset-level Jev selection, outcome evaluation,
and weekly promotion are not yet proved.

## LAYA and image decisions: observed local state

- `/Users/rig128gb/.rig/bin/rig-laya` exists. It loads a RIG decision head from
  `/Users/rig128gb/.rig/laya-training/rig-laya-head/rig-head.pt` by default,
  with an explicit `active_head` in output. Its training receipt says 1,304
  records, 978 train, 326 holdout, and final holdout accuracy 0.610 versus a
  0.521 baseline. This is a recorded run, not independently replicated here.
  The receipt's `best_holdout_acc` equals baseline while `final_holdout_acc`
  is higher; resolve that inconsistency before model promotion.
  Its optional calibrated wrapper also reads `ans["confidence"]` for a noul
  answer even though this answer type normally has no confidence field; test
  that path before using it as a completion checker.
- LAYA's installed `Router.predict` exposes text/dict/list state and questions,
  but no image argument. Its config names a ModernBERT-large encoder. Do not
  route raw screenshots or visual proof to this installed LAYA path.
- Local OpenJev at `127.0.0.1:8080` serves `openjev-0.1` and its live API
  schema includes `images`. A two-image red/blue PNG smoke returned the correct
  color choice for each. That proves transport and a trivial visual judgment,
  not calibration or coding-agent UI verification.
- Separate files under `~/.rig/openjev/results/v2/` report an 8,000-item
  image-NLI experiment (0.83825 for a Qwen3.5-4B v2 checkpoint versus 0.520125
  for an earlier checkpoint). Those files do not prove that checkpoint is the
  one served at `127.0.0.1:8080`. Treat it as a training candidate only.

For image gates, first collect labelled screenshots tied to actual acceptance
criteria, including confusing near-matches and negative cases. Hold out whole
projects/tasks so the model cannot memorize a UI. Compare the served OpenJev
baseline, the trained candidate, LAYA text-only route where appropriate, and
an independent visual verifier on accuracy, false PASS, calibration (Brier/ECE),
p95 latency, memory, and outage behavior. Version and hash the image encoder,
decision head, preprocessing, rubric, dataset, and threshold. Train only after
data-use and GPU budget checks. Keep the image gate in shadow until the held-out
result beats baseline; a trained checkpoint never silently replaces the live
endpoint. Images must never stand in for browser interaction proof.

## Coding-agent completion gate

Target order: trusted intent/acceptance contract → current diff/artifact hashes → rerun behavioral tests and a
planted failure → independent verifier in a different model family → Jev
`mission.completion` and existing `code.diff` semantic screens → deterministic
completion decision in a separately trusted adapter. The Jev decision must
carry a logged decision ID and source binding. A Jev outage or missing evidence
yields no DONE. The current adapter never returns DONE, even if a rubric changes.
Current `code.diff` rubric is explicitly uncalibrated: its 204 labelled commits
did not align to the rubric's actual questions. The new `mission.completion`
rubric is also uncalibrated and `never_auto`. Neither is authority to declare
work complete yet. Build a held-out corpus of *actual* claim-vs-evidence labels,
measure false PASS and false BLOCK, then certify exact question/threshold/model
before enabling an automatic semantic block. Deterministic tests and independent
verification remain required even after calibration.
