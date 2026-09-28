---
name: lv-creator-shanee-moret
description: >-
  Shanee Moret's LinkedIn doctrine (@shaneemoretgrowthacademy), distilled from 66 YouTube videos (2023 to 2026): newsletter launch and naming, live events and the free invite engine, short-form video, buyer-first positioning, and inbound client generation. Use when planning a newsletter or a LinkedIn Live, choosing a hook or CTA, sizing an inbound motion, or when asked what Shanee Moret says about something. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives (topic fit, hook choice, CTA clarity, event readiness) go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, shanee-moret, newsletter, live-events, short-video]
outcome: "content-publishing: LinkedIn work can apply Shanee Moret's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-shanee-moret
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-shanee-moret
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "66"
  distilled-videos: "66"
---

# Shanee Moret doctrine (newsletters, live events and short video as one inbound machine)

## JEV-first mandate (read first)

Where this rule lives: this description is loaded into every session at start, and the parent `linkedin-viral` is the first LinkedIn route from Mike's always-loaded AGENTS.md. An agent meets the rule before it touches LinkedIn work.

This doctrine produces typed judgments: does a topic fit the named buyer, which opening wins, does a CTA match the offer, is a live-event plan ready to promote. Each one goes to Jev through `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` (rubrics: `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`) BEFORE any frontier LLM call. A pass needs noul and confidence above 0.9. Fail closed: classifier down, error, or rubric missing means DEFERRED, never a guess, never a pass. An advisory PASS is never permission to publish, send, invite, boost or spend.

**Who:** Shanee Moret teaches LinkedIn growth to business owners and experts, selling coaching and done-with-you help around newsletters, live video and personal brand (she reports about 1,000 business owners helped and hundreds of clients, creator claims) [bCRYL6aL3ec, RDEugFeexyI]. She reports almost 1 million LinkedIn followers and a newsletter base she quotes anywhere from about 260,000 to 425,000 depending on the video, all creator claims that drift across the corpus. Channel: https://www.youtube.com/@shaneemoretgrowthacademy (12.7K subscribers).

**Source:** all 66 transcripts, scraped 2026-09-28, kept LOCAL ONLY at `~/Developer/brand-workspace/youtube-intel-pipeline/shanee-moret/` (manifest.json, transcripts-clean/, extraction/batch-1..3.md). 66 distilled; 26 planned videos had captions disabled and are absent. 5 of the 66 were machine-translated caption tracks with the English track restored on disk. This skill is synthesis in RIG's words; never paste transcript text into posts, Eden, or a public repo. `references/source-index.md` lists every video.

**Evidence standard:** every number here is a creator claim from the cited video, not a verified fact. Her algorithm statements are her reading of the platform and she says there is no trick behind reach [sqv-zZLDGAA]. The event-invite quota is stated inconsistently across her videos (about 1,000 a week versus about 4,000 a month, plus other variants) and stays flagged unverified, never silently reconciled. 16 batch-2 transcripts carry unknown publish dates. When Mike's measured results disagree, Mike's results win.

## The doctrine in 10 lines (current as of Sept 2026)

1. **One 90-day goal, one buyer, one CTA before anything else.** The buyer is defined from top-20% payment data and the trigger moment that made them call; content writes only to that moment. [6f3ZzY5-gUg, bm6_uMvLagQ, ScjYcHsuPvM]
2. **Own one narrow category and repeat one CTA.** About 8 of 10 posts sit on the category you want to be hired for; mind share means seeing you names the category. [bCRYL6aL3ec, v3TS92mls0k]
3. **The newsletter is the channel that does not need the feed.** Launch title is a permanent filter, editions reach subscriber inboxes, and she reports 40 to 50 percent open rates (creator claims). [pSncKW0JBFs, BDW169gFDy0, 93Wgv8WAHw4]
4. **Live events convert; the feed distributes.** She reports 10 to 30 percent live conversion against 1 to 3 percent for uploaded video (creator claim), so lives carry the offer. [Ec4xbXY8sjs, YBYkNwplEmE, bCRYL6aL3ec]
5. **Run the invite engine and the warm-up.** Spend the free first-degree event invites in weekly batches with the last batch 7-plus days out, promote the topic for 7 to 10 days first, and treat attend-clickers as the prospect list. Quota numbers conflict across her videos and are unverified. [g6zmV-Y90rs, Ec4xbXY8sjs, ebVmLIPyri8]
6. **Hooks go off baseline.** Say the one thing the top voices on the topic leave out, open on the claim with no greeting, and land any credibility line in about 4 seconds or cut it. [v3TS92mls0k, YggvR0eUj6E, rI4ZkkauCcU]
7. **Video is the trust accelerator.** Vertical shorts of about 45 to 90 seconds, phone-shot and unedited beats polished; live reps build the skill faster than gear. [YggvR0eUj6E, 4kkzQTa9Y-c, YBYkNwplEmE]
8. **Engagement is reciprocal and manual.** About 10 to 15 minutes a day of real commenting, give several times before any ask, and DM only people who already engaged. [aCUbwMrQ8GA, R-74V2EOWdE, g6zmV-Y90rs]
9. **Work the silent majority.** Decision makers read quietly and never like; subscribers and attendees are the warm list, converted to first-degree with short notes. [BDW169gFDy0, JwnyrcJAdaQ, 1kqCOtDeLRA]
10. **Score calls and emails, not views.** One metric per stage; four barren lives in a row is a messaging problem to fix, not a channel to abandon. [sqv-zZLDGAA, qSt2LtOCNy8, rI4ZkkauCcU]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Openings, off-baseline levers, title-as-filter, opening slots | `references/hooks.md` |
| Body craft, post and newsletter formats, CTAs, voice, length | `references/writing.md` |
| Headshots, banners, covers, selfie video, short-video specs, AI images, slides | `references/visuals.md` |
| Commenting, replies, DMs, subscriber work, live chat prompts | `references/engagement.md` |
| Cadence, launch windows, live-event timing, invite quotas, algorithm claims | `references/timing-and-algorithm.md` |
| Positioning, category, profile, offers, lead gen, repurposing, measurement | `references/strategy-and-growth.md` |
| Find the video behind a claim | `references/source-index.md` |

## Where this feeds

- `references/hooks.md` feeds lv-hooks.
- `references/writing.md` feeds lv-draft.
- `references/visuals.md` feeds lv-visuals.
- `references/engagement.md` feeds lv-engage.
- `references/timing-and-algorithm.md` feeds lv-launch and lv-plan.
- `references/strategy-and-growth.md` feeds lv-strategy, lv-profile, lv-outreach and lv-measure.

## Binding overlays for Mike (RIG rules win on conflict)

- **Lane first.** Enter through `linkedin-viral` for the lane guard: Lane A (personal brand in Eden, cast rules intact), Lane B (RIG B2B, evidence-led, named receipts, no mascots), the Ideawake client lane on Coby's account (assert the signed-in handle first), the job-search lane, and anything about a minor stops. Her tactics are generic B2B education; they never inherit a lane's voice.
- **Eden is the only publisher and the assigned generator.** Feed Eden a real story, interview transcript or receipt, never a bare topic. Her GPT-on-your-transcripts content machine [62b9R_HMLAY] is the same shape: raw material in, never a blank prompt.
- **Gate-D on every outward step.** Publishing or scheduling a post, sending DMs or connection notes, spending event invites in bulk, paid boosts (she teaches none), and profile edits each need Mike's explicit yes for that item. Her keyword-DM and registrant-DM plays [X8Mz2tpvN-8, Cv7QGjxA974] and her about-10-hellos-a-day rhythm [DdJYKsAfWqE] are outbound volume: they stay inside `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md` throttles and nothing sends automatically without Mike's yes.
- **Comments on other people's posts are positive-only** (Mike's rule) and never AI-written. Her manual commenting engine [aCUbwMrQ8GA] fits that rule as written; her reply-and-connect moves on other creators' threads land on strangers' inboxes, so they are sends.
- **Every number is a sourced receipt.** Her case-study skeletons rely on client revenue figures; Mike's posts use only numbers he can source.
- **Conflicts with RIG rules and with Tommy Clark's 2026 rules, named:** her 2026 cadence of about 10 posts a week [bCRYL6aL3ec] contradicts Clark's 2026 three-a-week rule [s6KMjhznXqs]; Mike's cadence follows the lane runner, not either doctrine. Her 2026 AI-image test where a story-paired render can beat a real photo [qPHqqOfZSEo] contradicts Clark's real-photo rule and its 27 percent impressions claim [szN0DF3Oqik, 2Yv8osegsKY]; an AI render of Mike or his cast is a Gate-D image asset and Lane A cast rules still bind. She never teaches paid boosts, where Clark spends about 30 dollars a day [s6KMjhznXqs]; on Mike's account any boost is a Gate-D spend item inside the RIG ad budget. Her cold-pitch origins are explicitly disavowed by her own 2024-02-04 video [i05h7QYsQIc]; do not resurrect them.

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-shanee-moret` is GREEN only when the frontmatter carries the JEV mandate, at least 3 topic sub-skills of 400-plus bytes exist beside `references/source-index.md`, the source index lists exactly the 66 videos the manifest reports transcripts for, no skill file shares a 12-word run with the local transcripts, and every backticked path resolves. `--self-test` plants a 16-word transcript run into a temp copy and passes only if that copy goes RED while the real folder stays GREEN. Without the local corpus the check exits SKIPPED, which is never a pass.
