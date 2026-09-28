# Sourcing and qualification

Who is worth an outreach slot, when they are worth it, and what the message anchors to.
Nothing here sends. The output is a list the convert step is allowed to touch.

## The gate before any copy

"Targeting certainly kills more campaigns than copy ever does" [creator, lg-qualify]. When
replies are low, audit this stage before rewriting anything. Fit without an observed artefact is
a guess; the `icp_evidence_present` gate refuses it.

## ICP fit card (one row per candidate, fields not optional)

| field | what goes in it | fails when |
|---|---|---|
| `who` | name + vanity slug taken from a real URL | a guessed slug (a constructed /in/ slug 404'd on this account) |
| `role_fit` | title, seniority, decision right, budget signal | title alone |
| `company_fit` | size, industry, revenue model, geography | unstated |
| `evidence[]` | kind + url or observed_in + quote; kind from post, comment, hiring_page, funding, role_change, award, event, company_post, website_page, article, job_listing, launch | empty, or kind=job_title |
| `timing` | a hot-signal score or `none` | a fit with no timing sold as hot |
| `fit_verdict` | `fit` or `no_fit`, no third value | maybe, warm, watch |
| `why_rejected` | required on no_fit | a rejection nobody can learn from |

Verdict shape: a direct yes or no with a reason. Prose hedging is a no_fit disguised as work.
Record fields that did not render as `unknown`, never as absent: a missing About section is not a
missing budget [icp-fit-card]. Fifty people screened to produce four cards is normal; twenty cards
from a 2,000-row list means the filter is not filtering.

## Hot signals: the timing half of fit

Tier 1 (budget or pain just changed): hiring the role you replace ("a red hot lead" [creator]),
a fresh funding round, end of financial year approaching, a new senior hire in the function, a new
product or market. Tier 2 (they showed up to the topic): engaged with your post (reach out within
5 minutes [creator], a claimed window), engaged with someone else's post on the problem, follows a
competitor's page (discounted by a claimed 70-80% fit decay on scraped follower lists), joined a
group or event on the topic. Tier 3: the reply itself is qualification; the ABCD letter is
self-segmentation [hot-signals].

Not signals: follower count, job-title keywords alone, generic engagement, anyone's promo post.

## Sourcing channels

Four safe routes [sourcing-channels]:

1. **Existing 1st-degree network** (warmest): filter on role fit, then mutual touchpoint, then
   time-since-touch; someone untouched for 24 months is functionally cold. Evidence may be a
   profile_view, a comment, or a post observed in your own thread.
2. **Content-driven inbound**: the sourcing is the content; the DM answers an engagement. Highest
   leverage for Lane B, though the gap over cold sourcing is unproven on RIG's account.
3. **Sales Navigator**: default for cold lists of 100 or more; use the posted-in-last-30-days
   filter and the seniority filter.
4. **Cold-SalesNav + video/voice on accept**: blank connect, wait 2-3 business days, then a video
   (up to 60 seconds, shoot for 30) or voice note that opens on them, not on you. The accept is
   the qualification gate; work per prospect is about 5 minutes.

Without Sales Navigator [sourcing-without-salesnav]: read the competitor audience natively via the
right-rail "From your industry" cluster; read in-topic commenters on 3-6 named creators' posts
(comment text beats likes, writing is the higher-cost act); use groups, communities and events
(manual on purpose); schedule intent reads against named company pages. Hard navigation to
LinkedIn post search is soft-blocked on this account: use the native search box, the "Past week"
chip, and never guess a vanity slug.

Refused sources, named and unavailable: third-party follower-list scraping, BuiltWith plus Clay
enrichment scraping, Growth Machine with voice cloning, cross-platform follower scraping
[sourcing-channels, sourcing-without-salesnav].

## Relevance bridge (what the message anchors to)

Three parts in order [relevance-bridge]:

1. **Signal**: one specific current public artefact from their world, last 14 days default (post
   with a challenge, comment, hiring post, company announcement; 30 days for company changes,
   awards, role changes). Not a 4-year-old milestone.
2. **Connection**: what you understand about the world that signal implies. No pitch, no service
   list, their language.
3. **Useful thing**: an insight, a framework, or a reframing question they can use in the next
   five minutes. Not a meeting request.

Model B (trust thread) upper bound: 10-15 accounts per month (about 30 minutes of research plus
3 hours of value prep per account). Above that the bridge work dilutes.

## Intent tracking

Watch named accounts' hiring and launch pages daily, own-post engagers every 30 minutes for four
hours after publish then daily, in-topic commenters 1-2x weekly, and the right-rail industry
cluster weekly. Output goes to the existing kanban and the staged envelope, never a parallel list
file. An empty watcher result is more often a broken watcher than an absent signal: name the
surface tried and what came back. An intent hit produces a card; a card produces a draft; the
draft sends only under batch Gate-D [intent-tracking].

## List-quality bar

Export a list where 90% of the people look like today's clients; a clean list of about 500 ICP
prospects outperforms 5,000 generic ones [creator, lg-qualify]. `icp_ceiling` refuses a filter
passing more than 60% of a list over 2,000 rows. Wrong seniority, industry, company size or
revenue model sinks the campaign; name the field that failed on a no_fit. Fit is not consent: this
stage never authorizes a send.

Absorbed from: lg-qualify, icp-fit-card, hot-signals, intent-tracking, relevance-bridge,
sourcing-channels, sourcing-without-salesnav.
