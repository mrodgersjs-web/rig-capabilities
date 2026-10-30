---
name: hermes-resume-only-applications
description: Prepare and assist Mike's job applications from current resume files only; enforce truthful prior-employer answers, preserve saved screening facts, and distinguish prepared forms from confirmed submissions.
version: 1.0.0
owner: rig-intelligence
status: internal
metadata:
  related_skills:
    - job-application-cockpit
    - rig-write-resumes
    - application-packet-builder
    - browser-skill
done_when:
  - grep:capabilities/skills/hermes-resume-only-applications/SKILL.md:A run processes at most five target jobs
  - grep:capabilities/skills/hermes-resume-only-applications/SKILL.md:Do not call a prepared or prefilled application APPLIED
  - cmd:python3 capabilities/skills/hermes-resume-only-applications/verify_sources.py | python3 -c "import json,sys;d=json.load(sys.stdin);assert d['status'] in ('PASS','BLOCK') and len(d['checks'])>0"
---

# Hermes resume-only applications

Read PROMPT.md, WORKFLOW.md and sources.json in this skill directory. Run `python3 verify_sources.py` using its absolute path before application work. This verifies source files, not career claims or application readiness. Hash changes require re-extraction and review; never silently refresh a pinned source.

Mike's instruction: the only places he has worked are on his resume. His requested No default applies to direct prior-employer questions about companies absent from that complete history. Preserve supported answers for other questions. Broad or ambiguous questions about contractors, subsidiaries, affiliates, previous applications, relatives or conflicts are not direct employment questions: use distinct evidence or NEEDS_MIKE. Do not infer previous application history from the resume. Never answer No to a known contradictory fact.

The selected DOCX is the sole employment-history authority. The answer bank may supply contact and personal screening facts but cannot add employers, titles, dates, credentials or metrics. Older personas, LinkedIn profiles, packet examples and memory are not career evidence. Client/partner references in achievement bullets are not employers. An employer alias must be supported by the resume or separately clarified by Mike. Preserve grouped manufacturing dates; do not assign a date range to individual employers when the resume groups them.

Use the AI Leadership DOCX for AI strategy, transformation, enablement, adoption and executive roles. Use the Forward Deployed Leadership DOCX for deployment-strategy, field/solutions and delivery-leadership roles. Coding-first individual-contributor and research roles need fit review. Do not use legacy resume_current.txt, old FDE files, or a Markdown companion when its content differs from the selected DOCX.

Load related skills only for their named job; these source rules override old persona examples. Missing required job descriptions, credentials or experience remain gaps. Tailoring changes emphasis and wording, never facts. Do not manufacture a metric to satisfy a writing template.

A run processes at most five target jobs or 45 minutes, whichever comes first. One target at a time until a full reviewed sample succeeds. Maximum two recovery attempts per portal; preserve evidence and move to manual handling after that. Never reset caps to continue a stalled run.

Application preparation and supported-field browser prefill are authorized when Mike requests them. Final submission remains the human step of the existing ApplyOps prefill workflow. Do not bypass its submit prohibition. A future explicitly authorized submission adapter needs separate verification. No recruiter messages, connection actions, paid services or unsolicited outreach are part of this skill.

Do not call a prepared or prefilled application APPLIED. Record APPLIED only after an employer confirmation/receipt or Mike's explicit reported completion, distinguishing those evidence types. Check existing application history first and reconcile uncertain outcomes before retrying. Never resubmit merely because a browser timed out.

No persistent schedule or inference starts by loading this skill. Keep private application artifacts local with directories mode0700/files0600. Store credentials only through existing credential stores; never copy them into packets, prompts or evidence.
