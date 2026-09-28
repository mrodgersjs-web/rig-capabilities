---
id: rig-hq-sub-j10-voice-capture
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: daphne-avis
parent: rig-hq-prompt-daphne-avis
task: Recurring sub-prompt (J10): file and route one dictated thought without losing it
triggers: file this, note this, capture this thought, route this note
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J10), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Voice capture (J10 recurring)

**Trigger.** A dictated thought arrives away from the keyboard ("file it", "route
it", "remember this").

**Typed inputs.** `raw_text` (the dictation verbatim), `captured_at` (timestamp),
`hint_department` (optional).

**Steps.**
1. Keep the raw dictation verbatim in the note header — never clean it away.
2. Homophone-test every name before filing (PROMPT-DESIGN.md §6); unknown after the
   test is recorded as unknown, not invented.
3. Classify the note's department and action type (decision, request, memory,
   content idea); DEFERRED to Mike if ambiguous.
4. File the note and route it to the owning department with the raw text attached.

**Output format.**
```
STATUS: FILED <note path> | BLOCKED <reason>
Raw: "<verbatim>"
Read as: <normalized interpretation>
Routed to: <department/agent>
Memory write: <receipt or none>
```

**Expected output.** One filed note with its raw text preserved and one routing line.

**Done test.** The note file exists with raw text intact and a named destination.

**Failure handling.** Ambiguous meaning after homophone test -> file it raw with
`STATUS: BLOCKED ambiguous:<word>` and ask one question. Never drop a thought.

**Persistence.** Note lands in the inbox folder; memory write goes through the
governed Memory OS front door and is verified.

**Redaction.** Strip credentials from the note; never echo a secret back.

**Stop / escape hatch.** One clarifying question is allowed and preferred over a
guessed filing.
