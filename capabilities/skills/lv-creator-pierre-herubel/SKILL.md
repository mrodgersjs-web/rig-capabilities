---
name: lv-creator-pierre-herubel
description: >-
  Pierre Herubel's LinkedIn doctrine (@pierreherubel9492), distilled from 28 YouTube videos (2024 to 2026): the Authority First content mix, two-line numeric hooks, one-concept infographics and carousels that earn dwell time and saves, a single cheap front-end offer on a one-CTA profile, and warm outbound scored from content consumption. Use when choosing a hook, structuring a post, picking a visual format, designing the profile or offer, or diagnosing a post stuck under 1,000 impressions. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives (hook shape, visual format, offer clarity, stall diagnosis) go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, pierre-herubel, hooks, infographics, authority-content]
outcome: "content-publishing: LinkedIn work can apply Pierre Herubel's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-pierre-herubel
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-pierre-herubel
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "28 transcripts on file"
  distilled-videos: "28"
---

# Pierre Herubel doctrine (expert-first posts, one-concept visuals, one cheap entry offer)

## JEV-first mandate (read first)

Where this rule lives: this description is loaded into every session at start, and the parent `linkedin-viral` is the first LinkedIn route from Mike's always-loaded AGENTS.md.

The typed judgments this doctrine drives are: which hook shape a post gets, which visual format carries the idea, whether a profile offer reads as one obvious next step, and why a post stalled under a thousand impressions. Each one goes to Jev through `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` (rubrics `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`) BEFORE any frontier LLM call. A pass needs noul and confidence above 0.9.

Fail closed: classifier down, error, or a missing rubric means DEFERRED. Never a guess, never a pass.

**Who:** Pierre Herubel is a designer (eight years in the trade before LinkedIn) turned LinkedIn educator and agency founder, selling audits, coaching and courses to marketers and founders. He reports 170,000 followers and 60 million views across four years of posting, plus a second business past seven figures and an agency he describes as past $85,000 a month. Channel: https://www.youtube.com/@pierreherubel9492 (11.8K subscribers, 28 videos in this corpus).

**Source:** local-only corpus at `~/Developer/brand-workspace/youtube-intel-pipeline/pierre-herubel/` (`manifest.json`, `transcripts-clean/`, `extraction/batch-1.md`). 28 transcripts on file, 28 distilled, 0 videos missing captions. See `references/source-index.md`. Never paste transcript text into posts, Eden, or a public repo.

**Evidence standard:** every number here is a creator claim from the cited video, not a verified measurement. His algorithm statements are his own reading of the platform and are labeled unverified. His follower and impression figures climb from video to video (85K to 170K followers, 30M to 60M views) and read as rolling self-reports. When Mike's measured results disagree, Mike's results win.

## The doctrine in 10 lines (current as of Sept 2026)

1. **Lead with expertise, not broad stories.** Authority First: 70% expertise, 15% personal, 15% offer (creator claim), and broad funnel-stage content is rejected outright for niche B2B. [zVC1HEH9060, 2HSavr17yq0, c_2g0KM7fqY]
2. **One post, one idea, from an insight only you have.** Mine it from client conversations, your own experiments, or your own frameworks, and give it a single angle. [i-YDUfx84f8, BkdOFSfFPD4, 9o4BqmpgVT8]
3. **The hook is the first two lines and does three jobs.** Attract, name the topic, make the right reader feel addressed; put numbers in both lines. [i-YDUfx84f8, 2eovlLOHOU4, SmuGlt1CDKY]
4. **Answer the hook immediately and write for skimmers.** Short sentences, bullets, blank lines; a deceptive hook that delays the payoff loses the boost. [Io7Uq-S8dpk, SmuGlt1CDKY]
5. **One concept per image.** Infographics, carousels, real screenshots and candid photos carry the dwell time and the saves; the image title acts as a second hook. [0ZKNmQnMQ7k, CphfSIw7WV8, 9o4BqmpgVT8]
6. **Show expertise, then sell the implementation.** Pitch content stays under 15% of output (creator claim), and every post bridges to one commercial action. [IAn0_pfzero, wbVwUpopQgI, 6RJb6qYq1gA]
7. **One audience, one expertise, one offer, one channel,** and the profile is a landing page for a single cheap front-end offer with one CTA. [wbVwUpopQgI, mV1Ma2ZVgU8, h9BQP6-IzZo, 3sf8fojVfpM]
8. **Repurpose instead of reinventing.** One insight into 10 to 15 formats (creator claim), roughly 30% of time creating and 70% repurposing proven ideas. [4OVxO2j24sw, 9o4BqmpgVT8]
9. **Warm outbound only.** Contact people who already consumed your content, score their signals in a CRM, and message manually referencing exactly what they consumed. [IAn0_pfzero, BkdOFSfFPD4]
10. **Expect a long flat stretch, and note his 2026 reversal.** Results land 2 to 3 months later (creator claim), and by June 2026 he stopped recommending the solo personal brand in favor of 3 to 5 coordinated team voices. [vzQrN8BVE9c, c_2g0KM7fqY, mc7nK3PYgjw]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Choosing or rewriting a hook | `references/hooks.md` |
| Structuring a post body, format or CTA | `references/writing.md` |
| Infographic, carousel, screenshot or photo decisions | `references/visuals.md` |
| Commenting, replies, DMs and engagement volume | `references/engagement.md` |
| Posting time, cadence, first-hour behavior, algorithm claims | `references/timing-and-algorithm.md` |
| Positioning, pillars, profile, offers, outreach, measurement | `references/strategy-and-growth.md` |

## Where this feeds

`references/hooks.md` feeds lv-hooks. `references/writing.md` feeds lv-draft. `references/visuals.md` feeds lv-visuals. `references/engagement.md` feeds lv-engage. `references/timing-and-algorithm.md` feeds lv-launch and lv-plan. `references/strategy-and-growth.md` feeds lv-strategy, lv-profile, lv-outreach and lv-measure.

## Binding overlays for Mike (RIG rules win on conflict)

- **Lane first.** Lane A (personal brand) publishes in Eden and keeps its own rhythm and cast rules. Lane B (RIG B2B) is evidence-led with named receipts and no mascots. The Ideawake client lane runs on Coby's account. The job-search lane is separate. Anything about a minor stops. Pierre's founder playbook maps to Lane B most directly.
- **Eden is the only publisher and the assigned generator.** He designs his own graphics in Canva and posts by hand [Io7Uq-S8dpk, 0ZKNmQnMQ7k]; on Mike's lanes the copy and brand imagery come out of Eden, fed a real story, transcript or receipt, never a bare topic. That is a direct conflict with his hands-on-Canva workflow, and RIG's rule wins.
- **Gate-D covers publishing, sending, boosting, spending and profile edits.** His seven-slot profile checklist [3sf8fojVfpM] is prepared and shown as exact values, then applied only after Mike approves it.
- **Comments on other people's posts stay positive only, and never AI-written.** His weekly influencer and ICP comment lists [DB-P9AUogXU] and his beginner commenting ratio [4OVxO2j24sw] run inside that rule. The deliberately debatable infographic trick [Io7Uq-S8dpk] is for Mike's own posts only.
- **Outreach stays inside `linkedin-site-mechanics` throttles, with no automated sends without Mike's yes.** His 10 DMs per working day habit [5wmCL8tA04I] and score-triggered messages [IAn0_pfzero] become drafts awaiting approval.
- **Every number is a sourced receipt.** His number-heavy hook skeletons [2eovlLOHOU4] accept only figures Mike can source.
- **Named conflicts with Tommy Clark's 2026 rules.** Pierre still teaches daily or 3x-weekly posting at a fixed clock time [DB-P9AUogXU, 4OVxO2j24sw]; Clark cut to three strong posts a week in Jan 2026. Pierre's explicit numbered hook skeletons [SmuGlt1CDKY] sit against Clark's rule that formula phrasing now reads as AI. Pierre's infographic-first visual system [0ZKNmQnMQ7k, 9o4BqmpgVT8] sits against Clark's finding that real photos beat branded graphics (about 27% more impressions on client posts). Pierre's June 2026 team-led content [mc7nK3PYgjw] sits against Clark's founder-person-over-page stance. RIG resolves these on Mike's own analytics, never by silently merging.
- **No golden hour to borrow.** He teaches none anywhere in 28 videos; `references/timing-and-algorithm.md` records that as none rather than importing another creator's doctrine.

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-pierre-herubel` verifies that the frontmatter name matches the folder, the body opens with the JEV-first mandate, at least three topic sub-skills of 400+ bytes exist alongside only standard reference files, `references/source-index.md` lists exactly the 28 transcripts the manifest reports, every backticked absolute path resolves on disk, and no doctrine file shares a 12-word run with the local transcripts. Its `--self-test` plants a 16-word transcript run into a temp copy of this folder and passes only if that copy goes RED while the real folder stays GREEN.
