---
name: sk-lessons
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. The lessons-learned pipeline that feeds the community: harvesting from memory, chat history, the Jake Studio vault and a daily internet scout; generalizing for public consumption; and publishing dated, sourced lessons into the classroom. USE WHEN the Lessons Learned library needs content, when a daily scout is running, or when an internal lesson should become public. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, lessons]
outcome: "content-publishing: a dated, sourced lessons library where every entry carries a trap, a rule, and honest lineage (member-observed / RIG-internal / public-source)"
done_when:
  - grep:capabilities/skills/sk-lessons/SKILL.md:strip credentials, personal names, client names
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-lessons
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "0"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-lessons: the lessons-learned engine (harvest, generalize, publish)

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this lesson publishable, is the lineage honest, is this source trustworthy enough to cite. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check atomic.claim --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `atomic.claim` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use continuously; the daily scout runs from here. sk-content owns WHERE lessons sit in the classroom; this stage owns what gets harvested and generalized. Not for community engagement (sk-engagement).

## Procedure

1. **Four harvest sources**: (a) RIG internal ledgers (memory, `~/.rig/jake/kpi/lessons.jsonl`, Jake Studio vault `Memory/lessons.json` and Doctrines), (b) chat/session history via recall, (c) community run records (de-identified), (d) a daily internet scan (surfaces: engineering blogs, postmortems, HN threads about AI/automation failures).
2. **Generalize before publishing**: strip credentials, personal names, client names (Ideawake/Coby/Jacob and any member), job-search and personal-finance detail, internal paths. A lesson that only works with the stripped detail is not portable and does not ship.
3. **The lesson shape**: title (specific), the trap (what goes wrong, concrete), the rule (what to do instead), lineage (internal id or URL + date).
4. **Screen with Jev `atomic.claim`**: one falsifiable rule per lesson; compounds are split.
5. **Publish with dates and lineage labels**; corrections are appended, never silently edited. A lesson overturned later gets a dated correction note.
6. **Quality bar for the daily scout**: at most 1-3 lessons per day; the scout reports empty days as empty, never fills quota with filler.

## Hands the next stage

`lessons-batch.md` per day: the candidates harvested, the ones generalized, the ones rejected with reasons, and the published ids. sk-gate screens each before it goes live in the classroom.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-lessons.md` (local corpus, not republished).

(no laws captured yet for this stage - see data/corpora/skool/BUILD-LOG.md for capture status)

## Where the creators disagree

(none recorded)

## Creator result claims (UNVERIFIED, never repeat as fact)

(none recorded)

## Platform mechanics (Skool's own behavior)

(none recorded)

## RIG application (RIG synthesis, not corpus claims)

The lessons-learned pipeline is a RIG invention, not corpus doctrine. Public-source candidates live in notes/lessons-harvest.md (18 generalized from internal ledgers).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/daily-scout.md` | running the daily lessons-learned internet scout |
| `references/lesson-shape.md` | shaping one lesson for publication |

## Hard rules

- Publication of any lesson is Gate-D per batch (draft freely; the publish step is his).
- Never publish a lesson whose lineage is internal-only without generalizing; never publish member stories without the member's yes.
- A scout finding is never repeated as fact without its URL and date; stale advice is labeled dated.
- The lessons library is a living document: corrections are dated additions, not rewrites.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-lessons/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-lessons` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
