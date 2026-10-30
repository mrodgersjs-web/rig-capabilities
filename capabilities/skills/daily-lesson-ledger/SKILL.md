---
name: "daily-lesson-ledger"
description: "Run the daily evening review that turns the day's work into tomorrow's brief and into durable skill changes. Produces one dated brief covering what happened, what it taught us, what changes, which skills/agents/harnesses to add or change, what to build next, and tomorrow's priorities. Use when the 19:00 routine fires, when asked for a daily review, a lessons recap, 'what did we learn', or tomorrow's plan."
when_to_use: "The 19:00 daily routine, or any request for a day review / tomorrow's priorities."
version: "1.0.0"
status: "active"
outcome: "agent-engineering: each day closes with a dated brief and any lesson that changes behaviour lands in a skill the same day"
done_when:
  - "file:/Users/rig128gb/.rig/daily-review/"
  - grep:capabilities/skills/daily-lesson-ledger/SKILL.md:Never substitute a text description for the artifact
  - grep:capabilities/skills/daily-lesson-ledger/SKILL.md:## Fail-loud guard
great_example: "examples/great/agent-engineering/daily-lesson-ledger.md"
quality_floor: "0.8"
---

# Daily lesson ledger

**Rule: a lesson that does not change a skill is a note, not a lesson.**

## Output

Write `~/.rig/daily-review/<TOMORROW>.md` - dated for the day it **plans**, not the day it
runs, because that is the brief Mike wakes up with. Use exactly these eight sections:

1. **What we did** - facts with times and receipts, not adjectives.
2. **What it taught us** - each lesson stated as a rule that would have prevented the failure.
3. **What changes going forward** - the mechanism, named and enforceable.
4. **Skills to add or update** - and the edit is made **in the same run**, not queued.
5. **Agents to add or change.**
6. **Harnesses to add or change.**
7. **What to build next.**
8. **Tomorrow's priorities** - ordered, with the one that matters most first.

Then announce it in one line with the file path.

## The enforcement that makes this real

Section 4 is the load-bearing one. If section 2 contains a lesson and the skills diff for
the run is empty, the review **has not happened**. Go back and write the skill.

Why: 2026-09-25 produced six real lessons and wrote none of them into a skill. The
`~/Developer/rig-skills` repo had zero commits, the lessons ledger had not been appended
since 09-22, and a literal grep for the four load-bearing phrases from that day's failures
returned 0 hits across every skill on the machine. The knowledge evaporated into a 605KB
transcript nothing will read again.

## The five mechanisms this review enforces

1. **Provider probe first** - see `provider-probe-first`.
2. **Done-claim verification** - see `done-claim-verification`.
3. **Plant a failure, prove the byte moved** - see `adversarial-verification-loop`.
4. **Explicit model on every spawn** - see `subagent-model-pinning`.
5. **Non-empty subject on every gate call** - see `gate-subject-required`.

Any day whose work touched these five must report on them explicitly.

## Fail-loud guard

If the brief cannot be produced, emit exactly one line beginning `BLOCKED:` naming the
reason, and stop. Never substitute a text description for the artifact. A clean run with
zero output is otherwise indistinguishable from success.

## Quality floor

Counts and claims in the brief must be independently verified. A number that only informs
is a dashboard; every metric in section 8 must drive a rank, a rewrite, or an escalation.
