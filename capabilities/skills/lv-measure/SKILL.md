---
name: lv-measure
description: >-
  Analytics and learning loop for LinkedIn: capture per-post numbers from their own surfaces, run the
  daily and weekly trackers, review outliers against the account's own baseline, and turn every number
  into one action. Use when asked how a post or week performed, when reporting impressions or reach,
  when a target needs a basis, when diagnosing a flop, or before any plan is written from memory.
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage (flop cause, outlier
  versus baseline, boost candidacy, metric-is-real screening) goes to rig-s1gate (Jev) BEFORE any
  frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of
  linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, analytics, measurement, kpi, learning]
outcome: "data-analytics: every reported number has a named source and a window label, and every metric forces exactly one decision (rerun, rewrite hook, change media, retire format, or propose a boost for Mike's approval)"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-measure
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "6"
---

# LV Measure: analytics and the learning loop

## JEV-first mandate (read first)

Typed judgments this stage forces: the most likely cause of a flop, whether a post is an outlier against
the account's own baseline, whether a post qualifies as a boost candidate, and whether a metric change
is real movement rather than noise. Each goes to Jev before any frontier LLM call:
`rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` with the
stored rubrics `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`, `doctrine.surface`.
A pass needs every required noul and confidence above 0.9; exactly 0.90 does not pass.
Fail closed: classifier down or a judgment no stored rubric covers (most of measurement does) is
DEFERRED to Mike, never a guessed verdict. Measurement arithmetic itself is deterministic: compute, do
not classify. An advisory PASS never authorizes a boost, spend or publish.

## When to use / when not to

Use at the end of every post day, on the weekly review, whenever a post or week's performance is
reported, when a target or forecast needs a basis, when a flop needs a cause, and before any plan is
written from memory. Do not use to write or gate content (lv-draft, lv-gate), to schedule (lv-launch),
or to build visuals (lv-visuals). Scraping here is read-only evidence gathering, never account action.

## Procedure

1. **Assert identity before any read.** The browser can hold Mike's and a client's LinkedIn at once;
   never click through an account chooser, and never attribute a number read from the wrong account
   [analytics-surface].
2. **Read `references/surfaces-and-reach-math.md` first.** Most wrong numbers on this account have been
   window errors, not fetch errors [lg-measure].
3. **Capture per post:** t0, t+90 minutes, end of day, and full snapshots at T+1h, T+4h, T+24h. Log the
   delta series (rising = still expanding, falling = decay starting, flat = done) [measurement-kpi-loop,
   linkedin-analytics-tracker].
4. **Re-derive every figure from the surface it came from.** Re-read any post before quoting a number
   from it: a published post is an editable source. Compare 7-day with 7-day. Missing means unknown,
   never zero. A single-day observation is never reported as a rate [lg-measure, analytics-surface].
5. **Store it:** dated scoreboard files, the true publish state in `publish_log.json`, and the daily
   metrics block in the lane's project page [measurement-kpi-loop, linkedin-analytics-tracker].
6. **Weekly (Friday):** outlier review of the last five or six posts against the account's own baseline,
   then rank formats, then set next week's slate. A tactic is never called a winner before about 10
   posts of data carry it [measurement-kpi-loop, outbound-and-pipeline].
7. **Buyer mix and attribution:** who engaged, who viewed the profile, which DMs arrived, and what
   self-reported attribution ("how did you hear about us") says. Clicks and qualified actions beat
   vanity impressions [measurement-kpi-loop, outbound-and-pipeline].
8. **Every number drives exactly one action:** rerun (proven winners verbatim at about three months,
   the origin story quarterly), rewrite the hook, change the media, retire the format (after one re-cut
   second life), or propose a boost for Mike's approval with a dollar amount [outbound-and-pipeline,
   measurement-kpi-loop].
9. **Flop diagnosis** runs in Clark's fixed order through Jev (mandate above); the order is in
   `references/outlier-review-and-actions.md` [distribution-and-algorithm].
10. **Close the loop:** promote measured winners into the hook library, bury dead patterns, and feed
    the next plan. The evolve agent mines published-post performance back into scoring weights and hook
    candidates as proposals only [li-measurement, evolve].

## Quality bar

- Identity asserted; every figure labeled with its surface and window
- Each figure re-derived from source in this session, never carried forward from an earlier note
- Delta series recorded for post days; the "what did not change" line reported beside what moved
- Outlier calls cite the baseline they measured against; no tactic called a winner under 10 posts
- Nulls recorded as nulls; nothing estimated where it cannot be measured
- Attribution split: organic versus self-generated, correlation versus cause, self-reported answers
  logged where the tracker can read them
- Every metric maps to exactly one named action, or it is dropped from the report
- Numbers come with receipts; a stale scorecard is reported as stale rather than repeated

## Lanes

- **B (RIG B2B):** the buyer mix matters more than reach: 5,000 impressions from the right people beat
  100,000 from the wrong ones. Track qualified clicks, profile views from target accounts and booked
  conversations; the program-level north star is booked ICP calls [li-measurement, outbound-and-pipeline].
- **A (personal brand, Eden):** same capture; format and hook learnings feed the themed week. Eden link
  tracking rewrites links to its redirect domain, which the site's allowlist may not carry, so click
  attribution can collapse to other: report that honestly [measurement-kpi-loop].
- **Client (Ideawake, Coby's account):** metrics are read for the client report; nothing is published or
  changed on Coby's account from this stage. Baseline table for that account is partial: historical
  posts measured, per-post impressions still TBD [linkedin-analytics-tracker].
- **Job search:** applications and recruiter responses are tracked in the job lane's own pages; profile
  view trends may be reported but never as a hiring probability.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| /scrape | command | `~/.hermes/commands/scrape.md` | general web evidence pulls behind a metric or benchmark |
| /scraper | command | `~/.hermes/commands/scraper.md` | alias into the fleet scrapers when that surface is the one loaded |
| /scrapers | command | `~/.hermes/commands/scrapers.md` | multi-engine scraping OS for anything outside LinkedIn |
| rig-linkedin-scrape | skill | `~/.hermes/skills/rig-linkedin-scrape/SKILL.md` | read-only LinkedIn evidence: a creator's posts and engagement, the logged-in feed, or a post's engagers; never writes |
| scrapers | skill | `~/.aside/u/0/skills/user/scrapers/SKILL.md` | scraper OS plus the canonical-session LinkedIn read path and the working Instagram read path |
| analytics-dashboard | skill | `~/.hermes/skills/analytics-dashboard/SKILL.md` | when a LinkedIn analytics export should become an interactive dashboard for review |
| evolve | agent | `~/Developer/rig-gtm-studio-v2/agents/evolve.md` | self-learning pass: mines published-post performance into scoring weights and hook candidates as scored proposals; never publishes |
| step-7-measure | agent | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-7-measure.md` | growth-os pipeline measurement step |
| metrics-rederiver | agent | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/sub/metrics-rederiver.md` | re-derive a metric from its own surface when a carried-forward figure is suspected |
| metrics-scorecard | tool | `metrics-scorecard` (Eden-resident skill, cite by name) | collect follower metrics and write the daily red/green scorecard; a morning red is not a failed runner |
| /linkedin-operate | runner | `~/.hermes/commands/linkedin-operate.md` | one verified daily cycle of the live LinkedIn OS: score goals, verify floors, seal the packet |
| li-measurement | runner | `~/.hermes/skills/rig-linkedin-virality/skills/li-measurement/SKILL.md` | P3 measurement cycle at its 21:00 MT slot, Sunday review, or on "how is LinkedIn doing": scorecard against floors, JSON-LD impression harvest, outlier promotion, dead-pattern burial |
| li-measurement-steward | runner | `~/.hermes/agents/li-measurement-steward.json` | the agent that runs li-measurement on schedule; it keeps transport-zero and engagement-zero apart and reports failures as transport failures |

## Sub-skills

| file | covers |
|---|---|
| `references/daily-and-weekly-tracker.md` | what to measure, where, at which cadence, and how to store it |
| `references/surfaces-and-reach-math.md` | where each number lives, window traps, target math and its four levers |
| `references/kpi-loop-and-attribution.md` | per-post capture, evidence bar, attribution caveats, the Friday loop |
| `references/outlier-review-and-actions.md` | baseline outlier review, flop diagnosis order, the action map |

## Hard rules carried forward

- A metric with no action attached is a dashboard: every figure reported here must change something or
  be dropped [lg-measure].
- Impressions are not outcome; a 400-impression post with two qualified DMs beats a 4,000-impression
  post with none [lg-measure].
- Follower count is not exposed by the available API; missing means unknown, not zero. A single-day
  observation is never a rate [lg-measure].
- Never compare the feed sidebar's unlabelled impressions figure to the creator-analytics 7-day
  figure; that produced a 16x error on first pass [analytics-surface, reach-math].
- Re-read any post before quoting a number from it; never report from a cached or stale snapshot
  [lg-measure, linkedin-analytics-tracker].
- Write what you measure; anything unmeasurable is recorded as null, never estimated [measurement-kpi-loop].
- No tactic is called a winner before about 10 posts of data carry it; only measured winners enter the
  hook library [measurement-kpi-loop].
- Separate organic from self-generated metrics (self-reposts are distribution, not virality), and say
  correlation when that is all it is [linkedin-analytics-tracker].
- Fake, ghost or pod engagement is a negative lever: it is inert under percentile scoring and
  re-classifies the audience [reach-math].
- Paid amplification sits under Mike's standing cap of $300 total, and every boost is a Gate-D item
  with a dollar amount Mike approves [reach-math, distribution-and-algorithm].
- Transport failure is never reported as engagement zero, and a broken analytics transport is reported
  as broken rather than silently substituted with stale numbers [li-measurement, li-measurement-steward].
- Reports lead with the north star (booked ICP calls); impressions and followers corroborate only
  [li-measurement].

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-measure`
verifies the frontmatter name and JEV-FIRST MANDATE description, the opening JEV-first mandate, at
least three sub-skills of 400+ bytes, a ledger action for every stage-map row of this stage, that every
backticked path resolves, and no 12-word run shared with a third-party merge source. GREEN = all hold.
