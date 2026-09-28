---
name: lv-engage
description: >-
  Comments and replies on LinkedIn: positive-only comments on other people's posts, reply handling and pinned first comments on Mike's own posts, target lists, daily cadence, borrowed attention, and the commenting executors used as tools. Use for "comment on posts", "reply to my comments", "pinned comment", "engagement sweep", "borrowed attention". JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage (comment gate, thread selection, target qualification, comment-type routing, throttle call) goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, comments, replies, engagement, cadence]
outcome: "content-publishing: every comment and reply leaves this stage human-written, positive, insight-carrying, inside the sweep caps, and staged or sent only under the lane's approval rule"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-engage
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "5"
---

# lv-engage (comments, replies, engagement)

## JEV-first mandate (read first)

The typed judgments this stage forces: does a drafted comment or reply pass the comment gate, does a target thread qualify for the sweep, which comment type (positive / negative / question / spam / prospect) routes an inbound reply, and is the surface throttled. Each goes to Jev before any frontier LLM call.

- Command: `rig-s1gate check comment.linkedin --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. Stored rubrics: `comment.linkedin` for comments and replies; `post.linkedin` (Lane B), `post.viral`, `post.eden` for anything that becomes a post; `doctrine.surface` for doctrine text. Thread-selection and throttle calls have no stored rubric: their verdict is DEFERRED to Mike.
- Fail closed: classifier down, erroring, or rubric missing means DEFERRED. DEFERRED is never a pass, never a local guess, never a frontier substitute. The item stays a draft.
- An advisory PASS is not permission to post. Gate-D still applies to anything outward.

## When to use / when not to

Use for: commenting on other people's posts, handling comments and replies on Mike's own posts, writing a pinned first comment, building or refreshing target lists, running a daily engagement sweep, and driving borrowed attention. Not for: drafting posts (lv-draft), DMs or outreach (lv-outreach), profile edits (lv-profile), measurement (lv-measure), or anything about a minor (STOP, route to the Jacob lane rules).

## Procedure

1. Fix the lane first (router `~/Developer/rig-capabilities/capabilities/skills/linkedin-viral/SKILL.md` Step 0). The lane decides the account, the voice, and whether anything may fire at all.
2. Assert the signed-in handle before any outward action. On mismatch, halt; never switch accounts to "get in" [profile-probe].
3. Pick targets (`references/comment-targets-cadence.md`): past-week threads, floor of 5 reactions or 3 comments, author in the ICP orbit and active, 14-day dedupe [borrowed-attention, engagement-comment-led].
4. Write the comment as a mini-post: validate the author's specific point by name, add exactly one insight they did not make, optionally point to Mike's related post as a complement and only under the link caps [engagement-comment-led, comment-ambassador]. Human-written only.
5. Gate each comment through Jev (`comment.linkedin`). Banned openers and generic praise fail the gate [alfred-comment-engagement].
6. Fire or stage per the lane: comment-engine runs PREP then FIRE only after human approval; the personal-brand lane stages and never publishes; the Ideawake lane needs Mike's explicit client approval and Coby's voice [comment-engine, personal-brand-lane].
7. Handle inbound on Mike's own posts inside the SLA: scan the extended window, route by comment type, reply with the Loop-Back shape (specific appreciation, one sourced value point, one open question) [alfred-comment-engagement]. Details in `references/reply-handling.md`.
8. Optionally stage a pinned first comment (`references/pinned-first-comment.md`) or run the sweep as borrowed attention (`references/comment-targets-cadence.md`).
9. Log honestly: comments attempted, posted, link-bearing, throttles hit. Zero is a reportable number [alfred-comment-engagement].

## Quality bar

- Positive-only on other people's posts: validate, add one real insight, never correct, pitch, or one-up [comment-ambassador, viral-core].
- Each comment engages one specific detail from the post (a number, a named system, a decision) and is 1-3 sentences, under 420 characters for the ambassador style; varied length 2-6 sentences for sweep comments so the batch is not a detection vector [comment-ambassador, borrowed-attention].
- Every reply ends with a question that needs the other person's expertise; yes/no questions fail [engagement-comment-led, alfred-comment-engagement].
- No AI-written comments anywhere. No engagement pods. No fabricated numbers, clients, or quotes [viral-core].
- Inside the sweep caps in `references/comment-targets-cadence.md`; a cap hit is a stop, not a rounding error.
- Jev verdict recorded (or DEFERRED with the item still staged) before anything leaves this stage.

## Lanes

- **Lane A (personal brand, Eden):** comments are staged for Mike and never published by an agent; the lane admits OpenBot staging and nothing more [personal-brand-lane, personal-brand-lane@eden]. Warm register is for Mike's own posts' replies, not for outbound comments.
- **Lane B (RIG B2B):** evidence-led outbound comments; receipts over adjectives; no mascots or proprietary cast anywhere [viral-core].
- **Ideawake client lane:** the browser may be signed in as Coby Skonord. Assert the handle, write in Coby's voice, never Mike's, and nothing fires without Mike's explicit client approval [personal-brand-lane, viral-core].
- **Job-search lane:** comments are part of the 20-10-5 routine and exist to look credible to recruiters and hiring managers who check activity; see lv-profile's `references/job-search-profile.md` for the routine and keep comments positive and generic-safe there too [lucy-skills/linkedin-activity].
- **Minor (Jacob):** STOP. Out of scope for this stage [viral-core].

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| rig-linkedin-desktop | tool | `~/Developer/rig-capabilities/capabilities/agents/rig-linkedin-desktop.md` | comment and relationship suggestions; human writes |
| /comment-engine | runner | `~/.hermes/commands/comment-engine.md` | PREP candidates, human approves, then FIRE |
| /ralph | tool | `~/.hermes/commands/ralph.md` | load the Ralph Prime Agent skill for a task |
| linkedin-site-mechanics | tool | `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md` | before any browser action: throttles and comment/reply mechanics |
| patchright-linkedin-proofer | tool | `~/.hermes/skills/.archive/patchright-linkedin-proofer/SKILL.md` | 4-phase safe run with per-line APPROVE before send |
| ralph | tool | `~/.hermes/skills/ralph/SKILL.md` | self-referential loop with architect verification |
| li-distribution | runner | `~/.hermes/skills/rig-linkedin-virality/skills/li-distribution/SKILL.md` | daily P2 cycle: target harvest, gated firing, reply sweep |
| li-distribution-runner | runner | `~/.hermes/agents/li-distribution-runner.json` | scheduled definition loading li-distribution |
| commenter | tool | `~/.claude/agents/commenter.md` | scrape, qualify, draft, approval card, reload-verify |
| prime-ralph | runner | `~/.omp/agent/agents/prime-ralph.json` | Prime Ralph run definition |
| ralph-linkedin | runner | `~/.prime/agent/skills/ralph-linkedin/SKILL.md` | Ralph LinkedIn Studio runner |
| personal-brand-lane | runner | `~/Developer/rig-gtm-studio-v2/skills/personal-brand-lane/SKILL.md` | Lane A: stage comments, never publish |
| comment-machine | tool | Eden skill `comment-machine` (eden://settings/skills/comment-machine) | Eden drafting and staging via eden-mcp |
| personal-brand-lane@eden | runner | Eden skill `personal-brand-lane` (eden://settings/skills/personal-brand-lane) | Eden Lane A runner; stage-only |
| comment-ambassador@eden | tool | Eden skill `comment-ambassador` (eden://settings/skills/comment-ambassador) | write_comment then stage_comment_card |

## Sub-skills

| file | covers |
|---|---|
| `references/comments-on-others.md` | positive-only comment construction, insight payload, link rules, banned patterns |
| `references/comment-targets-cadence.md` | target lists, thread selection, daily dose and sweep caps, borrowed attention, stop signals |
| `references/reply-handling.md` | inbound comments on Mike's posts: SLA, scan windows, comment-type routing, Loop-Back canon, honest null-state |
| `references/pinned-first-comment.md` | the pinned first comment format: image-first, four-line caption, the five tests |
| `references/eng-mechanics-and-lanes.md` | executor tool usage, browser mechanics pitfalls, handle assertion, lane fire rules |
| `references/creator-playbook.md` | cross-creator consensus, conflicts and gaps for this stage (11 doctrines) |

## Hard rules carried forward

- Never AI-written comments; no comment is better than a machine one [viral-core, engagement-comment-led]. No engagement pods, hashtag stacks, or automated outreach without approval [viral-core].
- Comments on other people's posts are positive only: validate, add one real insight, optionally point to Mike's related post as a complement [viral-core, comment-ambassador].
- Never correct, pitch, one-up, or self-introduce in a comment; never mention RIG or drop a link outside the sweep link caps [comment-ambassador, engagement-comment-led].
- Banned reply openers: "Great post!", "Love this!", "Couldn't agree more.", "Spot-on", "Nailed it" [alfred-comment-engagement].
- Sweep caps: max 12 comments per sweep, max 3 link-bearing comments per sweep, at most one carrying a site link, never two link comments inside the same hour (burst-link detection suppresses the promoted post), never on a day a follow batch runs behind the sweep [engagement-comment-led].
- Borrowed-attention dose 60-90 minutes a day; do not escalate toward the 100-300 comments a day precedents cited so people will not match them [borrowed-attention].
- Thread floor: 5 visible reactions or 3 visible comments, past-week threads, author in the ICP orbit; never guess a vanity slug [borrowed-attention].
- 14-day author dedupe: never comment on the same author twice inside two weeks [engagement-comment-led].
- Comment first, connect after; the lane keeps the engage-first side of the note-vs-no-note dispute [engagement-comment-led].
- Rejected connection requests suppress distribution; target selectively, never mass-connect [engagement-comment-led].
- Reply SLA on Mike's own posts: under 2 hours for comments inside the 24h SLA window; always scan the extended 72h window [alfred-comment-engagement].
- Every reply passes three gates before send: unique within the batch (anti-fingerprint), carries a specific number/framework/source (value), ends with an open-ended question (engagement driver) [alfred-comment-engagement].
- Spam comments get no reply and no response log row [alfred-comment-engagement].
- Never amplify off-site links dropped by others on Mike's posts [engagement-comment-led].
- Never fabricate engagement data; a null cycle reports zero honestly and names the transport state [alfred-comment-engagement].
- On any throttle signature or degraded surface: halt the sweep, log, resume next window; never push through [engagement-comment-led].
- Assert the signed-in handle before any outward action; on mismatch halt rather than switch accounts [profile-probe, viral-core].
- Ideawake lane: Coby's account, Coby's voice, nothing fires without Mike's explicit client approval [viral-core].
- Lane A stages comments and never publishes them [personal-brand-lane].
- No automated sends without Mike's explicit yes; Gate-D governs anything outward [viral-core].
- Comments are content: the same receipt rule applies, no invented numbers, quotes, clients or results [viral-core].

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-engage` verifies that the frontmatter and JEV mandate are in place, that the five sub-skills exist at size, that the ledger carries a named action for every stage-map row assigned to this stage, that every backticked path resolves, and that no sub-skill copies a 12-word run from a third-party merge source. GREEN means all of that holds.
