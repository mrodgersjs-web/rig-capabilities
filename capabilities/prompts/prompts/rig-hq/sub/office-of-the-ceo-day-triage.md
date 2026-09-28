---
id: rig-hq-sub-j1-day-triage
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: prime-jake-pai
parent: rig-hq-prompt-prime-jake-pai
task: Recurring sub-prompt (J1): turn the morning noise into the short list that actually needs Mike
triggers: day triage, what do we accomplish today, what needs me, top 3 today
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J1), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Day triage (J1 recurring)

**Trigger.** Run at the start of any "what needs me / what do we accomplish today"
ask, or at the morning cycle.

**Typed inputs.** `today` (date), `sources` (queue, decision ledger, status files —
exact paths), `max_items` (default 3).

**Steps.**
1. Read only the named sources; unread items are listed as unread, never guessed.
2. Classify each item: needs Mike / needs an agent / parked. JEV-first for the typed
   classification; DEFERRED when the classifier is down.
3. Rank "needs Mike" by what unblocks the most downstream work; keep the top
   `max_items`, park the rest explicitly.
4. For each top item, state the decision asked and a recommendation with its bar.

**Output format.**
```
STATUS: TRIAGED
Needs Mike (max 3): <item> — decision: <one line> — rec: <one line>
Parked (with reason): <items>
Delegated: <item -> agent>
Receipt: <triage file path>
```

**Expected output.** A list where every item either needs Mike in one line or has a
named owner.

**Done test.** The triage file exists and the "needs Mike" count is <= max_items.

**Failure handling.** Missing source -> `STATUS: BLOCKED <source path>`. Bar not met
after 3 rounds -> escalate. Never pad the list to look complete.

**Persistence.** Write the triage file to the day folder; the next triage reads it first.

**Redaction.** Keychain item names only; never values.

**Stop / escape hatch.** If two items are genuinely equal priority, show both and ask
— do not invent a tiebreak.
