---
name: lucyskills
description: Handle the exact /lucyskills alias by routing executive interview evidence and resume evidence work to the new leaves, while preserving the existing lucy-skills workflows for other Lucy career requests.
---

# /lucyskills

This is an alias and router. Preserve the user's actual task and the existing Lucy package.

The skill name is `lucyskills`. Use the host's explicit skill invocation where required, such as `/skill:lucyskills` in OMP. Do not claim that a bare `/lucyskills` is registered as a native command without observing that host behavior.

| Request | Read and execute |
|---|---|
| Executive interview answers, JD-to-proof mapping, truthful industry bridges, or fit gaps | [lucy-executive-evidence](../lucy-executive-evidence/SKILL.md) |
| Resume bullets, resume summary, resume evidence audit, or tailoring to a JD | [lucy-resume-evidence](../lucy-resume-evidence/SKILL.md) |
| LinkedIn, outreach, job-search cadence, salary negotiation, cover letter, interview drills, follow-up, career growth, or another established Lucy workflow | Existing [lucy-skills](../lucy-skills/SKILL.md), then only the relevant leaf it declares |
| Both interview and resume work | Keep the interview bank and resume working draft distinct. Use sourced history where available; let Mike map evidence to ideal resume achievements before an application-ready version |

Resolve paths relative to this skill directory. If the sibling Lucy package is a router, follow its declared route to the relevant full-pack leaf. Do not import, replace, or overwrite a different harness's full Lucy package. If a dependency is missing or loops back without reaching a leaf, report the broken route and request or locate the existing package within the permitted scope.

State the selected leaf briefly, then do the requested work. A bare `/lucyskills` with no task should offer the three relevant choices: executive interview preparation, resume evidence, or an existing Lucy career workflow. Do not silently choose a substantive task.

The alias adds no publishing, sending, submission, or profile-edit authority. Existing broader workflows retain their own boundaries and sources. Exact Lucy quotations require their source video IDs; new answer wording is an adaptation.
