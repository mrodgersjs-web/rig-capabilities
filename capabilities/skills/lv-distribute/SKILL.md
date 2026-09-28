---
name: lv-distribute
description: >-
  Take one proven LinkedIn asset beyond the feed: cross-platform repurposing to Reddit, LinkedIn Groups, Substack, X, trade publications and podcasts, newsletter and owned audience, and the per-channel route-back to Mike's profile or site. Use when a post has proven itself and Mike asks to repurpose, cross-post, syndicate, pitch an outlet, or run the weekly multi-channel pass. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage (channel fit for an asset, adaptation-quality call on a per-channel version, comment gate on group and Reddit comments, pitch screen) goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, distribute, cross-platform, repurpose, route-back]
outcome: "content-publishing: one proven asset reaches each buyer surface in that platform's own grammar, with a compliant route-back and per-channel attribution"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-distribute
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "8"
---

# lv-distribute: one asset beyond the feed

## JEV-first mandate (read first)

The typed judgments in this stage go to Jev (TypeSafe's System One) through `rig-s1gate` BEFORE any frontier LLM call: which channel an asset actually fits, whether a per-channel adaptation is genuinely re-architected rather than copy-pasted, whether a LinkedIn Group comment passes (rubric `comment.linkedin`), whether the repurposed version passes (`post.linkedin` or `post.viral`), and whether an outlet is worth a pitch.

- Command: `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
- Rubrics that exist: `post.linkedin` (Lane B), `post.viral`, `post.eden`, `comment.linkedin`, `doctrine.surface`. Where no stored rubric fits (a Reddit comment, a pitch email), the verdict is DEFERRED to Mike.
- Fail closed: classifier down, tool error or missing rubric means DEFERRED. Never a guessed verdict, never a frontier model standing in for the judgment.
- An advisory PASS is not permission to post, pitch or send. Gate-D covers every outward step in this stage.
- Any claim that "Jev judged X" cites the decision id from `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use when a post has proven itself (beats the account baseline, or Mike names it) and the ask is to take it off LinkedIn: repurpose it, cross-post it, run the weekly multi-channel pass, pitch a trade publication or a podcast, or build the newsletter version.

Do not use for writing the LinkedIn post (`lv-draft`), golden hour and in-feed amplification (`lv-launch`), comments on other people's posts (`lv-engage`), deciding whether a reader is worth a DM (`lv-outreach`), or reading results (`lv-measure`). Distribution that invents leads gets someone pitched without a fit card. A run that does not distribute is a skip, not a failure.

## Procedure

1. **Pick the asset and the claim set.** Extract the claims ledger: every claim that must survive, with its evidence and its evidence class. Distribution is optional per asset; if the asset is weak, skip.
2. **Read the queue and the account state before planning.** The publication queue is `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/specs/distribution-targets.json`, one row per outlet with its own verification date. Dated account state (subreddit rules, connection rows, signed-in identities) lives in `~/.aside/u/0/skills/user/linkedin-cross-platform/SKILL.md`. A fresh read of the live page beats both.
3. **Check first-run exclusivity first.** If any outlet in the queue carries `first_run_required`, that piece is written and submitted before the LinkedIn version exists. Intention does not survive a publish button; `first_run_exclusivity` enforces it by date.
4. **Run the channels in cost order:** LinkedIn Groups, then X, then owned email, then Substack (weekly digest, never per post), then Reddit (comments daily under the ramp, original posts only once the ramp clears), then trade publications (2-4 week lead), then podcasts (relationship, evergreen). Stop when the budget of attention is out.
5. **Re-architect per channel** (`references/repurpose-method.md`): different opener, ordering and depth per platform, same claims. Near-identical text on two channels within 48 hours is a silent delivery failure.
6. **Apply the route-back map per channel** (`references/channel-order-and-gates.md`): where the LinkedIn or site reference is allowed differs by platform, and a uniform "link back to my post" is a ban on one channel and a rejection on another.
7. **Gate before anything goes out:** `adapt_not_copy`, `route_back_compliance`, `pub_target_verified`, and a distinct `utm_source` per route-back that is already in the site's measurement allowlist.
8. **Gate-D the batch.** Every group post, Reddit post, X post, newsletter issue and pitch email is a batch-level approval naming recipients and exact text; a blanket "approve everything" does not clear a batch.
9. **Report movement, not activity.** The only output is a LinkedIn or site metric that moved and can be attributed to a named channel. "We posted in four places" is an input count.

## Quality bar

- Every channel version passes the claims ledger: all claims present, none exaggerated beyond the source.
- No two versions are near-identical; each respects the platform's native grammar and length.
- Every route-back sits where that platform tolerates it, and every link carries a distinct allowlisted `utm_source`.
- Every number carries an evidence class (`[primary] [secondary] [creator] [claimed] [ours]`); a `[claimed]` figure never reaches client or RIG copy as a fact.
- The signed-in identity was asserted before each outward action, and the batch that went out is the batch Mike approved.
- The report names what moved, what did not, and every channel skipped with its reason.

## Lanes

- **Lane B (RIG B2B):** the default lane here. Buyer surfaces are the four declared verticals (consultancies, software teams, engineering firms, Denver businesses); engineering is the best-covered publication vertical and Denver-local has zero verified routes, recorded as a gap.
- **Lane A (personal brand):** same mechanics, its voice and register carried into each adaptation; the proprietary cast stays inside the lane's rules and never rides into a third-party surface as a mascot.
- **Ideawake client lane (Coby's account):** every channel is a second person's reputation. Identity asserted, nothing fires without Mike's explicit client approval, and the client's own Reddit and X accounts are separate lanes from Mike's.
- **Job-search lane:** distribution of job-lane material stops at recruiter-visible surfaces; no commercial CTA.
- **Lane C (a minor's content):** out of scope at every approval level. No cross-distribution, no offer, no CTA, no funnel, no auto-schedule.

## Tools and runners

The stage map assigns no tool or runner rows to lv-distribute; these are the engines the procedure calls.

| name | kind | path | when to call |
|---|---|---|---|
| distribution-targets | register | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/specs/distribution-targets.json` | before any pitch: the publication queue with contacts, word counts, `first_run_required` and `contact_verified_on` dates |
| linkedin-mega | runner | `~/Developer/rig-linkedin-studio-luca/linkedin-growth-os/harness/mega/linkedin_mega.py` | the distribute stage of the optimizer harness, before touching anything |
| linkedin-cross-platform | account state | `~/.aside/u/0/skills/user/linkedin-cross-platform/SKILL.md` | dated subreddit rules, Eden/Ayrshare connection rows, signed-in identities |
| linkedin-site-mechanics | tool | `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md` | before every LinkedIn Group post: the composer fails silently and has shipped title-only posts |
| linkedin-analytics-tracker | tool | `~/.aside/u/0/skills/user/linkedin-analytics-tracker/SKILL.md` | whether any of it worked; per-channel attribution lands here |

## Sub-skills

| file | covers |
|---|---|
| `references/repurpose-method.md` | the claims ledger, per-platform re-architecture, voice fidelity, fan-out ratios |
| `references/channel-order-and-gates.md` | the cost order, the four gates, the route-back map, the hard stops |
| `references/linkedin-groups.md` | group mechanics, per-audience adaptation, what verifies a group post |
| `references/reddit-ramp.md` | the karma ramp, per-sub rule reality, kill switch, browser mechanics |
| `references/substack-x-and-email.md` | Substack as a weekly digest, X via the API carrier, the owned list, newsletter curation |
| `references/trade-and-podcasts.md` | first-run exclusivity, editorial writing rules, the pitch shape, podcast targeting |

## Hard rules carried forward

- Nothing sends from this stage without a batch-level Gate-D approval naming the recipients and the exact text; a blanket approval does not clear a batch. [lg-distribute]
- Adapt, never copy-paste: near-identical text on two channels inside 48 hours is a silent delivery failure and the gate is RED at 0.90 similarity or above. [lg-distribute, linkedin-cross-platform]
- A Reddit post body never carries a URL, and no product, company or brand name appears; the only LinkedIn surface a Reddit body may reference is the author bio. [reddit-and-groups, linkedin-cross-platform]
- Reddit order of operations: comment for about 14 days first; an original post requires comment karma above 10 and zero mod removals. [reddit-and-groups, linkedin-cross-platform]
- One removal or one suspension warning stops the Reddit ramp; do not repost and do not appeal. [reddit-and-groups, linkedin-cross-platform]
- "Zero custom rules" is not permission for self-promotion; site-wide rules and a moderator's judgement still apply. [reddit-and-groups]
- Assert the signed-in identity before every outward action and halt on mismatch; the browser's active X session is a 15-year-old's recruiting account, so X writes go through the API carrier to the linked handle only. [lg-distribute, substack-and-x, linkedin-cross-platform]
- Lane C content is never cross-distributed at any approval level. [lg-distribute]
- Trade publication pieces carry no product, no company and no link; bio line only, and a first-run outlet is written before the LinkedIn version. [trade-publications, lg-distribute]
- Ghost-written client bylines are refused at editorial outlets that require direct author contact; the client confirms in writing or the pitch does not go. [trade-publications]
- Never count a route-back as a result: attempts are inputs, and only an attributed metric that moved is an output. [lg-distribute, linkedin-cross-platform]
- Every outbound link carries a distinct `utm_source` already in the site's measurement allowlist; an unreviewed value collapses into "other" and makes the channel unmeasurable. [lg-distribute]
- No fabricated engagement anywhere: bought comments and pods re-classify the real audience. [lg-distribute, linkedin-cross-platform]
- Every number carries its evidence class; "50-500K readers per outlet" is a `[claimed]` figure and must never reach copy as a fact. [lg-distribute]
- Never post identical copy to two groups; LinkedIn detects cross-posting and the duplicate gate fails the batch. [linkedin-cross-platform, reddit-and-groups]
- X copy is written to 280 characters until Premium on the linked handle is confirmed by a human; the checkbox is never ticked on a guess. [substack-and-x, linkedin-cross-platform]
- Nothing is scheduled into Substack until one issue lands and is read back at the publication. [substack-and-x, linkedin-cross-platform]

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-distribute` is GREEN only when the frontmatter names the stage and carries the mandate, the body opens with the JEV-first section, at least three 400-byte sub-skills sit beside `ledger.md`, all 8 stage-map rows have a ledger row with a named action, every backticked path resolves, and no third-party 12-word run was copied.
