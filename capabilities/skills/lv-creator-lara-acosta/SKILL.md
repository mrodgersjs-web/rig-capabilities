---
name: lv-creator-lara-acosta
description: >-
  Lara Acosta's LinkedIn doctrine (@Laraacosta), distilled from 36 YouTube videos (2024 to 2026):
  profile-as-landing-page, story frames (SLAY and PAS), comment-led distribution, AI drafting with a
  human edit, and the lead-magnet and email pipeline. JEV-FIRST MANDATE, findable at task start:
  judgments this doctrine drives (hook choice, topic fit, post gate, comment gate) go to rig-s1gate
  (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down.
  Use when writing or fixing a LinkedIn post, planning cadence or a weekly calendar, rebuilding a
  profile or a Featured shelf, picking hooks and media, running a comment engine, or checking whether
  a dated rule of hers still stands. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, lara-acosta, personal-brand, hooks, ai-writing]
outcome: "content-publishing: LinkedIn work can apply Lara Acosta's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-lara-acosta
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-lara-acosta
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "36 transcripts on file"
  distilled-videos: "36"
---

# Lara Acosta doctrine (personal-brand LinkedIn: profile, story, and AI-assisted writing)

## JEV-first mandate (read first)

This description loads into every session at start, and the parent `linkedin-viral` is the first LinkedIn route from Mike's always-loaded AGENTS.md, so the rule arrives before any LinkedIn work.

The typed judgments this doctrine drives: which hook wins for a given post, whether a topic fits the lane, whether a draft passes the post gate, and whether a comment is worth sending. Each goes to Jev through `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`, rubrics `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`, BEFORE any frontier LLM weighs in. A pass needs noul and confidence above 0.9.

- Fail closed: classifier down, error, or rubric missing means DEFERRED. Never a guess, never a local verdict, never a pass.
- Her numbers are hypotheses on Mike's account, not evidence. An advisory PASS is not permission to publish, send or spend.

**Who:** Lara Acosta is a LinkedIn personal-brand and AI-writing creator who teaches solopreneurs, founders and career builders to turn one expertise into inbound revenue; she reports three to four businesses, a coaching and education arm, and an AI writing tool her own team built and began marketing in 2026 [wYIzZqpHs3Q, 7SKd2cchGd4]. She went from a zero-follower start in May 2022 to six- and seven-figure months on a personal-brand playbook, and her channel sells that playbook to people leaving employment or building a solo service [ueIjOIWS4fY, MLXZ_aa2ZKw]. Channel: https://www.youtube.com/@Laraacosta (54.5K subscribers, 36 videos in this corpus).

**Source:** all 36 transcripts, scraped 2026-09-28, 138,338 words, kept LOCAL ONLY at `~/Developer/brand-workspace/youtube-intel-pipeline/lara-acosta/` (manifest.json, transcripts-clean/, extraction/batch-1..3.md). 36 of 36 distilled; 0 videos had captions disabled. Six of the thirty-six were scraped as machine-translated captions (Arabic) whose English track is now restored on disk, so those extractions are translation-layer text with garbled proper nouns: UiKT7lxE4bo, 9QiqofqNHq8, LBa8SdmItjU, JDZYNJQOee0, 0ZVUVa4IFTw, b_sVHSaQqGA. This skill is synthesis in RIG's words. Never paste transcript text into posts, Eden or a public repo. `references/source-index.md` maps every claim to its video.

**Evidence standard:** every number below is a creator claim from the cited video, not a verified fact, and her figures drift in the retelling (follower counts climb from 100K to 340K across the corpus; one early post grows from about 330K impressions to nearly half a million in 42 hours) [ueIjOIWS4fY, Foh1r-TdnTk, b_sVHSaQqGA]. Her algorithm statements are her reading of the platform, and she says in 2026 that platform staff themselves do not know the mechanism [7SKd2cchGd4]. Where Mike's measured results disagree, Mike's results win.

## The doctrine in 10 lines (current as of Sept 2026)

1. **The profile is the landing page.** Banner states the result and the logos, the headline names the buyer's problem and a number, and Featured is a three-tier shelf (low, mid, high), never a pinned viral post. [UiKT7lxE4bo, hCzcM6jV_zY, LBa8SdmItjU]
2. **One lane, one problem, one buyer.** Repeat the topic until the platform files you under it; a single off-topic post can cost the whole account her 2026 reading. [_6lKN2fZgIs, e3E83C-Xxn0, b_sVHSaQqGA]
3. **Experiential beats informational.** A lived scene with real numbers carries what neither a generic how-to nor a bare how-I line can, which is why she reversed her own how-I rule twice in 2026. [OSzrHwHLT6M, 1ph8i-NDz4k, Ug5Np7RNX7A, 0ZVUVa4IFTw]
4. **Two frames only: SLAY and PAS.** SLAY is story, lesson, concrete list, question for the reader; PAS is problem, agitation, plan. SLAY is the default again as of Sept 2026. [_6lKN2fZgIs, ozhwN9ndetM, 0ZVUVa4IFTw]
5. **The hook's stable part is the outcome, not the word count.** First line names an outcome, second line challenges or re-hooks; the length spec flipped four times between 2024 and 2026. [6EYqnuncRrg, ObW3McgGG44, 1wsfrYzwKbk, 6d_oxo1R9gs]
6. **Four posts a week, each with a job.** Teach, document, story, sell, aimed at two readers (the buyer and the follower who routes the buyer); daily volume is the beginner's way to find the lane, not the standing system. [Qz003lp_5vA, L7a694gzKG4, JDZYNJQOee0, qap4n06dqfw]
7. **Comments are the distribution engine.** Mini-posts in the buyer's bubble on named accounts, no empty praise and no pods; her current shape is one substantive comment on about 20 large creators plus replies under it, which she insists is not a pod. [ZK-CBIFDR9w, 6EYqnuncRrg, e3E83C-Xxn0, 0ZVUVa4IFTw]
8. **Work the first 30 minutes, not the perfect clock.** Reply to everything and keep commenting if it is thin. Her 2024 golden hour and 2025 pre-post warm-up are, on her own June 2026 account, the dead system. [6EYqnuncRrg, 6d_oxo1R9gs, e3E83C-Xxn0]
9. **The feed is rented.** A weekly lead magnet and a real email list carry the revenue (she reports 70 to 80 percent there), and the offer lives in Featured and in the post; the pinned-comment CTA she once called a law no longer exists as a feature. [7ZfRNgn3oHs, hDknZIF9Wsc, 9QiqofqNHq8, 6d_oxo1R9gs]
10. **Media and AI both serve the lived scene.** A real photo beats an infographic, carousels lost to clear text in her 2026 watching, and a model drafts only after your profile and a scene you lived are in the prompt. [6d_oxo1R9gs, e3E83C-Xxn0, ibfdqyz4KhQ, wYIzZqpHs3Q]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Openings, hook shapes, the word-count flip ledger, re-hooks | `references/hooks.md` |
| Body craft, SLAY and PAS, post types, length, CTAs, voice | `references/writing.md` |
| Photo, banner, Featured thumbnails, carousels, video, AI images | `references/visuals.md` |
| Comment engine, replies, self-comments, target lists, pods | `references/engagement.md` |
| Posting time, first 30 minutes, cadence, algorithm claims | `references/timing-and-algorithm.md` |
| Positioning, profile rebuild, magnets, email, outreach, measurement | `references/strategy-and-growth.md` |
| Is this still her advice? Which video says what | `references/source-index.md` |

## Where this feeds

`references/hooks.md` feeds lv-hooks. `references/writing.md` feeds lv-draft. `references/visuals.md` feeds lv-visuals. `references/engagement.md` feeds lv-engage. `references/timing-and-algorithm.md` feeds lv-launch and lv-plan. `references/strategy-and-growth.md` feeds lv-strategy, lv-profile, lv-outreach and lv-measure. The parent `linkedin-viral` fixes the lane first; this skill never decides a lane on its own.

## Binding overlays for Mike (RIG rules win on conflict)

- **Lane first.** Her storytelling register maps to Lane A (personal brand in Eden) and her proof-first expertreneur material to Lane B (RIG B2B: evidence-led, named receipts, no mascots, Mike's proprietary cast never appears). The Ideawake lane runs on Coby's account and never inherits her voice. Anything about a minor stops before this doctrine applies.
- **Eden is the only publisher and the assigned generator.** Her 2025 stack runs on an AI writer fed with her profile, pillar map and proven hooks [ibfdqyz4KhQ, wYIzZqpHs3Q]. For Mike, Eden drafts copy and images from a real story, transcript or receipt, never a bare topic. This skill supplies the rules and the brief inputs.
- **Gate-D on publishing, sending, boosting, spending and profile edits.** Her schedule (post at midday, reply for 30 minutes) and her thought-leadership boosts of proven posts are strategy only until Mike says yes to the specific item [6EYqnuncRrg, OSzrHwHLT6M].
- **Comments on other people's posts are positive-only**, one real insight, never AI-written. Her one-plus-three comment machine on 20 large creators is engineered reciprocity however she labels it [0ZVUVa4IFTw]; take the targeting logic and drop the quota and the reciprocity choreography. She herself calls pods the wrong comment [e3E83C-Xxn0].
- **Outbound stays inside `linkedin-site-mechanics` throttles.** Her daily adds and 20-per-day free-value outreach are not a licence to automate sends [ZK-CBIFDR9w, Qz003lp_5vA]. Nothing sends without Mike's explicit yes.
- **Every number is a sourced receipt.** Her money and follower claims are creator claims; a Mike post carries only numbers he can source. Her wayfinding rule survives the filter: give the method openly, sell the implementation [1wsfrYzwKbk].
- **Where she conflicts with Tommy Clark's 2026 rules, say so.** Cadence: he holds three strong posts a week, she prescribes four with named jobs [Qz003lp_5vA, JDZYNJQOee0]. AI: he forbids a model taking a post from zero to draft; she runs AI drafting from day one, guarded by her own profile and scene in the prompt [wYIzZqpHs3Q, ibfdqyz4KhQ]. Boosts: he buys thought-leader ads at a daily figure for under-performers; she boosts only a proven winner. Media: both land on a real photo over graphics. Dated conflicts are listed per file, never silently merged.

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-lara-acosta` is GREEN only when the frontmatter carries the mandate, the body opens with the JEV section, at least three topic sub-skills are present and each is substantive, the source index lists exactly the 36 videos the manifest reports, no file shares a 12-word run with the local transcripts, and every backticked path resolves. `--self-test` plants a 16-word transcript run into a temp copy of this folder and passes only if that copy goes RED while this folder stays GREEN; the plant never touches the real skill.
