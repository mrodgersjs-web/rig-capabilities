---
name: lv-creator-diandra-escobar
description: >-
  Diandra Escobar's LinkedIn doctrine (@diandraescobarr), distilled from 14 YouTube videos (2026): hooks, commenting, four-bucket funnel mix, profile-as-prompt, and AI-search visibility. Use when planning LinkedIn growth, writing hooks, setting a comment cadence, fixing a profile for discovery, or judging citation readiness. JEV-FIRST MANDATE, findable at task start: judgments this doctrine drives (hook format, funnel-bucket fit, comment target, citation readiness) go to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, doctrine, diandra-escobar, hooks, commenting, ai-search]
outcome: "content-publishing: LinkedIn work can apply Diandra Escobar's current rules, each traced to a dated video, never copied transcript text"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-diandra-escobar
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py --self-test capabilities/skills/lv-creator-diandra-escobar
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  source-videos: "14"
  distilled-videos: "14"
---

# Diandra Escobar doctrine (hooks, comments, funnel, AI-search)

## JEV-first mandate (read first)

Where this rule lives: this description is loaded into every session at start, and the parent `linkedin-viral` is the first LinkedIn route from Mike's always-loaded AGENTS.md.

Typed judgments this doctrine drives (hook format, funnel-bucket fit, comment-target fit, citation readiness) go to Jev via `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json` before any frontier LLM call. Rubrics: `post.linkedin`, `post.viral`, `post.eden`, `comment.linkedin`. A pass needs noul and confidence above 0.9.

Fail closed: classifier down, error, or a missing rubric means DEFERRED, never a guess, never a pass. A claim that Jev judged a draft cites the decision id in `~/.rig/s1gate/decisions.db`. See `~/.aside/u/0/skills/user/s1gate/SKILL.md`.

**Who:** Diandra Escobar runs Distinctiva, a done-for-you LinkedIn content agency for B2B operators and founders who want qualified pipeline and invitations, not vanity reach. She also sells a community, a paid hour, and done-for-you tiers (creator-cited prices, not a RIG rate card) and uses the same system to book paid speaking. Channel: https://www.youtube.com/@diandraescobarr (12.6K subscribers on the 2026-09-28 manifest).

**Source:** Local-only corpus at `~/Developer/brand-workspace/youtube-intel-pipeline/diandra-escobar/` (14 transcripts, 38,479 words, scraped 2026-09-28; 0 captions disabled). All 14 were distilled. Video list: `references/source-index.md`. Never paste transcript text into posts, Eden, or a public repo.

**Evidence standard:** Every number below is a creator claim from the cited video, not a verified fact. Algorithm statements are her reading of papers, engineering posts, and vendor datasets, unverified by RIG. When Mike's measured results disagree, Mike's results win.

## The doctrine in 10 lines (current as of Sept 2026)

1. Comments are the growth engine before you have an audience: about 30 minutes a day on ICP-matched posts, for 90 days, before you judge the posts. [w3_109ygioY, R8nrEQx8rEY, ZAqIUNAvXXo, _ZFncQNrOhw]
2. The profile is a landing page and the text block retrieval reads: buyer-language headline, an about that states problem, solution, proof, and ask, and featured links into properties you own. [w3_109ygioY, R8nrEQx8rEY, PxjDCR29aKc, JtpBDc46w-k]
3. Write the body first, then lift the sharpest line into the hook. A hook does one of three jobs (curiosity, belief challenge, or a specific value), and the opening must name topic plus audience. [BPbf3JUm_dw, ZAqIUNAvXXo, Zc4E_K48v48, PxjDCR29aKc]
4. Four buckets (growth, authority, conversion, personal) with a point of view through all of them. Mix moved from 35/35/20/10 on 2026-03-05 to 40/30/20/10 on 2026-04-03, restated 2026-07-21. [ZAqIUNAvXXo, R8nrEQx8rEY, _ZFncQNrOhw]
5. Reach comes from attaching your expertise to attention that already exists: a brand, fresh news, a known person, a contrarian take, and (from 2026-07-21) a format that is already spreading. [twBrrKkhpOg, KlawrDJuqYc, _ZFncQNrOhw]
6. Generic how-to lost its edge once AI answers instructions for free. The durable post documents what you did, including the failure, with named tools and numbers. [a4uL3wTtjFk, D9DKTj85wWc]
7. She claims LinkedIn is the second most cited source in AI overviews, and that citations follow technical detail, named entities, and a narrow topic, not follower count. Pair the feed with one 500 to 2,000 word article a month, in plain text. [D9DKTj85wWc, BPbf3JUm_dw]
8. Mine calls, internal docs, and expert interviews. Do not invent topics. A text winner can move to a carousel, then to video. [Z3jHnYT8iJo, ZAqIUNAvXXo, w3_109ygioY]
9. Judge qualified pipeline, not impressions. She claims a roughly 5,000-impression post beat 100,000-impression posts on leads. [ZAqIUNAvXXo, BPbf3JUm_dw]
10. Hold a cadence you can keep for 90 days to 6 months. She stages posts 1-20 as practice, 21-40 as voice, 41 and after as momentum. Stated volume moved from 5 a week (2026-02-06) to 3-5 (March) to 5-7 in one lane (2026-08-17). [w3_109ygioY, ZAqIUNAvXXo, R8nrEQx8rEY, JtpBDc46w-k]

## Sub-skills (load only the one the task needs)

| Task | Load |
|---|---|
| Openings, four hook shapes, mobile fold, hook tests | `references/hooks.md` |
| Buckets, body craft, how-I, articles, AI drafting rules | `references/writing.md` |
| Images, carousels, talk footage, alt text, preview | `references/visuals.md` |
| Comment lists, reply window, pods, warm DMs | `references/engagement.md` |
| Posting window, first replies, cadence shifts, algorithm readings | `references/timing-and-algorithm.md` |
| Profile, positioning, sourcing, pipeline math, speaking discovery | `references/strategy-and-growth.md` |
| Find the video behind a claim | `references/source-index.md` |

## Where this feeds

- `references/hooks.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-hooks/SKILL.md`.
- `references/writing.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-draft/SKILL.md`.
- `references/visuals.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-visuals/SKILL.md`.
- `references/engagement.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-engage/SKILL.md`.
- `references/timing-and-algorithm.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-launch/SKILL.md` and `~/Developer/rig-capabilities/capabilities/skills/lv-plan/SKILL.md`.
- `references/strategy-and-growth.md` feeds `~/Developer/rig-capabilities/capabilities/skills/lv-strategy/SKILL.md`, `~/Developer/rig-capabilities/capabilities/skills/lv-profile/SKILL.md`, `~/Developer/rig-capabilities/capabilities/skills/lv-outreach/SKILL.md`, and `~/Developer/rig-capabilities/capabilities/skills/lv-measure/SKILL.md`.

Enter through `~/Developer/rig-capabilities/capabilities/skills/linkedin-viral/SKILL.md`. Do not load this doctrine as a second publisher.

## Binding overlays for Mike (RIG rules win on conflict)

Lane first. Lane A is the personal brand in Eden. Lane B is RIG B2B: evidence-led, named receipts, no mascots, and never Birch, Unit 7, The Coach, or "Be more Birch". The Ideawake lane is Coby Skonord's account: assert the handle, never borrow Mike's voice, nothing fires without Mike's explicit client yes. The job-search lane shows profile edits as exact before/after values and applies them only after Mike approves. Anything about a minor stops. This corpus has no minor content and does not license that lane.

Eden is the only publisher and the assigned generator (`~/.aside/u/0/skills/user/eden-mcp/SKILL.md`). Feed it a real story, transcript, or receipt, never a bare topic. Gate-D covers publishing, sending, boosting, spending, and profile edits. Comments on other people's posts are positive only, and never AI-written. Outreach stays inside `~/.aside/u/0/skills/user/linkedin-site-mechanics/SKILL.md`. No automated sends without Mike's yes. Every number in a post is a sourced receipt.

Where this creator conflicts:

- **Challenge comments.** Her three good-comment moves include a respectful challenge [w3_109ygioY, _ZFncQNrOhw]. Mike's rule is positive only on other people's posts. Challenge stays on Mike's own posts, if at all.
- **Overnight AI drafts.** In March 2026 she runs agents that emit about 10 drafts before the team wakes, then a human edits 5 to 10 minutes and never publishes the draft as-is [KlawrDJuqYc]. Tommy Clark, from Sept 2025, forbids a blank-to-draft model (`~/Developer/rig-capabilities/capabilities/skills/tommy-clark-doctrine/SKILL.md`). RIG reconciliation: Eden may draft only from a real story, call, or receipt. A news scrape with no Mike mechanism is a bare topic. Her n8n or Telegram setup is not the publisher.
- **Volume.** She states 5 a week on 2026-02-06, 3 to 5 in March, and 5 to 7 in one lane on 2026-08-17 [w3_109ygioY, Z3jHnYT8iJo, JtpBDc46w-k]. Clark's current rule (Jan 2026) is three strong posts a week. Do not merge them. Lane A keeps its own daily rhythm. Lane B does not chase her August volume if the receipts are thin.
- **Borrowed attention.** Brand frames, news frames, and person frames are her reach layer [twBrrKkhpOg, _ZFncQNrOhw]. Lane B may name a buyer-relevant vendor or operator only with Mike's receipt. A celebrity interrupt, a meme frame, or a mascot is out. Hot takes that exist to pick a fight are out on Lane B.
- **Speaking profile.** Services set to public speaking, a stage banner, and a booking link are her offer [JtpBDc46w-k]. Do not write those into the RIG or job-search profile unless that is the offer Mike named.
- **Link in the comments.** She claims a citation penalty for the post and a citation lift for the dropped URL [D9DKTj85wWc]. RIG does not hide the offer in comments as a hack. Featured links to owned pages are the shared rule.
- **Outbound.** She is comment-first, then a warm line once someone already engaged [_ZFncQNrOhw]. Clark's weekday connection volume and agency automation are not her system and are not approved here. Any DM or connection batch is Gate-D.
- **Algorithm math and the headline receipt.** The +226% reach and +327% engagement line is her claim about one SEO client after a headline and about edit [R8nrEQx8rEY, _ZFncQNrOhw]. The AI-search lifts (technical detail, named entities, Unicode, articles) are her reading of studies she cites [D9DKTj85wWc]. None of these are Mike's analytics. On 2026-04-10 she corrected an earlier claim: only five author fields travel with a post, and commenting shapes your own feed [PxjDCR29aKc]. Later videos still run both stories. Treat the correction as the current reading, still unverified.
- **Boosts.** This corpus does not teach paid boosts. Do not import Clark's thought-leader ads through this skill. Spend stays Gate-D.
- **Pods and comment bots.** She says both are dying or already suppressed [BPbf3JUm_dw, PxjDCR29aKc, _ZFncQNrOhw]. That agrees with RIG. Do not revive them.

## Done-test

From `~/Developer/rig-capabilities`, `python3 capabilities/skills/linkedin-viral/scripts/check_creator_doctrine.py capabilities/skills/lv-creator-diandra-escobar` is GREEN only when the folder name matches the frontmatter, the JEV mandate is in the description and the body, at least three topic files are present and large enough, `references/source-index.md` lists the same video count as the local manifest, no file shares a 12-word run with the local transcripts, and every backticked home path exists. `--self-test` plants a 16-word transcript run into a temp copy and passes only if that copy goes RED while this folder stays GREEN.
