---
name: ss-notes
description: >-
  Substack Notes as the discovery engine: note formats, daily cadence, restacks, replies and the engagement routine around each note. USE WHEN writing Notes, planning a Notes week, restacking a post, or when the publication is not being discovered inside Substack. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, notes]
outcome: "content-publishing: a Notes batch cut from real issues, each gated, plus a daily engagement routine that puts Mike's name under relevant writers' notes"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-notes/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-notes
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "15"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-notes: Substack Notes, restacks and replies

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: which notes to post, is a note on-pillar and non-generic, is a reply worth sending. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check substack.note --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `substack.note` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use daily once the publication has a clear promise. Not for full issues (ss-write) or recommendations and collaborations (ss-network).

## Procedure

1. **Cut Notes from the issue**: 3-5 per issue, each one idea (a line, a number with its source, a short list, a question).
2. **Restack the issue** on publish day with one line of context, not a bare link.
3. **Daily engagement slot**: read the Notes feed for the pillar topics; reply with substance under relevant writers' notes (validate, add one insight). Likes and replies are the cheap half of Notes growth.
4. **Cadence**: start at 1 Note per day and hold it for four weeks before adding more.
5. **Gate** each batch in ss-gate; then Gate-D: every Note is public.
6. **Measure** follows, clicks and subscriptions per Note from the note stats (ss-measure).

## Hands the next stage

`notes-<week>.md` batch with gate verdicts. ss-publish or Mike posts; ss-measure logs note stats.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-notes.md` (local corpus, not republished).

- L1. Publish notes on most days at roughly 1 to 3 per day, because you cannot predict which note will spread and posting volume is the only way to find out. CLAIM(7R1j2HmYqDg, PY9IwpPM-RQ, iFsuv6lZG6Q, ILNjZPn78lg, C_R4O_y87qM) | channels: 4 | status: consensus
- L2. For every note you broadcast, spend about three times that effort engaging on other people's notes and comments. CLAIM(69ZI7ofPxUA, ILNjZPn78lg, G3kol7GZ70w) | channels: 2 | status: consensus
- L3. Every time you publish a note, also like 10 notes from other creators, leave 5 meaningful comments, and start 1 genuine conversation. CLAIM(ILNjZPn78lg, Y3G8NrvlcE8, M7G5kXlIxo4) | channels: 1 | status: single-source
- L4. When you share someone else's note or article, restack it with your own commentary instead of restacking it bare. CLAIM(v9XZKbTN01M, IrKHQoq8mn4, RJeTy32hrIg) | channels: 3 | status: consensus
- L5. Reply to every genuine reply and acknowledge every comment on your notes, even the one-liners. CLAIM(G3kol7GZ70w, h7l_bkuSP68, pt8X9etCd48) | channels: 2 | status: consensus
- L6. Measure notes by followers gained, because the funnel is notes to followers to free subscribers to paid, not likes to money. CLAIM(PY9IwpPM-RQ, 9tjmiFAXzzI) | channels: 1 | status: single-source
- L7. Keep notes at tweet scale, under about 250 characters or 4 to 6 short spaced sentences, with the closing line bolded. CLAIM(SzJlV4PVvn8, mHRJfOWzdJQ, RJeTy32hrIg) | channels: 2 | status: contested
- L8. Open the note with a specific verifiable credential line about your own experience, not a topic hook and not a question. CLAIM(064AguKrp0M) | channels: 1 | status: single-source
- L9. Alternate two note types: value-complete notes that give everything away for reach, and open-loop notes that leave a reason to read your publication. CLAIM(NHlF-3aRiz0) | channels: 1 | status: single-source
- L10. Optimize notes for recommendations, restacks and real connections rather than for raw like counts. CLAIM(NHlF-3aRiz0, iGFItajDlN0, aFAsK2zNSJM, -s9dWPYSpAg) | channels: 3 | status: consensus
- L11. Keep the same voice and the same positions in notes as in the newsletter, so a note reader and a newsletter reader meet the same person. CLAIM(sGV4NbLJezU) | channels: 1 | status: single-source
- L12. Put your best comments on recent notes from larger creators in your niche, so their followers click through to your profile. CLAIM(-zzOuyl3PTA, pR9CcB8zuGw, m_gtoaMiWyI, 69ZI7ofPxUA) | channels: 3 | status: consensus
- L13. Turn your best-performing notes and the questions in your comment sections into full articles. CLAIM(C_R4O_y87qM, E4KFHhiebCw, M7G5kXlIxo4) | channels: 3 | status: consensus
- L14. Do not depend on the Notes algorithm alone; point at least two outside sources (other platforms, SEO, referrals) at your Substack. CLAIM(As2CPh3N1dM, qdPn6lIdYps, k3hbRtfpZ84) | channels: 3 | status: consensus
- L15. Use a weekly 3-2-1 mix of notes: 3 valuable notes, 2 engagement posts (questions, polls, discussions), 1 soft promotion. CLAIM(Fm8FHHJzKTE) | channels: 1 | status: single-source

## Where the creators disagree

- Note length. Short side: notes are tweet-scale, under 250 characters. CLAIM(SzJlV4PVvn8, mHRJfOWzdJQ) @Loriballen. Long side: two-or-three-sentence notes with a question drew zero engagement, so the writer lengthened them. CLAIM(RJeTy32hrIg) @TheCoachsAlchemist.
- Posting cadence. Fixed quota side: three notes a day plus one weekly article. CLAIM(PY9IwpPM-RQ, 9tjmiFAXzzI, ILNjZPn78lg). Inspiration side: no obligation to post, only when there is something worth sharing. CLAIM(As2CPh3N1dM, 0f89F3a4iqE) @soloshannonhq.
- Whether Notes reach is real. Optimist side: engagement on a note pushes it to a slice of the engager's followers. CLAIM(aFAsK2zNSJM, NHlF-3aRiz0) @sinemgunel. Skeptic side: a creator with a large follower count sees little delivery, and engagement per post falls as subscriber count rises. CLAIM(Pz3YrS7vEDc, JRPEiULkfmU) @creativelyconsciousUK.
- What actually grows the account. Content side: the bestseller run came from mastering notes, explicitly not from engagement. CLAIM(_gaJxqzTBiE, 7R1j2HmYqDg) @Loriballen. Engagement side: most growth comes from engaging with others and restacking their content. CLAIM(iFsuv6lZG6Q, 69ZI7ofPxUA) @MarkJThompson.
- How much a restack is worth. Big side: one restack from the right person can bring dozens of subscribers. CLAIM(Fm8FHHJzKTE, M7G5kXlIxo4) @sinemgunel. Small side: restacks get little traction beyond the person being restacked. CLAIM(m_gtoaMiWyI) @TheCoachsAlchemist.

## Creator result claims (UNVERIFIED, never repeat as fact)

- [quote in corpus notes] CLAIM(7R1j2HmYqDg) UNVERIFIED (@Loriballen, bestseller in 4 months).
- [quote in corpus notes] CLAIM(064AguKrp0M) UNVERIFIED (@sinemgunel, relaying an outside analysis of 9,000 notes from 600 writers).
- [quote in corpus notes] CLAIM(M7G5kXlIxo4) UNVERIFIED (@sinemgunel, one creator's restack of their article).
- [quote in corpus notes] CLAIM(JRPEiULkfmU) UNVERIFIED (@creativelyconsciousUK, one viral note).
- [quote in corpus notes] CLAIM(VXfo3mdAyNI) UNVERIFIED (@sutoscience, guest author on one viral note).
- [quote in corpus notes] CLAIM(C_R4O_y87qM) UNVERIFIED (@mattgiaro, one note versus his usual [quote in corpus notes]).
- [quote in corpus notes] CLAIM(pR9CcB8zuGw) UNVERIFIED (@MarkJThompson, 1,700 to 1,912 subscribers in 90 days).
- [quote in corpus notes] CLAIM(qch_WGVO4uM) UNVERIFIED (@MarkJThompson, one repurposed note).

## Platform mechanics (Substack's own channel)

- Launch readiness is judged on two pillars, reach and engagement, and a large list with low readership is not enough to ask for money. CLAIM(b4a8gHDyThU)
- Stated open-rate range for newsletters is 15 to 60 percent, with over 40 percent called very good. CLAIM(b4a8gHDyThU)
- Sending frequency self-selects the audience: daily sends select for heavy inboxes, weekly sends select for readers who want weekly. CLAIM(b4a8gHDyThU)
- The comment section is where recurring readers identify themselves week after week. CLAIM(30iZlg_073E)

## RIG application (RIG synthesis, not corpus claims)

- Zero Notes written is the single biggest gap on rigoperator.substack.com. The corpus's consensus daily surface is not the article, it is Notes plus commenting. Start at a dose RIG can sustain: one note a day plus 5 likes and 3 real comments on AI-ops and agency operators' notes, since with 2 subscribers the growth lever is borrowed audience (L2, L3, L12), not broadcasting.
- Note format for RIG: open with a verifiable credential line (for example, years running AI operations and what that taught), give one concrete operational takeaway, bold the closing line (L7, L8). Alternate reach notes that give the whole insight away with open-loop notes that end at the free weekly post (L9). If two-sentence notes draw zero engagement after two weeks, switch to the longer contested form rather than assuming the format is fine.
- Map the corpus funnel to RIG's actual job: notes to followers to free subscribers to paid becomes notes to followers to email list to discovery calls. Score notes by subscribers and replies started, not likes (L6, L9), and treat a booked call as the "paid" conversion event.
- LinkedIn is the 5,400-follower channel and it suppresses external links in post bodies, so use Notes as the Substack-side landing surface: drive LinkedIn attention to the Substack profile and publication (link in first comment or profile), then convert on Substack with restack-with-commentary on B2B AI content (L4, L14).
- Recycle ruthlessly: winning notes and comment-section questions become the weekly article (L13), and the weekly article stays the depth surface while notes stay the reach surface. Keep one voice across both so a note reader recognizes the newsletter (L11).
- Run a 30-day trial before adding any tooling or cadence machinery. The corpus holds both a claimed 800 to 2,000 subscribers from one viral note (unverified) and a 62K-follower creator seeing little delivery, so the honest position is that RIG's own measured sample decides the cadence, not the corpus's numbers.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/note-formats.md` | the note types and how to cut them from an issue |
| `references/engagement-routine.md` | the daily reply and like routine around Notes |
| `references/restack-playbook.md` | restacking posts and other writers' work |

## Hard rules

- Every Note and restack is public: Gate-D per batch, itemized.
- Replies are written by Mike or drafted for his approval; never generic praise ("Great post!").
- No engagement pods, bought likes or reply rings.
- Notes about Jacob are Lane C: never.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-notes/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-notes` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
