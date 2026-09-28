---
name: lv-creator-mark-firth
description: >-
  Mark Firth's LinkedIn doctrine (@markfirth1681), distilled from 32 YouTube videos (2023 to 2026): connect sequencing, post style, the distribution-model flip, profile conversion, and small-account outreach. Use when drafting a LinkedIn post, planning connection requests, diagnosing reach, or setting a service-seller profile. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives (hook choice, comment fit, connect sequence, distribution reading) go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, mark-firth, post-style, outreach, distribution]
outcome: "content-publishing: LinkedIn work can apply Mark Firth's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-mark-firth
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-mark-firth
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "32"
  distilled-videos: "32"
---

# Mark Firth doctrine (post style, connects, and a dated distribution flip)

## JEV-first mandate (read first)

Where the rule lives: this description is loaded into every session at start, and the parent `linkedin-viral` is the first LinkedIn route from Mike's always-loaded AGENTS.md.

Typed judgments this doctrine drives (hook choice, comment fit, connect sequence, which distribution reading is current) go to Jev via `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` before any frontier LLM call. Rubrics: `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`. A pass needs noul and confidence above 0.9.

Fail closed: classifier down, error, or rubric missing means DEFERRED, never a guess, never a pass.

**Who:** Mark Firth teaches LinkedIn post style, connection requests, and distribution to established professionals, especially people over 40 who sell done-for-you work rather than courses. The extraction does not name a firm; do not invent one. He claims years of outbound volume, on the order of 100,000 messages (creator claim, title on one video says 150k). Channel: https://www.youtube.com/@markfirth1681 (31.6K subscribers in the 2026-09-28 manifest). [ -0NvIx7Kjfo, ArYphaJtvmc, wplSBnjBxt0 ]

**Source:** local-only corpus at `~/Developer/brand-workspace/youtube-intel-pipeline/mark-firth/` (32 transcripts, 32 distilled, 0 captions disabled; 58,994 words). Index: `references/source-index.md`. Synthesis only. Never paste transcript text into posts, Eden, or a public repo.

**Evidence standard:** every number below is a creator claim from the cited video, not a verified fact. Algorithm statements are his reading of the platform, unverified. When Mike's measured results disagree, Mike's results win.

## The doctrine in 10 lines (current as of Sept 2026)

1. Distribution is two dated models, not one. From 2024-02-23 through 2025-06-19 he taught first-degree-only reach and no virality. On 2026-01-15 he reversed that and claimed an interest-based, platform-wide push (captions garble the update name). He repeated the interest-feed reading on 2026-02-04. On 2026-03-02 he re-uploaded the May 2024 playbook and taught first-degree-only again. Do not reconcile the re-upload with the January claim. [N2AOzgp-SIk, lzOWlqfHz-s, MJFCR1EJdrw, 0WBbXeM5pJM, PVX6FHGp4Uc]
2. Connection requests stay blank. Photo plus headline decide acceptance. He claims shared-history lists accept at about 90 percent, and a photo he scores above 8 doubles acceptance. Those figures are his, not a quota. [2X4XQLvSNWg, wplSBnjBxt0, ArYphaJtvmc, gJmXa4b-rTQ]
3. Do not message on acceptance day. Wait one to two days, warm their content first, then open with zero asks. A later January 2026 video swaps neutral openers for polarizing questions. That is a dated shift, not the same step as the blank request. [wplSBnjBxt0, lzOWlqfHz-s, rXs_4EsUB4w]
4. The headline answers whether this person can help, with a market plus a Monday-morning pain, pain-avoidance wording, and the work in the first 8 to 10 words (creator claim on the word count). [5k5Z-OJzEL8, rKwbCjanWCo, i4lHm-CGiwU, wplSBnjBxt0]
5. Current posts are belief-change and lived stories, not advice templates. Write the closer first. Line one names the buyer's live problem. End at the realization. One past weakness, one repeated common enemy. [T7G4_owju2A, FEOAeCCK9e0, r2LsebGinxs, iubQmgPG3ZM]
6. Close with a question tied to that post, and repeat the same question in the first comment. [gTkfDjUBXMY, lzOWlqfHz-s, uEHPPU2k_OM]
7. Comment where buyers already look: news, then posts from accounts in the 7K to 13K band he names. Agree, then add. Never contradict. April 2026 rejected the all-day comment grind. August 2026 brought comments back as reviewed drafts, not a volume quota. [MJFCR1EJdrw, iubQmgPG3ZM, bYj16aegr3E, 7qDcQrCbIbI]
8. Judge money by DMs and matched profile visits, not likes. He cites 100 likes with zero DMs as the common failure (creator claim). [FEOAeCCK9e0, uEHPPU2k_OM, -0NvIx7Kjfo]
9. Small accounts sell a done-for-you outcome to a pure buyer list. Banner holds 3 or 4 logos. Featured holds a call link, one low-commitment asset, and the best proof. Lead magnets were declared dead on 2025-09-10. The free-download featured link returned on 2025-11-21. Do not merge those two dates. [ArYphaJtvmc, 8BidcQ5viLs, g2MSqSUOX6c, i4lHm-CGiwU]
10. From 2026-08-21 he moves the loop into a browser agent, with approval gates, a claimed cap near 100 connects a week, and a manual click on each approved request. That is his picture of the work. It is not permission to send. [bYj16aegr3E, 7qDcQrCbIbI, gJmXa4b-rTQ]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Openings, slot skeletons, hook tests, the first-line date ledger | `references/hooks.md` |
| Body craft, formats, CTAs, voice, story vs advice | `references/writing.md` |
| Photo, banner, carousel, image, video specs | `references/visuals.md` |
| Comments on others, replies, targets, what he dropped | `references/engagement.md` |
| Posting time, first minutes, cadence, algorithm claims, the distribution flip | `references/timing-and-algorithm.md` |
| Positioning, profile, connects, DMs, offers, measurement | `references/strategy-and-growth.md` |
| Find the video behind a claim | `references/source-index.md` |

## Where this feeds

- `references/hooks.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-hooks/SKILL.md`.
- `references/writing.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-draft/SKILL.md`.
- `references/visuals.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-visuals/SKILL.md`.
- `references/engagement.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-engage/SKILL.md`.
- `references/timing-and-algorithm.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-launch/SKILL.md` and `~/Developer/rig-capabilities/capabilities/skills/lv-plan/SKILL.md`.
- `references/strategy-and-growth.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-strategy/SKILL.md`, `~/Developer/rig-capabilities/capabilities/skills/lv-profile/SKILL.md`, `~/Developer/rig-capabilities/capabilities/skills/lv-outreach/SKILL.md`, and `~/Developer/rig-capabilities/capabilities/skills/lv-measure/SKILL.md`.

Enter through `~/Developer/rig-capabilities/capabilities/skills/linkedin-viral/SKILL.md` so the lane is fixed before any of these files are applied.

## Binding overlays for Mike (RIG rules win on conflict)

Lane first. Lane A is the personal brand in Eden (themed days, proprietary cast only on its own rules). Lane B is RIG B2B: evidence-led, named receipts, no mascots. The Ideawake lane is Coby Skonord's account: assert the handle, never borrow Mike's voice, nothing fires without Mike's client yes. The job-search lane shows profile edits as exact before/after values and applies them only after Mike approves. Anything about a minor stops. Firth's over-40 life-stage positioning and common-enemy posts do not transfer onto Jacob's lane, onto Coby's account, or into Lane B as vibe copy.

Eden is the only publisher and the assigned generator (`~/.aside/u/0/skills/user/eden-mcp/SKILL.md`). Feed it a real story, transcript, or receipt, never a bare topic. His 2023 text-to-carousel app flow and his 2026 browser-agent content loop do not replace Eden. [2X4XQLvSNWg, bYj16aegr3E]

Gate-D on publishing, sending, boosting, spending, and profile edits. His profile overhaul, featured-link swaps, event-invite batches (he claims 200 to 300 a week), and network pruning are outward or hard to reverse. Drafts are free. Sends are not. [7qDcQrCbIbI, rKwbCjanWCo]

Comments on other people's posts stay positive: validate, add one real insight, no attack. No AI-written comments. His August 2026 pre-filled comment skill conflicts with that rule. A human rewrites. The agent does not post. [bYj16aegr3E, iubQmgPG3ZM]

Outreach stays inside `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md` throttles. No automated sends without Mike's yes. His blank-connect cap near 100 a week, his endorsed automation apps, and his browser-agent tabs are creator claims and a conflict, not a standing send order. [rXs_4EsUB4w, bYj16aegr3E, gJmXa4b-rTQ]

Every number is a sourced receipt. His impression jumps, accept rates, photo scores, and revenue figures stay in this doctrine as labeled creator claims. They do not go in Mike's posts.

Where he conflicts with Tommy Clark's 2026 rules, say so and do not merge. Clark's 2026 cadence is three strong posts a week and hidden formula hooks. Firth's June 2026 video cadence is two posts a week, and his March 2026 re-upload still teaches a visible 5-to-8-word formula hook. Clark converts warm signals with a short note or a short Loom. Firth's standing connect is blank, with the first ask delayed. Clark treats distribution as something you bend with connects, comments, and paid boosts. This corpus does not teach paid boosts. Firth's own distribution reading flips, and the March 2026 re-upload still teaches the old first-degree model. See `references/timing-and-algorithm.md`. Clark since Sept 2025 refuses AI that drafts from a blank page. RIG already routes generation to Eden with a real input. Firth's agent-written comments and carousel templates lose to that rule.

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py` on this folder is GREEN only when the frontmatter name matches the folder, the description carries the JEV-FIRST MANDATE, the body has a JEV-first mandate section, at least three topic files are 400 bytes or more, `references/source-index.md` lists the same video count as the local manifest, no file shares a 12-word run with the local transcripts, and every backticked home path exists. `--self-test` plants a 16-word transcript run in a temp copy and passes only if that copy goes RED while this folder stays GREEN. The plant never touches the skill. A missing corpus is SKIPPED, never a pass.
