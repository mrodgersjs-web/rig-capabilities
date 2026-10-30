---
name: "done-claim-verification"
description: "Bind every claim of 'done', 'fixed', 'installed', or 'working' to evidence taken through a DIFFERENT tool path than the one that did the work. Use whenever reporting completion, accepting a builder's completion report, or before any outward or irreversible action. Trigger on: 'is it done', 'verify this', 'did that work', 'the agent says it's fixed', before claiming success."
when_to_use: "Before any completion claim leaves your mouth, and before trusting one that arrives from a builder, subagent, or routine."
version: "1.0.0"
status: "active"
outcome: "misc: a done-claim is bound to an independent receipt; unverified completions are reported as unverified"
done_when:
  - 'grep:capabilities/skills/done-claim-verification/SKILL.md:a completion claim is a hypothesis\. Bind it to a receipt'
great_example: "examples/great/misc/done-claim-verification.md"
quality_floor: "0.8"
---

# Done-claim verification

**Rule: a completion claim is a hypothesis. Bind it to a receipt or label it unverified.**

## The check (choose the one that matches the claim)

| Claim type | Independent receipt |
|---|---|
| code changed / fixed | `git show <sha>` or `git diff` through a shell, not the editor that wrote it |
| file written | re-read it with a **different tool path** after the fact, plus byte count or checksum |
| byte content changed | checksum the target **before and after** the change and require movement |
| a count / total | compute it a **second way** and require the two to agree |
| a service is running | a real request returning expected content, not a PID or a port |
| a config value is set | read the value **back** after the write |
| a routine ran | the artifact it produces exists and is non-empty |

## Hard rules

- A `cat` from the same call that wrote the file is **not** verification. A file write shown
  verified by its own `cat` plus an 11-byte hex dump was later found absent by an independent
  read.
- An empty result from a check you just wrote is more often a **check bug** than an absence.
  Run the extractor against something known non-empty before reporting zero.
- A command that reports a suspiciously **small or round** number is suspect. Confirm with a
  second method before reporting it.
- "The agent said it is done" is a claim, never a receipt.

## Why this exists

2026-09-25 - a builder reported its fixes complete. `git show` proved the report false while
its own tests read 19/19 green. It happened at least twice that day, and one slice shipped a
fabricated $5,000 MRR fallback figure that nobody asked for and no evidence supported. The
afternoon was spent verifying fake reports instead of building.

The lesson is not "verify harder". It is that the verification must come from a **different
path** than the one that produced the claim, or it is the claim checking itself.
