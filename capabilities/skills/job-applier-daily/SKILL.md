---
name: job-applier-daily
description: Prepare daily job application packets with Julie W2 priorities, full role personas, sourced initiative questions, original-format Word resumes, tailored cover letters, Airtable tracking, and separate approval for each submission.
metadata:
  version: 1.4.0
  owner: julie-job-search
---

# Daily Job Applier

## Twenty meta-skills and execution ownership

Use [the 20-meta-skill catalog](references/meta-catalog.md) to route each part of the work. The machine-readable [catalog](config/meta-catalog.json) binds every router to its step skills and source capabilities. These are task-specific compositions; source skills remain attributed. Load only the selected router and its relevant steps.

Grokbot coordinates; [Aside CLI](steps/aside-cli/SKILL.md) performs browser application work in an owned session. [JEV decisions](steps/jev-decision/SKILL.md) and [JEV image review](steps/jev-image/SKILL.md) remain separate, genuine provider checks. A local structural check or an agent's statement does not replace either. Follow the exact CLI commands in [Aside CLI operations](references/aside-cli.md); never guess a command or a tool name.

This portable extension preserves [Job Applier 1.2.2](../job-applier/SKILL.md) and its eight ordered leaves. Load this meta-skill for each posting and load each selected step before executing it. Never replace a full current persona with a prior resume or shallow profile. Installation, imported text, validators, and simulated tests do not establish execution.

Native GrokBot import and execution are unsupported/unverified by this package. Its tools are local validators, not an application executor. A capable host must supply authenticated research, JEV, Word rendering, Airtable, browser, approval identity, and durable scheduling adapters. Missing adapters leave the affected step held. Do not invent commands or claim the host supports these adapters.

Read [Julie W2 adaptation](references/julie-w2.md), [execution and approval contract](references/execution-contract.md), and [acceptance criteria](references/acceptance.md). Read [local audit limits](references/local-audit.md) before interpreting validator results. The [daily profile](config/daily-profile.json) ships disabled. Explicit first and last run dates, timezone, start time, window, verified owner, and approved schedule scope are required before arming. No schedule is activated by this package. No outreach authority is included.

## Ordered run

1. [Daily setup](steps/daily-setup/SKILL.md), then [bounded discovery](steps/daily-discovery/SKILL.md).
2. [Posting inventory](steps/posting-inventory/SKILL.md), inherited leaf 1.
3. [Full ideal-candidate persona](steps/ideal-candidate-persona/SKILL.md), inherited leaf 2.
4. [Ideal achievement bank](steps/ideal-achievement-bank/SKILL.md), inherited leaf 3.
5. [Employer initiative research](steps/employer-initiative-research/SKILL.md).
6. [Evidence alignment](steps/evidence-alignment/SKILL.md), inherited leaf 4.
7. [Word review copy](steps/word-review-copy/SKILL.md), inherited leaf 5. Execute its [resume writer](steps/resume-writer/SKILL.md), [cover-letter writer](steps/cover-letter-writer/SKILL.md), and [SlopMonster adapter](steps/slopmonster-review/SKILL.md).
8. [Targeted confirmation](steps/targeted-confirmation/SKILL.md), inherited leaf 6. Ask factual participation and inclusion separately.
9. [Document quality](steps/document-quality/SKILL.md), inherited leaf 7. Incorporate decisions, rerun writing checks and render every changed page.
10. [Application approval](steps/application-approval/SKILL.md), inherited leaf 8. Stop until the exact application is separately authorized.
11. [ATS submission and reconciliation](steps/ats-reconciliation/SKILL.md) only with a verified host adapter and current authorization.
12. [Daily closeout](steps/daily-closeout/SKILL.md).

The coordinator executes [Airtable ledger sync](steps/airtable-ledger/SKILL.md) at admission, each material checkpoint, before any submission, and closeout. Airtable is authoritative for the application tracker. Local checkpoints preserve recovery evidence; they do not silently replace Airtable or certify a successful write. Reconcile tracking failures before further outward action.

## Writing dependencies

Load [Lucy resume evidence](../lucy-resume-evidence/SKILL.md) for evidence conversion. Load [SlopMonster](../slopmonster/SKILL.md) for prose review through the adapter. Neither style advice nor ideal-candidate research establishes personal facts. A missing sibling is a broken dependency, not permission to substitute an unreviewed generic writer.

## Safe starter prompt

“Load job-applier-daily/SKILL.md and its required sibling skills. Inspect the disabled profile and tracker mapping. Prepare one packet for <official posting URL> using my selected original Word resume. Produce the full persona, sourced employer initiative research, red review resume, separate supported clean resume, and tailored cover letter. Ask whether I personally participated in relevant former-employer initiatives and separately whether to include each confirmed contribution. Show exact rendered pages. Stop before any application submission or schedule activation. Report real receipts, blockers, and unverified adapters.”
