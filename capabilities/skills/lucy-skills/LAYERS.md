# lucy-skills: layer map

**JEV FIRST.** Picking which meta, skill or sub-skill fits a task is a typed judgment: run `/Users/rig128gb/.rig/bin/skill-surface route "<task>"` (one Jev choice per layer, logged decision ids) before any frontier model reads the catalog. If no classifier answers, the verdict is DEFERRED: use this map and `/Users/rig128gb/.rig/bin/skill-surface find`, never a guessed verdict. Use the hosted JEV API only. Redact secrets before sending state. If private details remain, redaction is unavailable, or JEV fails, defer. Do not install or restart OpenJev or Laya as a fallback.

Lucy career meta: profile, resume, interview practice, salary. Owner agent: julie-job-search. Profile edits retain exact before/after review and scoped approval.

| Layer | Path | Purpose |
|---|---|---|
| Meta | `SKILL.md` | Route the actual career task |
| Leaf | `../lucy-executive-evidence/SKILL.md` | Executive answers, requirement mapping, actual history and proposed industry application |
| Leaf | `../lucy-resume-evidence/SKILL.md` | Ideal-achievement working resume, Mike's evidence review, application-ready resume |
| Alias | `../lucyskills/SKILL.md` | Compact Lucy entrypoint |
| Existing full pack | `~/.omp/agent/skills/lucy-skills/SKILL.md` | Established Lucy workflows and source rules |

Legacy leaves live under that full-pack root: `sub-skills/positioning.md`, `sub-skills/resume.md`, `sub-skills/salary-negotiation.md`, `sub-skills/job-search.md`, `sub-skills/linkedin-activity.md`, `sub-skills/career-growth.md`, `playbooks/interview-practice.md`, and `playbooks/optimize-linkedin.md`. The entrypoint names the narrower job-lane and profile leaves. Read only the task's relevant branch.

Do not route legacy work through `~/.claude/skills/lucy-skills`; that is another thin meta. Native skill invocation syntax depends on the host; OMP supports `/skill:lucyskills`. A natural-language alias does not by itself register a bare slash command.
