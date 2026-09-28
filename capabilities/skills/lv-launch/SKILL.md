---
name: lv-launch
description: >-
  Take one approved LinkedIn draft from staged to live and amplified: Eden as the only publisher, the posting slot, the golden hour and first 24 hours, save assets, the 2026 algorithm model, and thought-leader ad boosts. Use when a draft has passed the gate and Mike asked to schedule, publish, boost or amplify it. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage (slot and lane call, expansion-window read, comment gate on amplification replies, boost-candidate screen) goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, launch, publish, golden-hour, eden]
outcome: "content-publishing: the approved post is live from Eden at the right slot, amplified in its golden hour with a save asset, and the 24-hour learning is logged"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-launch
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "7"
---

# lv-launch: from approved draft to live and amplified

## JEV-first mandate (read first)

The typed judgments in this stage go to Jev (TypeSafe's System One) through `rig-s1gate` BEFORE any frontier LLM call: which lane and slot the post belongs to, whether a post is still inside its expansion window or has aged past it, whether an amplification comment passes (rubric `comment.linkedin`), whether the staged artifact passes (`post.eden`), and whether a post qualifies as a boost candidate.

- Command: `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
- Rubrics that exist: `post.linkedin` (Lane B), `post.viral`, `post.eden`, `comment.linkedin`, `doctrine.surface`. Where no stored rubric fits, the verdict is DEFERRED to Mike.
- Fail closed: the classifier being down, erroring, or a missing rubric means DEFERRED. Never a guessed verdict, never a pass, never a frontier model's opinion substituted for the judgment.
- An advisory PASS is not permission to publish, schedule, repost, boost or spend; Gate-D applies to every outward step.
- Any claim that "Jev judged X" cites the decision id from `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use when a draft has cleared `lv-gate`, when Mike asks to schedule or publish it, when a post has just gone live and needs its golden hour, when he asks to boost, amplify or repost a live post, or when deciding what a slow first 12 hours mean.

Do not use for writing or fixing the draft (`lv-draft`), for scoring it (`lv-gate`), for comments on other people's posts (`lv-engage`), for taking a proven asset to Reddit, X, newsletters or trade publications (`lv-distribute`), or for analytics reporting beyond the 24-hour learning line (`lv-measure`). A minor's content (Lane C) is never launched from here: it is per-post human approval, always.

## Procedure

1. **Preconditions.** The critique verdict is `ship` and the score is on the record. The lane is named (A, B, client, job search). Mike has approved this exact post in this session after seeing the final text. A blanket "approve everything" does not cover a public post.
2. **Check the Eden connection.** Confirm `eden_*` tools exist in the session inventory. If the server is enabled but no tools are present, report `blocked: eden-not-connected` and stop; do not build a browser workaround. (See `references/eden-publishing.md`.)
3. **Check the slot before staging.** Call `eden_list_schedules` first, or you double-publish a slot. Respect the ramp ceiling in `rig-revenue-publish-ramp`: one level up only after 3-4 clean weeks, never a velocity spike.
4. **Pick the window.** Tue-Thu, 7-9am or 12-1pm in the ICP's timezone (Denver for Mike's lanes); launches Monday to Thursday; evenings are weak. Post when the ICP is awake.
5. **Stage in Eden as a draft.** Drafts are free. Live scheduling or publishing needs Mike's explicit yes for that post. Never auto-schedule: Eden's scheduler is not trusted for delivery, and publishing stays by hand until a test post demonstrably lands.
6. **Read the draft back out of Eden and diff it** against the approved text. A write call is not persistence evidence. Publish only after the diff is clean and Mike says yes for this post.
7. **Golden hour, 60-90 minutes, as a scheduled block** (`references/golden-hour.md`): the save asset first, then in-depth replies to every comment ending in a question, highest-status in-topic comment first. A human holds this hour; an agent stages replies.
8. **First 24 hours.** Do not delete a slow post. Distribution is spiky and late [s6KMjhznXqs]. Read the numbers once at +90 minutes and stop. At 24 hours log one to three learnings in `~/.aside/u/0/skills/user/linkedin-analytics-tracker/SKILL.md`.
9. **Second-wave writes.** One second save asset (a graded answer key) is allowed and is the only write that raises the strongest signal again after publish. An "Add your thoughts" repost is the only action that creates a new distribution event on a live post, and it is a public act: explicit yes first.
10. **Boost screen.** After one to two weeks organic, list ICP-relevant under-delivered posts as boost candidates with a dollar amount; every boost is a Gate-D spend item Mike approves (`references/boosts-and-peaks.md`).
11. **Plan the next peak.** One manufactured peak per month on top of the cadence: a launch, an event, a stunt, or a big data post.

## Quality bar

- The live post text matches the approved text exactly, verified by reading it back, not by the write call.
- Publish time, lane and account are recorded; the signed-in handle was asserted before any outward step.
- The save asset is in the golden hour, on the post itself, with no external link and no engagement bait.
- Every comment got a substantive reply or an explicit reason it did not.
- At +90 min the numbers were read once; the day's learnings (1-3) are logged where the measurement routines read them.
- Any action not taken is named with its reason. No invented metrics, ever.

## Lanes

- **Lane A (personal brand, Eden):** the themed day decides the slot; Birch is Tuesday-only and The Coach appears only from behind or in silhouette. Warm Ted Lasso register. Eden generates the copy and the image; this stage only stages and launches.
- **Lane B (RIG B2B):** evidence-led, named receipts, no mascots and none of Mike's proprietary cast. The moonshot post is the one that gets the peak treatment.
- **Ideawake client lane (Coby's account):** assert the signed-in handle before acting. Nothing launches without Mike's explicit client approval, per post. Never borrow Mike's voice or the RIG voice.
- **Job-search lane:** recruiter-visible activity only; profile-affecting moves are exact before/after values Mike approves. No boost spend.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| eden-mcp | tool | `~/.aside/u/0/skills/user/eden-mcp/SKILL.md` | the Eden Canvas MCP server for staging, scheduling state, auto-DM rules and analytics; the only publisher surface |
| eden-linkedin-platform | tool | `~/.hermes/skills/social-media/eden-linkedin-platform/SKILL.md` | Eden LinkedIn ops by name: `eden_list_scheduled_posts`, `eden_draft_post`, `eden_list_analytics_posts`; hard API facts (no comment tools, no scheduled-post delete) |
| step-5-publish | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-5-publish.md` | the executor/verifier pair for the publish step when running the linkedin-growth-os process harness |
| step-6-amplify | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-6-amplify.md` | the executor/verifier pair for the amplify step; owns its own sub-agent list and the comment-verification rule |
| rig-revenue-publish-ramp | runner | `~/Developer/rig-capabilities/capabilities/skills/rig-revenue-publish-ramp/SKILL.md` | every launch sets its cadence ceiling here: 1 to 5 to 10 items per week, one level up only after 3-4 clean weeks; a runner consuming this stage must ask it for the ceiling before it schedules |

## Sub-skills

| file | covers |
|---|---|
| `references/eden-publishing.md` | Eden as the only publisher, tool routing, slot conflict, read-back diff, the not-connected stop |
| `references/golden-hour.md` | the 60-90 minute block, the four writes, signal weights, the first 24 hours, the repost |
| `references/save-assets.md` | the reference comment, what qualifies as a save, the second asset, what is banned |
| `references/algorithm-model.md` | the 2026 feed model: interest graph, spiky and late, shelf life, rewards, diagnosis order |
| `references/boosts-and-peaks.md` | thought-leader ad boosts as Gate-D spend, manufactured peaks, the launch echo |
| `references/launch-safety-and-measurement.md` | caps, stop signals, verification, the delta series, the report format |

## Hard rules carried forward

- Eden is the only publisher of record; Postiz is retired and is never routed to. [lg-publish, eden-mcp]
- Never auto-schedule a post; Eden's scheduler is not trusted for delivery and publishing stays by hand until a test post lands. [lg-publish]
- Live scheduling or publishing needs Mike's explicit yes for that post, in this session, with the final text seen; a blanket approval does not substitute. [lg-publish, step-5-publish]
- Lane C content is never auto-scheduled and fails unconditionally without per-post human approval. [step-5-publish, lg-publish]
- Check `eden_list_schedules` before creating any slot; double-publishing a slot is a real failure mode. [step-5-publish, lg-publish]
- Read the draft back out of Eden and diff against the approved text; a write call is not persistence evidence. [lg-publish, step-5-publish]
- Report `blocked: eden-not-connected` rather than inventing a workaround when the MCP inventory is empty. [lg-publish, step-5-publish]
- Never fabricate engagement: no alt accounts, no pods, no bought signals, no coordinated bursts; the feed re-classifies the real audience as bots. [lg-amplify, linkedin-post-launch]
- Ceilings block rather than warn; a request for more volume does not lift them. [lg-amplify, step-6-amplify]
- Verify each posted comment by hard reload plus the string present exactly once; never `document.body.innerText`, which includes unsent composer drafts and once confirmed 13 of 16 replies that had never posted. [lg-amplify, step-6-amplify]
- Comments on other people's posts are positive-only: validate the point, add one original insight, link his own post only as a complement; no pushback and no "actually". [lg-amplify, linkedin-post-launch]
- Never fire a large burst of inbound links at one post; 20-plus link-bearing comments from one account within an hour can suppress the very post it promotes. [linkedin-post-launch]
- Do not delete a slow post in the first hours; distribution is spiky and can arrive 12 hours late. [algorithm-2026, distribution-and-algorithm]
- Do not add a second post the same day; the second post of a day is heavily cannibalised. [golden-hour, algorithm-2026]
- Every paid boost is a Gate-D spend item with a dollar amount Mike approves; let a post run organically one to two weeks before boosting. [distribution-and-algorithm]
- Never claim "viral" is achievable on demand; report impressions and comment counts as evidence. [linkedin-post-launch]
- Assert the signed-in handle before any outward action; this browser holds Mike's and a client's session at once. [step-6-amplify, lg-publish]
- A repost of a live post is a public act and gets an explicit yes first. [linkedin-post-launch]
- One before-and-after number is a story, not a rate; report the delta series and say when a rise is correlation. [linkedin-post-launch]

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-launch` is GREEN only when the frontmatter names the stage and carries the mandate, the body opens with the JEV-first section, at least three 400-byte sub-skills sit beside `ledger.md`, all 12 stage-map rows have a ledger row with a named action, every backticked path resolves, and no third-party 12-word run was copied.
