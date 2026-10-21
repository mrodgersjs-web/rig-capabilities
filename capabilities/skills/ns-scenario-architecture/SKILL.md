---
name: "ns-scenario-architecture"
description: "Design flows as small modular scenarios joined by webhooks, with error handlers, retries and one source of truth. Sub-skill of ns-automation-builds (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Design flows as small modular scenarios joined by webhooks, with error handlers, retries and one source of truth."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-automation-builds
---

# ns-scenario-architecture

Design flows as small modular scenarios joined by webhooks, with error handlers, retries and one source of truth.

## Steps
1. Draw the flow and cut it into scenarios under 20 modules.
2. Connect scenarios with webhooks.
3. Add a handler to every external call; store incomplete runs.
4. Use bulk endpoints where they exist.

## Laws
- Large single scenarios are hard to debug and time out; split them. CLAIM(QqE6tsHpr3U@0m) CLAIM(QqE6tsHpr3U@11m)
- Error handlers plus stored incomplete runs make failures recoverable. CLAIM(TtvSHo003UI@2m) CLAIM(5w6Bf5pponE@69m)
- Webhooks between scenarios beat polling. CLAIM(lK3veuZAg0c@0m) CLAIM(sGyj2HYZIEQ@3m)
- Keep one system as the source of truth for each record. CLAIM(898WpSTxbFU@2m) CLAIM(vHJH3TShGks@2m)

## Done-test (fails if any is true)
- Any scenario exceeds 20 modules.
- Any external call lacks a handler.
- "Continue on error" is set without a dead-letter log.

## Where this sits
Layer 3 under `ns-automation-builds`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
