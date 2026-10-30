"""Hand-written stage specs for the Substack growth family. Laws come from the corpus notes;
everything here is RIG's own procedure, rules and sub-skills. Edit here, then run build_family.py."""

ORDER = ["ss-strategy", "ss-plan", "ss-package", "ss-write", "ss-publish", "ss-gate",
         "ss-notes", "ss-network", "ss-distribute", "ss-convert", "ss-bestseller", "ss-measure"]

JEV = """## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` (\"JEV before done\"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: {judgments}. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check {rubric} --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `{rubric}` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`."""

GATES = ""

STAGES = {
"ss-strategy": dict(
 title="positioning, promise and pillars",
 desc="Positioning for a Substack publication: who it is for, the one-line promise, 1-3 pillars, the publication name and the About page as the offer. USE WHEN starting or re-positioning a publication, when readers read but do not subscribe, or when Mike asks what the Substack should be about.",
 outcome="content-publishing: the publication leaves this stage with a named reader, a one-line promise, 1-3 pillars and an About page that sells the promise",
 judgments="does a topic fit a pillar, is the promise specific enough, which positioning option wins",
 rubric="idea.solid",
 when="Use before post 10, before any growth push, and whenever the Growth page shows visitors who do not subscribe. Not for single-post packaging (ss-package) or pricing (ss-convert).",
 procedure="""1. **Name the reader** in one sentence (role, company size, the problem they carry). For RIG: an owner or ops lead at a small or mid-size company who has bought AI tools that are not running anything.
2. **Write the promise** in the corpus form `I help <reader> get <outcome> without <pain>` and test it against three unrelated LinkedIn visitors: can they say in 10 seconds what the email gives them?
3. **Pick 1-3 pillars** and brainstorm 10 post ideas per pillar. A pillar that cannot yield 10 ideas is cut (the corpus test).
4. **Rewrite the About page as the offer**: promise, what arrives and how often, who it is for, who it is not for, one proof receipt, the next step. Biography goes last.
5. **Name check**: the publication name should say the category, not the owner. "Mike's Substack" says nothing; propose 2-3 names to Mike (Gate-D: the rename is his call).
6. **Jev**: run the promise and each pillar through `idea.solid`; keep only PASS or record DEFERRED.
7. Hand the positioning card to ss-plan.""",
 handoff="`positioning-card.md`: reader, promise, pillars with 10 ideas each, About-page draft, name options. ss-plan builds the calendar from the pillars; ss-publish installs the About page after Mike approves it.",
 rules="""- The About page and publication name are public: drafted here, changed only after Mike's explicit yes.
- A claim on the About page needs a receipt (a dated number or a named, permissioned client). No invented results.
- Never position around the minor (Jacob) or reuse Lane A mascots (Birch, Unit 7, The Coach) on the RIG publication.
- Single-source laws are hypotheses: say so when one drives a recommendation.""",
 subs=[
  ("promise-and-pillars.md", "writing the one-line promise and testing pillars with the 10-ideas rule", """# Sub-skill: promise and pillars

Use when the publication has no clear promise, or pillars have multiplied past three.

1. Draft five promises in the form `I help <reader> get <outcome> without <pain>`. Ban the words unlock, empower, leverage, optimize.
2. Score each with Jev `idea.solid`; drop any that is not a PASS. If Jev is down, mark all DEFERRED and bring the five to Mike unranked.
3. For each candidate pillar, list 10 concrete post titles from real RIG work (a build, a failure, a client question). A pillar that stalls before 10 is cut.
4. Map the nine existing rigoperator posts onto the surviving pillars. A post that fits no pillar is not deleted; it is left out of the pillar navigation.
5. Output: the chosen promise, 1-3 pillars, 30 titles, and the map of existing posts, all in `positioning-card.md`."""),
  ("about-page-as-offer.md", "rebuilding the About page so it sells the promise", """# Sub-skill: About page as the offer

The corpus treats the About page as the second sales document after the welcome email (see ss-publish). Structure, top to bottom:

1. The promise in one line.
2. What arrives: format, day of the week, length, what is free and what is paid.
3. Who it is for and, in one line, who it is not for.
4. One receipt: a dated, sourced result from RIG work. If there is none that Mike has approved for public use, leave the slot out rather than soften a claim.
5. The next step: subscribe, plus the one RIG offer (the One-Workflow Review) as a quiet second link.
6. Biography, three lines, last.

Draft only. The change is made in Substack Settings > About page after Mike approves the exact text."""),
 ]),

"ss-plan": dict(
 title="cadence, calendar and batching",
 desc="Cadence and calendar for a Substack publication: publishing day, weekly baseline, batching, series formats, the free/paid rhythm and repurposing from LinkedIn. USE WHEN planning a Substack week or month, choosing a publishing day, or when the cadence has slipped.",
 outcome="content-publishing: a four-week Substack calendar with a fixed day, one issue per week, the Notes slots, and each issue tied to a pillar and a LinkedIn source",
 judgments="is this calendar realistic, which idea fills a slot, is the plan ready to execute",
 rubric="plan.readiness",
 when="Use weekly (Friday) to fill the next four weeks, and whenever an issue is missed. Not for writing the issue itself (ss-write) or its title (ss-package).",
 procedure="""1. **Fix the day and time**: one issue per week on the same day. Default for RIG: Tuesday morning Mountain time, matching the Tuesday LinkedIn rhythm, adjusted once Substack's reader-location stats exist.
2. **Fill four weeks**: each slot names the pillar, the working title, the LinkedIn post or RIG work it grows from, and its lead magnet if any.
3. **Source from LinkedIn first**: the week's strongest LinkedIn post (by its own analytics, read-only) becomes the next issue's seed. LinkedIn is the attention engine; the issue is the deeper version.
4. **Batch**: draft two issues and a week of Notes in one sitting; stage them in Substack as drafts or scheduled (scheduling a public send is Gate-D).
5. **Plan the Notes**: 3-5 Notes per issue cut from it, plus a daily engagement slot (see ss-notes).
6. **Free vs paid**: all-free until the list proves it opens and replies (RIG override of the corpus's one-free-one-paid baseline; see RIG application).
7. **Jev**: run the four-week plan through `plan.readiness`; fix or record DEFERRED.""",
 handoff="`calendar-<week>.md` with four issue slots and their Notes slots. ss-package takes each slot's working title; ss-write takes the source material.",
 rules="""- One issue per week is the floor; do not plan daily issues. Daily volume belongs in Notes.
- Scheduling a send or a Note is a public action: staged here, confirmed by Mike.
- Never plan an issue about Jacob (Lane C); that lane is per-post approval and never auto-scheduled.
- A slot with no real source (story, build, receipt, client question) is left empty, not filled with a topic.""",
 subs=[
  ("weekly-cadence.md", "setting the publishing day and the four-week calendar", """# Sub-skill: weekly cadence

1. Pull the last 4 weeks of LinkedIn posts and their impressions (read-only, from LinkedIn analytics or the Kanban scoreboard).
2. Rank by impressions and saves; the top one is next week's issue seed, the second is the week after.
3. For each of the four weeks write: day, pillar, working title, source link, lead magnet (optional), Notes count.
4. Check the calendar against Mike's real week (job search, client work). If a week is overloaded, drop that issue to a short one rather than skip it; the corpus puts consistency above length.
5. Save as `calendar-<ISO week>.md` and file the four issues on the Kanban board (`http://127.0.0.1:8913`, stream `funnel`)."""),
  ("repurpose-ladder.md", "turning one LinkedIn post into an issue and its Notes", """# Sub-skill: repurpose ladder

One source, four outputs, each adapted, never pasted:

1. **LinkedIn post** (already live): the hook and one idea.
2. **Substack issue**: the full version. Add the part LinkedIn cannot hold: the steps, the numbers, the template, the failure story.
3. **3-5 Notes**: one idea each, cut from the issue; one of them restacks the issue itself on publish day.
4. **Back to LinkedIn**: a later post that points to the issue in the first comment (never a raw link in the post body; see ss-distribute).

Rule: near-identical text on two surfaces inside 48 hours is a delivery failure. Change the opener and the ordering for each surface."""),
 ]),

"ss-package": dict(
 title="title, subtitle, cover image and first lines",
 desc="Packaging for a Substack post: title, subtitle, cover image, email subject and preview, and the opening lines. USE WHEN a post needs its title or cover, an issue under-opened, or before any post is published.",
 outcome="content-publishing: every post leaves with a ranked title, a subtitle that states the payoff, a 3:2 cover image and an opening that earns the second paragraph",
 judgments="which title wins, does the subtitle state the payoff, is the cover on-brand, does the opening earn the read",
 rubric="substack.issue",
 when="Use for every post before ss-gate, and to repackage an old post before re-sharing it. Not for the body's structure (ss-write).",
 procedure="""1. **Draft five titles** across different families (number, contrarian, how-to, story, named-problem). Keep each under about 60 characters so the email subject is not cut.
2. **Rank with Jev** (`rig-s1gate rank substack.issue --file <titles separated by --->`) on the set; keep the winner and a runner-up for the social preview.
3. **Subtitle states the payoff**: what the reader walks away with, in one line. It shows in email previews and link cards.
4. **Cover image**: every post has one. A real photo or the post's existing LinkedIn image first; otherwise an Eden or generated image in the RIG palette (charcoal, antique gold), no text baked in, 3:2 safe. Set it as the post's first image so Substack uses it as the social preview.
5. **Opening**: the first two lines carry the hook; no throat-clearing, no "In this post".
6. Hand the package to ss-gate.""",
 handoff="`package.md`: title (winner and runner-up), subtitle, cover image path, preview text, first two lines. ss-gate checks it; ss-publish installs it.",
 rules="""- Every post has a cover image; a post without one ships a blank link card on LinkedIn and X.
- No clickbait the body does not pay off; the title's promise must be in the post.
- Numbers in a title need a source in the body.
- Generated images: no text, no logos of other companies, no people's faces presented as real clients.""",
 subs=[
  ("title-lab.md", "generating and ranking title and subtitle options", """# Sub-skill: title lab

1. Write one title per family: number ("5 gaps..."), contrarian ("Your AI isn't the problem"), how-to ("How to..."), story ("I gave my juniors an AI assistant"), named problem ("The amnesia problem").
2. Cut any over about 60 characters or carrying a banned word.
3. Put all five in one file and run `rig-s1gate check substack.issue --file titles.md --subject "titles <post-id> sha256:<hash>" --json`. Keep the top two by score; if Jev is down, mark DEFERRED and pass all five to Mike.
4. Write the subtitle as the payoff sentence: "<what you get> so you can <outcome>".
5. Record the winner, runner-up and the Jev decision id in `package.md`."""),
  ("cover-images.md", "choosing or generating the cover image", """# Sub-skill: cover images

Order of preference:
1. The post's existing LinkedIn image (fetch the high-res `feedshare` asset; see the 2026-09-28 build log for the method).
2. A real photo from RIG work.
3. Eden image brief (Eden owns brand imagery for Mike's content).
4. `imagegen` in the RIG palette: charcoal and near-black with antique-gold accent light, editorial photo style, no text, no faces presented as real people.

Install: in the post editor put the image as the first block (Insert image > Image) with the caret at the very start of the body; a stray keystroke can split the first paragraph, so read the first paragraph back after inserting. Update the post with audience unchanged, then confirm on the public page that `og:image` points at the new asset."""),
 ]),

"ss-write": dict(
 title="post architecture and voice",
 desc="Body writing for a Substack issue: structure, length, formats, the reader-first voice and the brief that feeds rig-write-substack. USE WHEN drafting or rewriting an issue body, choosing a format, or turning a LinkedIn post into a full issue.",
 outcome="content-publishing: an issue body with one idea, a structure a skimmer can follow, receipts for every number, and a single next step",
 judgments="which format fits the idea, does the body pay off the title, is the draft good enough to gate",
 rubric="substack.issue",
 when="Use after ss-package has fixed the title. The drafting engine is `rig-write-substack` (Communications OS surface engine); this stage decides structure and brief and checks the result. Not for Notes (ss-notes).",
 procedure="""0. **Angle first** (sub-skill `angle-engine.md`): Eden social analysis (what is working on Substack for this topic) -> collision engine angle -> creativity gates (`rig-lattice idea score`) -> pick one angle with a named mechanism. No draft starts from a bare topic.
1. **Pick the format** that fits the angle (teardown, how-to, story-with-lesson, playbook, curated list). One idea per issue.
2. **Write the brief**: the real source (story, build log, transcript, receipt), the reader, the one takeaway, the next step, and the chosen angle card.
3. **Draft**: issue bodies are drafted overnight on the local Blackwell by `~/Desktop/Projects/substack/bin/night_writer.py` (Mike, 2026-09-28: write articles at night on the Blackwell). It uses the GPU 1 companion; Hemmingway-1 swaps in via `rig-writer-window` only for personal/research briefs or once a commercial agreement is recorded in `config/hemmingway-license.json` (CC BY-NC 4.0). Eden stays the generator for LinkedIn copy and imagery (Mike, 2026-09-17). Build the voice packet with `cd capabilities/skills/rig-communications-core && PYTHONPATH=. python3 -m rig_comms packet --surface substack --brief <brief>`, then send brief + packet + angle card to Eden (a RIG-voice Custom AI via `eden_list_custom_ai` / `eden_get_custom_ai`, or an Eden chat) and save the result with `eden_create_note`. If Eden tools are not available in the session, draft against the packet and label the draft `source: fallback (no Eden)`.
4. **Structure for skimmers**: short paragraphs, H3 subheads that each say something, one list where steps exist.
5. **Receipts**: every number carries a named source or is cut (Jev flagged Mike's April post for unnamed survey figures, decision 125944).
6. **One next step** at the end: reply prompt, subscribe, upgrade, or the review offer, never more than one.
7. **Score, then deviate, then grade**: `python3 -m rig_comms score --surface substack --artifact <draft>`; `rig-lattice audit <draft> --json` (40 deviation engines; any physics-gate HARD_BLOCK stops the draft); then Jev `substack.issue`. On ESCALATE run `rig-s1gate improve substack.issue --file <draft> --max 3` and re-grade; hand to ss-gate with all three results.""",
 handoff="`draft.md` scored green by rig_comms. ss-gate runs the full pre-publish gate.",
 rules="""- Eden and the Communications OS engine draft; agents brief, check and gate. Mike's voice pages (`users/mike-rodgers-voice.md`) govern register.
- No invented metrics, clients or quotes. A creator's claimed result is never presented as a fact.
- No Lane A cast on the RIG publication.
- No em dashes in Mike's published copy.""",
 subs=[
  ("angle-engine.md", "finding the angle before drafting: Eden social analysis, collision engine, creativity gates, deviation audit, Jev", """# Sub-skill: angle engine (run before every issue)

A topic is not an angle. This pipeline turns a topic into one angle with a named mechanism, then checks the draft is not generic. Every step writes its output into the issue folder so the grade can be traced.

## 1. Social analysis (Eden, read-only; research costs Eden credits, keep it to 2-3 calls)
- `eden_study_top_titles` with `platform: "substack"` on the niche (AI operations, SMB automation, governed AI). Keep the headline SKELETONS; never reuse a source's own numbers, names or story (`doNotReuse`).
- `eden_search_social_content` on the topic, `orderBy: "relevance"`, to see what angle is already saturated. Errors are not zero results.
- Output: `social.md` with 3 working title skeletons and the 2 saturated angles to avoid.

## 2. Collision (angle candidates)
- `python3 ~/Developer/rig-jtbd-packs/linkedin-studio-v2/engine/collision/collision_engine.py generate -n 3` for artifact x veteran x skeleton specs, or pick a type with `--type`.
- The engine was built for the personal-brand lane and its PREACH floor bans naming AI. For RIG B2B issues use the collision for the hook and the opening scene only; the body may name AI and must carry receipts.
- Output: `angles.md` with 3 candidates, each with its BlendValue.

## 3. Creativity gates (V3.1 Master Creativity Function)
- `~/Developer/rig-capabilities/capabilities/skills/rig-lattice-system/bin/rig-lattice idea score --title <angle> --content <one-paragraph pitch> --claims <n> --json` per candidate. The score rewards declared sources, claims and mechanisms; a bare pitch is rejected, so write the real receipt into the pitch.
- Keep `accept`, rework `revise` once, drop `reject`. Output the verdicts into `angles.md`.
- Jev `idea.solid` on the surviving card as a second opinion; DEFERRED if the classifier is down.

## 4. After drafting: deviation audit + Jev grade
- `rig-lattice audit <draft> --json`: physics-gate HARD_BLOCK stops the draft; any engine below threshold gets a patch or a named reason.
- `rig-s1gate check substack.issue --file <draft> --subject "substack-issue <date> sha256:<hash>" --json`; on ESCALATE, `rig-s1gate improve substack.issue --file <draft> --max 3` and re-grade once.
- Record every decision id in `gate.json`. Advisory: a PASS is not permission to publish.
"""),

  ("formats.md", "choosing the issue format", """# Sub-skill: formats

| Format | Use when | Shape |
|---|---|---|
| Teardown | a real workflow or failure from RIG work | problem, what broke, why, the fix, what to check in yours |
| How-to | a repeatable procedure | outcome first, numbered steps, the gotcha, a checklist |
| Story with lesson | a personal or client moment | scene, turn, lesson, the five-minute version for the reader |
| Playbook | a set of rules | the rules as H3s, one example each, the one to start with |
| Curated | a week of outside reading | 3-5 links, one sentence each on why it matters to an operator |

Pick one. Mixing two formats in one issue is the most common reason a draft reads as long."""),
  ("brief-for-engine.md", "writing the brief rig-write-substack drafts against", """# Sub-skill: brief for the engine

A brief has six fields, all required:
1. **Source**: the real material (LinkedIn post URL, build log, meeting note, receipt). No source, no brief.
2. **Reader**: from the positioning card.
3. **Takeaway**: one sentence the reader should be able to repeat.
4. **Receipts**: each number with where it came from.
5. **Next step**: exactly one.
6. **Out of scope**: what this issue will not cover.

Save as `brief-<slug>.md` and pass it to `rig_comms packet --surface substack --brief`."""),
 ]),

"ss-publish": dict(
 title="publication setup, settings and the send",
 desc="Publication setup and the publish action on Substack: welcome emails, About page install, sections, SEO basics, paywall placement, send settings and the audience radio. USE WHEN setting up or repairing a publication, before any send, or when a post must be updated after publishing.",
 outcome="content-publishing: the publication's sales surfaces are set, and every send goes out to the intended audience with the verified text",
 judgments="is the welcome email ready, is the About page install exact, is this send's audience correct",
 rubric="website.buyer",
 when="Use once to set up the publication and then on every publish or update. The content is decided upstream; this stage installs and sends.",
 procedure="""1. **Assert the account**: rigoperator.substack.com is owned by the Substack account on rodgemd1@gmail.com; mikerodgers317 is owned by mike@rodgersintelligence.com. Confirm the dashboard's publication before any write.
2. **Sales surfaces first**: rewrite the free, paid, imported and founding welcome emails and install the About page (text approved by Mike) before promoting anything.
3. **Sections**: one publication, 2-3 sections matching the pillars. Do not open a second publication for a second topic.
4. **SEO basics**: keyword-bearing title and H3s on how-to and teardown posts; the left-panel SEO title and description set per post.
5. **Before Send**: check the Audience radio. rigoperator's dialog has defaulted to "Paid subscribers only"; the button must read "Send to everyone now" for a public issue.
6. **After Send**: read the public page back (title, first paragraph, cover image, og:image) and confirm the author copy arrived.
7. **Updates to live posts**: Update, audience unchanged, no re-send; word-compare the body before and after.""",
 handoff="Published URL plus the read-back evidence. ss-notes and ss-distribute take the URL; ss-measure logs it.",
 rules="""- Publishing, sending, scheduling and every settings change are Gate-D: Mike's explicit yes per item.
- Never send twice: check Posts > Published on BOTH publications before any send (the 2026-09-25 duplicate Wax On is the precedent).
- Deleting a podcast or post needs an export first and Mike's yes.
- Paid subscriptions stay on; the paywall is used as a depth tool, not a gate on the diagnosis.""",
 subs=[
  ("welcome-emails.md", "writing and installing the four welcome emails", """# Sub-skill: welcome emails

Settings > Emails has four welcome emails: paid, free, imported, founding. Each gets:
1. Thanks in one line.
2. What arrives and when (the promise and the day).
3. The best three posts so far, linked.
4. One question to reply to (replies train deliverability and tell Mike who the reader is).
5. For free: one quiet line about the paid tier and the One-Workflow Review.

Rewrite the imported-subscriber email before any list import: it fires the moment the import lands. Draft here; install after Mike approves the exact text."""),
  ("send-checklist.md", "the pre-send and post-send checklist", """# Sub-skill: send checklist

Before Send:
- [ ] Right publication and signed-in account (rigoperator = rodgemd1@gmail.com).
- [ ] Not already published on either publication.
- [ ] Title, subtitle, cover image set; SEO panel filled.
- [ ] ss-gate verdict recorded (Jev decision id or DEFERRED noted to Mike).
- [ ] Audience radio = Everyone for a public issue; button reads "Send to everyone now".
- [ ] Mike's explicit yes for this send.

After Send:
- [ ] Public page read back: title, first paragraph, cover, og:image.
- [ ] Author copy received in the owner inbox.
- [ ] URL handed to ss-notes and ss-distribute; row added in ss-measure's log."""),
 ]),

"ss-gate": dict(
 no_notes=True,
 title="the pre-publish gate",
 desc="The single pre-publish gate for Substack issues and Notes: claim hygiene, Jev, the Communications OS score, anti-slop, lane check and the Gate-D request. USE WHEN a draft or Note is about to be shown to Mike as ready, before any schedule or send.",
 outcome="content-publishing: one verdict per artifact (READY, FIX or DEFERRED) with evidence, and a Gate-D request for anything public",
 judgments="does the artifact pass, which lane is it, is every claim sourced",
 rubric="substack.issue",
 rig="(RIG synthesis.) The gate exists because the 2026-09-28 audit found 9 published posts, 2 with no image, several with unresolved claims (134 vs 100+ agents; an 88%/78% title contradiction; an unlabeled salon case study) and one about a minor. Every one of those would have been caught here.",
 when="Use on every issue and every Note batch before Mike sees it as ready. Not a publishing step: a PASS never sends anything.",
 procedure="""1. **Lane check**: RIG publication (rigoperator) only. Anything about Jacob stops here (Lane C: per-post approval, never scheduled). Lane A cast never appears.
2. **Claim sweep**: list every number and named result. Each needs a source line. Creator-corpus numbers are never presented as facts. Cross-check against the other posts on the publication for contradictions (the 134 vs 100+ agents case).
3. **Engine score**: `python3 -m rig_comms score --surface substack --artifact <draft>` must exit 0.
4. **Anti-slop**: run the `anti-slop` skill lint; fix AI tells.
5. **Jev**: `rig-s1gate check substack.issue --file <artifact> --subject "substack <slug> sha256:<hash>" --json`. Record the decision id. DEFERRED if the classifier is down.
6. **Package check**: title, subtitle, cover image, one next step, no em dashes.
7. **Verdict**: READY (all green), FIX (named items), or DEFERRED (Jev down). Then a Gate-D request naming the publication, audience and exact text.""",
 handoff="`gate-<slug>.md` with the verdict, the Jev decision id, the rig_comms exit code and the Gate-D request. ss-publish sends only after Mike's yes.",
 rules="""- A PASS is advisory. Nothing ships without Mike's explicit yes for that item.
- DEFERRED is never upgraded to READY by a frontier model's opinion.
- A contradiction with an already-published post blocks until Mike picks the true figure.
- Content about a minor never passes this gate for automation; it goes to Mike as a draft only.""",
 subs=[
  ("claim-sweep.md", "finding and resolving unsourced or contradictory claims", """# Sub-skill: claim sweep

1. Extract every number, percentage, dollar figure, client name and "I built / I did" claim from the artifact.
2. For each, write the source: a dated receipt, a URL, or "Mike's own claim, needs his confirmation".
3. Search the publication's other posts for the same figure (use the drafts API: `/api/v1/post_management/published` then `/api/v1/drafts/<id>`). Different figures for the same fact = contradiction.
4. Illustrative examples (a salon, a hypothetical company) must be labelled as illustrative in the text.
5. Output a table: claim, source, status (sourced / needs Mike / contradiction / cut)."""),
  ("gate-d-request.md", "writing the approval request for a public action", """# Sub-skill: Gate-D request

Every public Substack action (send, schedule, Note, restack, recommendation, settings change, About page) goes to Mike as one request that names:
- the publication (rigoperator.substack.com) and the signed-in account,
- the action and the audience (Everyone / paid / Notes followers),
- the exact text or the diff for a change,
- the gate verdict and Jev decision id,
- what happens if he says no (the draft stays staged).

A blanket "approve everything" clears reversible drafts, not a batch of public posts: itemize the public ones."""),
 ]),

"ss-notes": dict(
 title="Substack Notes, restacks and replies",
 desc="Substack Notes as the discovery engine: note formats, daily cadence, restacks, replies and the engagement routine around each note. USE WHEN writing Notes, planning a Notes week, restacking a post, or when the publication is not being discovered inside Substack.",
 outcome="content-publishing: a Notes batch cut from real issues, each gated, plus a daily engagement routine that puts Mike's name under relevant writers' notes",
 judgments="which notes to post, is a note on-pillar and non-generic, is a reply worth sending",
 rubric="substack.note",
 when="Use daily once the publication has a clear promise. Not for full issues (ss-write) or recommendations and collaborations (ss-network).",
 procedure="""1. **Cut Notes from the issue**: 3-5 per issue, each one idea (a line, a number with its source, a short list, a question).
2. **Restack the issue** on publish day with one line of context, not a bare link.
3. **Daily engagement slot**: read the Notes feed for the pillar topics; reply with substance under relevant writers' notes (validate, add one insight). Likes and replies are the cheap half of Notes growth.
4. **Cadence**: start at 1 Note per day and hold it for four weeks before adding more.
5. **Gate** each batch in ss-gate; then Gate-D: every Note is public.
6. **Measure** follows, clicks and subscriptions per Note from the note stats (ss-measure).""",
 handoff="`notes-<week>.md` batch with gate verdicts. ss-publish or Mike posts; ss-measure logs note stats.",
 rules="""- Every Note and restack is public: Gate-D per batch, itemized.
- Replies are written by Mike or drafted for his approval; never generic praise ("Great post!").
- No engagement pods, bought likes or reply rings.
- Notes about Jacob are Lane C: never.""",
 subs=[
  ("note-formats.md", "the note types and how to cut them from an issue", """# Sub-skill: note formats

From one issue, cut:
1. **The one-liner**: the takeaway as a standalone sentence.
2. **The receipt**: one number with its source and what it means.
3. **The list**: 3-5 short items (steps, mistakes, questions).
4. **The question**: an open question the issue raised, inviting replies.
5. **The restack**: the issue itself with one line on who should read it.

Each note stands alone: a reader who never clicks should still get something. Change wording from the issue; do not paste paragraphs."""),
  ("engagement-routine.md", "the daily reply and like routine around Notes", """# Sub-skill: engagement routine

15 minutes a day, after posting the day's Note:
1. Search Notes for the pillar terms (AI operations, agents in production, small business AI).
2. Pick 5 writers' notes that are recent and on-topic.
3. Draft one substantive reply each: agree with the point, add one specific insight from RIG work, no link.
4. Like the notes you read in full.
5. Log who you replied to; writers who reply back twice are candidates for ss-network (recommendations, collaborations).

Replies are public: drafted for Mike's approval as a batch until he grants a standing rule for replies."""),
  ("restack-playbook.md", "restacking posts and other writers' work", """# Sub-skill: restack playbook

- **Own issue**: restack on publish day with one line on who it is for; again a week later with a different line pulling a different point.
- **Other writers**: restack a post in the pillar with a one-line comment that adds something. It shows the post to Mike's followers and tells the writer and the feed that the two publications overlap in topic.
- **Frequency**: at most one restack of other writers per day; the feed is for Mike's own ideas first.
- All restacks are public: Gate-D batch."""),
 ]),

"ss-network": dict(
 title="recommendations, collaborations and community",
 desc="The Substack network: recommendations in and out, cross-posts, guest posts, collaborations, Lives and chat. USE WHEN building recommendation swaps, planning a collaboration, or when growth inside Substack has stalled after Notes are running.",
 outcome="content-publishing: a target list of peer publications, outgoing recommendations with blurbs, and one collaboration a month, all tracked by subscribers gained",
 judgments="is a peer publication a fit, is a collaboration worth the time, which recommendation to add",
 rubric="idea.solid",
 when="Use after the publication has a promise and a few issues (peers check the archive before recommending back). Not for the daily Notes routine (ss-notes).",
 procedure="""1. **Build the peer list**: 10-20 Substacks whose readers are RIG's reader (ops leaders, founders, AI practitioners). Source from the writers met in the ss-notes routine and from Substack search.
2. **Qualify each** with Jev `idea.solid` on a short card (topic overlap, size, posting activity).
3. **Recommend out first**: add 3-5 recommendations with a real blurb each. Recommended writers are notified and prompted to recommend back.
4. **Collaborate**: one per month at most: a guest post, a cross-post or a joint Live with a peer in the pillar.
5. **Track**: the Recommendations tab shows subscribers gained per recommendation; drop recommendations that send nothing after 60 days.""",
 handoff="`peer-list.md` with status per publication. ss-measure tracks the recommendation numbers.",
 rules="""- Recommendations, guest posts, cross-posts, Lives and DMs are public or outward: Gate-D per item.
- Recommend only publications Mike would genuinely vouch for; the blurb is in his voice.
- No recommendation-for-recommendation spam asks in DMs.
- Never recommend or collaborate with a publication that would put a client's name or a minor in public.""",
 subs=[
  ("recommendation-swaps.md", "choosing and writing recommendations", """# Sub-skill: recommendation swaps

1. From `peer-list.md`, pick publications that are active (posted in the last 30 days) and on-pillar.
2. Write a two-sentence blurb per recommendation: what the publication is, and why an operator should read it. Mike's voice, no hype words.
3. Add in Substack: Recommendations > Add recommendation (Gate-D: itemized list to Mike).
4. Do not ask for a recommendation back; the platform prompts them.
5. After 60 days read the Recommendations tab: keep the ones sending subscribers, retire the rest."""),
  ("collaborations.md", "guest posts, cross-posts and Lives", """# Sub-skill: collaborations

- **Guest post**: pitch a peer a post that fits their readers and draws from RIG work; one link back in the bio line.
- **Cross-post**: share a peer's post to Mike's subscribers when it genuinely serves them; Substack's cross-post feature emails it.
- **Live**: a 20-30 minute joint Live on one question. Only once there is a cadence to point new listeners at.
- One collaboration per month. Each needs Mike's yes and, for anything naming a client, the client's written yes."""),
 ]),

"ss-distribute": dict(
 title="driving readers in from LinkedIn, X and beyond",
 desc="Off-platform distribution for Substack issues: LinkedIn route-back, X, email signature, the RIG site and other channels, each with its own link rules. USE WHEN an issue is published and must be amplified, or when the Growth page shows almost no outside traffic.",
 outcome="content-publishing: every issue gets a per-channel amplification set (LinkedIn first comment, X post, Note), each adapted and route-back compliant, with a distinct utm per channel",
 judgments="which channel fits this issue, is each adapted version good enough, is the route-back compliant",
 rubric="post.viral",
 when="Use after ss-publish on every issue, and to re-amplify the archive. Coordinates with `lv-distribute` (LinkedIn side). Not for Substack-internal discovery (ss-notes, ss-network).",
 procedure="""1. **LinkedIn first** (Mike's 5,400-follower channel): a native post carrying the issue's hook and one idea; the Substack link goes in the first comment, never the post body. Eden drafts LinkedIn copy.
2. **X**: one post with the hook and the link (X allows links in the post; 280 characters unless Premium is confirmed on @RodgersRIG).
3. **Substack Note** restack (ss-notes).
4. **Owned surfaces**: the Substack link in Mike's email signature, the LinkedIn Featured section, and a subscribe embed on rodgersintelligence.com (site change is Gate-D and goes through the website release process).
5. **Tag every link** with a distinct `utm_source` (linkedin, x, site, email) so the Growth page attributes it.
6. **Gate** the set in ss-gate; Gate-D itemized; pace one issue's set per day, never a burst across the archive.""",
 handoff="`amplify-<slug>.md`: the per-channel texts, links and utm values, gate verdicts. ss-measure reads the Growth page for them 7 days later.",
 rules="""- Every outward post is Gate-D, itemized by channel.
- No raw Substack link in a LinkedIn post body; first comment only (LinkedIn suppresses external links).
- Adapt, never paste: near-identical text on two channels within 48 hours is a delivery failure.
- X writes go only to @RodgersRIG; assert the signed-in handle first (the browser's X session can be a minor's account).
- Conflict logged: `lv-distribute` says Substack is a weekly digest "never per post". This family treats each issue as a native Substack post and uses the digest rule only for LinkedIn-to-Substack roundups. Mike decides which rule wins.""",
 subs=[
  ("linkedin-route-back.md", "moving LinkedIn attention to the Substack", """# Sub-skill: LinkedIn route-back

1. The LinkedIn post is native: hook, one idea, no link in the body.
2. First comment: "The full version, with the checklist, is on Substack: <url>?utm_source=linkedin&utm_medium=social&utm_campaign=<slug>".
3. Featured section: pin the Substack homepage (profile edit: Gate-D, exact before/after).
4. Existing LinkedIn posts that became issues: add the issue link as a new comment on the original post (public: Gate-D).
5. Eden drafts the LinkedIn copy; this sub-skill only supplies the route-back line and the utm."""),
  ("x-and-owned.md", "X posts, email signature and the RIG site", """# Sub-skill: X and owned surfaces

- **X (@RodgersRIG)**: hook in the first line, the link, no hashtag stack. Link card uses the issue's og:image, so ss-package's cover image matters here.
- **Email signature**: one line "Weekly operating notes: <substack url>".
- **rodgersintelligence.com**: a subscribe embed (`<iframe src="https://rigoperator.substack.com/embed">`) on the articles page. Site changes follow the website release process and Gate-D.
- **Utm values**: x, email-signature, site. Add them to the site's measurement allowlist before use."""),
  ("archive-reamplify.md", "re-sharing the back catalogue", """# Sub-skill: archive re-amplification

The 2026-09-28 audit found 9 rigoperator posts, none ever shared by Substack link. To re-amplify:
1. Sort the archive into ready (clean claims, has cover), fix-first (claim or contradiction open), and hold (off-lane or about a minor).
2. Ready posts: one per day, each through the full channel set above.
3. Fix-first posts: repackage (ss-package) and resolve claims (ss-gate) before any share.
4. Hold posts are never auto-shared.
5. Stop when the Growth page shows which channel actually sends subscribers; put the remaining effort there."""),
 ]),

"ss-convert": dict(
 title="free to paid, offers and readers to clients",
 desc="Monetization for a Substack publication: paid tier settings, founding members, lead magnets, next steps in every post, and the route from reader to client. USE WHEN setting prices, designing a lead magnet, adding a call to action, or deciding whether the Substack should earn subscriptions or clients.",
 outcome="business-ops: every post carries one next step, and the publication routes serious readers to the One-Workflow Review rather than relying on subscription revenue",
 judgments="is this offer or price sound, does a post's next step fit, is a lead magnet specific enough",
 rubric="opportunity.money",
 when="Use when designing the paid tier, a lead magnet or a post's call to action. Not for publication settings mechanics (ss-publish).",
 procedure="""1. **Decide the money model**: for RIG the Substack is the audience engine and the money is the back end (the $3,500 One-Workflow Review and fixed-scope builds). Paid subscriptions stay on as a filter, not the goal.
2. **One next step per post**: reply, subscribe, download the magnet, or book the review. Pick one.
3. **Lead magnets**: one specific asset per pillar (a workflow failure-test checklist beats "AI tips"). The RIG site's Client Intake Failure-Test Kit is the first candidate.
4. **Paid tier**: keep $8/month for now; if paid revenue becomes a goal, move toward the $10+ band with an announced change, never a silent one.
5. **Founding tier**: only when there is something distinct to give founding members (e.g. a quarterly workflow teardown call).
6. **Jev** `opportunity.money` on any new offer or price before it goes to Mike.""",
 handoff="The next-step line and magnet link for each issue (to ss-write and ss-package); price or tier proposals to Mike as Gate-D items.",
 rules="""- Price and tier changes are Gate-D; announce before changing.
- Never promise results in an offer; sell the scope and the acceptance test.
- Client case material needs the client's written permission before it appears in a post or offer.
- Creator income figures are UNVERIFIED and never quoted to Mike's buyers.""",
 subs=[
  ("reader-to-client.md", "routing serious readers to the One-Workflow Review", """# Sub-skill: reader to client

1. Every teardown and how-to issue ends with one line pointing to the One-Workflow Review for readers who want theirs done.
2. Readers who reply to the welcome email or an issue with a real problem get a personal reply from Mike (drafted here, sent by him).
3. The About page carries the review as the quiet second link.
4. Track: replies, review-page visits from utm_source=substack, and booked calls. One booked review is worth more than the whole paid tier at current list size."""),
  ("lead-magnets.md", "specific lead magnets per pillar", """# Sub-skill: lead magnets

A magnet is specific, useful in 10 minutes, and tied to one pillar:
- Intake and follow-up: the Client Intake Failure-Test Kit (exists on rodgersintelligence.com).
- Agents in production: a one-page "is my agent production-ready" checklist.
- Team adoption: the five-minute Tuesday rules exercise from the Wax On issue.

Deliver by link in the issue or the welcome email. Measure each magnet by subscribers and replies it drives; retire one that drives nothing in 60 days."""),
 ]),

"ss-bestseller": dict(
 title="the Bestseller track: 100 paid subscribers in 12 months",
 desc="The Bestseller track for a Substack publication: the math to 100 paid subscribers (the Substack Bestseller badge), the paid tier designed as a membership, upgrade entry points (premium content library, start-here post, free preview with a paywall), trust cadence, quarterly sprint launches and the 30/60/90/180-day roadmap. USE WHEN Mike asks to make the Substack a bestseller, to get paid subscribers, to redesign the paid tier, to plan a paid launch, or to check progress toward the badge.",
 outcome="business-ops: the publication runs a dated roadmap to 100 paid subscribers, with a membership-grade paid tier, at least three upgrade entry points, a weekly trust cadence and one sprint launch per quarter, each milestone read from Substack's own stats",
 judgments="is the paid tier worth more than its price, is a perk distinct from the free tier, is a launch plan ready, is a milestone movement real",
 rubric="opportunity.money",
 when="Use when the goal is paid subscribers or the badge, when designing or repricing the paid tier, before any paid launch, and on the monthly bestseller review. Not for the general money model or lead magnets (ss-convert), the send itself (ss-publish) or Notes craft (ss-notes).",
 procedure="""1. **Baseline from the source**: signed in as the owner account (rodgemd1@gmail.com for rigoperator), read Settings > Payments and Stats: free subscribers, paid subscribers, paid conversion. Never a remembered number. If the browser is signed in as a different account, stop with `BLOCKED: wrong Substack account`.
2. **Run the math** (sub-skill `bestseller-roadmap.md`): 100 paid divided by a planning conversion of 1 to 3 percent gives the free list the badge needs (roughly 3,300 to 10,000). Turn that into a weekly free-subscriber target and a dated milestone ladder.
3. **Design the paid tier as a membership** (sub-skill `paid-tier-as-membership.md`): perks that are different in kind from the free issues (live sessions, templates, a resource vault, guides), not more of the same emails. Jev `opportunity.money` on the tier before it goes to Mike. Price and tier changes are Gate-D.
4. **Build the upgrade entry points** (sub-skill `upgrade-entry-points.md`): a premium content library page, a pinned start-here post with the upgrade link, and a free preview with the paywall placed after real value on every premium issue.
5. **Hold the trust cadence** (sub-skill `trust-cadence.md`): Notes on weekdays (ss-notes), one long-form issue a week (ss-plan), credentials on the About page and bio (ss-strategy), one live session a month (ss-network).
6. **Sprint launch once a quarter** (sub-skill `sprint-launch.md`): a three-day campaign with a clear reason to join now; between sprints, no constant pitching.
7. **Monthly review**: compare the ladder with Substack's own stats (ss-measure), name the one lever that moves next month, and file it on the Kanban `funnel` stream.""",
 handoff="`bestseller-plan.md` (math, ladder, tier design, entry-point checklist, next sprint date). ss-convert keeps the back-end offer; ss-plan schedules the premium issues; ss-publish installs pages and paywall placement after Mike approves; ss-measure reads the ladder weekly.",
 rules="""- The badge is a paid-subscriber count Substack shows; it is never claimed, rounded up or implied before Substack's own dashboard shows it.
- Price, tier, founding-plan, discount and launch changes are Gate-D: drafted here, applied only after Mike's explicit yes for that item.
- Perks must be deliverable every month by RIG as it is staffed today; never promise a live session or a vault that nobody will run.
- No fake scarcity: a sprint deadline or discount must be real and must actually end.
- Creator income and subscriber claims from the corpus are UNVERIFIED and never shown to readers as proof.
- The minor's lane (Jacob) is never material for a paid perk, a launch or a case study.""",
 subs=[
  ("bestseller-roadmap.md", "the math to 100 paid and the dated 30/60/90/180-day ladder", """# Sub-skill: bestseller roadmap

The badge needs 100 paying readers. Everything else is arithmetic on Substack's own numbers.

## Math (recompute every month from Stats)
- Planning conversion band: 1 to 3 percent of free subscribers become paid (the corpus puts published platform averages higher than what practitioners report; plan on the low end).
- Free list needed = 100 / conversion: about 10,000 at 1 percent, 5,000 at 2 percent, 3,300 at 3 percent.
- Weekly free target = (free list needed - current free) / weeks left in the 12 months.
- If the weekly target is above what the last four weeks actually delivered, say so plainly and name the lever (more LinkedIn route-back, recommendations, a sprint), never a softer target.

## Ladder (dates set from the day the plan is adopted)
| Window | Milestone | Evidence |
|---|---|---|
| Day 0-30 | publication, About page and bio set; paid on; Notes daily; weekly issue; first premium piece | Settings screenshot, post list |
| Day 30-60 | membership tier live; premium library page; first sprint launch; first organic paid subscriber | Payments page count |
| Day 60-90 | entry points on every premium issue; dozens of paid; next revenue step drafted | Stats export |
| Day 90-180 | second and third sprints; recommendations network; rising-leaderboard attempt | Growth sources |
| Month 6-12 | 100 paid and the badge | badge visible on the profile |

Every row's status is read from Substack, dated, and filed on the Kanban funnel stream."""),
  ("paid-tier-as-membership.md", "designing the paid tier as a membership whose value clearly beats its price", """# Sub-skill: paid tier as a membership

A paid tier that only adds more issues rarely converts. Design it as a membership with perks that are different in kind from the free issues.

1. List the reader's top three pain points and desired outcomes (from ss-strategy).
2. Pick one or two anchor perks and at most four supporting ones. Candidate perks: a monthly live working session with replay, a template and checklist vault, step-by-step implementation guides, a searchable archive of premium pieces, a quarterly behind-the-scenes report, a member chat used for discussion (not a support desk).
3. Split content by depth: free issues carry the what and the why; paid material carries the how (implementation, templates, walkthroughs).
4. Write the membership page top-down: who it is for, what unlocks today, what arrives each month, price, the upgrade button.
5. Value test: a reader should be able to name what they get on day one. If the perk list reads as more emails, redesign.
6. Jev `opportunity.money` on the tier; bring the tier and price to Mike as one Gate-D item.

RIG draft anchors (for Mike to approve or cut): a monthly live governed-workflow teardown, and a vault of the failure-test checklists and build templates RIG already uses."""),
  ("upgrade-entry-points.md", "premium content library, start-here post and free-preview paywall placement", """# Sub-skill: upgrade entry points

Readers cannot upgrade to a tier they never see. Put the offer where readers already are.

## Premium content library
A custom page linking every premium resource, grouped by category or format. Paid readers use it to find things; free readers see exactly what unlocks the moment they pay. Link it from the About page, the welcome email and the membership page.

## Start-here post
A pinned post that orients new readers: what the publication is, the three best free pieces, and one clear upgrade call with its reason.

## Free preview, then the paywall
On premium issues and replays, let a substantial part run free (for a long article, well past the halfway point of the setup; for a workshop replay, the first ten or more minutes), then place the paywall with an upgrade link right at the cut. A taste converts better than a pitch.

## Checklist per premium issue
- paywall placed after real value, not after the first paragraph
- upgrade link at the cut and one near the top
- premium library link in the footer
- the issue added to the library page the same day"""),
  ("sprint-launch.md", "a three-day paid-tier sprint launch instead of constant promotion", """# Sub-skill: sprint launch

Promote the paid tier in short, planned bursts, then go back to serving readers. One sprint per quarter.

1. **Reason to join now**: a new perk, a founding or annual offer, or a price that is really going up. The reason must be true and must end on the stated date.
2. **Assets** (drafted a week ahead, all Gate-D): an announcement issue, a mid-sprint issue answering objections, a last-day reminder, 3 to 6 Notes, a LinkedIn route-back post with the link in the first comment, and an update to the membership page.
3. **Window**: three days. Everything ships inside the window; nothing is left running after it closes.
4. **Measure**: paid subscribers before and after from the Payments page, and which asset was clicked.
5. **Close**: write what moved and what did not into the scoreboard, and pick the next sprint date.

Between sprints, the only upgrade asks are the standing entry points (library, start-here post, paywall cuts)."""),
  ("trust-cadence.md", "consistency, expertise and personality as the weekly trust routine", """# Sub-skill: trust cadence

People pay those they know, like and trust. Trust is built on a cadence, not a campaign.

- **Consistency**: Notes on weekdays and one long-form issue every week, on the same day. A missed week is logged, not hidden.
- **Expertise**: the bio and About page state concrete credentials and dated receipts. Every issue shows working knowledge on a real problem.
- **Personality**: some Notes show the person behind the work (training, family life only where Mike approves it, the view from the desk). Never the minor's lane without Mike's per-post yes.
- **Live**: one Substack Live or guest live a month; replays feed the premium library.

Weekly check (Friday, with ss-measure): Notes posted vs planned, issue shipped yes/no, live held yes/no. A gap in any column is the first thing fixed next week."""),
 ]),

"ss-measure": dict(
 title="stats, attribution and the weekly review",
 desc="Measurement for a Substack publication: the weekly stats read, Growth-page sources, per-post and per-Note numbers, and turning each number into one action. USE WHEN asked how the Substack is doing, after every issue, or before planning the next month.",
 outcome="content-publishing: a weekly scoreboard with subscribers by source, opens, and the one action each number triggers",
 judgments="is a metric movement real, what caused a flop, which channel earns more effort",
 rubric="signal.performance",
 when="Use weekly (Friday, before ss-plan) and 7 days after each issue. Not for LinkedIn analytics (lv-measure), though the two scoreboards are read together.",
 procedure="""1. **Read weekly, not daily**: Stats > Posts, Growth (sources), Notes, Recommendations.
2. **Log per issue**: views, open rate, new free and paid subscribers, top traffic sources, link clicks on the next step.
3. **Attribute**: Growth-page sources plus the utm values from ss-distribute. A channel that sends nothing for four weeks loses effort.
4. **Wire each number to an action**: low open rate -> ss-package retest; visitors without subscriptions -> ss-strategy (positioning); Notes followers without subscribers -> ss-notes format change.
5. **Jev** `signal.performance` on whether a movement is real before acting on it.
6. File the scoreboard on the Kanban `funnel` stream.""",
 handoff="`scoreboard-<week>.md` with actions. ss-plan reads it before filling the next four weeks.",
 rules="""- A number without an action is a dashboard; every row names what changes.
- Read stats from Substack's own pages; never quote a remembered figure.
- With single-digit subscribers, percentages are noise: report counts.
- Activity (posts made, notes sent) is input, never a result.""",
 subs=[
  ("weekly-scoreboard.md", "the Friday stats read", """# Sub-skill: weekly scoreboard

Columns: week, total subscribers, new free, new paid, top 3 sources with counts, issues sent, open rate per issue, Notes posted, Note follows, recommendations in/out with subscribers gained, review-page visits from substack.

Rows are read from rigoperator.substack.com/publish/stats and /publish/growth, signed in as the owner account. Each row ends with one action or "hold". Keep the file under `~/Desktop/Projects/kanban` notes for the funnel stream."""),
  ("flop-diagnosis.md", "diagnosing an issue that underperformed", """# Sub-skill: flop diagnosis

Work down the funnel, stop at the first break:
1. **Delivered?** Delivery rate and recipients. Low = list or deliverability.
2. **Opened?** Open rate vs the publication's own median. Low = subject line and sender name (ss-package).
3. **Read?** Views vs opens and time on page. Low = opening lines (ss-package) or format (ss-write).
4. **Acted?** Clicks on the next step and new subscribers. Low = the next step (ss-convert).
5. **Shared?** Reader sharing and restacks. Low = the idea was not worth passing on (ss-strategy).
Run Jev `signal.performance` on the diagnosis; write the one fix into next week's plan."""),
 ]),
}
