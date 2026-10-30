---
name: traject-target-qualify
description: "Traject OS sub-skill, stages 1-2 (target-qualify, source-dedupe): qualify a role against Mike's band and shape, and dedupe it against the ApplyPilot store and Gmail receipts before any apply work. Gated by JEV job.fit, company.fit, jobhunt.select; dedupe is a CODE gate. DEFER when the classifier is down; never tailor or apply a role that fails fit or is a duplicate."
tags: [rig, traject-os, sub-skill, qualify, dedupe, job-search]
metadata:
  parent: traject-os
  tier: sub
  stage: target-qualify
  covers: [target-qualify, source-dedupe]
  extends: "aside-job-source, resume-screening-stack"
outcome: "A qualified, deduped target: a job.fit/company.fit/jobhunt.select verdict with its decision ids, a clean dedupe receipt against ~/.applypilot/applications.sqlite3 and Gmail, and a named reason for any reject."
activation: "Load at the start of any new role before tailoring or applying, and whenever a target list needs deduping."
instruction: "Gate fit with rig-s1gate job.fit and jobhunt.select (band is base $250K target / $180K floor, 2026-09-27; all Group A locations; unknown pay allowed with the recorded token), dedupe by employer+role+req against the store and receipts, and pass only clean, in-band, non-duplicate roles to traject-apply-bridge. Never loosen the band to hit a volume number."
applies_when:
  env: "the Traject cockpit and ~/.applypilot store; Aside for official postings"
  runtime: "SQLite store, Gmail receipt search, official employer postings"
  deps: "aside-job-source dedupe logic; rig-s1gate with job.fit/company.fit/jobhunt.select"
  params: "role, company, req id/url, source of the posting"
  budget: "minutes per role; batch dedupe over a target list"
  scale: "one role per qualify; a list for dedupe"
permissions:
  - fs.read
  - bash
  - browser.read
flow:
  - Resolve the official posting and read the band, location, and shape.
  - Gate fit with job.fit and jobhunt.select; unknown pay needs the recorded decision token.
  - Dedupe against ~/.applypilot/applications.sqlite3 and Gmail receipts (employer+role+req).
  - Pass clean in-band roles to traject-apply-bridge; record rejects with a reason.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/job.fit.json"
  - "file:capabilities/harnesses/s1gate/rubrics/jobhunt.select.json"
out_of_scope:
  - tailoring the résumé (traject-apply-bridge / aside-job-resume)
  - filling or submitting any application form
  - loosening the compensation band to satisfy a weekly volume target
---

# traject-target-qualify

JEV FIRST on fit: an agent whose only context is this excerpt routes the fit and select
verdicts to `rig-s1gate check job.fit` and `jobhunt.select` BEFORE any frontier call;
dedupe is CODE. Classifier down: DEFER, never guess. A required signal passes only above 0.9.

Sub-skill of `traject-os`, stages 1-2 of 11. Main skills: `aside-job-source` (qualification
and dedupe), `resume-screening-stack` (fit against the real hiring stack). Agents:
`traject-conductor`, `traject-company-researcher`, `traject-dedupe-checker`.

## Procedure

1. **Resolve the official posting** (employer site or the recorded source), then read the
   base band, location, and role shape. Mike's band is **base $250K target, $180K floor**
   (2026-09-27 decision), all Group A locations (remote-US, Denver/CO, NYC, Bay Area, Boston,
   Chicago, Austin, Seattle, DC). Unknown pay is allowed with the recorded token
   MIKE-2026-09-27-GRILL-Q3 — never silently reject unknown pay and never accept a stale floor.
2. **Gate fit**: `rig-s1gate check job.fit --file <posting> --subject "job.fit:<company>-<role> sha=<sha12>" --json`,
   then `jobhunt.select`. Rewrite-free (this is a verdict stage): below 0.9 the role is a
   named reject, not a maybe.
3. **Dedupe (CODE gate)**: check employer+role+req against `~/.applypilot/applications.sqlite3`
   and Gmail receipts. A duplicate (already applied, or a receipt exists) is dropped with the
   receipt id. Beware Gmail offset pagination repeats a page (TL-06): dedupe by message id
   across pages and verify the count against the source of truth.
4. **Hand off** clean, in-band, non-duplicate roles to `traject-apply-bridge` with the JEV
   decision ids and the dedupe receipt.

## Lessons that fire here

- **TL-06** dedupe by message id across Gmail pages; verify the receipt count.
- **TL-11** the compensation floor is the current $180K decision, not a stale script constant.
- Run `python3 capabilities/skills/traject-os/scripts/fire_lessons.py "<task text>"` for the list.
