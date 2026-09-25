# Decision criteria: what good and bad look like, per situation

Companion to `../SKILL.md`. Each situation answers four things: when it fires in a
session, what exactly goes to Jev (state and question shape), what good use looks
like, what bad use looks like. Answer hygiene and hard prohibitions at the bottom
apply to every row.

Situations S1-S13 are the decision inventory of Step 1. An agent that has read its
mission should be able to walk this list and mark which rows it will meet.

---

## S1. Mission routing (session start, and after any mission change)

- Fires: first turn; again whenever scope shifts.
- To Jev: one `choice` over work types (the lane or workflow that should own the
  work). State = mission line + constraints + what is out of scope.
- GOOD: the typed answer selects a route (which rubric pack, which workflow, which
  lane rules apply) and code applies it. A wrong route is a one-line fix.
- BAD: a frontier model reasons about routing in prose for a paragraph and the
  agent acts on its own paraphrase of that prose.

## S2. Intake triage and admission screening (files, notes, mail, tabs, alerts)

- Fires: a batch of incoming items must be sorted before any real work.
- To Jev: ONE call carrying N items as state, with `choice` (kind), `noul`
  (keep? in scope? credential-bearing?) and `score` (urgency) questions per item.
- GOOD: code maps answers to actions (file / escalate / archive / quarantine); low
  confidence routes to a review queue; nothing irreversible is ever executed from
  this path; every item keeps its decision id.
- BAD: an LLM call per item in a bulk loop; generated prose re-parsed with regex to
  find the category; a triage answer that silently deletes or sends anything.

## S3. Cheap-reject ordering (disqualify first)

- Fires: a large candidate set where most items should never reach full evaluation
  (resumes, leads, postings, ideas).
- To Jev: the disqualifying `noul` FIRST (is this even eligible), then fuller
  questions only for survivors.
- GOOD: the reject runs in the low tens of ms and the expensive evaluation only sees
  survivors; the reject threshold is tuned to avoid false blocks (law 4 of s1gate:
  a gate that blocks good work gets switched off).
- BAD: full evaluation of everything, then rejection; or a reject so aggressive it
  discards good candidates with no label trail to prove it later.

## S4. Verification (claims x evidence)

- Fires: a document, diff, report, or answer contains factual claims that must
  survive scrutiny before being repeated or shipped.
- To Jev: `jev_verify`-style per-claim `noul`/`choice` verdicts (supported /
  contradicted / not-addressed) with the evidence passed in state.
- GOOD: verdict per claim, bound to the specific evidence, cited by id in the
  output; unsupported claims get deleted or flagged, never softened silently.
- BAD: one global "is this true" score; a mean over heterogeneous claims; trusting
  the verdict without the evidence in the same state string.

## S5. Ranking and selection (order candidates by fit)

- Fires: choosing among options: leads, roles, skills, models, tabs, posts to reply to.
- To Jev: `score` (fit level) or `choice` (best option) per candidate against a
  stated criterion; ordering computed in code from the probabilities.
- GOOD: the criterion is written down and one-dimensional; ties and low-confidence
  rows fall to a named fallback (human, FIFO, do-nothing) rather than a coin flip.
- BAD: a composite "quality" score mixing three dimensions; ranking by a bimodal
  mean; the ordering logic living in prose.

## S6. Quality screen before expensive work (shortlist for System 2)

- Fires: before spending a frontier call, a long build, or a human's review time.
- To Jev: broad screen (`jev_review` / `code.review` / `plan.readiness` shape) over
  the whole artifact or diff, returning the reasons a shortlist deserves System 2.
- GOOD: the screen collapses "spin up an agent to look at this" into a threshold
  check; the shortlist plus the reasons is what the frontier model receives.
- BAD: sending everything to System 2 anyway "to be safe" (the cost case dies), or
  using the screen as a final verdict on work that needed deep reading.

## S7. Stage gate before a transition (plan -> build, diff -> merge, draft -> publish)

- Fires: any irreversible-ish step boundary in a workflow.
- To Jev: `rig-s1gate check <rubric> --file <artifact> --subject <id> --json`; the
  consumer is a hook reading the exit code (0 PASS / 1 BLOCK / 2 ESCALATE / 3 config).
- GOOD: the gate sits in front of the transition in code (Stop/PostToolUse hook),
  its BLOCK reasons are fed back into the same session as correction, and advisory
  rubrics warn without blocking until calibrated.
- BAD: a gate whose output nobody consumes (a dashboard to him: a score that only
  informs is not a control); re-prompting a fresh session instead of the same one;
  treating an uncalibrated PASS as authority.

## S8. Comparison (A vs B under a stated criterion)

- Fires: two patches, two drafts, two designs, two routes head to head.
- To Jev: `jev_compare`-style paired questions under one written criterion.
- GOOD: one criterion at a time, the pairs randomized or double-run to kill order
  effects, the decision recorded with the criterion in state.
- BAD: "which is better" with no criterion; five criteria collapsed into one mean;
  the comparison used as the sole gate on work that needs deep review.

## S9. Typed extraction (fields out of prose, logs, forms, patches)

- Fires: unstructured text must yield typed fields (a form fill, a schema, a CSV
  column mapping, an alert's owning team).
- To Jev: `choice`/`noul` per field against a closed vocabulary; code templates the
  questions so the same field always asks the same thing.
- GOOD: a deterministic pass first (exact name equality, schema match), Jev only on
  the remainder, and anything below threshold left visible for a human rather than
  guessed. One batched call carrying all fields is fine (253 questions in one call
  measured at 915 ms, $0.0012).
- BAD: Jev first where code would do; guessing an unmapped field; prose answers
  string-parsed back into fields.

## S10. Release light/block (ship it or not)

- Fires: publish, deploy, send, merge-to-main moments.
- To Jev: `jev_gate` / lane rubric (`post.*`, `email.outreach`, `code.diff`) with
  per-criterion signals and reason sentences on any block.
- GOOD: three-band consume with stakes-scaled thresholds; every BLOCK carries reason
  sentences a human can act on at 11pm; false blocks loop to the author as rewrite
  guidance, never to Mike as a complaint.
- BAD: hard block from an uncalibrated rubric (law 3 of s1gate); a machine PASS
  treated as authorization to spend or publish (Gate-D is unchanged); a block with
  no reasons.

## S11. Content lane assignment (Lane A / B / C)

- Fires: any content, comment, or engagement touching a social account.
- To Jev: `choice` over lanes plus the lane rubric's own questions. Lane C
  (content about a minor) detection has precedence over everything.
- GOOD: lane decided before drafting; `nil.jacob` and all `never_auto` rubrics
  downgrade even a clean PASS to ESCALATE; comments stay positive-only per house rule.
- BAD: letting one lane borrow another's voice; auto-scheduling Lane C; reading a
  machine PASS as permission to post.

## S12. The meta-route: code vs Jev vs System 2 vs human

- Fires: whenever a new judgment appears mid-session that no inventory predicted.
- To Jev: this decision itself can be a Jev question (the jev-fit test as a `noul`
  set: bounded state? fixed answer set? consumed by code?), with a non-task guard
  `noul` in front and "not sure" as a legal answer.
- GOOD: the fallback ladder is explicit and code vetoes Jev where Jev cannot help
  (needs images, needs live browsing, needs generation), then lands on System 2 or a
  human. External precedent: jev-fit routes exactly this way.
- BAD: reflexively sending every new judgment to the frontier model; or forcing a
  Jev call on something that needs generation and then narrating around the answer.

## S13. In-session skill and tool selection

- Fires: the mission names an outcome and the session must pick which skill/tool
  set executes it.
- To Jev: one `choice` over the installed roster (skills, tools, workflows) plus a
  gate `noul` ("does anything here even apply"), with a per-candidate fit floor.
- GOOD: shadow mode first (log the pick, do not inject) until the decision traces
  look clean; only the chosen skill's instructions reach the prompt; a weak match is
  DECLINED (gate says no) instead of guessed; deterministic pre-filtering removes
  ineligible candidates before Jev sees them.
- BAD: stuffing the whole catalog into the prompt and hoping; injecting skill
  instructions on a sub-floor match; no record of what was picked and why.

---

## Answer hygiene (every situation)

- **A score mean is only meaningful when the distribution is unimodal.** A bimodal
  result (observed live: mean 1.39, confidence 0.0, mass at opposite ends) means the
  question measures two things: split it.
- **`noul` has no confidence field at all.** Missing is not zero. `noul ~ 0.5` means
  yes and no are equally likely.
- **Confidence summarizes distribution concentration. It is never permission to act.**
  Score/choice rules carry a companion confidence floor (s1gate default 0.9): below
  the floor, ESCALATE, never PASS.
- **Thresholds scale to the stakes**, three bands (act / caution / do-not-act), with
  the middle band going to a human or a review queue that has a defined owner.
- **Rule syntax traps:** `choice` criteria is a dict `slug -> description` and rules
  compare against the slug (a slug with a space is unreachable); a rule's left side
  is `<question>.<attr>` with exactly one dot (an option probability is
  `q.p.OPT`). An invalid rule is a valid string: load and evaluate every rule, do
  not merely parse it.

## Hard prohibitions (bad by definition, refused on sight)

- Frontier LLM calls in a per-item bulk loop where a rubric answers.
- Text-parsing a model's prose where a typed answer exists.
- A rubric marked `calibrated: true` without `rig-s1gate calibrate` output.
- Sending unredacted state to Jev (credentials, tokens, client source you do not
  own, health or financial detail, anything private about Jacob).
- Silent local fallback verdicts when the provider is down.
- Letting a model pick file destinations, approvals, or spend decisions directly.
- Wrapper laundering: a model inside the deployed decision path is A2 work however
  it is packaged (D85 rule).
