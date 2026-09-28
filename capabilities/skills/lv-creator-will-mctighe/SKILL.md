---
name: lv-creator-will-mctighe
description: >-
  Will McTighe's LinkedIn doctrine (@WillMcTigheOfficial), distilled from 16 YouTube videos (2025 to 2026): studied hook research, proof-first openings, funnel-split post types, niche customization of proven formats, winner reuse, and the profile as a 5-second landing page. Use when ranking hook variants, choosing a post type by funnel stage, adapting a proven format to a named niche, scheduling a winner rerun, or auditing a profile. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives (hook variant ranking, post type fit, winner reuse timing, profile pass) go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, will-mctighe, hooks, b2b-content, founder-brand]
outcome: "content-publishing: LinkedIn work can apply Will McTighe's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-will-mctighe
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-will-mctighe
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "16 transcripts on file"
  distilled-videos: "16"
---

# Will McTighe doctrine (hook research plus proof-first B2B content)

## JEV-first mandate (read first)

Where this rule lives: in this description, which every harness loads at session start, and at the top of the parent `linkedin-viral`, the first LinkedIn route from Mike's always-loaded AGENTS.md. An agent meets the rule before it uses any line below.

This doctrine drives typed judgments: which hook variant wins, which funnel job a post type is for, whether a winner is due for reuse, and whether a profile passes the 5-second test. Each goes to Jev through `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` with rubric `post.linkedin`, `post.viral`, `post.eden` or `comment.linkedin`, BEFORE any frontier LLM call. A pass needs noul and confidence above 0.9. Fail closed: classifier down, error, or rubric missing means DEFERRED, never a guess, never a pass.

**Who:** Will McTighe is a LinkedIn growth founder (his product is Saywhat, a small SaaS he reports past $500K ARR with 2 people) who teaches hook research, format systems and B2B conversion content to founders and operators. He reports growing from a few thousand to over 400,000 LinkedIn followers in about 20 months starting February 2024 [UJvAtV63vk0, 3UcZFurI_yw]. Channel: https://www.youtube.com/@WillMcTigheOfficial (1.86K subscribers, 16 LinkedIn videos).

**Source:** 16 transcripts, scraped 2026-09-28, kept LOCAL ONLY at `~/Developer/brand-workspace/youtube-intel-pipeline/will-mctighe/` (manifest.json, transcripts-clean/, extraction/batch-1.md). All 16 were distilled. This skill is synthesis in RIG's words; never paste transcript text into posts, Eden, or a public repo. `references/source-index.md` maps every claim to a video ID.

**Evidence standard:** every number is a creator claim from the cited video. His channel is small (1.86K subscribers), so reach and revenue claims are unverified and sometimes inconsistent between videos: followers appear as 400,000+, 415,000, 420,000 and 430,000 [3UcZFurI_yw, TTH-75XOgJE, pyPoIYDg_a0, D_MY33bviuQ], revenue as $500K, $600K then $500K ARR again [0_8TCrdBPVM, pyPoIYDg_a0, UJvAtV63vk0]. Trust what he demonstrates (format mechanics, process, his post teardowns) over what he claims to earn. Algorithm statements are his reading, labeled unverified. Mike's measured results win.

## The doctrine in 10 lines (current as of Sept 2026)

1. **Split the job before writing.** Reach, trust and conversion posts are different products with different scores; judging conversion posts by likes is the beginner error [0_8TCrdBPVM, 5rLlzb6_vgA, TTH-75XOgJE].
2. **The hook is the whole forced view**, not the first sentence: the visible lines plus the visual (first slide, first frames, or the graphic) carry the stop [rlbI4ztEBFU, pyPoIYDg_a0].
3. **Proof outranks tips.** Open with a receipt a model cannot invent, then one lesson; a clean value promise alone gets overrun [rlbI4ztEBFU, wVWXbYuoXYg, pyPoIYDg_a0].
4. **Customize proven formats to a named buyer.** A broad topic with a generic body stays generic career advice; rename the format and rewrite the body into the niche's world [O1LeyZsrnls, 9CsBaaYOgGM, EUueg8xudKk].
5. **Useful means usable tomorrow**, and saves outrank likes as the value signal; top-of-funnel must still fit the whole audience [3UcZFurI_yw, UJvAtV63vk0].
6. **Visuals do at least half the hook work.** Niche infographics and carousels travel furthest, work photos and short video build trust, proof screenshots make case studies believable [rlbI4ztEBFU, Ej7WFBI9NS4, TTH-75XOgJE].
7. **The profile is a 5-second page**: who you help, the outcome, and relevant proof, with Featured holding a magnet, a booking link or a case study [Ql4gXPDhalk].
8. **Human niche comments on same-size peers plus DMs to warm signals.** Pods, comment volume targets and robot comments fail; a wrong-niche audience imports the wrong buyers [Ej7WFBI9NS4, 3UcZFurI_yw, UJvAtV63vk0].
9. **Reuse winners on a clock**: a similar variant within a week, a new visual on the same topic in 3 to 4 weeks, an exact rerun after 2 to 3 months [A9acfOArp98].
10. **One unfinished public challenge with a date outperforms a finished lecture**; publish the bad updates too [F8IGilhJItA, 5rLlzb6_vgA].

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Openings: the 8 hook types, forced-view unit per format, interrupt selection | `references/hooks.md` |
| Body craft, frameworks, post type catalog, AI drafting rules, CTAs | `references/writing.md` |
| Carousels, infographics, work photos, proof screenshots, video, profile visuals | `references/visuals.md` |
| Commenting, peer support pods done honestly, DM warm signals, lead magnets | `references/engagement.md` |
| First-hour myths, reuse windows, news speed, cadence, algorithm claims | `references/timing-and-algorithm.md` |
| Positioning width, funnel mix, growth timeline, profile, outbound, measurement | `references/strategy-and-growth.md` |
| Find the video behind a claim | `references/source-index.md` |

## Where this feeds

`references/hooks.md` to lv-hooks. `references/writing.md` to lv-draft. `references/visuals.md` to lv-visuals. `references/engagement.md` to lv-engage. `references/timing-and-algorithm.md` to lv-launch and lv-plan. `references/strategy-and-growth.md` to lv-strategy, lv-profile, lv-outreach and lv-measure.

## Binding overlays for Mike (RIG rules win on conflict)

- **Lane first.** McTighe teaches founder accounts, which maps to Lane B (RIG B2B) and the job-search lane. Lane A keeps its own cast rules (Birch Tuesday-only, The Coach from behind or in silhouette). The Ideawake client lane runs on Coby's account with Mike's explicit client approval per action. Anything about a minor stops; this doctrine never applies there.
- **Eden is the publisher and the assigned generator.** McTighe trains AI to draft from a framework plus your notes and then restores the voice [TTH-75XOgJE]; RIG routes that job to Eden, and Eden gets a real story, transcript or receipt as input, never a bare topic. His AI-first drafting also conflicts with Tommy Clark's September 2025 rule against any zero-to-draft AI [2XeAckxuAKM, tYd_MnpXU90]; the dated split is recorded in `references/writing.md` and RIG follows Clark plus Eden.
- **Gate-D on publishing, scheduling live, DMs and connection requests in volume, boosts or spend, and profile edits.** McTighe's habit of 100 DMs in a day [pyPoIYDg_a0] is never run on Mike's account without his yes, and outbound stays inside `linkedin-site-mechanics` throttles.
- **Comments on other people's posts are positive-only and never AI-written** (Mike's rule). McTighe's advice is compatible in spirit (real niche comments) but his volume figures are not a target.
- **Every number is a sourced receipt.** His skeletons carry invented-sounding money and metrics; Mike's posts use only numbers he can source. Reach claims from this small channel stay labeled unverified.
- **Spend is Gate-D.** McTighe has no paid playbook here beyond one guess that a peer's campaign added spend after it worked [F8IGilhJItA]; RIG ad spend follows the approved budget only.
- **Where he conflicts with Clark:** McTighe retires the first-hour rule entirely (2025-09-27) [Ej7WFBI9NS4], while Clark's playbook keeps launch-day actions; McTighe endorses AI drafting (2025-12-01) where Clark forbids it. Believe the dated one and Mike's own analytics over either.

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-will-mctighe` is GREEN only when the frontmatter name matches the folder and carries the JEV-FIRST MANDATE, the body opens with the JEV-first section, references/ holds 3 or more topic sub-skills of at least 400 bytes with no stray files, source-index rows equal the 16 transcripts the manifest reports, no file shares a 12-word run with the local transcripts, and every backticked absolute path resolves on disk. The `--self-test` run plants a 16-word transcript run in a temp copy and passes only if that copy goes RED while this folder stays GREEN; the planted text never touches the skill.
