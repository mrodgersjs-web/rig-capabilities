---
id: rig-hq-sub-j6-post-cycle
version: 1
status: draft
tier: sub
department: Growth & Content
agent: ralph-linkedin
parent: rig-hq-prompt-steve-content
task: Recurring sub-prompt (J6): one content cycle — lane call, hooks, draft, gate
triggers: content cycle, write a post, draft this content, hooks for this
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J6), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Post cycle (J6 recurring)

**Trigger.** A piece of content is needed in some lane.

**Typed inputs.** `lane` (RIG B2B | personal brand | Ideawake client | job search),
`format`, `source_material` (exact file/transcript/receipt), `word_budget`, `bar`.

**Steps.**
1. Fix the lane first; a draft may carry exactly one lane's voice.
2. Bind to the supplied source bytes; pull the story/numbers from them, not memory.
3. Draft 3 hooks + one body that pays the winning hook; mark any example as never to
   be emitted verbatim.
4. Gate the draft against the bar (external anchor: what actually performs for top
   influencers in the niche). Record the score.

**Output format.**
```
STATUS: DRAFTED | GATED <score> | BLOCKED <reason>
Lane/Format/Words: <lane> | <format> | <n/limit>
Hooks (3): <lines>
Draft: <path>
Bar: <anchor> — <score>
Publish: HELD for Gate-D
```

**Expected output.** A gated, lane-tagged draft bound to its source.

**Done test.** Gate score recorded against the named anchor; source cited in header.

**Failure handling.** Bar not met in 3 rounds -> `STATUS: BLOCKED bar-not-met` with
the weakest dimension named.

**Persistence.** Draft lands in the queue with its gate record.

**Redaction.** No private client detail or credentials in copy.

**Stop / escape hatch.** Lane ambiguity -> ask before drafting; never mix lanes to
cover the guess.
