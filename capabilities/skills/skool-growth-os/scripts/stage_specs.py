"""Hand-written stage specs for the Skool community family. Laws come from the corpus notes;
everything here is RIG's own procedure, rules and sub-skills. Edit here, then run build_family.py."""

ORDER = ["sk-strategy", "sk-launch", "sk-content", "sk-engagement", "sk-growth",
         "sk-monetization", "sk-ads", "sk-lessons", "sk-gate", "sk-distribute",
         "sk-measure", "sk-ops"]

JEV = """## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: {judgments}. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check {rubric} --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `{rubric}` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`."""

GATES = ""

STAGES = {
"sk-strategy": dict(
 title="positioning, promise and the offer shape",
 desc="Positioning for a Skool community: who it is for, the one-line promise, community-first versus course-first, free versus paid, and the About page as the offer. USE WHEN starting or re-positioning a community, when members join but do not engage, or when Mike asks what the community should be about.",
 outcome="content-publishing: the community leaves this stage with a named member, a one-line promise, an offer shape (free/paid/price), and an About page that sells the promise",
 judgments="does a topic fit the promise, is the promise specific enough, which positioning option wins, is free or paid the right shape",
 rubric="idea.solid",
 when="Use before the first public invite, before any growth push, and whenever members churn without engaging. Not for classroom content (sk-content) or pricing detail (sk-monetization).",
 procedure="""1. **Name the member** in one sentence (role, company size, the bottleneck they carry). For RIG Intelligence Lab: an owner or ops lead at a small or mid-size company with AI tooling that is not running anything reliably.
2. **Write the promise** in the form `I help <member> get <outcome> without <pain>` and test it against three strangers: can they say in 10 seconds what happens inside?
3. **Community-first, not course-first** (corpus consensus): the community is a container where people solve real problems together; the classroom content is the byproduct collected from that work. Design the room before the curriculum.
4. **Choose the offer shape**: free community as top-of-funnel with a paid tier named after an outcome, or paid-only with a clear first-24-hours win. The corpus holds both winning; the deciding question is whether Mike's proof is visible before payment.
5. **Rewrite the About page as the offer**: promise, what members do each week, who it is for, who it is not for, one proof receipt, the next step. Biography goes last.
6. **Jev**: run the promise and offer shape through `idea.solid`; keep only PASS or record DEFERRED.
7. Hand the positioning card to sk-launch.""",
 handoff="`positioning-card.md`: member, promise, offer shape with price band, About-page draft. sk-launch tests it on a tiny cohort; sk-content builds the classroom from the promise.",
 rules="""- The About page, community name and price are public: drafted here, changed only after Mike's explicit yes (Gate-D).
- A claim on the About page needs a receipt (a dated number or a named, permissioned client). No invented results. Creator revenue numbers from the corpus are UNVERIFIED self-reports.
- Never position around the minor (Jacob) or reuse Lane A mascots (Birch, Unit 7, The Coach) in this community.
- Single-source laws are hypotheses: say so when one drives a recommendation.""",
 subs=[
  ("promise-and-shape.md", "writing the one-line promise and choosing free vs paid", """# Sub-skill: promise and offer shape

Use when the community has no clear promise, or the free/paid question is open.

1. Draft five promises in the form `I help <member> get <outcome> without <pain>`. Ban the words unlock, empower, leverage, optimize.
2. Score each with Jev `idea.solid`; drop any that is not a PASS. If Jev is down, mark all DEFERRED and bring the five to Mike unranked.
3. For the offer shape, answer in writing: does a stranger see proof before paying? Is the first win inside 24 hours? Can Mike run the room 3 months without new content? Each no pushes toward free-top-of-funnel.
4. Name 3 paid-tier candidates by OUTCOME (not by "premium"), and one price from the corpus bands ($7-25 one-time, $27-49/mo volume, $67-97/mo outcome-sharp). Mark the price UNVERIFIED if it came from a creator claim.
5. Output: the chosen promise, offer shape, price band with rationale, and the About-page draft, in `positioning-card.md`."""),

  ("about-page-audit.md", "auditing the About page against the promise", """# Sub-skill: About page audit

Use when the community has members but they join and go quiet, or before any growth push.

1. Read the About page and list every claim. For each: receipt or cut. A claim with no receipt is cut, not softened.
2. Run the stranger test on the first line: would a stranger know the outcome in 10 seconds?
3. Check the page answers: who it is for, what happens each week, who it is NOT for, the first win, the next step (one CTA).
4. Check it does not promise what the classroom cannot deliver in the first 30 days.
5. Output: a before/after About page (draft), the cut list, and the receipt list. Publishing the after-version is Gate-D."""),
 ],
),

"sk-launch": dict(
 title="validation, first members and the tiny test",
 desc="Validating a community idea with a tiny cohort before building anything heavy: the first 10-30 members, the enrollment conversation, and the kill/continue call. USE WHEN the idea is untested, when the first push to fill the room is due, or when growth has stalled at the start.",
 outcome="content-publishing: the idea survives or dies on evidence from a named tiny cohort, with the first 10-30 members inside and their first win recorded",
 judgments="is the idea validated enough to build, is this member a fit, did the test pass or fail",
 rubric="idea.solid",
 when="Use before building the classroom, and whenever member count stalls under ~30. Not for ongoing growth (sk-growth) or content design (sk-content).",
 procedure="""1. **Define the tiny test in writing** before inviting: how many members, over how many days, what counts as validation (for example: 10 members, 14 days, 5 of them complete one real workflow). A test without a written pass bar is a vibe.
2. **Recruit by conversation, not broadcast**: invite people Mike already knows have the bottleneck; the corpus favors direct conversations and problem interviews over open links at this stage.
3. **Interview every first-wave member** within 48 hours of joining: what bottleneck did they bring, what would make this worth paying for. Record answers verbatim; they are the content plan.
4. **Deliver one win manually** before automating anything: run one member's workflow through the lab's method (owner, sources, gates, approval boundary, ProofPacket) yourself.
5. **Make the kill/continue call at the deadline** against the written bar. If it fails: change the promise or the member, not the volume.
6. Hand to sk-content with the interview answers as the curriculum seed.""",
 handoff="`launch-record.md`: cohort roster, the written pass bar, interview answers verbatim, the win delivered, and the kill/continue call. sk-content builds the classroom from the interview answers.",
 rules="""- No paid ads in the tiny test (sk-ads waits until the promise converts organically).
- Interview answers are member material: never republish them without the member's yes.
- A failed test is recorded as failed. Do not redefine the pass bar after the deadline.
- Gate-D before any public post, invite blast or price change.""",
 subs=[
  ("tiny-test-design.md", "designing the validation test with a written pass bar", """# Sub-skill: tiny test design

Use when the community idea is untested or the first fill push is being planned.

1. Write the cohort size (10-30), the window (14-30 days) and the pass bar as one sentence: "N members do X by date D".
2. List 20 people Mike can invite by direct message who carry the bottleneck. Mark each: knows Mike / knows the problem / both. Invite the "both" tier first.
3. Write the enrollment question set (3-4 questions, bottleneck + what a win looks like + willingness to pay).
4. Pre-write the kill/continue rules: what evidence continues, what evidence kills, what evidence means "change the promise".
5. Output `tiny-test-plan.md`. Any public invite is Gate-D."""),
 ],
),

"sk-content": dict(
 title="classroom design and the value delivery engine",
 desc="Designing the classroom and the weekly value loop: what to teach, in what format, how the community's own work becomes content, and the lessons-learned pipeline. USE WHEN the classroom is empty or stale, when content is being planned, or when community work should become reusable lessons.",
 outcome="content-publishing: the classroom has a named path (first win -> core method -> advanced), a weekly value rhythm, and a working pipeline from community work to reusable lessons",
 judgments="does this content earn a classroom slot, is the format right, is this lesson publishable",
 rubric="post.viral",
 when="Use after the tiny test, before promising any curriculum, and whenever classroom usage drops. Not for member engagement mechanics (sk-engagement) or the publish gate (sk-gate).",
 procedure="""1. **Build backward from the first win**: the first classroom item must deliver the outcome the promise names, inside the first session. Everything else waits.
2. **Community-first content**: every real workflow the lab runs for a member becomes a de-identified classroom case (owner, sources, gates, approval boundary, ProofPacket shape). The byproduct model beats planned curriculum (corpus consensus).
3. **Format rules from the corpus**: short screenshotted walkthroughs over long lectures; one concept per item; checklists and templates over theory; each item ends with the member's next action.
4. **The lessons-learned pipeline** (sk-lessons owns the harvest; this stage owns placement): every published lesson gets a slot in the classroom's "Lessons Learned" section, dated, with the trap and the rule.
5. **Cadence**: one new classroom item per week maximum; stale-and-correct beats thin-and-often.
6. **Jev**: screen each item with `post.viral` before it enters the classroom.""",
 handoff="`classroom-plan.md`: the path (first win -> core -> advanced), the weekly rhythm, the de-identified case pipeline, and the Lessons Learned section layout. sk-gate screens items before they go live.",
 rules="""- De-identify every member case: no names, no company names, no raw numbers without permission.
- No verbatim transcript text from the corpus in classroom items; paraphrase and cite the video id.
- Every classroom claim of result is labeled: member-observed, RIG-internal, or creator self-report (UNVERIFIED).
- The classroom is public surface: adding items is reversible, but any item naming a client or a price goes through Gate-D.""",
 subs=[
  ("lesson-pipeline.md", "turning community work into reusable lessons", """# Sub-skill: lesson pipeline

Use when the lab has run workflows worth generalizing, or when the Lessons Learned section is empty.

1. Harvest candidates from: the run records of community workflows, Mike's memory ledgers, chat history, the Jake Studio vault, and the daily internet scout (sk-lessons runs the scout).
2. For each candidate write: title (specific), the trap (what goes wrong, concrete), the rule (what to do instead), source lineage (internal id or URL + date).
3. Strip before publishing: credentials, personal names, client names, job-search detail, internal paths, unflattering third-party specifics. Generalize the specific into the portable.
4. Screen with Jev `post.viral`; a lesson that only flatters or only warns without a rule does not ship.
5. Publish into the classroom Lessons Learned section with date + lineage label (member-observed / RIG-internal / public-source)."""),
 ],
),

"sk-engagement": dict(
 title="onboarding, conversation and retention",
 desc="Making members talk and stay: the first-48-hours onboarding, conversation prompts, the weekly rhythm, gamification that earns its place, and the churn signals. USE WHEN members join and go quiet, when the room feels dead, or when retention drops.",
 outcome="content-publishing: a new member gets a first win and a first conversation inside 48 hours, and the room has a weekly rhythm members can rely on",
 judgments="is this member at risk, is this prompt worth posting, is this gamification mechanic earning its place",
 rubric="signal.performance",
 when="Use once members are joining (sk-launch feeds it), continuously after. Not for getting members in the door (sk-growth) or content design (sk-content).",
 procedure="""1. **The 48-hour rule**: every new member gets a personal welcome referencing the bottleneck they named at enrollment, plus one concrete next step, within 48 hours. The corpus calls out talking to new members as the highest-leverage retention act.
2. **Prompt the room weekly**: one discussion prompt tied to a real workflow, not to "how is everyone doing". Prompts members can answer with their own work get replies; abstract prompts do not.
3. **Wins are the engine**: run a Wins thread; celebrate member outcomes with specifics. Leaderboards reward contribution (helpful replies, completed workflows), never raw activity.
4. **Office-hours rhythm**: one recurring live touch (call, hot seat, or async review) at a fixed time; consistency is what members cite when they stay.
5. **Churn signals to watch**: no post within 14 days of joining, no reply to the welcome, missed two sessions. Each triggers one personal check-in, not an automation.
6. **Gamification audit**: points/levels/badges only where the corpus evidence is that they drive the behavior wanted (replies, completions). Cut mechanics that only inflate vanity counts.""",
 handoff="`engagement-playbook.md`: the 48-hour onboarding script, the weekly prompt bank, the Wins ritual, the churn-signal list with check-in scripts. sk-measure tracks whether these work.",
 rules="""- Never fabricate engagement: no fake members, no reply rings, no engagement pods.
- Personal check-ins are personal: no mass DMs dressed as check-ins.
- A member's situation stays in the room: no republishing member problems as content without a yes.
- Public posts on behalf of the community go through sk-gate and Gate-D.""",
 subs=[
  ("onboarding-48h.md", "the first 48 hours for a new member", """# Sub-skill: onboarding-48h

Use when a member joins, and to audit the onboarding flow.

1. Within 48 hours, send a personal welcome that names the bottleneck they gave at enrollment (or their profile if the community is open-join).
2. Give ONE next step (a classroom item or a workflow to bring), not a list.
3. Ask one question that invites a real answer ("what's the workflow that's most broken right now?").
4. Log the welcome and the answer; the answer seeds the weekly prompt bank.
5. If no reply in 7 days: one follow-up. If no reply in 14: mark at-risk and stop messaging until they move."""),
 ],
),

"sk-growth": dict(
 title="traffic, lead magnets and filling the room",
 desc="Getting members in the door: the traffic sources that work for communities, lead magnets, the zero-audience playbook, YouTube/content funnels, and referral loops. USE WHEN the room is under-filled, when a growth channel is being chosen, or when a lead magnet is being built.",
 outcome="content-publishing: a named traffic source with a measured member-per-week rate, one lead magnet earning its keep, and a referral loop members actually use",
 judgments="is this channel worth the effort, is this lead magnet strong enough, is this growth tactic honest",
 rubric="idea.solid",
 when="Use after the promise survives its tiny test (sk-launch). Not for paid acquisition (sk-ads) or distribution of community content (sk-distribute).",
 procedure="""1. **One channel at a time**: pick the single channel where the member already spends attention (for RIG: LinkedIn and YouTube for ops/AI buyers), run it 30 days, measure members per week before adding another.
2. **Zero-audience playbook** (corpus): direct conversations and borrowed audiences (comments, collaborations, podcasts, others' newsletters) beat broadcasting into an empty room; show up where the bottleneck is already discussed.
3. **Lead magnet = a solved slice of the promise**: a checklist, template, or mini-workflow that delivers one win without the community, ending with the natural next step inside. The corpus's strongest magnets are outcome-named and small.
4. **Content funnel**: publish the de-identified cases and lessons publicly (sk-distribute places them); the community link is the CTA, one per piece.
5. **Referral loop**: ask members who got a win to name one person with the same bottleneck; make the ask specific and easy, never incentivized into spam.
6. **Jev**: screen each tactic with `idea.solid`; growth that needs deception is cut.""",
 handoff="`growth-plan.md`: the chosen channel with a 30-day plan, the lead magnet spec, the referral ask script, and the members-per-week target. sk-ads is the paid escalation; sk-measure reports the rate.",
 rules="""- No fake engagement, no bought members, no link spam in other people's spaces (comment rules: positive-only, add value, one soft link at most).
- Every growth claim is labeled measured vs projected.
- Cold outreach beyond warm connections follows the gtm-cold-send-safety-gate before anything sends.
- Anything that publishes or sends externally is Gate-D.""",
 subs=[
  ("lead-magnet-slice.md", "building a lead magnet that is a solved slice of the promise", """# Sub-skill: lead magnet slice

Use when a lead magnet is needed or an existing one is not converting.

1. Take the promise and pick the slice a stranger can complete in under 30 minutes (one workflow, one checklist, one template).
2. Build it so it delivers a real win WITHOUT the community; the community then sells the next win, not the first.
3. Name it by outcome ("the workflow owner map", not "AI guide v2").
4. End with one CTA: the next step inside the community. One link, one action.
5. Track: downloads -> joins -> first-win rate. A magnet with downloads but no joins gets its CTA rewritten before its content."""),
 ],
),

"sk-monetization": dict(
 title="pricing, offers and the free-to-paid conversion",
 desc="The money model: price bands, free-to-paid conversion, offer ladders, high-ticket offers, and what the corpus says actually sells on Skool. USE WHEN setting or changing price, when free members are not converting, or when designing an upsell.",
 outcome="content-publishing: a price and offer ladder with a named conversion path from free member to paid outcome, each rung justified by a receipt or labeled untested",
 judgments="is this price right, is this offer sound, is this conversion path honest",
 rubric="offer.eval",
 when="Use after engagement works (members talk and stay). Not for growth volume (sk-growth) or positioning (sk-strategy).",
 procedure="""1. **Price from the outcome band**: the corpus price bands that clear are $7-25 one-time (small assets), $27-49/mo (volume communities), $67-97/mo (outcome-named, persona-sharp), $199+ only as ladder-top with thin visible demand. Pick the band the promise can carry and label any creator number UNVERIFIED.
2. **Name the paid tier after the outcome**, not "premium": members buy the named transformation.
3. **Free-to-paid path**: the free room proves the method; the paid tier carries the named outcome (done-with-you workflows, reviews, live seats). Publish exactly what changes at the boundary.
4. **The conversion moment is a win**: convert members right after they experience a first win, not on a timer.
5. **Offer ladder**: free -> paid community -> high-ticket (done-for-you or intensive). Each rung needs its own promise; do not stack vague "VIP" tiers.
6. **Jev**: run each offer through `offer.eval`.""",
 handoff="`monetization-card.md`: tier map with prices and outcome names, the conversion moment design, the ladder. sk-gate screens all public price/offer language; the price change itself is Gate-D.",
 rules="""- No invented scarcity and no fake countdowns; price changes are announced honestly with the real reason.
- Never quote a creator's revenue figure as expected outcome; the corpus's $61K/mo, $100K/mo, $18K/mo claims are self-reports (UNVERIFIED).
- Refund and cancellation terms are published before the first charge.
- Setting or changing a price is Gate-D.""",
 subs=[
  ("tier-map.md", "designing the free/paid/ladder tier map", """# Sub-skill: tier map

Use when pricing is being set or the free members are not converting.

1. Write the free tier's job in one sentence (prove the method, build trust, feed the ladder).
2. Write the paid tier's named outcome and exactly what the member gets (sessions, reviews, templates, access).
3. Pick the price band from the corpus bands and justify it against the outcome; if the justification is a creator claim, label it UNVERIFIED.
4. Define the conversion moment (which win, which message) and the offer ladder above it if any.
5. Check every public claim has a receipt or is labeled projected. Output `monetization-card.md`; the price change is Gate-D."""),
 ],
),

"sk-ads": dict(
 title="paid acquisition and the spend discipline",
 desc="Paid traffic for the community: when to spend, what to test, budget caps, and the honest read of whether ads worked. USE WHEN organic growth is proven and scaling is the goal, or when an ad test is being designed.",
 outcome="content-publishing: a capped, dated ad test with a pre-written success bar and an honest read of members-per-dollar against organic",
 judgments="is this ad worth spending on, did the test pass, is this audience honest",
 rubric="offer.eval",
 when="Use only after the promise converts organically (sk-growth shows a measured members-per-week rate). Not for organic channels (sk-growth).",
 procedure="""1. **Precondition**: organic conversion exists on the current promise. Ads amplify a working message; they do not fix a weak one.
2. **Test design**: one audience, one message, one lead magnet, a written success bar (cost per member vs the band), and a hard spend cap ($300 total was Mike's stated test cap for RIG's first ad test; treat any other cap as needing his yes).
3. **Two-way honesty**: report cost per member, but also 30-day retention of paid-ad members versus organic; cheap members who leave are not growth.
4. **Kill fast**: a test that misses the bar at the cap is killed, not extended "one more week".
5. **Jev**: screen the audience and message with `offer.eval` before spend.""",
 handoff="`ad-test-record.md`: audience, message, magnet, success bar, cap, and the honest read (cost/member + retention). sk-measure holds the funnel numbers.",
 rules="""- Every dollar spent is Gate-D: the cap, the audience and the message appear in the request before spend.
- No exaggerated or unprovable ad claims; ads obey the same receipt rules as any public content.
- Never spend on a promise that has not converted organically.""",
 subs=[
  ("ad-test-card.md", "designing one capped ad test", """# Sub-skill: ad test card

Use when scaling is on the table and organic conversion is measured.

1. State the pre-written success bar: cost per member at or below X, or the test fails.
2. Fix the cap in writing (default $300 total for a first RIG test) and the window.
3. One audience, one message, one lead magnet; no multi-variant sprawl in test one.
4. Pre-write the kill condition and the 30-day retention read.
5. Output `ad-test-card.md` and file a Gate-D request before a single dollar moves."""),
 ],
),

"sk-lessons": dict(
 title="the lessons-learned engine (harvest, generalize, publish)",
 desc="The lessons-learned pipeline that feeds the community: harvesting from memory, chat history, the Jake Studio vault and a daily internet scout; generalizing for public consumption; and publishing dated, sourced lessons into the classroom. USE WHEN the Lessons Learned library needs content, when a daily scout is running, or when an internal lesson should become public.",
 outcome="content-publishing: a dated, sourced lessons library where every entry carries a trap, a rule, and honest lineage (member-observed / RIG-internal / public-source)",
 judgments="is this lesson publishable, is the lineage honest, is this source trustworthy enough to cite",
 rubric="atomic.claim",
 when="Use continuously; the daily scout runs from here. sk-content owns WHERE lessons sit in the classroom; this stage owns what gets harvested and generalized. Not for community engagement (sk-engagement).",
 procedure="""1. **Four harvest sources**: (a) RIG internal ledgers (memory, `~/.rig/jake/kpi/lessons.jsonl`, Jake Studio vault `Memory/lessons.json` and Doctrines), (b) chat/session history via recall, (c) community run records (de-identified), (d) a daily internet scan (surfaces: engineering blogs, postmortems, HN threads about AI/automation failures).
2. **Generalize before publishing**: strip credentials, personal names, client names (Ideawake/Coby/Jacob and any member), job-search and personal-finance detail, internal paths. A lesson that only works with the stripped detail is not portable and does not ship.
3. **The lesson shape**: title (specific), the trap (what goes wrong, concrete), the rule (what to do instead), lineage (internal id or URL + date).
4. **Screen with Jev `atomic.claim`**: one falsifiable rule per lesson; compounds are split.
5. **Publish with dates and lineage labels**; corrections are appended, never silently edited. A lesson overturned later gets a dated correction note.
6. **Quality bar for the daily scout**: at most 1-3 lessons per day; the scout reports empty days as empty, never fills quota with filler.""",
 handoff="`lessons-batch.md` per day: the candidates harvested, the ones generalized, the ones rejected with reasons, and the published ids. sk-gate screens each before it goes live in the classroom.",
 rules="""- Publication of any lesson is Gate-D per batch (draft freely; the publish step is his).
- Never publish a lesson whose lineage is internal-only without generalizing; never publish member stories without the member's yes.
- A scout finding is never repeated as fact without its URL and date; stale advice is labeled dated.
- The lessons library is a living document: corrections are dated additions, not rewrites.""",
 subs=[
  ("daily-scout.md", "running the daily lessons-learned internet scout", """# Sub-skill: daily lessons scout

Use for the daily scan of the public web for lessons worth teaching.

1. Scan the surfaces: engineering blogs and postmortems, HN (AI/automation failure threads), practitioner newsletters, and the Skool/creator growth channels where tactics are tested publicly.
2. Collect at most 5 candidates; score each: trap concreteness (does it name a failure mode), rule actionability (can an operator act on it), source honesty (named source + date).
3. Generalize and shape (trap/rule/lineage); reject anything that needs a name, a customer, or a credential to make sense.
4. Write `lessons-batch.md` dated with ids LL-YYYYMMDD-NN; mark each member-observed / RIG-internal / public-source.
5. The publish step into the classroom is a separate, Gate-D-gated action. Empty day? Report zero and stop."""),
  ("lesson-shape.md", "shaping one lesson for publication", """# Sub-skill: lesson shape

Use when one internal lesson is being generalized for the public library.

1. Title: specific and concrete ("the green gate that never turns red", not "testing matters").
2. Trap: what goes wrong, with the mechanism, not the mood.
3. Rule: one falsifiable instruction ("checksum before/after every planted failure"), not a value ("be rigorous").
4. Lineage: internal id or URL + date; label the class (member-observed / RIG-internal / public-source).
5. Strip list check: no credentials, no personal or client names, no internal paths, no personal finance. Then Jev `atomic.claim`."""),
 ],
),

"sk-gate": dict(
 title="the pre-publish gate for community surfaces",
 desc="The single gate before anything goes live on community surfaces: claim hygiene, Jev screen, the anti-slop pass, the lane check (minor/client/personal), and the Gate-D request for anything outward. USE WHEN a classroom item, lesson, post, About change or price language is about to go live.",
 outcome="content-publishing: nothing goes live on community surfaces without a dated gate record naming the claims checked, the Jev verdict or DEFERRED, and the Gate-D request id when one is due",
 judgments="post gate verdict, is this claim supported, is this lane clean",
 rubric="post.viral",
 when="Use before every live change to the classroom, About page, community posts, or price language. Not for drafting (any stage drafts freely).",
 procedure="""1. **Claim hygiene**: every number, result and comparison gets a receipt or a label (projected / self-report UNVERIFIED). A claim with no receipt is cut.
2. **Lane check**: content about a minor (Jacob) is STOP - never published here; client-lane material (Ideawake/Coby) never inherits this community's voice; personal-brand mascots (Birch, Unit 7, The Coach) stay out.
3. **Jev screen** with `post.viral` (or `atomic.claim` for lessons); record the decision id. DEFERRED blocks the "judged" claim but not the draft.
4. **Anti-slop pass**: no banned words (unlock, empower, synergy, leverage, disrupt, hustle, utilize, iterate, optimize), no hype without mechanism, no fabricated urgency.
5. **Verdict**: SHIP (reversible, in-lane, claims clean) or HOLD-with-reason. Anything outward, priced, or naming a person gets a Gate-D request with the exact payload; only Mike's approval releases it.""",
 handoff="`gate-record.md` per item: the claims table (claim / receipt / label), lane verdict, Jev id or DEFERRED, verdict SHIP or HOLD, and the Gate-D request id when one is due.",
 rules="""- The gate never publishes; it clears or holds. Publishing is a separate action with its own Gate-D check when outward.
- A Jev DEFERRED is never reported as a pass.
- Minor-lane content is never cleared, under any wording.
- The gate record is dated and kept; a later correction references the original record id.""",
 subs=[
  ("claim-hygiene.md", "the claims table for one item", """# Sub-skill: claim hygiene

Use when a classroom item, lesson or post carries numbers or results.

1. List every claim in the item as a row: claim text, receipt (file/URL/date) or label (projected / self-report UNVERIFIED).
2. Cut every row with neither receipt nor label. Do not soften; cut.
3. Cross-check labels against the corpus rules: creator revenue figures are always self-report UNVERIFIED; member results need the member's yes.
4. Output the claims table into `gate-record.md`; the table is the evidence for the gate verdict."""),
 ],
),

"sk-distribute": dict(
 title="multi-channel advertising of community content",
 desc="Taking community content and lessons to the channels where the member already is: LinkedIn, X, Reddit, Substack, YouTube, and the per-channel adaptation rules and route-back. USE WHEN a piece of classroom content or a lesson should reach beyond the community, or when the advertising plan is being run.",
 outcome="content-publishing: each piece reaches its channels with per-channel adaptation done and one clear route back to the community, measured by joins per piece",
 judgments="is this channel a fit for this piece, is the adaptation quality, is this comment/pitch acceptable",
 rubric="post.viral",
 when="Use when content has cleared sk-gate and the goal is reach beyond the community. Not for growth mechanics inside a channel (sk-growth) or the gate itself (sk-gate).",
 procedure="""1. **One piece, adapted per channel**: never raw cross-post. LinkedIn gets the professional frame and no raw links in the body (first comment carries the link); X gets the compressed claim; Reddit gets the value-first long version with the link only where the subreddit allows; Substack gets the full narrative; YouTube gets the walkthrough.
2. **Route-back rule**: every channel piece ends with one next step into the community (the lead magnet or the About page), one link, one action.
3. **Community-first comment rule**: comments on others' posts are positive-only - validate the point, add one insight, at most one soft link. (RIG's measured lesson: untargeted following/engagement suppresses reach.)
4. **Pacing**: the corpus and RIG's own measurements both say burst patterns suppress reach; spread actions with jitter, hold daily ceilings.
5. **Measure joins per piece per channel**, not impressions; a channel that earns impressions and no joins gets its route-back rewritten before it gets cut.""",
 handoff="`distribution-log.md`: piece id, channels used with adaptation notes, the route-back link, joins per channel. sk-measure reads the log for the funnel.",
 rules="""- Every public post is Gate-D before it goes out; drafts and adaptation are free.
- No engagement pods, no bought reach, no link spam; comment rules are positive-only.
- Client-lane accounts (Ideawake) are never used to advertise this community.
- Reddit and group rules are read before posting; a subreddit's rules beat this skill's procedure.""",
 subs=[
  ("channel-adaptation.md", "adapting one piece for a named channel", """# Sub-skill: channel adaptation

Use when a cleared piece is being prepared for a specific channel.

1. Restate the piece's one claim in the channel's grammar: LinkedIn (professional, no body links), X (compressed, thread if needed), Reddit (value-first, rules-checked), Substack (narrative), YouTube (walkthrough).
2. Keep the claim identical across channels; only the frame changes. A number altered per channel is a lie.
3. One route-back per piece, in the channel's allowed position.
4. Jev screen the adapted version (`post.viral`); adaptations that drift from the source claim fail the gate.
5. Log it in `distribution-log.md` with the joins target."""),
 ],
),

"sk-measure": dict(
 title="the numbers that decide what to do next",
 desc="Measurement for the community: the weekly numbers, the funnel (visitor -> member -> engaged -> paid -> win), what each number makes you do, and the honest read of what is not measurable. USE WHEN reporting how the community is doing, before planning the next month, or when a tactic's results are being judged.",
 outcome="content-publishing: a weekly community report where each number carries one action, and every unmeasurable is named as unmeasurable",
 judgments="is this movement real, is this number trustworthy, what does this data make us do",
 rubric="signal.performance",
 when="Use weekly and before every planning round. Not for designing tactics (their stages own that).",
 procedure="""1. **The funnel**: visitors (About views), members (joined), engaged (posted/replied/completed a workflow), paid, wins (named outcomes). Each stage has one number, one owner, one action threshold.
2. **Weekly read, not daily**: compare week to week; daily numbers on a small community are noise.
3. **Every number drives an action**: a metric with no action is a dashboard decoration and is cut or given an action. (Mike's rule: a number that only informs is a dashboard.)
4. **Name what is not measurable**: Skool's analytics are limited; do not infer intent from impressions. Anything not measured says "not measured", never zero.
5. **Retention read**: 30-day retention of paid-ad members versus organic; this is the honest growth read.
6. **Jev**: movement claims pass `signal.performance` before they drive a plan change.""",
 handoff="`weekly-report.md`: the funnel table with actions, the week-over-week deltas with verdicts, and the named-unmeasurables list. sk-strategy and sk-growth consume it for the next plan.",
 rules="""- No number appears without its source (Skool dashboard, community run record, or a named measurement) and date.
- A small-n movement (under ~10 events) is labeled noisy, not significant.
- Nothing is reported as zero when it is unmeasured.
- The report is internal; publishing any number publicly goes through sk-gate.""",
 subs=[
  ("funnel-table.md", "building the weekly funnel table", """# Sub-skill: funnel table

Use when the weekly report is due or a tactic is being judged.

1. Fill the funnel rows: About views / members / engaged / paid / wins - each with the number, its source, and the date window.
2. For each row add: the action threshold and the current action (grow / fix / cut / measure first).
3. Mark each movement: real (n>=10 and sustained), noisy (n<10), or unmeasured.
4. Add the 30-day retention split (ad vs organic) when ads have run.
5. Output `weekly-report.md`; the report ends with at most 3 plan changes, each tied to a number."""),
 ],
),

"sk-ops": dict(
 title="running the room: systems, automations and time",
 desc="The operating layer: what runs the community day to day, what to automate (and what never to), the routine inventory, the local-first tooling stance, and the time budget of the owner. USE WHEN standing up automation for the community, when the weekly workload is unsustainable, or when auditing what is actually running.",
 outcome="content-publishing: a named operating rhythm where every automation has a fail-loud guard, an owner, and a proven run, and the owner's weekly time in the room is stated and bounded",
 judgments="is this automation safe to run unattended, is this routine actually running, is this process worth its time",
 rubric="plan.readiness",
 when="Use after the room has real members and real rhythms to automate. Not for content or growth design.",
 procedure="""1. **Automate the repeatable interior, never the outward act**: welcome sequences, weekly prompt scheduling, metrics collection, and scout runs are automatable; posting publicly, pricing changes, and member conversations with weight stay human (Gate-D).
2. **Fail-loud guard on every routine**: a scheduled job that cannot do its work emits one explicit `BLOCKED:` line and stops; a clean run with zero output is indistinguishable from success otherwise. Verify produced counts from the source of truth.
3. **Proven run, not a live definition**: a routine counts as running only when a run reached `completed` with an artifact. (RIG's measured lesson: scheduled, full-access routines sat suspended on approval gates for weeks while their definitions claimed schedules.)
4. **Local-first with a named fallback** (Mike's standing model policy): community automations route to a dependable local model first; any paid route carries a fallback procedure, since a settings lane holds exactly one model.
5. **Time budget**: state the owner's weekly hours in the room (onboarding, prompts, live touch) and hold it; a community that needs 20 unlisted hours a week is a job, not an asset.
6. **Inventory audit**: before adding any tool, check what already covers the ground; no second system for the same job.""",
 handoff="`ops-map.md`: the routine inventory (name, schedule, model lane, guard, last proven run), the automation boundary table (automate / human / Gate-D), and the weekly time budget.",
 rules="""- Nothing outward runs unattended without a Gate-D-approved boundary; the approval names the action and the target.
- A routine without a proven `completed` run is reported as not running, however live its definition looks.
- Never print or store raw secrets; reference keychain item names (`com.rig.env.*`).
- Deleting or pausing a working routine is reversible but named to Mike first.""",
 subs=[
  ("routine-inventory.md", "auditing what is actually running", """# Sub-skill: routine inventory

Use when adding community automation or when reporting what runs the community.

1. List every routine touching the community: name, schedule, model lane, permission mode, and its LAST PROVEN RUN (completed + artifact path).
2. Mark each: running (proven), dormant (defined, no proven run), or blocked (last run emitted BLOCKED/errored/suspended).
3. For each automation, state the guard that makes failure loud.
4. Check for duplicate coverage before adding anything new.
5. Output `ops-map.md`; report dormant routines as dormant, never as running."""),
 ],
),
}
