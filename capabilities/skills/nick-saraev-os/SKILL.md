---
name: "nick-saraev-os"
description: "Nick Saraev doctrine (349 cited videos): AI automation agency work, agentic workflows with Claude Code/Codex, n8n/Make builds, lead gen and cold email, offers, pricing, sales, scaling, AI career and content. Routes to one stage skill. Use for 'how would Nick Saraev do this', AI agency playbook, Saraev method."
tier: meta
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Every Nick Saraev-method request lands in exactly one stage skill, carrying cited doctrine and a done-test that can fail"
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
---

# nick-saraev-os (routes only)

Front door for Nick Saraev's operating method, distilled from every upload on @nicksaraev (330 videos, 19 shorts, 1 stream, about 255 hours; 349 transcripts, 1 has captions disabled). Built 2026-10-21 through a Recall Chat build card (see metadata). This skill routes; it does no work itself.

## Route (first match wins)

| Skill | Use it to | Typical asks |
|---|---|---|
| `ns-agentic-workflows` | Turn a business SOP into an agent built in three layers (directive, orchestration, execution) that a separate checker can verify. | build an agent for this, turn this SOP into an agent, directive / agents.md, sub-agents |
| `ns-automation-builds` | Build n8n or Make flows that keep working when an API fails, a payload is malformed or volume grows. | n8n workflow, Make scenario, webhook, HTTP module |
| `ns-lead-gen-outbound` | Build a list of verified contacts keyed by company domain and draft personalized outreach that sends only after approval. | scrape leads, find emails, enrich this list, cold email campaign |
| `ns-offer-and-sales` | Turn a qualified conversation into a priced, scoped first project that is built to become a retainer. | price this, write the proposal, structure the offer, prep the sales call |
| `ns-agency-scale` | Find the one constraint limiting throughput, widen it, measure again, and productize whatever repeats. | we are stuck, where is the bottleneck, should I hire, productize this |
| `ns-ai-career-and-content` | Keep value rooted in business judgment as AI absorbs execution, and run content as a governed authority engine. | what should I learn, is this model release worth testing, content pipeline, repurpose this video |

Tie-break between a canvas flow and an agent: repeatable deterministic work goes to scripts or flows (`ns-automation-builds`), judgment and routing go to an agent (`ns-agentic-workflows`).
Boundary between outbound and sales: before a conversation exists it is `ns-lead-gen-outbound`; after, it is `ns-offer-and-sales`.

## How to use
1. Pick one stage skill from the table. Load only it, then only the sub-skill it names.
2. Cite laws as written (CLAIM tags). Creator revenue and rate figures are his claims, not facts.
3. Respect each skill's "does not fit RIG" list: Nick sells cheap automation volume; RIG sells governed builds for operators.

## How he changed his mind (date order)
Make, then n8n (self-hosting, cost at scale, curl import), then agentic workflows in Claude Code and Codex with deterministic scripts. Treat it as a ladder: Make for simple linear flows, n8n for volume or custom code, scripts under an agent for anything orchestrated. See each stage doctrine's "Changed views".

## Done-test (can fail)
`python3 capabilities/skills/nick-saraev-os/scripts/check_family.py` must exit 0: all 26 skills present, every CLAIM tag resolves to a real video id inside its length, every skill has a done-test. `--plant` must exit 0 by proving a planted bad tag is caught.

## References
- `references/sources.json`: every video id, title, minutes, stage.
- `references/build-card.md`: the Recall Chat build card (both halves) this family follows.
- Stage doctrines live in each stage skill's `references/doctrine.md`.
