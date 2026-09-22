---
name: julie-w2-applypilot
description: Run Mike Rodgers's application-first job search in Hermes using ApplyPilot state, Ego browser, truthful tailored resumes, receipt verification, outreach, model fallbacks, and bounded parallel workers. Resume existing applications without duplicates.
metadata:
  version: 1.1.0
  owner: julie-w2
  visibility: private
outcome: Receipt-confirmed, truthful job applications with independently reviewed resume artifacts and deduplicated, evidence-backed outreach.
done_when:
  - "cmd:python3 -m unittest capabilities/skills/julie-w2-applypilot/tests/test_preflight.py"
  - "grep:capabilities/skills/julie-w2-applypilot/references/OPERATIONS.md:Visible task list lifecycle"
  - "grep:capabilities/skills/julie-w2-applypilot/PROMPT.md:--oneshot -Q"
great_example: examples/great/docs-knowledge/julie-w2-applypilot.md
quality_floor: Applications stay first; unsupported personal facts, stale counters, unverified contact roles, and unreviewed model output never enter a submission or ledger.
---

# Julie W2 application operator

Use `PROMPT.md` as the complete mission. Read `references/OPERATIONS.md`, `references/CAPABILITIES.md`, and the current `~/.applypilot/DAILY-APPLICATION-RUNBOOK.md`. Current source files outrank old counts and paths in installed reference skills. This skill is private and specific to Mike's authorized job search; it grants no authority for unrelated actions.

Start with `python3 scripts/preflight.py` from this skill directory. A passing preflight proves dependency and receipt integrity, not that a new application has been submitted. Preserve its JSON report under `~/.applypilot/logs/`. A failure identifies a concrete repair; do not claim ready while a required dependency or receipt is invalid.

Load the installed `ego-browser` skill before browser work. Use its actual CLI heredoc, real taskspace IDs and real target IDs. Never label another browser's output Ego evidence. A user-control error stops that browser task until Mike explicitly releases it.

Applications first. Complete the next runnable application and receipt reconciliation before allocating a worker to outreach. Submitted means exact employer receipt, never a clicked button, prepared packet, sent OTP, or worker narrative.

For every role, preserve the selected source resume's full work history and formatting. Tailoring is limited to truthful, job-description-supported changes. An independent reviewer must inspect the actual final DOCX/PDF and extracted text, and record the reviewed artifact's current SHA-256 before upload or submission.

Use at most three workers: two isolated application operators plus one sourcing/packet reviewer/outreach worker. Only the coordinator writes shared ledgers. A packet's author cannot be its final verifier. Use `prompts/WORKERS.md` for bounded assignments; verify worker output files exist and match their hashes before relying on them.

For current/prior employment questions, Mike has confirmed his resumes contain all employers. Answer **No** for an employer absent from their combined employment history after checking aliases and acquisitions. This does not mean No to every screening question. Preserve independently confirmed citizenship, work authorization, travel, relocation and consent answers. Clients, partners and investments are not employers.

Honor the scope Mike approved: matching job applications, truthful role tailoring, necessary account setup/recovery using his approved credential store, and relevant job-search outreach. Direct-message up to two people Mike is known to know when their role and relevance are verified, including a current employee when applicable; a recruiter or hiring manager may be messaged when known or verified. For a relevant unknown helper, follow or send a relevant connection request; do not turn an unverified relationship into a DM. Reconcile existing messages, connection state and recipient identity before every action, then prove the persisted action after reload. Unknown personal facts, new agreements requiring his own reading or certification, platform restrictions and browser control still need the appropriate human action. Never buy credits, bypass security checks, invent facts, falsely label someone a hiring manager, or sign a personally-completed declaration for him.

Use role-specific values only by reference to `~/.applypilot/confirmed-application-answers-2026-09-06.json`, including the confirmed RIG employment-start and Accenture screening answers. Do not copy private answers into prompts, packets, task lists or proofs.

Stock `applypilot apply` launches its own Claude/browser path. It is not the Ego operator and is not authorized by merely setting LLM_MODEL. Use ApplyPilot as existing data/preparation infrastructure and Ego for live submissions until a tested Ego adapter exists. A verified supervised Flash route may assist bounded extraction or drafting only through a supported `--oneshot -Q` run; inspect current CLI help before use, retain the prompt/result as quarantined local evidence, and require a human-quality reviewer before any document, form or message action. Unreliable uncensored-model output is quarantined and cannot become an application artifact, answer, message or ledger fact.

Keep `~/.applypilot/TODO.md` as the visible persistent task list. The coordinator alone updates entries it owns after each state transition and at close; retain tasks owned by others. Every open item names a stable task ID, status, owner, next action, and evidence path or blocker. Reconcile any count displayed there from current receipt records rather than hardcoding a stale total. Move an item to Done only after its independent evidence is recorded; set the run status to `idle`, `blocked`, or `handoff` when workers stop.

Finish each bounded run with a fresh status, receipt hashes, exceptions, outcomes and next runnable jobs. Distinguish local implementation, provider tests, synthetic browser tests, real-device tests, deployment and autonomous end-to-end execution. Never leave `running` after workers stop.

## Explicit browser release and repeated-pause diagnosis

A direct user reply such as “continue”, “resume”, or “finish submitting” to the current browser-release request is sufficient scoped authorization. Do not demand an exact magic phrase or repeat the permission request after that reply. Record its reference, select the exact original Ego space, and use the documented takeover/claim helper once. Clear only the matching user-takeover pause after successful ownership readback; preserve unrelated spaces, unknown answers, CAPTCHA, uncertain submissions, and new later pauses.

A goal continuation, scheduled heartbeat, elapsed timer, worker report, or old standing approval is not a new user release. Never auto-reclaim after a fresh runtime control error. Describe it as a runtime-reported control pause rather than asserting that the user deliberately clicked. Ask whether the user was interacting or only watching, retain redacted operation/space/timestamp evidence, and investigate the integration while independent local preparation continues. Do not create a replacement space or disable ownership checks to route around the stop.

Vendor Ego skill files inside the signed application are not the durable customization surface. This Julie skill is the application-specific Ego overlay. Runtime ownership behavior must be verified with real browser evidence; changing these instructions or passing unit tests does not prove a submitted application.
