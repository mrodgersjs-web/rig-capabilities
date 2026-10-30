# LinkedIn post gates: external evidence

Tier key: **(a)** platform-official  **(b)** measured study with numbers  **(c)** practitioner opinion.
Never present (c) as (b). Every gap below is stated as a gap rather than filled with an opinion.

Compiled 2026-09-27. Two of these correct long-standing practice in this repo.

---

## Correction 1: the link penalty is on the preview card, not the URL

Practice here has been "zero external links in body" (CG-06). The measurement says that is the wrong rule.

| Condition | Median impressions |
|---|---|
| Link preview card attached | **414** |
| No link in post | 795 |
| Bare URL typed in body | **858** |
| Link-free (control) | 786 |

- **(b)** MagicPost, "Do External Links Kill Your LinkedIn Reach?", 566,957 posts with synced analytics from a 1,207,853 corpus. https://magicpost.in/blog/linkedin-external-links-reach (2026-06-05)
- **(a)** LinkedIn Help a1339724 ("LinkedIn relevance"): distribution tapers "low-quality and unsafe content". **No rule naming links is published anywhere.** https://www.linkedin.com/help/linkedin/answer/a1339724
- **(a)-relayed:** LinkedIn team guidance relayed by Buffer: "Will LinkedIn penalize external links? No." https://buffer.com/library/linkedin-algorithm (2025-12-15)

**The conflict, not papered over:** measured data says the preview card costs ~48% while a bare body URL costs nothing; LinkedIn publishes no link rule at all. Both hold because the cost can be behavioural (people click away, dwell and engagement fall) rather than a ranking rule. The defensible position is "no preview card", not "LinkedIn downranks links", which is not evidenced.

Conflicting magnitudes elsewhere, reported as a spread not a single number: van der Blom 2024 25-35% and 2025 ~60% reduction (both **(b)-secondhand**, primary PDFs gated behind sales.richardvanderblom.com and not read). Do not cite those figures as primary.

**Honesty clause from the largest source itself:** MagicPost "did not measure first-comment links specifically" and calls the first-comment workaround "a reasonable but unmeasured workaround."

---

## Correction 2: question endings do nothing

The house habit of closing on a conversation prompt is folklore.

- **(b)** AuthoredUp, "LinkedIn Engagement Rate in 2026", n=417,550: posts ending in a question **2.57%** median ER vs **2.55%** without (n=63,373 with, 354,177 without). https://authoredup.com/blog/how-to-calculate-engagement-rate-on-linkedin (2026-09-08)
  Source's own line: *"The 'always ask a question at the end' advice? The data doesn't support it."*
- Also: question openers underperform statement openers (2.38% vs ~2.5%).

---

## Saturation: the AI lane is the worst lane to post into

- **(b)** MagicPost, "LinkedIn Engagement Rate by Topic: 44 Topics Ranked", **41,127 posts**: AI-topic posts earn **0.24%** median ER vs followers, **2nd lowest of 44** topics (top: Graphic Design 1.16%). https://magicpost.in/blog/linkedin-engagement-rate-by-topic (2026-06-05). Vendor's own dataset, individual creators, last 12 months, ER = (likes+comments)/followers. Authors note AI posts still get healthy raw likes because large accounts write them, so this is an efficiency finding, not a raw-reach finding.
- **(b)** Pangram, "AI in Your Feed", **1,002,627 posts**: **>40% of longform (>250 words) LinkedIn posts** flagged fully AI-generated; LinkedIn is ~1/3 of scanned items but **62% of all flagged AI content**. https://www.pangram.com/blog/ai-in-your-feed (2026, window Apr-Jul 2026). Opt-in sample, detector-based.
- **(b)** CoSchedule, 900 marketing professionals: **29%** name "AI-generated content flooding channels" their top 2026 concern (2026-02-17).
- **(b)** 2021 Edelman-LinkedIn: **38%** of decision-makers say the market is oversaturated with thought leadership; **47%** say most of it is not made for their needs. https://www.edelman.com/sites/g/files/aatuss191/files/2021-09/2021_EdelmanLinkedIn_B2B_ThoughtLeadershipImpact.pdf
- **(a)** LinkedIn Engineering: the 2025-26 LLM retrieval stack is explicitly intended to reduce "engagement bait and generic posts". Near-duplicate content must win a relevance contest against its own clones. https://arxiv.org/html/2510.14223v1 (2025-10)

**Measured advice:** sharpen the angle, do not change the subject. The rate is the warning.

**Gap:** no measured source counts "why AI pilots fail" posts in a window and links post-count to reach decay. No measured source validates a pre-post crowding threshold. The pre-flight count is a practitioner heuristic (**(c)**), which is why the gate returns RANK rather than a hard block.

---

## Audience / ICP match is a distribution determinant, not a nicety

- **(a)** LinkedIn feed retrieval "serves suggested content from outside of the member's network **based on the member's topical interests**"; semantic matching is by post text as concepts. https://arxiv.org/abs/2510.14223 (2025-10-16) and https://arxiv.org/pdf/2412.20366 (2024-12). **The words of a post decide the audience it gets.**
- **(a)** LinkedIn Help a1499047 ("Suggested posts in feed"): out-of-network distribution requires content **"not overly promotional in nature"**, that provides "context for the topic", and where **"all aspects of the post relate to one another."** https://www.linkedin.com/help/linkedin/answer/a1499047. This is the criterion CG-10 enforces, and it is stronger evidence than any blog's algorithm-hacks list.
- **(b)** Edelman-LinkedIn (n=1,300+): **30% of decision-makers and 35% of C-suite removed a company from consideration** after thought leadership they judged poor, un-insightful, or **not relevant**. Irrelevance is not neutral, it is negative.
- **(b)** LinkedIn B2B Institute + Bain + NewtonX (500+ senior buyers): brands are **>20x more likely to be bought** when the whole buying group is familiar with them at the outset. LinkedIn's Mimi Turner, verbatim: reach, traffic, clicks and engagement "no longer guarantee the growth we are looking for, because that system was built on visibility"; "existing metrics no longer ladder up to being bought." https://www.marketingweek.com/b2b-marketing-metrics-linkedin/ (2026-03-27). **Strongest citable source for vanity vs meaningful metrics, because it is LinkedIn's own research programme saying it.**

**Gap:** no measured source directly correlates an organic post's engagement demographics with its conversion. The LinkedIn papers give the mechanism; Edelman and Bain give adjacent measured effects. Any specific "non-ICP engagers converted at X% vs Y%" figure is practitioner-claimed only.

---

## Format and length (house band is policy, not optimum)

- **(b)** AuthoredUp, 3M+ posts, personal profiles Mar 2025-Feb 2026 (reach / engagement vs format average): **document-carousel 1.39x / 1.30x** (only format strong on both), image 1.20x / 1.33x, text-only 1.07x / 0.78x, **poll 1.78x / 0.37x (reach trap)**, video 0.86x / 0.93x (reach -36% YoY). https://authoredup.com/blog/best-performing-content-on-linkedin (2026-09-02)
- **(b)** AuthoredUp, 372,126 posts: ER peaks at **2,001-2,500 chars (2.67%)**; median impressions keep climbing to **2,501-3,000 (1,400)**. 1-400 chars: 575 impressions. **Reach and engagement peak at different lengths.** https://authoredup.com/blog/linkedin-character-limit (2026-08-12)
- **(b)** Socialinsider, 1.3M posts from 16,645 **company pages** Jan 2024-Dec 2025: native document 7.00% ER ... **link 3.25% (lowest)**. https://www.socialinsider.io/social-media-benchmarks/linkedin (2026-03-16). **Scope caveat: company pages. Do not mix with the AuthoredUp personal-profile tables.**

---

## Reposts: the measured reason to skip the self-repost lever

- **(b)** MagicPost, "How to Repost on LinkedIn": median likes **original 28, repost with thoughts 8, one-click repost 2**. https://magicpost.in/blog/how-to-repost-on-linkedin (2026-06-05)
- **(b)-secondhand** van der Blom Jan 2024 data via https://www.thinklikeapublisher.com/linkedin-algorithm-secrets-the-archive/ (2026-08-02): an instant repost boosts the original by ~4% but does **not** increase the reposter's visibility; a repost-with-thoughts reaches 8-10% of typical reach, 15-20% with 10+ engagements; thoughts should be >=100 words or it underperforms 3x.
- **(c)** the "self-repost gives +20-40% reach" claim is a Reddit agency anecdote with no n and no method. **Do not present as measurement.**

**Gap, named:** "repost" in these sources means resharing via the Repost button. No measured source covers republishing your own content as a brand-new post. Say so rather than borrow the reshare numbers.

---

## Groups: no measured reach figure exists

- **(a)-secondhand** LinkedIn's published feed description lists group posts as a feed source but does not state different ranking criteria.
- **(b)-weak** getcreator.io (2026-03-31): ~2.3M groups, **~4% with weekly engagement** (vendor crawl estimate, methodology unpublished), engagement "collapsed ~73% 2019-2023".
- **(c)** group content is members-only by default and **cannot be reshared outside the group**; group posts surface in home feeds "rarely".

**Defensible statement:** groups are a separate members-only surface with low and unmeasured reach. **No measured source found for typical group-post impressions.** Our own single observation (5 groups, ~102K nominal members, 0 reactions and 0 comments across all five) is one datapoint and must be reported as one.

**Excluded as untrustworthy:** getcreator.io's "LinkedIn internal 2026 engagement report" and "LinkedIn Creator Lab 2026 study" (unverifiable attributions to non-public sources), and LinkBoost's "Thoughts of Muskan 2026 B2B Strategy Report" (its hyperlink resolves to `example.com`, a placeholder). These are the kind of thing that gets laundered into doctrine.

---

## Things measurement does NOT support

1. **"Golden hour" comment velocity permanently caps reach.** No measured source found. Every source asserting it is tier (c) self-reference. LinkedIn's own "posts resurface days or weeks later" contradicts the strong form. **The whole 90-minute window premise of the campaign rests on this unmeasured claim.**
2. **"A comment is worth 15 likes."** No traceable primary source. AuthoredUp's 621,833-post analysis puts comments at roughly 2x a like, saves roughly 2x a comment (secondhand).
3. **Comment-link CTR.** No measured source. Sprout's own methodology note explains why: LinkedIn analytics cannot capture clicks on a link placed in a comment. Use UTMs or accept you cannot see it.
4. **Group-post reach.** No measured source.

Sprout's "put the link in the comments" test (2023-04-26, n=8 posts, one brand, one month) used **different copy** in each condition, so format and copy are confounded. It is a test of two whole post strategies, not of link placement. https://sproutsocial.com/insights/linkedin-link-in-comments/
