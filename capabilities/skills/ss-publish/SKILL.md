---
name: ss-publish
description: >-
  Publication setup and the publish action on Substack: welcome emails, About page install, sections, SEO basics, paywall placement, send settings and the audience radio. USE WHEN setting up or repairing a publication, before any send, or when a post must be updated after publishing. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, publish]
outcome: "content-publishing: the publication's sales surfaces are set, and every send goes out to the intended audience with the verified text"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-publish/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-publish
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "14"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-publish: publication setup, settings and the send

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: is the welcome email ready, is the About page install exact, is this send's audience correct. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check website.buyer --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `website.buyer` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use once to set up the publication and then on every publish or update. The content is decided upstream; this stage installs and sends.

## Procedure

1. **Assert the account**: rigoperator.substack.com is owned by the Substack account on rodgemd1@gmail.com; mikerodgers317 is owned by mike@rodgersintelligence.com. Confirm the dashboard's publication before any write.
2. **Sales surfaces first**: rewrite the free, paid, imported and founding welcome emails and install the About page (text approved by Mike) before promoting anything.
3. **Sections**: one publication, 2-3 sections matching the pillars. Do not open a second publication for a second topic.
4. **SEO basics**: keyword-bearing title and H3s on how-to and teardown posts; the left-panel SEO title and description set per post.
5. **Before Send**: check the Audience radio. rigoperator's dialog has defaulted to "Paid subscribers only"; the button must read "Send to everyone now" for a public issue.
6. **After Send**: read the public page back (title, first paragraph, cover image, og:image) and confirm the author copy arrived.
7. **Updates to live posts**: Update, audience unchanged, no re-send; word-compare the body before and after.

## Hands the next stage

Published URL plus the read-back evidence. ss-notes and ss-distribute take the URL; ss-measure logs it.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-publish.md` (local corpus, not republished).

- L1. Rewrite the welcome email before you promote anything: it is the first thing a new subscriber reads and the place to introduce your paid tier. CLAIM(W3jen6QERo8, mNWXLFbK78o, xZtrPtlccBE) | channels: 3 | status: consensus
- L2. Treat the about page and welcome email as your two sales documents, and answer who you are, what they get, and whether they belong in the first 200 words. CLAIM(W4rXKY5h6Fk, U0IWoCaBw_o, k3hbRtfpZ84) | channels: 3 | status: consensus
- L3. Put the paywall at 50 to 60 percent of the post, at the exact point where the story ends and the how-to begins. CLAIM(GxC2VEWFhrg, SzJlV4PVvn8, 9tjmiFAXzzI, k3hbRtfpZ84) | channels: 2 | status: consensus
- L4. Paywall different content, not better content: free material builds belief in your expertise, paid material hands over the shortcut or the asset. CLAIM(6PguVWHtnlw, 9aTSqDpUHQg) | channels: 2 | status: consensus
- L5. Keep one publication and organize it into sections used as content pillars, three to seven of them, instead of starting a second publication. CLAIM(3Qh3V8E3WjE, aDqcuK3bOqU, TDwX1rRjcLM, eJyj92oulOs) | channels: 2 | status: consensus
- L6. Give a podcast its own section so readers can subscribe to it or opt out of it without leaving your whole publication. CLAIM(BRXIY1GJJ7s, MhrSQpnY20c) | channels: 1 | status: single-source
- L7. Run interview episodes as a growth channel: every guest brings a network that will share your content. CLAIM(C4IO3Yd4t4c, 4IEBRt8X2f0) | channels: 2 | status: consensus
- L8. Never delete a podcast before exporting your data; deleting a podcast has taken whole publications down with it. CLAIM(wEcOTy2gKcA, GSGOISFfmt0) | channels: 2 | status: consensus
- L9. Optimize a share of your posts for search with keyword-rich titles and subheadings, because one good post keeps returning new subscribers for months. CLAIM(IPB-9owShKY, 5W0tys60VrI, mNWXLFbK78o) | channels: 3 | status: consensus
- L10. Know the send settings before you hit publish: web publishing and email sending are separate choices, and a paywalled post defaults to paid subscribers. CLAIM(KrtBd8dnRSw, Be3px_oTo1s) | channels: 2 | status: consensus
- L11. Customize all four welcome emails (paid, free, imported), and remember that drip campaigns override them once unlocked. CLAIM(j67SabtPjGA, mNWXLFbK78o) | channels: 2 | status: consensus
- L12. Before importing a subscriber list, rewrite the welcome-to-imported-subscribers email, because it fires the moment the import lands. CLAIM(dlbvoyg448I, j67SabtPjGA) | channels: 2 | status: consensus
- L13. Cross-publish posts with embedded video to YouTube, so Google and AI search see you covering the same topic from more than one surface. CLAIM(As2CPh3N1dM) | channels: 1 | status: single-source
- L14. Work the notes feed daily, three to four notes a day alongside one weekly article, because notes are where followers start. CLAIM(9tjmiFAXzzI, mHRJfOWzdJQ) | channels: 1 | status: single-source

## Where the creators disagree

How much SEO work Substack deserves. For: SEO-structured posts bring readers for months and search is one of the few autopilot traffic sources. CLAIM(IPB-9owShKY, 5W0tys60VrI)
Against: Substack is treated as news rather than evergreen, so ranking is weaker than a normal website and a second site should carry the SEO.

How hard to paywall. For a selective paywall at the how-to line: CLAIM(GxC2VEWFhrg, 6PguVWHtnlw) as in L3 and L4. Against hiding work: leave content open and monetize elsewhere, because paywalls turn casual readers away and subscriber conversion is tiny.

## Creator result claims (UNVERIFIED, never repeat as fact)

(none recorded)

## Platform mechanics (Substack's own channel)

Feature facts, not doctrine. CLAIM(UsQVnG7kIAI, oPlu_mielxg, QL4i-67bfFw, xhBEqqC43hk, 6nT6G_do-6c, 1tiIL1OdyQs)

## RIG application (RIG synthesis, not corpus claims)

RIG synthesis, not corpus claims.
- Fix the about page and welcome email this week, before any promotion. With roughly 2 subscribers these two pages are the only sales surface the corpus says most writers leave on default settings, and the welcome email is where the One-Workflow Review gets its first mention.
- Use one publication with 2 or 3 sections (case receipts, workflow playbooks, maybe a podcast section later). Do not open a second Substack for a second topic; sections stay subscribable and keep the whole feed coherent for an ops-buyer audience.
- For posts that travel from LinkedIn, keep the diagnosis fully free and paywall only the applied layer: checklists, prompts, workflow blueprints. That is L4 applied to a B2B buyer who is deciding whether Mike is credible, not whether the article was worth $8.
- Since the Substack's job is owned email rather than subscription revenue, follow the anti-paywall side of the contested section: most posts should stay open so they spread from 5,400 LinkedIn followers, and paywall depth is a credibility tool, not a revenue tool.
- Skip the podcast until there is a steady article cadence. If it starts, interview format only, guests chosen for their audience of ops and AI leaders (L7), and the podcast gets its own section from day one (L6).
- Do the minimal SEO layer now: keyword-bearing titles and subheadings on the case-study posts (L9), and expect Google to send little traffic until the archive is deep, per the contested view.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/welcome-emails.md` | writing and installing the four welcome emails |
| `references/send-checklist.md` | the pre-send and post-send checklist |

## Hard rules

- Publishing, sending, scheduling and every settings change are Gate-D: Mike's explicit yes per item.
- Never send twice: check Posts > Published on BOTH publications before any send (the 2026-09-25 duplicate Wax On is the precedent).
- Deleting a podcast or post needs an export first and Mike's yes.
- Paid subscriptions stay on; the paywall is used as a depth tool, not a gate on the diagnosis.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-publish/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-publish` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
