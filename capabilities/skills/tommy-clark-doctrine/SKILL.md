---
name: tommy-clark-doctrine
description: >-
  Tommy Clark's founder-led B2B LinkedIn doctrine (@tclarkmedia, CEO of Compound Content Studio), distilled from all 79 of his YouTube videos (Jan 2024 to Sept 2026, about 317K words of transcript) into positioning, content system, hooks and media, distribution and algorithm, outbound-to-pipeline, and a dated ledger of the rules he later reversed. Use when planning, writing, scoring or diagnosing LinkedIn content, when a post underperforms, or when asked what Tommy Clark says about something. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives (topic fit, hook choice, flop cause, boost candidate) go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, doctrine, founder-led-content, b2b, hooks, algorithm, tommy-clark]
outcome: "content-publishing: LinkedIn work applies Clark's current 2026 rules, each traced to a dated video, never a superseded rule or copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/tommy-clark-doctrine/scripts/check_no_verbatim.py
  - cmd:python3 capabilities/skills/tommy-clark-doctrine/scripts/check_no_verbatim.py --self-test
  - grep:capabilities/skills/tommy-clark-doctrine/references/evolution-2024-2026.md:Current rule
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "79"
  corpus: "~/Developer/brand-workspace/youtube-intel-pipeline/tommy-clark/"
---

# Tommy Clark doctrine (founder-led B2B LinkedIn)

## JEV-first mandate (read before applying the doctrine)

Where this rule lives: it is repeated in this skill's description (loaded into every session at start by each harness) and at the top of the parent `linkedin-viral`, which is the first LinkedIn route from Mike's always-loaded AGENTS.md.

This doctrine produces typed judgments: does a topic pass content-market fit, which of three hooks wins, what caused a flop, is a post a boost candidate. Each one goes to Jev through `rig-s1gate check` (rubrics `post.linkedin`, `post.viral`, `post.eden`) BEFORE any frontier LLM weighs in, and a pass needs noul and confidence above 0.9.

- **Fail closed:** when the classifier is down, errors, or the rubric is missing, the answer is DEFERRED. DEFERRED is never a pass and never replaced by a guess.
- The doctrine's numbers are hypotheses. A claim with no cited video and no measured result from Mike's analytics is refused, not assumed.

**Who:** Tommy Clark runs Compound Content Studio, an agency that writes LinkedIn content for B2B founders (he cites 30 to 100+ founders and 150 to 250 client posts a week over time), and the Social Files newsletter. He reports about 45K LinkedIn followers in 2026. Channel: https://www.youtube.com/@tclarkmedia (12.6K subscribers, 79 videos).

**Source:** all 79 transcripts, scraped 2026-09-27, kept LOCAL ONLY at `~/Developer/brand-workspace/youtube-intel-pipeline/tommy-clark/` (manifest.json, transcripts-clean/, extraction/batch-1..6.md). This skill is synthesis in RIG's words. Never paste transcript text into posts, Eden, or a public repo. `scripts/check_no_verbatim.py` enforces that.

**Evidence standard:** every number below is a creator claim from the cited video, not a verified fact. His algorithm statements are his reading of the platform, and he says himself that nobody fully understands it [s6KMjhznXqs]. Treat them as hypotheses to test on Mike's own analytics. When Mike's measured results disagree, Mike's results win.

## The doctrine in 12 lines (current as of Sept 2026)

1. **Position before you post.** One sentence answers why a specific buyer should follow you (his "golden question"), and every topic must sit where buyer interest, product adjacency and your lived credibility overlap (content-market fit). [0EA0n1Ka41k, E0uu_GLIkw0, HFCfw6gznRM]
2. **The person, not the company page.** Pages convert visitors; people create reach. [N2b0QVoCEPg, 2Yv8osegsKY]
3. **How-I beats how-to.** Every take carries something AI cannot produce: a real story, proprietary numbers, or physical proof such as a real photo or stunt. [gZwWBtiZ7qE, szN0DF3Oqik, nbXzXfthKl0]
4. **One post, one person.** Write to a single named buyer type and decide the behavior you want (like, comment, save) before writing. [szN0DF3Oqik]
5. **Less but better.** Three strong posts a week in 2026 (one per funnel stage, or a moonshot, a scrappy post and an experiment). Five a week was his norm until Jan 2026. [s6KMjhznXqs, QKNc515DSro]
6. **The hook is the biggest lever.** Lines 1-3 carry 2-3 stacked levers, drafted three ways, hidden under a natural voice because formula phrasing now reads as AI. [UjDZLhuEpnQ, SL8yfxUVFKE]
7. **Media is the second hook.** Real photos of real people and places beat branded graphics; he cites about 27% more impressions for IRL photos across a month of client posts. [szN0DF3Oqik, 2Yv8osegsKY]
8. **Turn the dial up about 20%.** Real opinions framed as personal boundaries; punch up, never down; lose only non-buyers. [HFCfw6gznRM, zMzPmTETIyU, RpOt0kEWAFc]
9. **Bend the algorithm yourself.** Roughly 20 connection requests per weekday to named ICP people (about 100 a week is the platform ceiling he cites) plus 5-10 thoughtful comments a day on buyers, the creators they follow, and competitors. Comments are content. [gZwWBtiZ7qE, BMfXeo02bvo, 2Yv8osegsKY]
10. **Convert warm signals, not cold lists.** Profile viewers and engagers get a short value-first note or a 60-90 second Loom audit with one quick win and a soft close. [E5vxr1IZCpI, 29hBCF7N7Jg]
11. **Pay to control distribution.** Boost ICP-relevant posts that under-delivered (he names roughly 17-31 likes) as thought-leader ads at about $30 a day, after a week of organic run, with a PS-line link edited in first. [s6KMjhznXqs, QKNc515DSro]
12. **Repetition is a tool.** Bank winners and rerun them (verbatim is fine after about 3 months; the origin story quarterly), and judge the system on self-reported attribution and buyer mix, not reach. [UjDZLhuEpnQ, E0uu_GLIkw0, yBKOrgQS-q8]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Who to be, what to talk about, which game to play (leads, recruiting, fundraising) | `references/positioning.md` |
| Cadence, funnel mix, format catalog, content interview, AI rules, team accounts, voice | `references/content-system.md` |
| Write or fix a hook, choose media, pick a length | `references/hooks-and-media.md` |
| Why a post flopped, what the feed rewards, post-launch actions, paid boosts, peaks | `references/distribution-and-algorithm.md` |
| Profile, daily outbound engine, warm-signal DMs, launches, lead magnets, measurement | `references/outbound-and-pipeline.md` |
| Is this still his advice? Any rule that has a date on it | `references/evolution-2024-2026.md` |
| Find the video behind a claim | `references/source-index.md` |

## Binding overlays for Mike (RIG rules win on conflict)

- **Lane first.** Enter through `linkedin-viral` for the lane guard. Clark writes for founder accounts; that maps to Lane B (RIG B2B) most directly. Lane A (personal brand) keeps its own rhythm and cast rules. The client lane (Ideawake) and anything about a minor are outside these growth tactics.
- **Automation.** Clark's agency now automates connection requests (Apollo into HeyReach, about 15 a day) [UjDZLhuEpnQ, szN0DF3Oqik]. On Mike's account, outbound volume stays inside `linkedin-site-mechanics` throttles and nothing is sent automatically without Mike's explicit yes.
- **Paid boosts are spend.** Each thought-leader ad is a Gate-D item Mike approves, inside the RIG ad budget.
- **AI drafting.** Since Sept 2025 Clark forbids AI taking a post from zero to draft [2XeAckxuAKM, tYd_MnpXU90]. RIG reconciliation: Eden is the assigned generator, so Eden gets a real story, interview transcript or receipt as input, never a bare topic.
- **Comments on other people's posts stay positive** (Mike's rule). The +20% intensity dial applies to Mike's own posts only.
- **Numbers are receipts.** Clark's skeletons use money and metrics; Mike's posts use only numbers he can source.
- **Measure on Mike's account.** `linkedin-analytics-tracker` decides what works; this doctrine proposes what to test.

## Done-test

`python3 scripts/check_no_verbatim.py` is GREEN only when no doctrine file shares a 12-word run with any of the 79 local transcripts and the source index lists all 79 videos. It exits 3 (SKIPPED, never a pass) on a machine without the corpus. `--self-test` pastes a 16-word transcript run into a temp copy of this folder and passes only if that copy goes RED while the real folder stays GREEN; the planted text never touches the skill.
