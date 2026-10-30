---
name: job-applier
description: Prepare a complete role-specific executive resume and application packet, review factual claims with the candidate, run typed Jev quality checks and rendered-page review, then stop for separate approval of each specific application.
metadata:
  version: 1.1.0
---

# Job Applier

Start with one official active job posting and the candidate's selected resume. Produce a complete polished working resume, obtain factual review, produce the final resume, and stop at exact application review. Installing or invoking this skill does not submit anything.

The candidate can say: "Use Job Applier for this official posting. Build the full executive working resume, walk me through the factual review, and stop before submission."

## Read before running

- Read [the portable process](references/process.md) for the actual execution and record requirements.
- Read [the Lucy resume evidence skill](../lucy-resume-evidence/SKILL.md) for drafting and claim conversion.
- Read [the quality procedure](references/quality.md) for all fifteen criteria, typed Jev gates, image review, and executable helpers.
- Read [pilot and recovery](references/pilot-and-recovery.md) before the first-five pilot or a resumed application.

These are ordinary Aside user skills. Ask Aside to use Job Applier or select the skill through the host's supported picker. A bare `/job-applier` command is not promised. The bundle does not install a model, browser, automation, or the separate local Work application used by the author.

## Required ordered step skills

This existing Job Applier entry is the meta-skill. Reload it for each new role, then load and execute every linked leaf in order, including recovery runs. Existing chat context, an old resume, or a shallow ideal profile cannot replace the full current persona.

1. [Posting and atomic inventory](steps/posting-inventory/SKILL.md).
2. [Full ideal-candidate persona](steps/ideal-candidate-persona/SKILL.md).
3. [Ideal achievement bank](steps/ideal-achievement-bank/SKILL.md).
4. [Candidate evidence alignment](steps/evidence-alignment/SKILL.md).
5. [Word review copy](steps/word-review-copy/SKILL.md).
6. [Targeted factual confirmation](steps/targeted-confirmation/SKILL.md).
7. [Document and page quality](steps/document-quality/SKILL.md).
8. [Specific application approval and receipt](steps/application-approval/SKILL.md).

The full persona must cover all thirteen areas in [the packet contract](references/family-packet.md), including role mandate, decision rights, industry economics, 90-day/year outcomes, capability and leadership depth, ideal proof, constraints, tradeoffs, hiring questions and adjacent fit. Persona research is not candidate history. Every substantive requirement needs an ideal result/action/strategy example and evidence alignment or an honest gap.

Use the candidate's selected Word file as an immutable template. Preserve its styles, margins, numbering and sections in separate output copies. Produce a complete tailored review copy before a full factual questionnaire. Unconfirmed examples must use actual red Word text `FF0000`, literal UNCONFIRMED labels and clearly marked tentative placement. Keep a separate clean supported-content version. Ask focused factual questions and obtain real confirmation before promoting any example. Render and review actual pages; factual and exact-page review precede separate application approval.

Run `python3 scripts/validate_packet.py <packet.json>` from the installed Job Applier folder at persona, working, final and submitted checkpoints. Keep actual step execution and source/artifact hash bindings. This structural check is not a truth, Jev, human-identity or authorization certificate. Source-only recovery is **TAILORING INCOMPLETE**, never a completed tailored resume.

Draft-first requires the full captured JD, current activity evidence, correct target identity, passing deterministic source checks, and a valid live provider receipt passing active identity (`c01`). After those checks, preserve every downstream pre-draft semantic finding as a visible hold and input to the provisional draft, including failed or unknown provider results. Keep the original receipts and `can_advance` values unchanged; this is preparation only. Generated output still requires valid schema, source IDs, and candidate-fact attribution. Inactive, stale, unreadable, or mismatched sources and missing or failed live identity verification do not qualify. Any failed or unknown gate blocks final content, final files, application readiness, and submission. The portable adapter does not clear holds. Recheck after meaningful corrections, without manufacturing PASS or repeating unchanged requests until one passes.

## Truth and attribution

Unsourced achievements remain clearly labeled patterns with bracketed employer, role, outcome, units, mechanism, scope, and period fields. Unmatched patterns stay separate; any tentative employer placement in the red review copy must be clearly marked UNCONFIRMED and never treated as candidate history. Never invent dates, figures, employers, tools, credentials, clients, industry experience, or individual ownership. Missing metrics permit truthful qualitative results, not fabricated numbers.

The summary and experience bullets follow the same evidence ledger. Preserve cost versus revenue, inventory stock versus recurring savings, business size versus transaction price, and prototype versus production distinctions. Employment duration is not achievement duration. Approval of wording is not confirmation that an event occurred.

For a replacement, use the candidate's actual example and preserve its facts. A changed draft, source, final attachment, or material answer invalidates the affected prior review. Never transfer approval between roles or versions. Source-cited Lucy advice is paraphrased; this workflow's evidence controls and pilot are adaptations.

## First five and routines

Guide the first five applications one at a time. The candidate reviews each resume before separately approving that specific submission. Count only actual employer/ATS receipts linked to the exact factual review and submission approval. Drafts, model runs, clicks, and approvals alone do not count. Start at 0/5 when no qualifying receipt chain exists. Completing five does not authorize autonomous future submissions.

Existing application routines must use this preparation and review sequence. Preserve their active or inactive state. A routine can prepare a draft and wait, but cannot silently approve the candidate's facts, submit a batch, or send outreach.

Missing tools, source evidence, Jev credentials, a typed receipt, or an actual rendered page holds the affected transition. Preserve progress and report the exact missing requirement. Never guess a Jev verdict or call a pending application submitted. The helpers validate local evidence and invoke the configured provider; they do not authenticate an employer receipt independently or perform submissions.
