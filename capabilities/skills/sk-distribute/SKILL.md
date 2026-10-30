---
name: sk-distribute
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Taking community content and lessons to the channels where the member already is: LinkedIn, X, Reddit, Substack, YouTube, and the per-channel adaptation rules and route-back. USE WHEN a piece of classroom content or a lesson should reach beyond the community, or when the advertising plan is being run. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, distribute]
outcome: "content-publishing: each piece reaches its channels with per-channel adaptation done and one clear route back to the community, measured by joins per piece"
done_when:
  - grep:capabilities/skills/sk-distribute/SKILL.md:Route-back rule
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-distribute
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "0"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-distribute: multi-channel advertising of community content

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this channel a fit for this piece, is the adaptation quality, is this comment/pitch acceptable. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check post.viral --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `post.viral` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use when content has cleared sk-gate and the goal is reach beyond the community. Not for growth mechanics inside a channel (sk-growth) or the gate itself (sk-gate).

## Procedure

1. **One piece, adapted per channel**: never raw cross-post. LinkedIn gets the professional frame and no raw links in the body (first comment carries the link); X gets the compressed claim; Reddit gets the value-first long version with the link only where the subreddit allows; Substack gets the full narrative; YouTube gets the walkthrough.
2. **Route-back rule**: every channel piece ends with one next step into the community (the lead magnet or the About page), one link, one action.
3. **Community-first comment rule**: comments on others' posts are positive-only - validate the point, add one insight, at most one soft link. (RIG's measured lesson: untargeted following/engagement suppresses reach.)
4. **Pacing**: the corpus and RIG's own measurements both say burst patterns suppress reach; spread actions with jitter, hold daily ceilings.
5. **Measure joins per piece per channel**, not impressions; a channel that earns impressions and no joins gets its route-back rewritten before it gets cut.

## Hands the next stage

`distribution-log.md`: piece id, channels used with adaptation notes, the route-back link, joins per channel. sk-measure reads the log for the funnel.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-distribute.md` (local corpus, not republished).

(no laws captured yet for this stage - see data/corpora/skool/BUILD-LOG.md for capture status)

## Where the creators disagree

(none recorded)

## Creator result claims (UNVERIFIED, never repeat as fact)

(none recorded)

## Platform mechanics (Skool's own behavior)

(none recorded)

## RIG application (RIG synthesis, not corpus claims)

Cross-channel distribution laws pending capture from the remaining channel videos (Magnetic Founders covers the YouTube funnel: 600 -> 8.3K subscribers).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/channel-adaptation.md` | adapting one piece for a named channel |

## Hard rules

- Every public post is Gate-D before it goes out; drafts and adaptation are free.
- No engagement pods, no bought reach, no link spam; comment rules are positive-only.
- Client-lane accounts (Ideawake) are never used to advertise this community.
- Reddit and group rules are read before posting; a subreddit's rules beat this skill's procedure.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-distribute/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-distribute` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
