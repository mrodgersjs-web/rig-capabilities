---
name: rig-communications-wounds
description: >-
  Wound/Euphoria library + communications doctrine exported from Mike's Recall
  corpus — the emotional engine behind every RIG surface.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [wounds,voice,communications,writing,gates]
outcome: "content-publishing: every emotional surface draws on the named wound, depth layer, and euphoria flip instead of generic pathos"
done_when:
  - file:capabilities/skills/rig-communications-wounds/wounds/core-wounds.md
  - file:capabilities/skills/rig-communications-wounds/euphoria/euphoria-protocol.md
  - grep:capabilities/skills/rig-communications-wounds/wounds/core-wounds.md:W3
  - cmd:python3 -c "import pathlib as p; d=p.Path('capabilities/skills/rig-communications-wounds'); fs=['wounds/core-wounds.md','wounds/depth-layers.md','euphoria/euphoria-protocol.md','doctrine/master-composition.md','doctrine/master-comms-v1.md','sequences/wmaqo.md','gates/email-reply-scoring.md','surfaces/songs/suno-architecture.md','voice/craft-archetypes.md','voice/sigma-targets.md','doctrine/email-linkedin-v1.md','doctrine/linkedin-v2.md','voice/genius-imperfection.md','behavior/wound-classifier.md']; missing=[f for f in fs if not (d/f).exists()]; assert not missing, missing"; test $? -eq 0
quality_floor: 0.6
---

# RIG Communications Wounds

The emotional IP layer: wound taxonomy, euphoria flips, depth layers, and the
per-surface communications doctrine, exported verbatim from Mike's Recall
corpus (app.recall.it) on 2026-09-06 via `jake_recall`. Each file carries its
card id in a provenance line. Doctrine text is canonical as exported — never
rewrite a card body; corrections go upstream in Recall first (see delta-sync).

## File map — when each file applies

| File | Use it when |
|---|---|
| `wounds/core-wounds.md` | any emotional surface — wound definitions (W3–W6 exported fragments + W8 flip reference), euphoria flips E2/E7/E8, buying-decision depth Layers 1–3. **Card source is truncated in Recall** (flagged in-file). |
| `wounds/depth-layers.md` | calibrating 0σ→10σ deviation scale per criterion (this card is the Deviation Scale Doctrine; the L1–L5 buyer-depth model lives in core-wounds.md's Layers section). |
| `euphoria/euphoria-protocol.md` | the positive pole: E1/E5/E6 euphoria triggers + Emotional Symphony scoring. |
| `sequences/wmaqo.md` | drafting any email: Wound→Mirror→Autonomy→Qualification→Open Loop sequence. |
| `gates/email-reply-scoring.md` | scoring an inbound email reply (Wound/Autonomy/Mirror algorithm). |
| `surfaces/songs/suno-architecture.md` | songwriting surfaces (SUNO Billboard Engine, 3σ–10σ). |
| `doctrine/master-comms-v1.md` | unified email+LinkedIn master protocol (LinkedIn primary). |
| `doctrine/linkedin-v2.md` | LinkedIn Protocol V2: 8σ depth-score + prediction swarm. |
| `doctrine/master-composition.md` | full composition scoring: 20 criteria, 6 formulas. |
| `doctrine/email-linkedin-v1.md` | deviation-calibrated email/LinkedIn doctrine. |
| `voice/craft-archetypes.md` | voice: -20→+20 communications deviation engine archetypes. |
| `voice/sigma-targets.md` | per-domain -10→+10 deviation target registry. |
| `voice/genius-imperfection.md` | deliberate imperfection as deviation signal. |
| `behavior/wound-classifier.md` | classifying an audience/inbound message → wound ranking + layer + reply strategy (spec; executable in v6). |

Routing quick-reference: **email** → sequences/wmaqo.md + gates/email-reply-scoring.md;
**songs** → surfaces/songs/suno-architecture.md; **LinkedIn** →
doctrine/master-comms-v1.md + doctrine/linkedin-v2.md; **any emotional surface** →
wounds/core-wounds.md + euphoria/euphoria-protocol.md.

## Export honesty

W1, W2, W7 wound definitions are NOT present in the exported card set (the
core-wounds card exports W3–W6 fragments and references W8 via its flip).
Do not invent W1/W2/W7 text — recover from Recall if a card surfaces later.

## Weekly Recall delta-sync (C4)

Procedure (manual until v15 cron scheduling):
1. Re-run the export for all 13 card ids (`jake_recall get <id>` via
   `~/.jake/abilities/recall/jake_recall`, full body — the MCP wrapper truncates at 12k).
2. Diff each output against the committed file (H1+provenance header stays; body compared).
3. On change: update the file, bump the export date in its provenance line, and record
   card-id + changed sections in the commit message. No change → no commit.
4. New wound doctrine in Recall: add to this skill only via the same provenance rule
   (card id in every file).
