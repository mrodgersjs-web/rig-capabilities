# Prompt routing table

_Generated from `registry.json` by `node tools/route.mjs --write-routing`. Do not hand-edit._

Registry updated: 2026-09-24 | prompts: 26

## code

- **independent-read-only-review** v1 [draft] - Independent read-only review of a landed fix: bugs, security, violations, run the check, no source writes
  - triggers: independent review, read-only review, always recheck, review this fix, pass with exact evidence
- **independent-verification-sidecar** v1 [draft] - Design green-path and red-path tests for a harness without editing files
  - triggers: verification sidecar, propose red-path tests, green path red path, propose gates not edit, independent test design
- **worktree-unit-spec-packet** v1 [draft] - Parallel worker packet: isolated worktree, read the spec in full, run tests and paste real output, commit
  - triggers: worktree worker prompt, isolated track handoff, assign track, builder spec in full, sealed unit of work

## coding

- **coding-mission-outcome** v1 [draft] - Implement and verify a bounded coding change from a hash-bound mission packet
  - triggers: Python parser, coding mission, implement code, fix an API bug, regression test

## gtm-outreach

- **off-linkedin-distribution-push** v1 [draft] - Off-LinkedIn distribution push for a live post: execute what is executable, name the exact blocker for the rest
  - triggers: push this post off linkedin, cross post distribution, execute the lanes, exact blocking report, off-platform amplification
- **read-only-icp-outreach-targets** v1 [draft] - Read-only prospect selection from the existing network using primary sources, no sending
  - triggers: find outreach targets, who should i email, prospect list no sending, target selection read only, best network prospects

## job-search

- **job-receipt-reconciliation** v1 [draft] - Read-only application receipt reconciliation in a bounded window, sqlite readonly only
  - triggers: reconcile application receipts, new application evidence, check submissions read only, receipt check, application ledger audit
- **job-search-state-audit** v1 [draft] - Full audit of job-search state: materials, moves today, resume and LinkedIn and saved-jobs alignment
  - triggers: job search audit, full audit of what we have, moves today, job strategy alignment, step back on the job search

## ops-automation

- **nightly-memory-consolidation** v1 [draft] - Nightly Memory OS consolidation: set the memory budget, run consolidation, record what changed
  - triggers: nightly memory consolidation, consolidate memories, memory budget, memory os maintenance, run the consolidation
- **ops-fleet-reliability-sweep** v1 [draft] - Read-only fleet reliability sweep reporting only new breakage since the last report
  - triggers: reliability sweep, read-only report, watchdog report, fleet status, new failures, cron health
- **ops-heartbeat-heal-report** v1 [draft] - Run rig-heartbeat heal and write the VERDICT report with mandatory receipt
  - triggers: heartbeat, heal the fleet, ops health report, run the heartbeat, automation receipt, fleet receipt

## planning-strategy

- **decision-grade-morning-brief** v1 [draft] - Decision-grade morning brief sized for a phone, gathering read-only inputs before ranking decisions
  - triggers: morning brief, decision grade brief, brief for today, what needs deciding today, phone length brief
- **future-back-versioned-gtm-roadmap** v1 [draft] - Future-back versioned roadmap and GTM design for a program going from now to a named version
  - triggers: future back roadmap, design out v20, versioned upgrade plan, go to market plan, deep layers

## prompt-craft

- **pattern-few-shot-block** v1 [draft] - Add structured few-shot examples that hold style and decision boundaries
  - triggers: few shot examples, add examples, example block, match this style, show examples, decision boundary
- **pattern-prompt-chain-3step** v1 [draft] - Chain three single-purpose prompts: summarize, extract insights, create action items
  - triggers: prompt chaining, break it into steps, summarize then insights, action items from, chain of prompts, one shot failing
- **pattern-sectioned-prompt** v1 [draft] - Structure any task prompt into delimited sections: background, instructions, tool guidance, output description
  - triggers: section the prompt, structure the prompt, xml tagged prompt, background information instructions, output description, prompt layout
- **pattern-subagent-search-isolate** v1 [draft] - Isolate search in sub-agents so the lead agent only synthesizes and decides
  - triggers: sub agent research, isolate search context, lead agent synthesizes, research with subagents, delegate the search, context isolation

## research

- **linkedin-growth-2026-research** v1 [draft] - Research what works on LinkedIn now using outside sources only, no account writes
  - triggers: what is working on linkedin, research growth tactics, outside sources only, no account writes, current linkedin best practices
- **recall-product-inventory** v1 [draft] - Source-cited product and technical inventory of a named product in numbered coverage areas
  - triggers: reverse engineer this product, source-cited product inventory, technical inventory of, research the product, factual stack analysis

## rig-gtm

- **lead-triage-classifier** v0 [draft] - Classify an inbound message (LinkedIn/email) as client-lead, job-opportunity, vendor-spam, or other

## verification-probe

- **probe-connectivity-ack** v1 [draft] - One-shot connectivity check that echoes an exact ack literal and touches nothing
  - triggers: connectivity check, reply with exactly, echo the ack, liveness probe, ack literal
- **probe-exec-raw-stdout** v1 [draft] - Run one exact command and return raw stdout, stderr and exit code with zero interpretation
  - triggers: run exactly this, raw stdout, no interpretation, prove the command ran, exec proof, exit code only
- **probe-repl-once** v1 [draft] - Connection test exercising exactly one repl call and reporting one observed value
  - triggers: connection test, repl exactly once, report the page title, one tool call, fresh observation
- **secret-scan-memory-probe** v1 [draft] - Scan memory for secrets and report presence without ever printing values
  - triggers: scan memory for secrets, credentials in memory, sensitive values check, memory secret audit, api keys check
- **stop-report-no-edits** v1 [draft] - Stop exploration now and return strongest findings with evidence, no edits
  - triggers: stop exploring, return strongest findings, wrap up with evidence, no edits just findings, timebox stop

## writing-content

- **linkedin-draft-no-publish** v1 [draft] - Draft a short LinkedIn post and print only, never publish or schedule
  - triggers: draft a short linkedin post, do not publish, two sentence post, print the draft only, draft only post

