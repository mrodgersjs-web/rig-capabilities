---
name: lv-outreach
description: >-
  Turn LinkedIn attention into pipeline: audience design and connection requests, lead sourcing
  and ICP qualification, warm-signal conversion, DM copy and sequences, reply ops, campaign
  operations, and the monetization handoff. Use when staging any LinkedIn DM, connection request,
  follow-up or campaign, or asking who to message and what to say. JEV-FIRST MANDATE, findable at
  task start: every typed judgment in this stage (ICP fit verdict, hot-signal timing, reply
  classification, DM-model pick, DM quality pass, batch send readiness) goes to rig-s1gate (Jev)
  BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child
  of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, outreach, dm, pipeline]
outcome: "content-publishing: every outreach batch leaves as a qualified list plus staged, evidence-backed, unsent drafts and a Gate-D request, never a send"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-outreach
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "35"
---

# lv-outreach: attention to pipeline

## JEV-first mandate (read first)

Typed judgments here: ICP fit, hot-signal timing, DM-model pick, draft pass, reply classification,
batch send readiness. Route each to Jev before any frontier LLM call:
`rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
Stored rubrics: `post.linkedin` (Lane B), `post.viral`, `post.eden`, `comment.linkedin`,
`doctrine.surface`; a pass needs every required noul and confidence above 0.9. Where no stored
rubric fits (DM copy, fit cards, reply calls) the verdict is DEFERRED to Mike. Fail closed:
classifier down or rubric missing means DEFERRED, never a guess, never a pass; an advisory PASS is
not permission to send. Cite the decision id from `~/.rig/s1gate/decisions.db`.
## When to use / when not to

Use for: who to connect with and what the request says; sourcing and qualifying leads; warm
signals (profile viewers, engagers, comment-to-DM, Loom audits); DM and follow-up copy; reply
handling and inbox triage; campaign runs; the offer, lead magnet and call-prep handoff. Not for:
posts (lv-draft), comments on others' posts (lv-engage), profile edits (lv-profile), measurement
(lv-measure), or the minor's lane (no outreach ever).

## Procedure

1. **Lane and identity.** Assert the signed-in handle before any outward act; halt on mismatch
   (this browser can hold Mike's and a client's LinkedIn).
2. **Model.** A (fast triage, 3-touch, ABCD) default; B (trust thread, 5-message opener, 10-15
   accounts/month) for small lists and large deals; C (chase) only behind a declared
   `chase_sequence_override`.
3. **Source.** Existing 1st-degree network, content inbound, Sales Navigator (lists of 100+),
   cold-SalesNav with video on accept; daily warm signals (profile viewers, engagers, commenters).
   Refused sources stay refused.
4. **Qualify.** One ICP fit card per candidate (observed artefact, hot-signal timing, yes/no
   verdict); enforce the list-quality bar and `icp_ceiling`.
5. **Bridge.** Anchor each message in one current public signal (signal, connection, useful
   thing); three specific observations of this person, or no draft.
6. **Draft.** Model opener recipe, line rules, ABCD close (one letter set), medium (text, voice
   note with permission ask, opted-in video); second-agent review then quality score; staged and
   stamped UNSENT.
7. **Sequence.** Spacing, value-add follow-ups, no-reply ladder, exit conditions; default ceiling
   3 messages per prospect.
8. **Gate-D the batch.** One request per batch naming recipients and exact text; Mike's yes arms
   it; a blanket "approve everything" clears nothing; the engine sends live only when armed.
9. **Send and operate.** Pacing 60-120s, fresh browser per DM for batches, proof sealed per
   session; replies forward to Mike, never auto-answered.
10. **Convert.** Reply routing and probe ladder, pre-call nurture, monetization handoff (offer,
    brief, terms); pricing and terms are Gate-D for Mike.
11. **Measure.** Reply rate per batch and model from RIG's own ledger; one variable set at a time;
    the A/B/C/D distribution feeds sourcing and offer first, not copy.

## Quality bar

- Every batch name carries a fit card with an artefact and a `fit` or `no_fit` verdict.
- Every draft cites its observations; no model-memory claims, merge tags, cold-DM links, banned
  openers, or creator-verbatim scripts; one question and one cheap ask per message; under 70 words.
- Sequence plan present: touches, gaps, value shape per follow-up, exit conditions, no-reply route.
- Second-agent review recorded; quality scorer 80+ on the chosen variant; variant diversity.
- Gate-D request names recipients and exact text; identity asserted; caps checked (strictest
  per-day: 8 connects, 15 DMs; 3 messages per prospect).
- No creator reply-rate claims; no invented numbers, quotes, clients or results.

## Lanes

- **B (RIG B2B):** Model A default; evidence-led, named receipts, jargon out; compare-notes
  template (competitors) capped 5/day.
- **A (personal brand):** warm register in DMs as in posts; same caps and Gate-D; no Birch or
  Coach material in outreach copy.
- **Ideawake (Coby's account):** assert the handle; nothing fires without Mike's explicit client
  approval; never borrow Mike's voice for a client draft.
- **Job search:** hiring-manager outreach runs through the same gates; profile edits as exact
  before/after values, applied only after Mike approves.
- **C (minor):** out of scope entirely; no prospecting, drafting, connecting, DMs or monetization
  at any approval level.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| linkedin-automation | tool | `~/.hermes/skills/linkedin-automation/SKILL.md` | browser sends/reads beyond CDP |
| linkedin-dm-batch-sender | tool | `~/.hermes/skills/linkedin-dm-batch-sender/SKILL.md` | send an approved DM batch |
| timyakubson-linkedin-sales-navigator | tool | `~/.pi/skills/timyakubson-linkedin-sales-navigator/SKILL.md` | extract SalesNav leads (lists of 100+) |
| linkedin-connection-strategist | tool | `~/Developer/rig-linkedin-studio-luca/.claude/agents/linkedin-connection-strategist.md` | connection copy/targeting; drafts only |
| linkedin-deal-pipeline-manager | tool | `~/Developer/rig-linkedin-studio-luca/.claude/agents/linkedin-deal-pipeline-manager.md` | pipeline health, next actions |
| linkedin-social-seller | tool | `~/Developer/rig-linkedin-studio-luca/.claude/agents/linkedin-social-seller.md` | Wound, Mirror, Autonomy, Qualify, Open-Loop sequence + reply bank (drafts) |
| step-9-qualify | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-9-qualify.md` | qualify-stage agent |
| step-10-convert | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-10-convert.md` | convert-stage agent (owns dm-scribe) |
| step-11-monetize | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-11-monetize.md` | monetize-stage agent |
| call-briefer | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/call-briefer.md` | brief a booked call |
| homework-researcher | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/homework-researcher.md` | produce the brief dm-scribe reads |
| intent-radar | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/intent-radar.md` | recurring intent watch |
| lead-sourcer | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/lead-sourcer.md` | candidate lists per channel |
| sequence-tracker | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/sequence-tracker.md` | touches, gaps, pause state |
| linkedin-follower-outreach@eden | tool | Eden skill linkedin-follower-outreach (Eden Settings > Skills) | run the loop from Eden |
| /linkedin-outreach | runner | `~/.hermes/commands/linkedin-outreach.md` | engine overview/manual run |
| /outreach-arm | runner | `~/.hermes/commands/outreach-arm.md` | Gate-D arming (watched test, typed approval) |
| /outreach-daily | runner | `~/.hermes/commands/outreach-daily.md` | daily dry-run batch + proof |
| /outreach-replies | runner | `~/.hermes/commands/outreach-replies.md` | detect replies, forward, pause nudges |
| /outreach-send | runner | `~/.hermes/commands/outreach-send.md` | live send loop (armed only) |
| /outreach-status | runner | `~/.hermes/commands/outreach-status.md` | read-only queue/proof/funnel/arm state |
| /linkedin-machine | runner | `~/.hermes/commands/linkedin-machine.md` | whole-operation loop; supplies its outreach pieces |
| conference-outreach-playbook | runner | `~/.hermes/skills/conference-outreach-playbook/SKILL.md` | attendee-list-to-meetings campaign |
| linkedin-event-engagement | runner | `/Users/rig128gb/.aside/u/0/skills/user/linkedin-event-engagement/SKILL.md` | conference surge (T-21, T-5, live, follow-up) |
| follower-outreach | runner | `~/Developer/rig-gtm-studio-v2/harnesses/follower-outreach.yaml` | goal harness for the daily run |

## Sub-skills

| file | covers |
|---|---|
| `references/audience-and-connections.md` | audience design, blank vs noted requests, caps, warm routes, draft contract |
| `references/sourcing-and-qualification.md` | fit card, hot signals, sourcing with/without SalesNav, relevance bridge |
| `references/dm-copy-and-openers.md` | three DM models, line rules, ABCD close, voice and video |
| `references/sequences-and-followup.md` | spacing, value-add follow-ups, reply routing, pre-call nurture |
| `references/campaigns-and-outreach-ops.md` | Dykema receipts, Darius ops, DM corpus, follower engine |
| `references/monetize-and-conversion.md` | offers, quiz funnels, owned audience, call prep, terms, client engine |

## Hard rules carried forward

- Gate-D on every send (DMs, connection batches, follow-ups): drafts free; per-batch yes from Mike
  naming recipients and exact text; a blanket "approve everything" clears nothing;
  build-approval is not send-approval. [lg-convert]
- Assert the signed-in handle before any outward action; halt on mismatch. [lg-client-engine]
- Engine dry-run by default; live only with env flag + single-day armed token + watched test +
  typed approval. The bot never auto-answers a prospect (replies forward, nudges pause). Never
  claim done without a sealed proof. [linkedin-follower-outreach]
- Blank connection note by default; a note only under `connect_note_policy` with a stated reason;
  never a note to someone you have not met. Connections: about 20/weekday, ~100/week platform
  ceiling [outbound-and-pipeline]; stricter 8/day governs [darius-linkedin-outreach-agent].
  [dm-sequences]
- DMs: 25/day ceiling [dm-sequences]; stricter 15/day governs [darius-linkedin-outreach-agent];
  the engine's 45/day goal stays dry-run until reconciled [linkedin-follower-outreach].
- Hard cap 3 messages per prospect; the 9-step chase is a gated override (`chase_reason`,
  `cross_platform: ["linkedin"]`, `pattern_interrupt_only: true`, `followup_step_max` 4-9). Never
  follow up after any reply; a D or "stop" terminates on every channel, permanently. [lg-convert]
- Never a link in a cold DM (no calendly, loom, PDF); links only to a booked prospect in pre-call
  nurture. One question per DM, ending on a question, permission CTA or closed framing. Never a
  booking link or demo ask in touch 1 or 2. [dm-copy-craft]
- Never the banned openers ("I came across your profile", "I hope this finds you well", "I would
  love to connect", "explore synergies", "just 10 minutes", unfilled merge tags); never
  creator-verbatim scripts. [dm-copy-craft]
- Never invent numbers, quotes, clients or results; creator reply-rate claims (24%, 85%, 10x,
  70-80%) never appear in RIG or client copy; revenue from RIG's own ledger. [dm-sequences]
- Never AI-written comments; comments on other people's posts are positive only. [viral-core]
- Never reuse a browser session past 5 consecutive DMs; never the compose page for batches over
  5; never one send-button selector; never skip the Escape-dismiss after typeahead. Never a DM
  over 70 words (3-4 sentences, no jargon, research-backed hook, one clear ask). Never skip the
  second-agent review. Pacing 60-120s between sends; never stale cookies (li_at about 24h); a ban
  signal auto-disarms and halts. [dykema-dm-campaign-learnings]
- Never message Oracle / Oracle Health / Cerner employees (F1) or anyone on the skip list (F2);
  90-day sent-log dedup (F3); compare-notes template capped 5/day. [linkedin-follower-outreach]
- Sourcing caps: profile loads past about 60 per session degrade; comments cap 30/day; re-probe
  any LinkedIn platform limit before quoting it. Never the refused sources: third-party follower
  scraping, BuiltWith plus Clay scraping, Growth Machine with voice cloning, cross-platform
  follower scraping. [sourcing-channels]
- Model C's "absence of a stop reply is consent" is refused; a stop reply terminates immediately.
  [opener-recipes]
- Voice-note scripts are generated; the audio is recorded by Mike. Never synthetic voice to a cold
  contact. [voice-video-dms]
- Never schedule a follow-up against a D; unclassifiable replies go to Mike, never a queue.
  [no-reply-ladder]
- Pricing, contract terms, anything committing money or liability is Gate-D for Mike; the terms
  file is not legal advice. [lg-monetize]
- Lane C (the minor) does no outreach, conversion or monetization at any approval level.
  [lg-convert]

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-outreach`
is GREEN only when the frontmatter matches the folder and carries the mandate, references/ holds
3+ sub-skills of 400+ bytes plus ledger.md, the ledger names an action for all 60 stage-map rows
(35 merge, 15 tool, 10 runner), every backticked path resolves, and no sub-skill shares a 12-word
run with a third-party merge source.
