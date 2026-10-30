---
name: ss-write
description: >-
  Body writing for a Substack issue: structure, length, formats, the reader-first voice and the brief that feeds rig-write-substack. USE WHEN drafting or rewriting an issue body, choosing a format, or turning a LinkedIn post into a full issue. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, write]
outcome: "content-publishing: an issue body with one idea, a structure a skimmer can follow, receipts for every number, and a single next step"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-write/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-write
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "15"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-write: post architecture and voice

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: which format fits the idea, does the body pay off the title, is the draft good enough to gate. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check substack.issue --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `substack.issue` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after ss-package has fixed the title. The drafting engine is `rig-write-substack` (Communications OS surface engine); this stage decides structure and brief and checks the result. Not for Notes (ss-notes).

## Procedure

0. **Angle first** (sub-skill `angle-engine.md`): Eden social analysis (what is working on Substack for this topic) -> collision engine angle -> creativity gates (`rig-lattice idea score`) -> pick one angle with a named mechanism. No draft starts from a bare topic.
1. **Pick the format** that fits the angle (teardown, how-to, story-with-lesson, playbook, curated list). One idea per issue.
2. **Write the brief**: the real source (story, build log, transcript, receipt), the reader, the one takeaway, the next step, and the chosen angle card.
3. **Draft**: issue bodies are drafted overnight on the local Blackwell by `~/Desktop/Projects/substack/bin/night_writer.py` (Mike, 2026-09-28: write articles at night on the Blackwell). It uses the GPU 1 companion; Hemmingway-1 swaps in via `rig-writer-window` only for personal/research briefs or once a commercial agreement is recorded in `config/hemmingway-license.json` (CC BY-NC 4.0). Eden stays the generator for LinkedIn copy and imagery (Mike, 2026-09-17). Build the voice packet with `cd capabilities/skills/rig-communications-core && PYTHONPATH=. python3 -m rig_comms packet --surface substack --brief <brief>`, then send brief + packet + angle card to Eden (a RIG-voice Custom AI via `eden_list_custom_ai` / `eden_get_custom_ai`, or an Eden chat) and save the result with `eden_create_note`. If Eden tools are not available in the session, draft against the packet and label the draft `source: fallback (no Eden)`.
4. **Structure for skimmers**: short paragraphs, H3 subheads that each say something, one list where steps exist.
5. **Receipts**: every number carries a named source or is cut (Jev flagged Mike's April post for unnamed survey figures, decision 125944).
6. **One next step** at the end: reply prompt, subscribe, upgrade, or the review offer, never more than one.
7. **Score, then deviate, then grade**: `python3 -m rig_comms score --surface substack --artifact <draft>`; `rig-lattice audit <draft> --json` (40 deviation engines; any physics-gate HARD_BLOCK stops the draft); then Jev `substack.issue`. On ESCALATE run `rig-s1gate improve substack.issue --file <draft> --max 3` and re-grade; hand to ss-gate with all three results.

## Hands the next stage

`draft.md` scored green by rig_comms. ss-gate runs the full pre-publish gate.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-write.md` (local corpus, not republished).

- L1. Open with a hook the reader already recognizes, then the story or the problem. Do not warm up with context they did not ask for. CLAIM(E4KFHhiebCw, mnHTohgtAMo) | channels: 2 | status: consensus
- L2. Tell a story from your own experience instead of a tip list. Tips get bookmarked and forgotten. Stories get remembered and shared. CLAIM(CSAXPQnfxYc, _gaJxqzTBiE, NmWqzOdPc9o) | channels: 3 | status: consensus
- L3. Write how the reader's life changes, not a description of what you do. CLAIM(7pyoUVBcBnk, Y3G8NrvlcE8) | channels: 2 | status: consensus
- L4. Make yourself the niche. Write your successes and failures, not a generic how-to an AI can clone. CLAIM(cQl88Ga2WTk) | channels: 1 | status: single-source
- L5. Do not draft until the big idea is broken into an outline of three to five smaller ideas. CLAIM(_DT4L2KAXTs, gfETuDIRyi8) | channels: 2 | status: consensus
- L6. Finish the draft, then edit in one pass. Do not sit in a loop swapping adjectives. CLAIM(_DT4L2KAXTs, QeE_vPNatUQ) | channels: 2 | status: consensus
- L7. State the one conclusion before the supporting detail. If you only dump information, readers invent their own ending. CLAIM(NmWqzOdPc9o, AmzBKd7hCGE) | channels: 2 | status: consensus
- L8. Do not publish a thick block of text. Use short lines, double breaks, and bullets so the page can be scanned. CLAIM(dnTEJZZDXYA, mHRJfOWzdJQ) | channels: 2 | status: consensus
- L9. Treat the long-form post as the asset that holds clients. Use Notes and other short posts to get discovered, then cut them from the long piece. CLAIM(dBlSgcbHcug, _X_nTR0rNi8, 8CejgQDXwUQ) | channels: 3 | status: consensus
- L10. If a tool writes or cleans your words, lock one framework and keep your structure. Do not say "write like" a list of writers, and do not let the tool make the final voice call. CLAIM(E-R7qIJE5bM, v9XZKbTN01M, HyFZDPuoN_o) | channels: 3 | status: consensus
- L11. The opening must prove the click was the right choice. A personal story, the big problem, or a rant does that job. A slow warmup does not. CLAIM(mnHTohgtAMo, E4KFHhiebCw) | channels: 2 | status: consensus
- L12. The ending must pay off the promise you opened with. Title, first paragraph, and last paragraph have to match. CLAIM(HyFZDPuoN_o, NmWqzOdPc9o) | channels: 2 | status: consensus
- L13. Do not publish a life update the reader cannot use. Attach the story to the transformation, the system, or the point. CLAIM(9tjmiFAXzzI, xy2ELDsdSVY) | channels: 2 | status: consensus
- L14. Paywall the extra tangible walkthrough, not the only value. Free the information that gets them bought in. Put the asset behind the wall. CLAIM(-zzOuyl3PTA, 9aTSqDpUHQg) | channels: 2 | status: consensus
- L15. Write Notes as one sentence per line, about four to six sentences, near 250 characters. Do not write them as a Facebook paragraph. CLAIM(mHRJfOWzdJQ) | channels: 1 | status: single-source

## Where the creators disagree

- Order of formats. Long form first, then short posts cut from it: CLAIM(8CejgQDXwUQ, ceQN0LmRpB8). Start with Notes when you do not yet know the publication, or when a long post will not reach anyone: CLAIM(Y3G8NrvlcE8, gMOA9rMYSlo). Same estate, opposite start line. sutoscience also says short-form followers do not become paid subscribers: CLAIM(_X_nTR0rNi8).
- How hard to edit. One pass, and early adjective-swapping is a waste: CLAIM(_DT4L2KAXTs, QeE_vPNatUQ). Line-edit every sentence and cut fluff because longer is not better: CLAIM(HsLrz9jiUlc). Developmental edit (arc, pacing) versus line edit is a third split, for books more than posts: CLAIM(cdUNLLWh1hQ).
- Length. About 150 words per section, three sections already enough: CLAIM(mnHTohgtAMo). A Substack post around 800 words: CLAIM(c8dslu2PbaE). Use as many words as the story needs, and a strong piece can be 800, 2,000, or 5,000: CLAIM(C79BMJsVCo8). No shared word-count rule.
- Story versus how-to. Stories beat tips for comments and memory: CLAIM(CSAXPQnfxYc). A make-money audience still needs the system blended into the transformation story, or the post fails that reader: CLAIM(7R1j2HmYqDg, 9tjmiFAXzzI).
- Who the niche is. You are the niche, not the topic: CLAIM(cQl88Ga2WTk). Creatives selling to companies must translate the same story into corporate language: CLAIM(lfQfA32U0DE).

## Creator result claims (UNVERIFIED, never repeat as fact)

- [quote in corpus notes] and the story pieces, not the tip pieces, get the comments. CLAIM(CSAXPQnfxYc) UNVERIFIED.
- [quote in corpus notes] and [quote in corpus notes] CLAIM(x2e3c4GF8sw) UNVERIFIED.
- Title states $10,000 on Substack in 4 months. The sampled window does not repeat that figure. CLAIM(9tjmiFAXzzI) UNVERIFIED.
- Title states best seller in 4 months. No dollar figure in the sampled window. CLAIM(-zzOuyl3PTA) UNVERIFIED.
- Title states 1,070 subs in 30 days. The sampled windows describe the writing workflow, not the count. CLAIM(_DT4L2KAXTs) UNVERIFIED.
- Title states 9,531 Substack subscribers. CLAIM(w8_OjKm4VPs) UNVERIFIED.
- Title states $21,000 in 14 months. In-window: [quote in corpus notes] and [quote in corpus notes] CLAIM(VRlix-8tXtM) UNVERIFIED.
- Inside a @substackinc window, a guest says [quote in corpus notes], "50 people signed up", and [quote in corpus notes] CLAIM(5Hx2Kok6BM4) UNVERIFIED. Not a Substack product stat.

## Platform mechanics (Substack's own channel)

- Recording studio exports one mixed track, not separate tracks. [quote in corpus notes] CLAIM(6nT6G_do-6c).
- You cannot pause a recording, and there are no programmatic branded intros. [quote in corpus notes] CLAIM(6nT6G_do-6c).
- Save the recording to drafts before publish so you can edit title, body, free preview, and paywall. [quote in corpus notes] Co-hosts each get a draft. CLAIM(6nT6G_do-6c).
- A voiceover player shows in the email and in the app. If text-to-speech is on, the voiceover replaces it. [quote in corpus notes] CLAIM(xhBEqqC43hk).
- You can push that voiceover to the podcast RSS. To keep the text free and paywall only the voiceover, move the paywall to the end of the draft. CLAIM(xhBEqqC43hk).
- Official formatting guidance: keep formatting consistent so readers know what to expect, and use paragraphs as the basic grouping. A shown long-post pattern is two to four paragraphs, then an image. Pull quotes, emoji anchors, and a table of contents are shown as navigation, not required fields. CLAIM(g2k6H0vkoa0, WcT0TV-TlnA).

## RIG application (RIG synthesis, not corpus claims)

- Each RIG post gets one promise, one operator story (a real build, a failed run, a counted receipt), then the mechanism, then a one-line takeaway. No tip roundups. Title, first lines, and last lines must say the same thing.
- Nine posts and zero Notes is the gap. Cut Notes from posts already written: one sentence per line, four to six sentences, no new voice. Do not start a second content engine.
- LinkedIn is the attention (about 5,400 followers) and it suppresses a Substack link in the body. The LinkedIn post is the story without the link. The Substack post is the long form. The welcome email is the owned copy. X (1 follower) is not the distribution plan.
- With about 2 subscribers, do not paywall the lesson. Free the information. A template or workflow file can sit behind the wall later, as the extra, not the only value.
- If AI drafts, give it one RIG framework and Mike's words. Do not prompt "write like" a stack of these creators. Reject rewrites that sand off the receipt.
- Success test for a post: a stranger can name the conclusion from the first screen, the last paragraph restates it, and one Note cut from it can stand alone.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/angle-engine.md` | finding the angle before drafting: Eden social analysis, collision engine, creativity gates, deviation audit, Jev |
| `references/formats.md` | choosing the issue format |
| `references/brief-for-engine.md` | writing the brief rig-write-substack drafts against |

## Hard rules

- Eden and the Communications OS engine draft; agents brief, check and gate. Mike's voice pages (`users/mike-rodgers-voice.md`) govern register.
- No invented metrics, clients or quotes. A creator's claimed result is never presented as a fact.
- No Lane A cast on the RIG publication.
- No em dashes in Mike's published copy.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-write/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-write` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
