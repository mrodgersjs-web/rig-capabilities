---
id: rig-hq-sub-j10-1-a-dictated-name-matches-nothing
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: daphne-avis
parent: rig-hq-prompt-daphne-avis
task: Interrupt sub-prompt (J10): a dictated name matches nothing — test homophones before filing
triggers: unknown name in dictation, name matches nothing, homophone
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J10 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (section 5)
provenance: first-party RIG design | Reese J10 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a dictated name matches nothing

**Trigger.** A name in a dictation resolves to no known entity.

**Typed inputs.** `raw_name`, `context_sentence`, `known_entities` (contacts, tools,
models, lanes).

**Steps.**
1. Run the homophone table (PROMPT-DESIGN.md §6) against the raw name: Kobe=Coby,
   Quinn38=Qwen 3.8, gemini 3.8 flash=Qwen 3.8 Flash on Blackwell, memo v 2.6=MiMo
   v2.6, chat GBT=ChatGPT, open bot rig=OpenRouter, workflowz=workflows,
   traject=trajectory/Traject, Pewakie Pirate=Pewaukee Pirates, All My Pie=all my
   PAI, soul id=Sol, AV IS=Avis, adn/buidl/untip = and/build/until.
2. Check the non-homophone list before "correcting" anything: Blackwell, GrokBot,
   OpenBot, MiMo, Jev, ApplyPilot, Birch, Hudl, marimo, Prefect are real names.
3. If still unknown: file the note raw and ask Mike one question. Never invent an
   entity.

**Output format.**
```
STATUS: RESOLVED <name> -> <entity> (via homophone table) | ASKING
Raw: "<name>"
Tested: <candidates tried>
Ask: <one question or none>
```

**Expected output.** Corrected filing or one honest question.

**Done test.** The filing names which table entry resolved it, or the raw note is
preserved with the question asked.

**Failure handling.** Never file a guessed entity as fact.

**Persistence.** Resolution recorded so the same homophone resolves faster next time.

**Redaction.** n/a.

**Stop / escape hatch.** One question is cheaper than a wrong filing.
