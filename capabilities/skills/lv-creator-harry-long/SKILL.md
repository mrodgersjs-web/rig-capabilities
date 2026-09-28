---
name: lv-creator-harry-long
description: >-
  Harry Long's LinkedIn doctrine (@harry.the.marketer), distilled from 27 YouTube videos (2026):
  golden-hour replies, dwell-versus-likes, hook skeletons, DM sequences, and the Sept 2026 AI-reader
  shift. Use when scoring a first hour, ranking openings, designing a DM sequence, or checking which
  of his algorithm claims still stands. JEV-FIRST MANDATE, findable at task start: judgments this
  doctrine drives (hook choice, golden-hour action, post gate, DM shape) go to rig-s1gate (Jev)
  BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child
  of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, harry-long, golden-hour, hooks, outreach]
outcome: "content-publishing: LinkedIn work can apply Harry Long's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-harry-long
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-harry-long
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "27 transcripts on file"
  distilled-videos: "27"
---

# Harry Long doctrine (LinkedIn hooks, golden hour, and outbound)

## JEV-first mandate (read first)

This description loads into every session at start, and the parent `linkedin-viral` is the first LinkedIn route from Mike's always-loaded AGENTS.md, so the rule arrives before any LinkedIn work.

The typed judgments this doctrine drives: which hook wins, what to do in the first hour after a post, whether a draft passes the post gate, and which DM shape is allowed. Each goes to Jev through `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`, rubrics `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`, BEFORE any frontier LLM weighs in. A pass needs noul and confidence above 0.9.

- Fail closed: classifier down, error, or rubric missing means DEFERRED. Never a guess, never a local verdict, never a pass.
- His numbers are creator claims. An advisory PASS is not permission to publish, send, boost or spend.

**Who:** Harry Long runs a LinkedIn growth and outbound practice under @harry.the.marketer. He sells client acquisition on the platform: connection volume, DM sequences, and a content front that warms the room so the message can close. Audience is service founders and small operators who want booked calls, not career builders. He reports revenue figures that do not agree with each other across the summer (spoken dollars versus a pound title, then a later monthly figure), so treat every money line as a creator claim, not a receipt [voRG26IXYS8, bGPALjhoXYA, B1uJ-pdbIFc]. Channel: https://www.youtube.com/@harry.the.marketer (5.02K subscribers, 27 videos in this corpus).

**Source:** all 27 transcripts, scraped 2026-09-28, 57,234 words, kept LOCAL ONLY at `~/Developer/brand-workspace/youtube-intel-pipeline/harry-long/` (manifest.json, transcripts-clean/, extraction/batch-1.md). 27 of 27 distilled; 0 videos had captions disabled. The extraction was rewritten the same day from the English caption tracks after a first pass used translated tracks; this skill follows that rewrite. Synthesis is in RIG's words. Never paste transcript text into posts, Eden, or a public repo. `references/source-index.md` maps every claim to its video.

**Evidence standard:** every number below is a creator claim from the cited video, not a verified fact. His algorithm statements are his reading of the platform, unverified, and they moved twice in two months (link penalty, then the whole engagement-test model). Where Mike's measured results disagree, Mike's results win.

## The doctrine in 10 lines (current as of Sept 2026)

1. **Blank connection requests beat a note.** A note marks you as a salesperson. The 28 June wrap-up briefly said include one; the tested rule that held after that is blank. [voRG26IXYS8, 27IqjaAYSa0, aWw3kS2hOBI]
2. **Most writing time goes to the first lines.** About two seconds before a scroll. Name one role, open a question, hint without spoiling, match the proof, write as you talk. [_ddwk79BB3s, YHx4UWulQ3I]
3. **Date the algorithm.** Through 29 Aug 2026 he taught an engagement test: dwell and comments beat likes, and the first 60 minutes decide viral or dead. On 2 Sept 2026 he said an AI reader replaced that test: easy to classify, then a small buyer sample, and lower views can mean more revenue. Both readings are creator claims, unverified. Do not apply the older model as if it were still his. [XbDKE82gRf0, qt_YMXlefXo, sUC5UAXni6M, hWhYdDbcVCg]
4. **Park the link.** On 19 July he claimed a link can cut reach by up to 60 percent. On 31 July the same claim shrank to about 19 to 20 percent. Current practice either way: no link in the body; park it in a comment. [_ddwk79BB3s, XbDKE82gRf0, YHx4UWulQ3I]
5. **Cadence is 2 to 5 posts a week, one niche, not daily.** Daily posting, which he says he taught for years, he now calls wrong. A 13 Aug line softened that to "or more." On 8 Sept "weekly" became the bar for being in the small share who post at all. Current working range is 2 to 5, one buyer. [27IqjaAYSa0, XbDKE82gRf0, uK6p4gAV8zU, hWhYdDbcVCg, kK5H2Uu1L6Y]
6. **Stay the first hour if you are still on the pre-Sept model, and do not retire the reply habit after the shift.** Reply in the first hour, including DMs. On 29 Aug he added a self-comment and named the first 60 minutes the golden hour. On 2 Sept he demoted that hour: buyers may never comment. The reply habit was not retired. [XbDKE82gRf0, qt_YMXlefXo, sUC5UAXni6M]
7. **Comment on bigger creators before you post more.** Rent reach with posts, borrow it in comments, own the relationship on an email list. His account of Lara Acosta's comment block dropped from 4 to 5 hours to about an hour a day by 25 Sept. No pods. [q_EkkPZ1vX4, kK5H2Uu1L6Y]
8. **Outbound is small yeses, then one letter, not a meeting.** Blank connect, a short voice note, permission, then a screen video only after a yes. The letter menu grew from three choices to four, and the middle bucket flipped from "not now" to "tell me more" on 19 Sept. Ignore the 85 percent title: the spoken track never states that figure. [0kLvQW0aPJE, smWHLEKYucQ, rGWmeMul31I]
9. **A model may draft. It never sends.** Train it on calls and winners, pick the hook yourself, and run a second chat as critic. A bare topic prompt fails. This conflicts with Tommy Clark's Sept 2025 ban on a model taking a post from zero to draft. Do not merge the two. [uK6p4gAV8zU, -BHLc3TIXMc, NqHd-89RycA]
10. **The profile is the landing page, and the company page borrows the face.** Follower display, paid headshot, headline as role plus who you help, one next step. People follow faces; the page is a trust check, written in first person and reshared both ways. [27IqjaAYSa0, 1GlNXA31E9o, JAta-iCI5gk]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Openings, slot skeletons, hook time split, testing | `references/hooks.md` |
| Body craft, line breaks, CTAs, voice, AI tells | `references/writing.md` |
| Headshot, banner, photo of you versus graphics, Loom, feed video | `references/visuals.md` |
| Comment blocks, golden-hour replies, self-comment, pods | `references/engagement.md` |
| First 60 minutes, cadence, link penalty, the 2 Sept algorithm shift | `references/timing-and-algorithm.md` |
| Profile, company page, lists, DM sequences, lead sources, measurement | `references/strategy-and-growth.md` |
| Which video says what | `references/source-index.md` |

## Where this feeds

`references/hooks.md` feeds lv-hooks. `references/writing.md` feeds lv-draft. `references/visuals.md` feeds lv-visuals. `references/engagement.md` feeds lv-engage. `references/timing-and-algorithm.md` feeds lv-launch and lv-plan. `references/strategy-and-growth.md` feeds lv-strategy, lv-profile, lv-outreach and lv-measure. The parent `linkedin-viral` fixes the lane first; this skill never decides a lane on its own.

## Binding overlays for Mike (RIG rules win on conflict)

- **Lane first.** His DM-plus-content system maps most cleanly to Lane B (RIG B2B: evidence-led, named receipts, no mascots; Mike's proprietary cast never appears). Lane A (personal brand in Eden) keeps its own rhythm. The Ideawake client lane runs on Coby's account and never inherits this voice. The job-search lane uses profile rules only, and only after Mike approves the exact before-and-after. Anything about a minor stops before this doctrine applies.
- **Eden is the only publisher and the assigned generator.** He names a scheduler he calls Post It, then later a browser-driven Claude session [uK6p4gAV8zU, NqHd-89RycA]. For Mike, Eden drafts copy and images. Feed it a real story, transcript or receipt, never a bare topic. Postiz stays retired.
- **Gate-D on publishing, sending, boosting, spending and profile edits.** His HeyReach caps, blank-connect volume, and "the extension asks first" story are not permission to automate sends [voRG26IXYS8, NqHd-89RycA]. Nothing sends, publishes, or edits a profile without Mike's yes for that item.
- **Comments on other people's posts are positive-only**, one real insight, never AI-written. His comment-as-mini-post habit is usable only inside that rule [q_EkkPZ1vX4]. No pods, which he also rejects [fWhBOPC1eLA, hWhYdDbcVCg].
- **Outreach stays inside `linkedin-site-mechanics` throttles.** His 200 to 250 requests a week, multi-sender stacks, and 40 to 50 messages a day are creator operating claims, not a licence [aWw3kS2hOBI, NqHd-89RycA]. No automated sends without Mike's explicit yes. Voice notes and Loom videos are drafts until he approves the send.
- **Every number is a sourced receipt.** His reply-rate ladder (24 percent, then 70 to 80 percent, then a 10x claim, then an 85 percent title the transcript never speaks) must not enter a Mike post [smWHLEKYucQ, bGPALjhoXYA, Ic9_SzU8DH8, rGWmeMul31I].
- **Where he conflicts with Tommy Clark, say so.** AI: Clark has forbidden a model taking a post from zero to draft since Sept 2025. Long, from 13 Aug 2026, trains a model on calls and winners, has a second model critique, and says the model never sends. Those are different rules. Do not merge them into "AI is fine if you edit." Cadence: Clark holds three strong posts a week; Long's current range is 2 to 5. Outbound: Clark converts warm signals with a short note or a short Loom; Long's default is blank connect plus a letter menu, with Loom only after a yes. Media: both prefer a photo of a real person over a branded graphic, but Long's own 31 July "visuals pull 3 times" claim fights his later photo-only and no-image posts.

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-harry-long` is GREEN only when the frontmatter carries the mandate, the body opens with the JEV section, at least three topic sub-skills are present and each is substantive, the source index lists exactly the 27 videos the manifest reports, no file shares a 12-word run with the local transcripts, and every backticked path resolves. `--self-test` plants a 16-word transcript run into a temp copy of this folder and passes only if that copy goes RED while this folder stays GREEN; the plant never touches the real skill.
