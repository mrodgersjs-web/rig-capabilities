---
name: "ns-automation-builds"
description: "Build n8n or Make flows that keep working when an API fails, a payload is malformed or volume grows. Nick Saraev method. Use for: n8n workflow; Make scenario; webhook; HTTP module; map this JSON; automation keeps breaking."
tier: main
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Build n8n or Make flows that keep working when an API fails, a payload is malformed or volume grows."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: nick-saraev-os
  stage_doctrine: references/doctrine.md
---

# ns-automation-builds

Build n8n or Make flows that keep working when an API fails, a payload is malformed or volume grows.

**Use when:** n8n workflow; Make scenario; webhook; HTTP module; map this JSON; automation keeps breaking.

## Laws
- Split any flow past roughly 15 to 20 modules into child scenarios joined by webhooks; big flows are hard to debug and time out. CLAIM(QqE6tsHpr3U@0m) CLAIM(QqE6tsHpr3U@5m) CLAIM(QqE6tsHpr3U@11m)
- Give every third-party call an error handler and store incomplete runs so they can be retried. CLAIM(TtvSHo003UI@2m) CLAIM(TtvSHo003UI@3m) CLAIM(5w6Bf5pponE@69m)
- Trigger with webhooks, not polling; polling burns operations and adds delay. CLAIM(lK3veuZAg0c@0m) CLAIM(sGyj2HYZIEQ@3m) CLAIM(Qbi41HouOiI@16m)
- Treat every input and output as an array, even with one item. CLAIM(6b442bN0CyI@49m) CLAIM(2GZ2SNXWK-c@120m) CLAIM(Ksr_H30Oris@9m)
- Check JSON syntax and data types strictly; commas, escaping and string-versus-number errors cause most 400s. CLAIM(JdKC8TOPfJE@24m) CLAIM(6b442bN0CyI@46m) CLAIM(898WpSTxbFU@10m)
- Never paste credentials into the canvas; blueprint exports leak them. CLAIM(JdKC8TOPfJE@16m)
- Build from templates so a new client needs about a fifth custom work. CLAIM(4gGWba-6nOk@12m) CLAIM(fIWUAodAgJw@12m)
- Automate the back office, not the high-value sales conversation where rapport decides the deal. CLAIM(oUpC98ueWn8@5m) CLAIM(oUpC98ueWn8@9m)

## Procedure: Iterative module testing
1. Add the trigger, then a short sleep so test data persists. CLAIM(942qTUO2Nds@7m)
2. Limit list modules to one record while building. CLAIM(942qTUO2Nds@7m)
3. Run each new module alone and inspect its output. CLAIM(Qbi41HouOiI@1m)
4. Cache API outputs in variables so retests do not burn operations. CLAIM(942qTUO2Nds@14m)
5. RIG addition: finish with one end-to-end run on a payload shaped like the client's real data.

## Sub-skills (load one at a time)
- `ns-api-http-integration`: Connect any service through raw HTTP: auth, request shape, JSON parsing, and hidden APIs found in the browser network tab.
- `ns-scenario-architecture`: Design flows as small modular scenarios joined by webhooks, with error handlers, retries and one source of truth.
- `ns-data-transformation`: Clean and reshape scraped or inbound data: regex for simple extraction, a model for messy text, array and JSON reshaping.

## Done-test (fails if any is true)
- Any scenario has more than 20 modules.
- Any third-party call has no handler.
- An exported blueprint contains a key.
- Any trigger polls.
- An injected 4xx or 5xx does not land in the incomplete-executions store.

## Does not fit RIG
- Tuning designs around one vendor's operation pricing as the main goal.
- "Parasite" content systems that copy other creators' top posts; anyone can publish the same output.
- Vendor-specific voice-agent settings as laws; keep them as recipes.

## Deeper doctrine
`references/doctrine.md` holds the full stage doctrine: core laws marked consensus or single-source, procedures, decision rules, failure modes and changed views, all cited. Malformed tags from distillation were removed by the tag validator.

## Where this sits
Layer 2 under `nick-saraev-os`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
