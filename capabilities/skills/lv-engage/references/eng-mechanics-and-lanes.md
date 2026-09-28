# Executor mechanics and lane fire rules

The executors in this stage are tools, not authors. Every one of them drafts, stages, or suggests; a human and the lane's approval rule decide what fires [viral-core].

## Executor map

- **comment-engine (`~/.hermes/commands/comment-engine.md`):** the 85%-deterministic commenting engine. PREP is not FIRE: it harvests candidates, drafts, and stages approval cards; only the human-approved line posts.
- **commenter (`~/.claude/agents/commenter.md`):** scrape recent posts, deterministic ICP qualification, drafts, approval card, then reload-verify after any post.
- **Ralph family (`/ralph`, ralph, prime-ralph, ralph-linkedin):** the iteration loop with architect verification. Use when a comment task needs a loop; the same approval gates stand.
- **patchright-linkedin-proofer:** the safe proofing path: read-only cookie probe, roster pre-warm, per-line APPROVE before every send, post-action audit.
- **Eden skills (comment-machine, comment-ambassador, personal-brand-lane):** cited by name, called through `~/.aside/u/0/skills/user/eden-mcp/SKILL.md`. comment-machine drafts and stages; the ambassador variant writes one comment per post through write_comment then stage_comment_card, and a skipped write is never staged [comment-ambassador].
- **Runners (li-distribution, li-distribution-runner, prime-ralph, ralph-linkedin, personal-brand-lane, personal-brand-lane@eden):** lanes and scheduled runs load this stage at run time and apply it inside their own caps; a runner never widens a cap.

## Browser mechanics that cost sessions (observed)

- The reply composer's submit needs a real mouse click at coordinates after centering the element; a synthetic element click does nothing [borrowed-attention].
- Unsubmitted composers persist and stack, so the next reply can land in a stale composer. Clear or confirm the composer before each reply [borrowed-attention].
- A reply renders nested inside its parent article, so "first article containing this author" can match your own thread and post to the wrong parent. Anchor on the intended parent and confirm via its reply counter [borrowed-attention].
- Default comment sort hides comments: switch to "most recent" before concluding a comment is absent [borrowed-attention].
- Throttle detection lives in `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md`; its caps bind every executor in this stage.

## Identity and lane fire rules

1. Assert the signed-in handle before any outward action (getMe-style identity read or the profile /in/ href). On mismatch, halt; never switch accounts to continue [profile-probe, viral-core].
2. The browser may hold Mike's and a client's LinkedIn at once; an account chooser showing both is live, and picking the wrong identity posts as the wrong person [profile-probe].
3. **Lane A:** stage comments; never publish. The lane admits OpenBot staging and stops there [personal-brand-lane].
4. **Lane B:** outbound comments fire only inside the sweep caps and the approval rule; evidence-led, no cast.
5. **Ideawake:** Coby's account and Coby's voice; nothing fires without Mike's explicit client approval [viral-core].
6. **Job lane:** comments support recruiter visibility; see lv-profile's job-search sub-skill for the routine [lucy-skills/linkedin-activity].
7. Anything outward that is not a staged draft is Gate-D: Mike's explicit yes per item [viral-core].
8. A throttle signature, a degraded surface, or a login/checkpoint/CAPTCHA is a hard stop: report and do not retry [engagement-comment-led, rig-job-search-campaign].

## Failure honesty

An executor that cannot read comments reports zero with the transport state named; it never invents replies, counts, or "responded to N comments" lines [alfred-comment-engagement]. A runner that cannot do its job emits one explicit BLOCKED line and stops rather than substituting a description for the real artifact [alfred-comment-engagement].

Absorbed from: alfred-comment-engagement, borrowed-attention, engagement-comment-led, comment-ambassador, personal-brand-lane, profile-probe, viral-core
