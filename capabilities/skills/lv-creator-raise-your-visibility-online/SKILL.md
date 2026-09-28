---
name: lv-creator-raise-your-visibility-online
description: >-
  Louise Brogan's LinkedIn doctrine (@RaiseYourVisibilityOnline), distilled from 111 YouTube videos (2024 to 2026): profile as a searchable landing page, native photo stacks and PDF carousels, vertical video specs, and comment-led distribution. Use when choosing images, carousels or video, fixing a profile or company page, or when asked what this channel says. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives (format fit, keyword-first hook, comment depth, profile-view diagnosis) go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, raise-your-visibility-online, visuals, profile, video]
outcome: "content-publishing: LinkedIn work can apply Louise Brogan's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-raise-your-visibility-online
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-raise-your-visibility-online
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "111"
  distilled-videos: "111"
---

# Louise Brogan doctrine (profile, native visuals, comment-led reach)

## JEV-first mandate (read first)

This description loads at session start. Parent `linkedin-viral` is the first LinkedIn route from Mike's always-loaded AGENTS.md, so the rule is in force before any Brogan tactic is applied.

Typed judgments this doctrine drives: which format fits (photo stack, PDF, or vertical video), whether the opening words are the search noun, whether a comment is deep enough to post, and whether a flop is an impressions problem or a profile-view problem. Each goes to Jev via `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` before any frontier LLM call. Rubrics: `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`. A pass needs noul and confidence above 0.9.

Fail closed: classifier down, error, or rubric missing means DEFERRED. Never a guess. Never a pass. An advisory PASS is not permission to publish, send, boost, or edit a profile.

**Who:** Louise Brogan hosts Raise Your Visibility Online, a teaching channel on LinkedIn mechanics, with guests on some episodes (Neal Schaffer on influence; client Fiona Walsh on a monthly plan). She sells profile and visibility help, including a small group she prices in one 2026 webinar, and she runs a personal newsletter plus a company page. Audience is operators, job seekers, and small B2B teams who want the product UI explained, not a growth theory. Channel: https://www.youtube.com/@RaiseYourVisibilityOnline (109K subscribers on the 2026-09-28 scrape). Attribute claims to the channel unless a guest is named.

**Source:** local-only corpus at `~/Developer/brand-workspace/youtube-intel-pipeline/raise-your-visibility-online/` (manifest planned 137; 111 transcripts on file, 127,025 words; 26 captions disabled and excluded; 111 of 111 distilled into `extraction/batch-1.md` through `batch-3.md`). Cite by video ID. Index: `references/source-index.md`. Never paste captions into posts, Eden, or a public repo. Nineteen extraction sections passed through machine-translated captions before the English track was restored on disk; treat those sections as translation-layer text. The extraction itself flags Arabic captions on collaborative posts [Sbr_l0pQZlo], the newsletter subscribe button [ULsAaRmFm4c], and inbox filters [u9nLIx6F40E]. Numbers from undated or translation-layer files are softer than dated English files.

**Evidence standard:** every number below is a creator claim or a figure she relays from LinkedIn, Buffer, Social Insider, AdExchanger, or 6sense. Algorithm lines are her reading, unverified. Where two videos disagree, both dates stay. Mike's measured results win over any of hers. Tommy Clark's 2026 rules are a separate doctrine; conflicts are named, not merged.

## The doctrine in 10 lines (current as of Sept 2026)

1. The profile is the landing page. First words name the searchable noun, who it helps, and the result, not a job title and not a helping-verb opener. [z_GORdsjCs0, kqCm7DyEDZk, gs6W-WEH9Q8]
2. Profile, posts, and comments must name the same craft, or search and outside AI answers will not attach the name. [MVbCMTE5cR8, K_sGlIEm_7E, xLhvT0Fmyc8]
3. Photo stacks and PDF carousels are both taught. Native multi-image versus document is a dated conflict, not one rule. Test both. Swipes are why she says they travel. [zKeqRAwi-Bc, NQWX07rcCrc, ObIMdGuYZZ0]
4. Feed video is vertical, captioned on the file, hooked in the first seconds. Length moved from under 2 minutes (Nov 2024) to under 60 seconds (Apr 2026). Live is a separate, longer show. [tP_IpeaKZqU, KfqDg3sc9Ms, kMTLSZwriSA]
5. Comments do the distribution. Sentences, a real point, replies in the first hour. No pods, no bait, no AI comment. [c9vkQ-wxle4, KfqDg3sc9Ms, C6CKFidysR4]
6. A small network that replies beats a large cold one. No pitch in the first note. Follow the famous. Connect with the useful. [ZK1--ycHErs, QemxS3MX6co, ACWNXl0RvMg]
7. One long piece becomes the week: newsletter or article, then a thin visual, a short video, and native posts. Do not drop a blog link as the post. [lf7dLXWwb24, 5ClUpiebzsY, g4pHWR15mqg]
8. Judge outside-network share, profile visits, and later newsletter opens. Raw impressions are the weak score. [pzkFjBumMCs, ZSS7Dh2WmcE, rkud8XdrQAY]
9. Invite math is unreconciled. Dated files say about 5 free notes a month. An undated file says 100 invites per 7 days and a freeze past that. Do not collapse them. [qvmIiwBXoXE, gtwM_m3iZb0, 6SQ6KEIn1qM]
10. Show the newsletter or the booking path on the profile. Banner text is not a link. Featured, contact, and a Premium post button are the clickable surfaces. [gRHeFSRav1U, 3i5pl7dYulM, ULsAaRmFm4c]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Openings, headline-as-hook, poll prompts, video first frame | `references/hooks.md` |
| Body craft, formats, length, CTAs, voice, articles vs newsletters | `references/writing.md` |
| Images, carousels, video specs, Live, banners, tools | `references/visuals.md` |
| Comments, replies, target lists, pods, invite notes | `references/engagement.md` |
| Cadence, first hour, algorithm claims, dated reversals | `references/timing-and-algorithm.md` |
| Profile, company page, outreach, lead paths, measurement | `references/strategy-and-growth.md` |
| Find the video behind a claim | `references/source-index.md` |

## Where this feeds

| Sub-skill | Stage |
|---|---|
| `references/hooks.md` | lv-hooks |
| `references/writing.md` | lv-draft |
| `references/visuals.md` | lv-visuals |
| `references/engagement.md` | lv-engage |
| `references/timing-and-algorithm.md` | lv-launch and lv-plan |
| `references/strategy-and-growth.md` | lv-strategy, lv-profile, lv-outreach, lv-measure |

Stage files live under `~/Developer/rig-capabilities/capabilities/skills/`. Enter through `~/Developer/rig-capabilities/capabilities/skills/linkedin-viral/SKILL.md`. Do not apply this doctrine until the lane is fixed.

## Binding overlays for Mike (RIG rules win on conflict)

Lane first. Lane A is the personal brand in Eden (themed days, cast rules). Lane B is RIG B2B: evidence-led, named receipts, no mascots, and Mike's cast (Birch, Unit 7, The Coach, "Be more Birch") never appears. Ideawake is Coby's account: assert the handle, never borrow Mike's voice, nothing fires without Mike's client yes. Job-search profile work (Open to Work, resume upload, recruiter flags) stays in the job lane and is not a RIG post tactic. Anything about a minor stops.

Eden is the only publisher and the assigned generator (`~/.aside/u/0/skills/user/eden-mcp/SKILL.md`). Feed it a real story, transcript, or receipt, never a bare topic. Brogan's Sep 2026 flow uses AgoraPulse Archie to turn her own Sunday newsletter into company-page drafts, and she says review before ship [5ClUpiebzsY]. That source rule can inform the Eden brief. Archie, Canva, Napkin, and Claude are not RIG publishers. She also suggests Claude for a services blurb [XvgXc1tR720]. RIG does not hand a bare offer line to a model and ship it.

Gate-D on publishing, sending, boosting, spending, and profile edits. Her Premium tests, Accelerate ads, and Calendly-on-the-button setups are spend or account changes. Vendor percentages she repeats (42% better cost per action, 3x lead-form completion) are not her results and are not a forecast for Mike [TFaMsZTSPy4, lgp7QIusK-Y].

Comments on other people's posts stay positive: validate, add one real insight, no AI-written comments. She agrees on the AI ban and names a tell (thanks, then a comma, then the name) [C6CKFidysR4, yXk5rjO0EWg]. Her "seed the first hour with staff comments" [c9vkQ-wxle4] is the conflict: that is a coordinated burst, adjacent to a pod, and RIG does not run it.

Outreach stays inside `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md`. No automated sends without Mike's yes. Her undated 100-invites-per-7-days line, page auto-invites with no note, and Live invite batches are not a send plan [6SQ6KEIn1qM, bjs0W9Qa-mM, kMTLSZwriSA].

Every number is a sourced receipt. Her $10,000-a-month frame, Fiona's 50,000 euro label, and the $1,000 first-month story are her claims, not Mike's metrics [aq-Jyu42jUQ, QemxS3MX6co, gfbZ_5-fHDU].

Tommy Clark, current as of his 2026 videos: three strong posts a week, real photos over branded graphics, about 20 connection requests per weekday, no blank-to-draft AI, and paid boosts on under-delivered ICP posts. Brogan's cadence swings (daily, twice a week, Buffer's high-frequency relay, then once or twice a week). Her Canva and PDF teaching fights his photo-first rule. Her invite files fight each other and his weekly ceiling. Her ad walkthroughs are vendor claims, not his boost method. Where they disagree, date both and let Mike's analytics pick the test. Do not silently merge.

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py` on this folder is GREEN only when the frontmatter name matches, the JEV mandate is present, at least three topic files clear 400 bytes, `references/source-index.md` lists 111 videos, no skill file shares a 12-word run with the local transcripts, and every backticked home path exists. `--self-test` plants a 16-word transcript run in a temp copy and passes only if that copy goes RED while this folder stays GREEN.
