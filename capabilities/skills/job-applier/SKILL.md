---
name: job-applier
description: Prepare a job-specific executive resume and application packet in Aside using the Lucy evidence workflow, then guide Mike through factual resume review and a separate approval for each specific submission. Use for Job Applier, application preparation, application routines, or the first-five hand-held application pilot.
metadata:
  display-name: Job Applier
  owner: julie-job-search
  version: 1.2.2
---

# Job Applier

This is the existing Job Applier meta-skill. It orchestrates the ordered family below; each leaf owns one workflow step. Keep the existing entry name and app workflow ID.

Use one official job posting and one application record at a time. Produce the complete polished working resume first, then let Mike confirm, replace, or omit the claims. Finish with a clean final resume and application review. This skill never treats preparation, installation, a routine run, or resume approval as permission to submit.

## Mandatory ordered leaf execution

Every invocation, routine and recovery run must load and execute these exact leaves in order. Do not skip the full ideal-candidate persona because a resume, shallow ideal profile, or old run already exists. Persona research describes the role; it never supplies candidate facts. Existing local app stages are not proof these leaves ran.

1. [posting-inventory](steps/posting-inventory/SKILL.md).
2. [ideal-candidate-persona](steps/ideal-candidate-persona/SKILL.md).
3. [ideal-achievement-bank](steps/ideal-achievement-bank/SKILL.md).
4. [evidence-alignment](steps/evidence-alignment/SKILL.md).
5. [word-review-copy](steps/word-review-copy/SKILL.md).
6. [targeted-confirmation](steps/targeted-confirmation/SKILL.md).
7. [document-quality](steps/document-quality/SKILL.md).
8. [application-approval](steps/application-approval/SKILL.md).

Every role also requires the authenticated, multi-account GitHub portfolio audit inside [evidence alignment](steps/evidence-alignment/SKILL.md), using [the portfolio evidence contract](references/github-portfolio-evidence.md). Refresh accessible account/repository coverage and inspect JD-relevant code and tests before asking Mike for facts already recoverable from his portfolio. Historical public repositories alone are not the full estate. Keep repository implementation evidence separate from personal contribution and commercial outcomes; only the residual gaps become targeted questions. A saved evidence bank is a starting point, not proof of current HEAD or full account coverage.

Read [the family packet contract](references/family-packet.md) for artifact schemas and actual step-execution evidence. Run `python3 scripts/validate_packet.py <packet.json>` at working/final/submitted checkpoints. This validates structure and current hash bindings only. It does not establish truth, semantic quality, authentic approval or provider authority. Preserve Jev holds and existing application gates.

The Word review copy must show actual `FF0000` red proposals in appropriate existing resume slots. Put explicit **UNCONFIRMED** status and tentative placement in Word comments or a separate linked review worksheet bound to the exact draft hash and claim ID, never extra resume-body paragraphs. Keep a separate clean supported-content version. This review copy is not a final employer-facing resume. Ask targeted factual questions after the useful full draft, then verify and approve the exact clean pages.

## Bounded Aside execution

Run exactly one bounded leaf step per Aside session. Follow [the context and recovery limits](references/bounded-step-execution.md): pass durable checkpoint pointers and hashes, use bounded JSON projections, default to at most 8,000 source-pack tokens and 1,500 characters per tool output. A context-limit failure is nonretryable in the old session; recover the same step in a fresh session from its saved checkpoint. These limits never bypass evidence, image, Jev or human approval gates.

## Daily durable execution

For the daily application process, Aside must implement and follow [the daily Temporal execution contract](references/temporal-daily-workflow.md). Use eight durable child workflows, one per leaf, attached to a stable employer/requisition application lineage across days. The configurable default is 18:00 America/Denver with a target of 30 daily applications, overlap SKIP and bounded catchup. Targets never override factual/page review, Jev holds, first-five receipt counting or separate application authorization. Codex supplies this skill contract; Aside owns implementation/execution. Installation does not prove a live schedule or durable worker behavior.

## Start here

Mike can say: **“Use Job Applier for this role: <official posting URL>. Prepare the full resume, then walk me through the evidence review. Stop before submission.”**

In the local Aside Work interface, select **Job Applier**. The existing app workflow ID is `executive-resume`; keep that ID for compatibility. See [the workflow contract](references/workflow-contract.md) for the local entry point and durable review sequence. A skill name is not proof that a bare `/job-applier` slash command is registered.

Read the installed [Lucy resume evidence skill](/Users/rig128gb/.aside/u/0/skills/user/lucy-resume-evidence/SKILL.md) for the resume-writing step. It owns the ideal-achievement draft and evidence conversion. Its shared evidence contract and full Lucy resume source leaf remain authoritative for claim handling and attributed Lucy advice. Do not overwrite or replace `lucy-skills`, `lucyskills`, `lucy-executive-evidence`, or `lucy-resume-evidence`.

## 1. Verify the target and avoid duplicates

- Open the complete current employer or ATS posting. Record employer, exact title, requisition ID when present, canonical URL, location/work arrangement, full JD, retrieval time, and source hash. An aggregator snippet, search result, stale cached JD, or a page shell is not a complete active posting.
- Confirm the posting is still active. If closed, removed, unreadable, or contradictory, stop this job with that specific reason. Do not draft an application-ready packet against an unverified target.
- Check the existing application ledger and any saved checkpoint by requisition ID plus employer and canonical URL. Keep discovery records separate from applications. If a prior application may have submitted but lacks a receipt, reconcile it before another submission; do not create a new record to dodge the duplicate.
- Load Mike's selected source resume and source-backed career evidence. Preserve the master and its hash. Known facts can be reused within their stated scope; an old AI-generated answer is a derivative reference, not evidence that an event happened.
- Read requirements, including the minimum qualifications, before responsibilities. Separate direct evidence, adjacent experience, proposed approaches, and unresolved gaps. Do not silently relax location, compensation, credentials, or other standing requirements to fill a queue.

Draft-first requires the full captured JD, current activity evidence, correct target identity, passing deterministic source checks, and a valid live provider receipt passing active identity (`c01`). After those checks, downstream pre-draft semantic findings guide a clearly labeled provisional working draft. Preserve every finding, including failed or unknown provider results, as a visible hold and input to drafting; never rewrite its receipt as PASS. Generated output must still satisfy its schema, source-ID, and candidate-fact validation. Inactive, stale, unreadable, or mismatched sources and missing or failed live identity verification do not qualify. Any failed or unknown gate blocks evidence-to-final advancement, final downloads, application readiness, and submission.

## Preserve the selected Word template and prove tailoring

Read [the original Word fidelity contract](references/word-format-fidelity.md). The original DOCX package and existing paragraph/run layout are the baseline. Keep banners, editorial notes, full JD checklists, questions and unplaced hypothetical patterns in the linked review worksheet, not the resume body.

Use the selected source DOCX as the document template, not merely a text source. Mike's current selected master is `/Users/rig128gb/.applypilot/resumes/masters/Mike-Rodgers-Resume-FINAL-v3-2026-10-06.docx`; confirm the actual selected path and hash for each run. Keep the master immutable and write a separate job-specific output copy. Preserve its Word styles, fonts, margins, numbering and bullet definitions, paragraph/run formatting, section order and section settings, headers/footers, and page setup. Replace supported content within existing appropriate slots while preserving section order; do not rebuild it from Markdown into a generic Word layout. If the available renderer cannot preserve the selected template, retain the text draft and report **Word-template preservation blocked**. Do not present that export as the finished resume.

Tailoring must change the summary, capabilities emphasis, and relevant experience wording/order to address this exact posting using supported career facts. A new target title, a copied source resume, or a requirement map alone does not prove tailoring. For each substantive JD requirement, show its priority, source evidence and employer, exact original wording, proposed job-specific wording, and any gap. Distinguish direct evidence from adjacent experience; missing history requires a specific question to Mike, never an invented achievement, title, metric, or industry claim. Do not force a rewrite where the source already fits; explain retained wording in the map.

Show Mike the before/after content review beside the complete Word draft. Verify the source hash remains unchanged, compare paragraph/run properties, tabs, dates, bullets, spacing and section order as well as style/numbering/section properties, and visually compare every original/output page using the same renderer and settings. Matching style hashes alone cannot pass fidelity. Content length may change pagination; do not silently change margins or shrink fonts to force a page count. Treat loss of the original layout or absence of meaningful job-specific rewriting as an unresolved defect.

A source-only recovery document must be labeled **SOURCE-ONLY RECOVERY — TAILORING INCOMPLETE** in the review surface and its receipt. Keep that status outside the employer-facing resume body. It preserves usable source content but is not a completed tailored resume, cannot clear tailoring or final-readiness gates, and must return to job-specific rewriting and before/after review before advancement.

## 2. Deliver the whole executive working resume

Label the review surface and linked worksheet **IDEAL-ACHIEVEMENT WORKING DRAFT — PENDING MIKE'S EVIDENCE REVIEW**, not the resume body. Do not withhold this useful draft while waiting for a fact questionnaire.

Deliver a coherent resume: identity/contact fields from sources, target positioning, executive summary, relevant experience, capabilities, education, and credentials where supported. Provide exact before/after changes and a requirement-to-achievement map in the separate linked review worksheet. Keep unmatched hypothetical patterns there. A proposed edit in an appropriate existing resume slot is red; record its tentative/UNCONFIRMED status in a Word comment or the linked worksheet using the exact draft hash and claim ID. It is never attributed candidate history until confirmed.

For each substantive line, record a stable claim ID, the requirement served, source pointer, claim status, employer, role, dates/period, personal action, mechanism, result and units, scope, and remaining factual questions. Preserve unknown values as visible brackets in the linked review worksheet, not appended resume-body notes. Complete drafting means the whole document is composed; it does not mean unknown facts have been invented.

- Lead resume achievements with a supported outcome, then personal action and mechanism. Bracketed hypothetical patterns belong in the linked review worksheet. Keep prose polished and executive-level.
- Never attach fictional ideal achievements to real employers, assign a JD's industry to past employment, rename an actual title, fabricate dates, or claim sole ownership of a team result.
- Missing metrics remain bracketed in the worksheet working pattern or become a truthful qualitative result after review. A plausible number is not a fact. Employment duration is not the time taken to achieve an outcome.
- Keep cost, revenue, inventory stock, recurring savings, business size, transaction value, prototypes, and production results distinct.
- The summary follows the same evidence rules as experience bullets. It cannot reintroduce an unsupported claim removed elsewhere.
- Use [the source map](references/source-method-map.md) when attributing a rule to Lucy. This Job Applier sequence and five-application pilot are Mike's workflow, not a claim that Lucy prescribed or endorsed them.

Optional advisory step: once the working draft and its requirement map are saved, you may run the [behavioral advisory pass](references/bx-advisory-pass.md). It writes `bx-advice.json` beside the packet (hiring-committee view, bias audit of the draft, falsification of the top claim) for the review conversation. It never edits the resume, never changes a claim's status, and never passes or fails a gate.

## 3. Mike reviews the exact draft

Save the working draft, requirement map, claim ledger, source hashes, and exact draft hash before asking for review. Show the complete resume and concise claim decisions beside it.

Render the actual working DOCX, review its sanitized page images, and retain the `working_image` quality receipt before the factual review. A polished text preview does not prove that the DOCX layout is readable.

For every material claim Mike chooses **confirm**, **replace**, or **omit**. Record his factual response and provenance durably against that exact draft hash. Confirm means the statement's actual employer, role, period, action, result, and qualification are supported. “Sounds good,” “make it stronger,” or approval of phrasing alone does not supply those facts. User-confirmed history remains candidate-reported unless separate evidence corroborates it.

If Mike supplies an alternative real example, map it to the requirement and preserve the actual employer and facts. If wording or source content changes after review, invalidate the stale review and show the new exact version. Do not infer a replacement fact or use an old approval to bypass this step.

## 4. Final resume, then application review

Produce the review Markdown and DOCX from the reviewed content. Omit or truthfully narrow unsupported claims. The final resume must contain no unresolved placeholders, working labels, or fictional patterns. Check every final factual clause against the ledger and check that the rendered DOCX matches the final text without clipping, blank bullets, or broken sections. The app pauses at `awaiting_document_review`; only after the required live quality receipts and Mike's exact-page approval may it expose final artifacts and advance to `application_review`.

The final packet includes the official posting, exact final resume and hashes, claim/requirement map, unresolved fit gaps, and proposed form answers or cover letter if requested. Do not invent missing screening answers, consent preferences, protected demographic disclosures, work authorization, or sponsorship facts. Existing evidence or Mike's explicit answer must support each one.

Stop at **application review**. Present the employer, title, requisition ID, exact destination, resume attachment and hash, complete form answers, optional attachments, and any employer attestations. Ask for approval of that specific application only after Mike has reviewed the resume. The local Job Applier app stages this packet; it does not submit applications or send outreach.

## First five applications: hand-held pilot

Read [the pilot and recovery rules](references/pilot-and-recovery.md) before preparing or resuming the pilot. All first five applications require Mike's resume review **before** his separate approval for each specific submission. Keep one application at a time through those checkpoints.

The count advances only from an actual submission receipt linked to the matching resume review and specific submission approval. A draft, model completion, approval alone, test run, or click is not a submission. Missing receipts mean the count stays unchanged, including **0/5** when none exist. The fifth receipt does not grant future autonomous submission authority.

Run [the fifteen quality criteria and typed Jev transitions](references/quality-gates.md) throughout this sequence. Keep actual receipts. Unavailable Jev or unresolved blocking questions holds the next transition. Inspect the actual rendered final resume page images and preserve Mike's page approval; an image-review receipt cannot substitute for his factual review or submission approval.

## Routine integration and stop conditions

Every current or formerly active job-applying routine routes preparation through Job Applier. Existing routine enabled/disabled state is preserved: installation and prompt routing do not reactivate an inactive routine. A scheduled run may source roles and prepare the working packet, then wait for Mike; it cannot batch-approve claims or submissions.

Never import old blanket batch-submit or outreach authority from legacy Lucy/application skills into this pilot. Current task authorization governs, and this workflow requires separate per-application review. No submit, send, message, profile edit, or resume-registry replacement occurs merely because this skill was installed or invoked.

If the required app route, source, ledger, or review persistence is unavailable, report the exact blocker and retain existing artifacts. Continue independent read-only preparation when useful. Do not silently skip a gate, erase a checkpoint, restart infrastructure, or switch to an autonomous submission tool.

Report only observed states: **working draft awaiting evidence review**, **final packet awaiting application review**, **blocked**, **submission unknown**, or **submitted with receipt**. Include the saved record/artifact location and the smallest next human step. “Ready for review” is not “submitted.”
