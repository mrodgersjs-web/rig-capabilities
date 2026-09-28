---
name: lv-creator-kasey-brown
description: >-
  Kasey Brown's LinkedIn doctrine (@kasetheace), distilled from 55 YouTube videos (2024 to 2026): authority posts that convert instead of viral reach, curiosity-gap hooks with the photo as a second hook, warm comment-to-DM conversion, and narrow positioning for experts. Use when a post must earn business rather than likes, when designing warm outreach, lead magnets or a launch, or when asked what Kasey Brown says about something. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives (hook stop-strength, post-type fit, revenue-versus-reach diagnosis, DM readiness) go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, kasey-brown, authority-posts, dm-conversion]
outcome: "content-publishing: LinkedIn work can apply Kasey Brown's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-kasey-brown
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-kasey-brown
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "55"
  distilled-videos: "46"
---

# Kasey Brown doctrine (revenue over reach: authority posts, warm DMs, one narrow reader)

## JEV-first mandate (read first)

This description is loaded into every session at start, and the parent `linkedin-viral` is the first LinkedIn route from Mike's always-loaded AGENTS.md, so the rule lives where the work begins.

This doctrine drives typed judgments: is the stop strong enough, which post type fits this goal, is a flop a reach problem or an intent problem, is this person ready for a DM. Each goes to Jev through `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` (rubrics `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`) BEFORE any frontier LLM call. A pass needs noul and confidence above 0.9.

- **Fail closed:** classifier down, error, or rubric missing means DEFERRED. Never a guess, never a pass.
- Every number here is a creator claim from a dated video. No cited video and no measured result from Mike means the claim is refused, not assumed.

**Who:** Kasey Brown (@kasetheace) runs a boutique LinkedIn writing and ghostwriting agency for executives, founders and experts (he reports 10-15 long-term clients, referral-only, closed to new clients as of Sept 2026), plus a recurring cohort program he calls Brick by Brick (roughly 20 to 30 seats, priced about $3,500 in early 2026 and about $5,000 later). His own audience is around 70,000 LinkedIn followers and his pitch is inbound revenue from content, not influence. Channel: https://www.youtube.com/@kasetheace (31.3K subscribers, 55 videos on file).

**Source:** the corpus is local-only at `~/Developer/brand-workspace/youtube-intel-pipeline/kasey-brown/` (55 transcripts, about 211K words, of which 46 were distilled across `extraction/batch-1.md` to `batch-3.md`; one video, LNaOe5v1-H0, had captions disabled). This skill is synthesis in RIG's words. Never paste transcript text into posts, Eden, or a public repo; cite by video ID, and find IDs in `references/source-index.md`.

**Evidence standard:** every number is a creator claim from the cited video. His algorithm statements are his own reading of the platform, unverified. Some captions are machine translations (Arabic or Bengali) flagged in the extraction headers, so their wording is approximate and their numbers should be cross-checked against an untranslated video before use. His figures drift across retellings; the variants are recorded with dates in `references/strategy-and-growth.md` rather than silently reconciled (the big post reads 8M, 8.1M or 8,274,498 impressions; the paying post reads 3,200 or 3,500 impressions). When Mike's measured results disagree, Mike's results win.

## The doctrine in 10 lines (current as of Sept 2026)

1. **Score posts on intent, not impressions.** His largest post earned zero revenue while a low-thousand-impression post earned five figures; every post gets a Stop, Stay, Share grade plus an intent grade. [hC7ZCVsG7qM, EfHijF0P6bo, kuipymgFpjk]
2. **Authority posts pay the bills.** Specific hook, credibility in the first lines, a named framework, a proof number, then a soft CTA that adds value; inspiration and engagement posts build reach but rarely revenue. [M0dAWh95NaQ, 2t-EBcS43Lw]
3. **The first two lines plus the photo are the post.** About 70 to 80 percent of the writing effort goes there, line three re-hooks with fresh tension, and the payoff stays below the fold. [4jnS31Fh5QE, LvA5pocucUM, yrI3QPIUk0Q]
4. **Position before you post.** One sentence that is almost entirely about the buyer, a profile that converts in three seconds, and a studied list of 50 real prospects. [aPa6qCvPFao, rGypgxFz3TM]
5. **Reach, then relationships, then revenue, in that order.** Filling the room and earning trust come before any offer; building the money machine first is the common failure. [bCxD79Wl6ec, iDK3ptwXCpo, dI8ZqDwPBNY]
6. **Comments are a working surface, not a metric.** Five to fifteen thoughtful comments a day on chosen people, insight or a sharp question instead of praise, and reply to every commenter in the first 60 to 90 minutes. [vc3FaWfXggY, hC7ZCVsG7qM]
7. **Human DMs close; AI never owns the conversation.** Warm order is existing engagers, then new connections within 48 hours, then cold with a personal video or voice note; the ask is usually more content, not a pitch. [NjyEXaX8nQU, dI8ZqDwPBNY]
8. **AI is a sparring partner and formatter, never the writer of record.** Thinking and research first, then structure, then heavy hand-editing toward your own voice, with gate outputs the model is forced to prove. [wqbIWGV9GDg, Lo7cSO2XH2k, jcxbBuiW2vE]
9. **Write so a phone scanner gets it.** About a fourth-grade reading level, story first, digits instead of spelled-out numbers, and every line advancing the story. [TcvoXYSHqe4, EfHijF0P6bo, m9VFFCW_qZs]
10. **Consistency with a long horizon beats intensity.** His own test is whether the insight would be worth $1,000 to a buyer, and his stated timeline is roughly six months to momentum and twelve to steady business results at three to four posts a week. [2t-EBcS43Lw, B18w0jPdXiI, eyfNP4ipgrI]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Openings, hook slots, the brutal honesty test, hook testing | `references/hooks.md` |
| Body craft, post types, story arcs, reading level, CTAs | `references/writing.md` |
| Photos as a second hook, banner and cover, video and carousels | `references/visuals.md` |
| Commenting, replies, comment volume, moving to DMs | `references/engagement.md` |
| Hour-one behavior, cadence, week slots, quiet seasons, algorithm claims | `references/timing-and-algorithm.md` |
| Positioning, profile funnel, DMs and asks, lead magnets, launches, measurement | `references/strategy-and-growth.md` |
| Find the video behind a claim | `references/source-index.md` |

## Where this feeds

`references/hooks.md` feeds lv-hooks. `references/writing.md` feeds lv-draft. `references/visuals.md` feeds lv-visuals. `references/engagement.md` feeds lv-engage. `references/timing-and-algorithm.md` feeds lv-launch and lv-plan. `references/strategy-and-growth.md` feeds lv-strategy, lv-profile, lv-outreach and lv-measure.

## Binding overlays for Mike (RIG rules win on conflict)

- **Lane first.** Enter through `linkedin-viral` for the lane guard. His playbook maps most directly to Lane B (RIG B2B, evidence-led, named receipts, no mascots). Lane A (personal brand in Eden) keeps its own voice and cast rules. The Ideawake client lane runs on Coby's account and never inherits this voice. Job-search lane work follows its own doctrine. Anything about a minor stops at the lane boundary.
- **Eden is the only publisher and the assigned generator.** Feed Eden a real story, transcript or receipt, never a bare topic. His live-write sessions show the intent: posts are hand-built story arcs, so an agent-built post without a real input violates both his method and RIG's rule. His habit of drafting in Google Docs first because the LinkedIn editor lost his text [jcxbBuiW2vE] is compatible with this and worth keeping.
- **Gate-D** governs publishing, sending, boosting, spending and profile edits. His cohort launch math, ad-scaling plans [P_78dP1UWcI, jYCnMnYF9EE] and any comment-keyword auto-DM delivery [jcxbBuiW2vE, jYCnMnYF9EE] are spend or send items, so they need Mike's explicit yes.
- **Comments on other people's posts are positive-only and never AI-written.** This conflicts with his comment doctrine: he teaches adding respectful challenges and contrarian takes in comments [uHgHT0fg3As, vc3FaWfXggY], and his AI stack is built for drafting volume [TcvoXYSHqe4, Lo7cSO2XH2k]. On Mike's account, insight-plus-one-positive-point replaces the challenge, and the comment text is human. His volume advice (5 to 15 a day) is inside RIG's comfort; anything like a pod or a comment trade [DXqN9z7HK-w, which he also rejects] stays out.
- **Outreach stays inside `linkedin-site-mechanics` throttles and nothing sends automatically without Mike's yes.** His funnel math assumes 20 DMs a day and his case studies assume 20/20/20 daily contact volume [NjyEXaX8nQU, 7vl7hhn_y78]; that volume is a ceiling to negotiate down, not a target. Cold custom video DMs are fine as a technique and still gated per send.
- **Every number is a sourced receipt.** His skeletons lean on big money figures and named client wins; Mike's posts use only numbers he can source, and client results are anonymized or approved first.
- **Deliberate imperfection is a conflict point.** He adds occasional intentional typos as a human signal [jcxbBuiW2vE]; on RIG lanes this collides with the quality floor and with the anti-slop lint, so it is noted as his claim and not adopted.
- **Scheduling.** He refuses to schedule anything he cannot be present for in hour one [uHgHT0fg3As], which agrees with RIG's distrust of the Eden scheduler; publish by hand and stay for the first 90 minutes.
- **Measure on Mike's account.** `linkedin-analytics-tracker` decides what works; this doctrine proposes what to test.

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-kasey-brown` is GREEN only when the frontmatter and JEV section are in place, at least three topic sub-skills exist at 400 bytes or more, `references/source-index.md` lists exactly the 55 transcripts the local manifest reports, no skill file shares a 12-word run with any local transcript, and every backticked absolute path resolves on disk. The `--self-test` plants a 16-word transcript run in a temp copy of this folder and passes only if that copy goes RED while the real folder stays GREEN. Both must print GREEN.
