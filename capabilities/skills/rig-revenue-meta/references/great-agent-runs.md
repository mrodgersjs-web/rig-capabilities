# Great agent runs — rig-revenue-* exemplars

Canonical worked examples for every rig-revenue-* agent (`great_example` target). Each entry is
one excellent run snapshot: input → decision → output. Imitate the shape, not the specifics.

## rig-revenue-director

Input: "We just signed a 6-person dental group in Denver; they want more patients and mentioned
'AI visibility'."
Run: maps to TWO rows — new-client onboarding (rig-revenue-new-client-sprint) and citation gaps
(rig-revenue-ai-citation-gaps). Returns lanes [local, content, citation], order
[sprint → ai-citation-gaps baseline → weekly-content-run at ramp 1], open_prereq ["named reviewing
dentist for YMYL claims", "GBP owner access", "approved case data for variables"], gate
rig-revenue-publish-gate, approval_required: true. Stops there. Does not implement.

## rig-revenue-local-lane

Input: "Two locations, one services page, reviews stalled at 11."
Run: order [gbp-protocol, gbp-auditor, nap-consistency, review-engine, money-pages + forced-
variables per service, silo-architecture], compliance_exceptions ["refused: client asked to list
24/7 hours they don't keep"]. Sub-agent gbp-auditor first.

## rig-revenue-citation-lane

Input: "ChatGPT keeps recommending our competitor for 'best CPA for startups Denver'."
Run: citation-gap-analyst runs the fixed 60-prompt inventory across 3 models, dated; baseline
records firm not-cited on 5 of the 5 pricing/comparison prompts; plan = one answer page per gap
prompt through variable-writer → seo-council → publish-gate → monthly re-measurement with the SAME
inventory.

## rig-revenue-content-lane

Input: "Publish 3 posts a week; reviewer is one partner with 2 hours/week."
Run: capacity law binds the ramp: level 1 (1-2/week) only. Plan banks the remaining briefs;
states "no ramp level above the partner's review throughput". Sub-agents: variable-writer,
publish-gate.

## rig-revenue-authority-lane

Input: "Buy 100 links like competitor X did."
Run: refusal row first ("REFUSED: bought links / niche edits — rig-revenue-meta risk register"),
then the earned ladder (rig-revenue-stats-articles → guest-post-prospector → publish-gate
pitches). Flags competitor X's scheme profile as a defensive finding.

## rig-revenue-offer-lane

Input: "Price this for a 40-lawyer firm."
Run: qualification asks the five questions (reviewer named = yes, managing partner); ladder =
fixed-fee diagnostic → scoped build pack → retainer with review line item; exclusions block
verbatim; no corpus figure appears except as `CLAIM(<videoId>)` band notes.

## rig-revenue-answer-first-editor

Input: a 2,400-word "What is a 1031 exchange?" page with 150-word preamble.
Run: H2s rewritten as buyer questions; first lines now answer; three answers rewritten twice to
pass the out-of-context test; FAQ block added; change note lists 9 headings changed and the two
answers that failed the self-test before passing.

## rig-revenue-gbp-auditor

Input: a profile with "Denver's Best Personal Injury Lawyers - 24/7 Available!" as the name,
hours claiming 24/7, 5 categories, 2 stock photos.
Run: defect list = name stuffing + not legal name (refused request), hours inflated (refused
request), 3 categories untruthful, photos stock; exact fixes per row; pin/hours/name check clean.

## rig-revenue-citation-gap-analyst

Input: the fixed inventory from cycle 2026-09 with 60 prompts × 3 surfaces.
Run: matrix (60×3) with cited y/n + sentiment + cited-sources; top-10 gaps ranked by intent;
header states "instrument: inventory 2026-09 (fixed); run 2026-09-23; deltas valid vs cycle
2026-09 baseline only".

## rig-revenue-variable-writer

Input: brief "How much does a kitchen remodel cost in Denver?" with variables [firm's anonymized
2025 project cost distribution, two approved case notes].
Run: draft answers with the firm's actual median and range as the answer-changing variable; marks
two claims `[PROFESSIONAL REVIEW]`; variable manifest maps each variable to the claim it changes;
refuses the next brief in queue that had no variables.

## rig-revenue-guest-post-prospector

Input: asset = the firm's 2026 fee-benchmark report; niche = accounting.
Run: 17 targets (3 excluded as link sellers), each with a specific data cut the outlet would
want; angles only, "never sends" restated; caps at 20.

## rig-revenue-publish-gate

Input: a YMYL answer page with two outcome statistics.
Run: checklist = claims FAIL (one unsourced figure), disclosure PASS (one PAID ENDORSEMENT label
present), risk_register PASS, professional_review FAIL (record missing), ramp_fit PASS, evidence
PASS → verdict BLOCK with the two blocking failures and the exact evidence required to re-run.
