# Reddit: the ramp before the right to post

Reddit is free, permanent, Google-indexed, and the fastest way to get banned. It is not a same-day amplifier: it is a 14-day account-building obligation that precedes any original post.

## Identity first

- Assert the signed-in Reddit identity before every outward action: read the user's own about payload same-origin inside the page and halt on mismatch. Never assume the signed-in user is Mike.
- One browser, one Reddit identity. The client lane's Reddit account is separate; never run both from one session and never inherit approval across the two.
- A dated observation of Mike's account state (2026-09-21) lives in `~/.aside/u/0/skills/user/linkedin-cross-platform/SKILL.md`. Re-read it before planning; it is state, not law.

## The karma ramp

| | |
|---|---|
| Cadence | 3-5 genuine comments a day, 15-20 minutes apart |
| Window | about 14 days to the first original post |
| Gate | comment karma above 10 and zero mod removals before any original post |
| Allowed | answering the actual question, one specific thing from operating experience, respectful disagreement |
| Banned | links, any product, company or brand name, any tool pitch |
| Kill switch | one removal or one suspension warning stops the ramp; do not repost, do not appeal |

Comments build the account; posts spend it. A zero-karma account posting a founder narrative is a ban, not a launch. Ramp comments are the one pre-approved exception in this stage once Mike has approved the ramp itself: reversible, capped at five a day, no link, no brand.

## Rules that survive contact

- No links in a post body, ever. If someone asks where the data comes from, that is a comment reply; comment links convert better because they read as an answer.
- No brand, product, company or self-promotion. Write as a practitioner sharing an observation.
- Native Reddit tone: casual, direct, framed as a question or discussion. No headers, no bullets, no LinkedIn voice.
- One subreddit at a time; cross-posting the same text is visible and flagged.
- "Zero custom rules" is not permission. Site-wide rules and a moderator's judgement still apply, and a vendor-looking post that survived is not evidence it was approved.
- Reply to every comment within four hours, with unique text per commenter. If a mod removes the post, do not repost.

## Per-sub reality (audited 2026-09-21, dated observations)

- Permissive with zero custom rules: r/SixSigma and r/LeanManufacturing. Comment freely; original posts allowed once the ramp clears.
- Ban-risk surfaces: r/ProjectManagement issues a permanent ban for links to blogs, tools, services or social media; r/humanresources bans anything a moderator judges to be advertising, including blogs; r/manufacturing says business representatives are not welcome; r/managers bans spam ads; r/consulting bans ads and AI slop. On those, reply-only and value-first at most.
- Dead or wrong: r/lean is banned site-wide, r/kaizen is a video game's subreddit, several lean/HR subs have been dead for years. Stale advice still recommends the first two.

Re-verify rules from the sub's own pages before any posting decision.

## Browser mechanics that work

The new UI defeats scripted reads: the generic browse path returns an indeterminate marker and a host-side HTTP read of the user payload gets 403. The working path is a logged-in tab fetching the sub's own JSON endpoints same-origin inside the page. A rules payload returning an empty array means zero custom rules, not missing data. A banned subreddit still returns data-shaped responses with undefined scores, so check the subscriber count is defined before believing any post list. Verify a join from the group page; a silent selector match is not an answer.

Absorbed from: reddit-and-groups, linkedin-cross-platform, lg-distribute.
