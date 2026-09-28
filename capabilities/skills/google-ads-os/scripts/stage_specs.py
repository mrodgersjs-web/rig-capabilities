"""Hand-written stage specs for the Google Ads family. Laws come from the corpus notes;
everything here is RIG's own procedure, rules and sub-skills. Edit here, then run build_family.py."""

ORDER = ["ga-strategy", "ga-structure", "ga-tracking", "ga-keywords", "ga-campaigns",
         "ga-bidding", "ga-ads", "ga-landing", "ga-budget", "ga-reporting", "ga-local-b2b"]

JEV = """## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: {judgments}. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check {rubric} --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `{rubric}` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`."""

STAGES = {
"ga-strategy": dict(
 title="goals, offers and the measurement plan before any build",
 desc="Strategy for a Google Ads account: business goal, offer, target customer and geography, budget reality, the measurement plan and the pre-build audit. USE WHEN starting an account or a new motion, when spend is planned without a named conversion, or when Mike asks what the ads should be doing.",
 outcome="revenue-gtm: the account leaves this stage with a named goal, a named conversion, an approved budget ceiling, and a written plan before any campaign exists",
 judgments="is the goal measurable, is the offer specific enough to buy, is this plan ready to execute",
 rubric="plan.readiness",
 when="Use before the first campaign, before any budget decision, and whenever a new service or geography enters the account. Not for building campaigns (ga-structure, ga-campaigns) or writing ads (ga-ads).",
 procedure="""1. **Name the business goal in money terms**: calls, booked estimates, signed deals - not impressions or clicks. State the value of one conversion so every later number has a denominator.
2. **Name the conversion actions** that prove the goal (call, form submit, purchase, booked meeting) and hand them to ga-tracking. No campaign is planned before these exist.
3. **Sharpen the offer**: what is being sold, to whom, at what entry point. A landing page and an ad both paraphrase this line (ga-landing, ga-ads).
4. **Set the budget ceiling as math**: monthly budget divided by realistic cost-per-lead, times lead-to-sale rate. If the arithmetic cannot plausibly buy one customer, the plan is not ready - say so instead of spending.
5. **Audit any existing account first** (change history, tracking state, disapprovals, past spend and results) before proposing anything new (sub-skill account-audit-first).
6. **Jev**: run the plan document through `plan.readiness`; fix the plan or record DEFERRED. DEFERRED blocks "ready to spend".
7. Hand the plan to ga-structure. Any spend or budget figure is Gate-D through Mike.""",
 handoff="`ads-plan.md`: goal, conversion actions, offer line, customer/geography, budget ceiling with arithmetic, audit findings. ga-structure designs the account from it; ga-tracking builds the conversions.",
 rules="""- No budget number changes, campaign enablement or spend action ever happens without Mike's explicit approval (Gate-D). Sub-agents draft; the parent operator acts.
- Every number in the plan is a sourced receipt (account data, keyword planner range, client CRM figure) or is labelled as an assumption.
- A plan without a named conversion action is not a plan; it is a wish. Return it to step 2.
- Creator case-study numbers from the corpus are UNVERIFIED and never appear in a plan as expected results.
- Platform mechanics cited from the corpus are dated; re-verify in the live account before relying on them.""",
 checklist=["Goal and one conversion value named in money terms",
            "Conversion actions listed and handed to ga-tracking",
            "Offer line written in one sentence",
            "Budget ceiling math shown (budget / CPL / close rate)",
            "Existing account audited or explicitly new",
            "Jev `plan.readiness` run on the plan document; decision id recorded",
            "Spend and budget changes routed to Mike (Gate-D)"],
 subs=[
  ("offer-and-goal-card.md", "writing the one-line offer and the goal card that every later stage cites", """# Sub-skill: offer and goal card

Use when the account has no written goal, or when the offer has drifted into generic service language.

1. Write the goal card: one line for the business goal (money), one for the conversion action that proves it, one for the value of one conversion, one for the monthly ceiling.
2. Write the offer line in the form `We help <who> get <outcome> via <service> starting at <entry point>`. Ban the words solutions, innovative, partner, and best-in-class.
3. Test the offer line against the actual service pages: if the site does not say it, the ad cannot promise it.
4. Score the offer with Jev `offer.eval` (advisory); record the decision id. If Jev is down, mark DEFERRED and bring the options to Mike unranked.
5. Output: `ads-plan.md` opening section. Every later stage cites this card instead of re-deciding the goal."""),
  ("account-audit-first.md", "auditing an existing account before proposing any change", """# Sub-skill: account audit first

Use before touching any account that has history. An account that has already spent money carries evidence; read it before rebuilding.

1. Change history: who changed what and when. Note the last 90 days of budget, bid and status changes.
2. Tracking state: conversion actions present, status recording or no recent conversions, any duplicate tags. Google prompting "Set up conversion tracking" means clicks were being bought blind.
3. Serving state read live: campaign and keyword status, `Eligible (Limited)` flags, disapprovals, low-search-volume markers, billing holds.
4. Results so far: spend, conversions, cost per conversion by campaign. Read from the account, never from a report document that may be stale.
5. Search terms and negatives: what the account has been matching on.
6. Output: `audit-<date>.md` with findings and three proposed next actions, ranked. The audit goes through Jev (`signal.performance` for any result claim) before the plan cites it."""),
 ]),

"ga-structure": dict(
 title="account structure in the keyword-signal era",
 desc="Account structure for Google Ads: campaign purpose, theme-based ad groups, brand vs non-brand separation, geo and language splits, naming, and shared-budget rules. USE WHEN building a new account, when an account has grown by accretion, or when structure questions (SKAGs, match control, single-keyword themes) come up.",
 outcome="revenue-gtm: a written account architecture where every campaign has one stated job, every ad group one theme, and every split exists because bidding or budgets differ",
 judgments="is this structure sound for the goal, does this theme deserve its own ad group, which architecture option wins",
 rubric="idea.solid",
 when="Use after ga-strategy and before ga-campaigns builds anything. Not for keyword selection itself (ga-keywords) or campaign-type mechanics (ga-campaigns).",
 procedure="""1. **One job per campaign**: name each campaign's job (brand defence, inbound search, outbound/display, PMax for feed-driven reach, local). A campaign with two jobs gets split.
2. **Theme-based ad groups**: each ad group holds one theme (service x intent), with keywords, ads and landing page all saying the same thing. SKAG thinking is dead (corpus consensus); rebuilds of single-keyword ad groups add maintenance without control.
3. **Brand separated**: brand defence runs in its own campaign so its cheap, certain conversions never inflate or subsidise prospecting metrics.
4. **Split only where money differs**: geo, language, device or daypart splits are justified only when bids or budgets must differ. Structural purity is not a reason to split.
5. **Match philosophy**: keywords are signals to Google's meaning matching, not exact control. Structure for intent and message match; the negative system (ga-keywords) is the control surface.
6. **Naming convention**: `<goal>-<geo>-<theme>-<type>` so any report, script or 3am incident sorts correctly.
7. **Jev**: run the architecture doc through `idea.solid`; record or DEFERRED. Hand to ga-campaigns.""",
 handoff="`architecture.md`: campaign jobs table, ad group themes, split rationale, naming convention. ga-campaigns instantiates each campaign type; ga-keywords fills the themes.",
 rules="""- Never rebuild SKAGs. The matching system that made them necessary no longer exists (corpus consensus; the 2019 advice in the corpus is flagged dated).
- Brand campaigns are worth running even when they feel redundant; never merge brand into prospecting.
- A split needs a money reason (different bids or budgets), not tidiness.
- Smart bidding works at the campaign's conversion data level: never fragment themes so thin that each campaign starves the learning system.
- Spend-affecting structural changes go through Gate-D.""",
 checklist=["Every campaign has one stated job in `architecture.md`",
            "Every ad group is one theme, and its ad and landing page agree",
            "Brand is its own campaign",
            "Each split states its money reason (different bids/budgets) or is removed",
            "Naming convention documented and applied",
            "No SKAG rebuilds anywhere in the plan",
            "Jev `idea.solid` run on the architecture doc"],
 subs=[
  ("single-purpose-campaigns.md", "splitting accreted accounts into single-purpose campaigns", """# Sub-skill: single-purpose campaigns

Use when an account has grown by accretion: campaigns doing two jobs, ad groups that are theme soup, brand mixed into prospecting.

1. List every campaign and write its job in one line. A campaign whose line contains "and" is a split candidate.
2. Map each existing ad group to a theme. Themes that share a landing page and an offer stay together; themes that need different ads or pages split.
3. Move brand keywords into their own campaign first; it is the cheapest, least risky split and immediately clarifies the rest of the metrics.
4. Count conversions per resulting campaign against the bidding strategy's need (corpus rule of thumb: smart bidding wants ~30+ conversions per month per campaign to learn; below that, consolidate rather than split).
5. Migrate with history in mind: prefer restructuring gradually over pausing everything at once; a rebuilt campaign restarts learning.
6. Write the before/after map into `architecture.md` so the change is auditable after the fact."""),
  ("naming-and-hierarchy.md", "the naming convention, labels and hierarchy that keep reports honest", """# Sub-skill: naming and hierarchy

1. Adopt one convention everywhere: `<goal>-<geo>-<theme>-<type>` (example: `leads-denver-hvac-search`). Keep it lowercase, hyphen-delimited, no personal names.
2. Encode budget tier in the name only if budgets actually differ by tier; names describe mechanics, not hopes.
3. Use labels for everything soft (test status, funnel stage, priority, quarter): labels sort and filter without forcing a rename.
4. Document the convention at the top of `architecture.md`; future audits and scripts parse names.
5. Reconcile existing campaigns against the convention before building new ones; rename in one pass, and never rename mid-experiment (it destroys the readable history of the test).
6. Check that the convention survives export: no commas or pipes inside names."""),
 ]),

"ga-tracking": dict(
 title="conversion tracking as the foundation",
 desc="Conversion tracking for Google Ads: conversion actions, the Google tag and GTM, call and form tracking, enhanced conversions, GA4 imports, offline/CRM imports and consent mode. USE WHEN building a new account, before any bidding strategy change, when Google prompts to set up conversion tracking, or when reported conversions disagree with the CRM.",
 outcome="revenue-gtm: every conversion action defined, firing, and proven by a test before any money is spent",
 judgments="is this conversion a real, single, attributable action, is this tracking setup sound",
 rubric="atomic.claim",
 when="Use before the first campaign goes live and before any smart bidding. Not for account structure (ga-structure) or reporting (ga-reporting).",
 procedure="""1. **Define conversion actions** from the goal card (ga-strategy): one primary action per goal (call lead, form submit, purchase, booked meeting). Duplicates and vanity micro-conversions are demoted to secondary or removed.
2. **Install the Google tag** (direct or GTM) on every page; confirm it fires in Tag Assistant / the real-time report, not just in the source code.
3. **Call and form reality** (corpus consensus for lead gen): track phone calls at the account level with call detail, and form submits via a thank-you-page or event trigger. Phone is the primary conversion for most local service businesses.
4. **Enhanced conversions** on: hashed first-party data improves measurement in a consent-restricted world; verify the setting is actually recording.
5. **Import the right second source**: GA4 key events or offline CRM imports (with Google Click ID capture) for sales-qualified outcomes. One conversion action fires once per goal; count the click's downstream outcome, not the same lead twice.
6. **Consent mode and privacy**: regions with consent requirements get a consent-mode setup; never model or fabricate conversions to compensate for lost tracking.
7. **Prove it live**: fire a test conversion of each type and see it land in the account before spend. Google showing "Set up conversion tracking" is a red flag, not a suggestion.
8. **Jev**: each conversion action definition through `atomic.claim`; DEFERRED blocks launch.""",
 handoff="`tracking-plan.md`: conversion actions with primary/secondary status, firing mechanism, test evidence (screenshot or real-time check), import sources. ga-bidding is only allowed after this is proven.",
 rules="""- Never turn on spend, and never switch to smart bidding, with unproven conversions (corpus consensus; the failure mode is bidding against noise).
- One real-world outcome = one conversion action. No duplicate goals counting the same lead.
- Never edit tracking to make a report look better; tracking reflects reality.
- Do not model, backfill or fabricate conversions when consent blocks measurement; report the gap instead.
- Account-level changes to conversion settings are audited through change history (ga-reporting).""",
 checklist=["Every conversion action defined with primary/secondary status",
            "Google tag verified firing on all key pages",
            "Call tracking and form/thank-you-page tracking both proven (lead gen)",
            "Enhanced conversions on and recording",
            "GA4/offline imports wired where the goal lives downstream",
            "Consent mode handled for the target regions",
            "Test conversions fired and observed landing in the account",
            "Jev `atomic.claim` run on each conversion definition"],
 subs=[
  ("conversion-actions.md", "defining, deduplicating and prioritising conversion actions", """# Sub-skill: conversion actions

1. Start from the goal card: each business goal maps to exactly one primary conversion action.
2. Classify every existing action: primary (bids optimise toward it) or secondary (reporting only). Anything counting the same real-world event twice is deleted, not demoted.
3. Set conversion windows to match the real sales cycle; a 3-day window on a 3-week B2B sales cycle manufactures false zeros.
4. Set count settings correctly: one-per-click for leads (a person filling two forms is one lead), every conversion for purchases.
5. Attribution: prefer data-driven where available; if switching models, note the date - attribution changes make before/after comparisons dishonest.
6. Record each action's trigger mechanism and owner in `tracking-plan.md`; unowned tracking silently dies."""),
  ("enhanced-and-offline.md", "enhanced conversions, offline imports and the CRM feedback loop", """# Sub-skill: enhanced conversions and offline imports

1. Turn on enhanced conversions (web) and confirm in Diagnostics that it is recording, not just enabled.
2. Capture the Google Click ID (gclid) into the CRM on every lead form and call-tracking record; without it, offline import is impossible.
3. Define the offline stage worth importing (qualified lead, closed sale) and its timestamp rule (conversion time = the event date, not the import date).
4. Import on a schedule or via API; test with one manual upload first and watch it appear against the right clicks.
5. Keep the loop honest: if only 10% of leads get a CRM outcome recorded, the smart bidding signal is 90% noise - fix the CRM hygiene before scaling spend.
6. Document the data flow in `tracking-plan.md`: click -> lead -> CRM stage -> import, with owners at each hop."""),
 ]),

"ga-keywords": dict(
 title="keywords as signals and the negative system that stays in control",
 desc="Keyword research and the negative keyword system: theme selection, match-type strategy in the keyword-signal era, negative lists, search-term mining, and brand/competitor term policy. USE WHEN building themes, when search terms drift off-offer, or when someone proposes match-type surgery as the fix.",
 outcome="revenue-gtm: themes selected from real query language, a negative system that runs before spend, and a mining cadence that keeps it true",
 judgments="is this theme sound, is this negative justified, which keyword option wins",
 rubric="idea.solid",
 when="Use after ga-structure sets themes and before ga-campaigns fills them. Not for bidding (ga-bidding) or ad copy (ga-ads).",
 procedure="""1. **Research from real language**: keyword planner volumes plus the actual query phrasing customers use (sales calls, site search, support tickets). Theme names come from the customer's words, not internal jargon.
2. **Match types are signals**: exact/phrase/broad select how far Google may stretch the meaning. Broad is defensible where negatives and multiple themed keywords per group exist; broad without negative discipline is how small budgets burn (corpus consensus).
3. **Build the negative system BEFORE spend**: account-level and campaign-level negative lists for off-offer services, jobs, free/DIY intent, geographies never served, and internal terms. The list is the control surface now.
4. **Search term mining cadence**: weekly read of the search terms report (ga-reporting); new negatives added the same session; new theme candidates logged for ga-structure rather than dumped into live ad groups.
5. **Brand policy**: brand terms in their own campaign (ga-structure); competitor terms only with a written decision on cost and message honesty.
6. **Jev**: theme and negative additions through `idea.solid` when they change serving; DEFERRED means the change waits.""",
 handoff="`keyword-map.md`: themes with sample queries and match approach; negative lists by level; brand/competitor policy; mining cadence. ga-campaigns and ga-ads consume the themes.",
 rules="""- No campaign goes live without its negative lists in place (corpus consensus).
- Never add a negative from a single bad click without reading the pattern; one-off negatives pile up into a strangled account.
- Never stuff competitor names into ad copy as keywords without a policy decision; trademark and trust costs are real.
- Every keyword change that affects serving goes through Gate-D when it changes spend exposure.
- Dated-match-era advice (SKAGs, heavy exact-match surgery) is flagged as dated in the doctrine and never executed as current practice.""",
 checklist=["Themes named in customer language with sample queries",
            "Match approach stated per theme, with negatives as the control story",
            "Account-level and campaign-level negative lists built before launch",
            "Brand policy documented (own campaign)",
            "Competitor-term policy documented or terms excluded",
            "Weekly search-term mining cadence on the calendar",
            "Jev `idea.solid` run on serving-changing additions"],
 subs=[
  ("negative-keyword-system.md", "building and maintaining the negative keyword system", """# Sub-skill: negative keyword system

1. Build the standing lists first: off-offer services, job-seeker and DIY/free intent, never-served geographies, internal project names. Keep them in shared negative lists so one edit protects many campaigns.
2. Assign levels deliberately: account-wide negatives only for terms that are wrong everywhere; theme-specific negatives live with their campaign.
3. Use match types on negatives more loosely than on positives: a broad negative blocks a meaning; an exact negative blocks one string.
4. Review schedule: weekly mining session adds negatives with a one-line rationale each (the record is how the account learns).
5. Prune: every quarter, export the negative lists and look for false positives - negatives that blocked good traffic. The list is a hypothesis about the world, not a monument.
6. Never paste a competitor's negative list wholesale; their offers differ and copy-paste lists carry their blind spots."""),
  ("search-term-mining.md", "the weekly search-term read and what to do with each finding", """# Sub-skill: search-term mining

1. Pull the search terms report filtered to spend above a small threshold; read every row that spent money.
2. Sort findings into four buckets: exact theme (add as keyword/theme evidence), adjacent theme (log for ga-structure), off-offer (add negative), junk (add negative).
3. Do not react to a single click's word; look for the meaning pattern Google is stretching toward.
4. Promote winning query language into the ads (ga-ads) and the landing page (ga-landing) verbatim where it matches the offer - the report is a copywriting oracle.
5. Log every action with date and rationale; after a month the log shows which theme needs restructuring.
6. Feed lead-quality outcomes back (ga-local-b2b): terms that fill the CRM with junk get negated even when they look relevant on paper."""),
 ]),

"ga-campaigns": dict(
 title="campaign types, Performance Max and local, chosen by job",
 desc="Campaign-type selection and mechanics: Search, Performance Max, Shopping, Demand Gen, Display, Video, local campaigns and Local Services Ads boundaries, with asset groups, signals and exclusions. USE WHEN choosing which types to run, when PMax is proposed for a lead-gen account, or when a new type is added to the mix.",
 outcome="revenue-gtm: each campaign type in the account has a stated job, its required assets are complete, and the budget map shows where the money lives and why",
 judgments="is this campaign plan ready, does this type earn its budget, is this PMax setup sound",
 rubric="plan.readiness",
 when="Use after ga-structure fixes the jobs and before builds. Not for keywords (ga-keywords), bidding (ga-bidding), or creative (ga-ads).",
 procedure="""1. **Choose the type by the job**, not by novelty: Search serves existing demand (people already looking); Shopping/PMax serve feed-driven retail; Demand Gen/Video create demand; local formats serve store/area visits; Local Services Ads (where available) serve pay-per-lead local services.
2. **Inbound before outbound**: search/inbound gets the first claim on budget; display/outbound is the most expensive and most frustrating, and runs last (corpus consensus, prior skill R7).
3. **PMax discipline**: PMax is a feed-and-asset machine. Run it with complete asset groups, audience signals, brand exclusions where brand runs separately, and a written statement of what it is for. Do not put a local lead-gen account's whole budget into PMax first (corpus consensus, prior skill R4).
4. **Local mechanics**: explicit location targeting to the real service area, call tracking in place, and a serving check at 48 hours (ga-local-b2b). Geo-narrowing that starves the auction is a launch bug, not a strategy.
5. **One type, one measurement**: each type's success metric is named before launch (Search: cost per qualified lead; PMax: value/conv with feed health; Video: qualified reach or view-through to action).
6. **Jev**: the campaign plan through `plan.readiness`; DEFERRED blocks the build.""",
 handoff="`campaign-plan.md`: type-by-type job table, budget map, asset requirements per type, measurement per type. ga-bidding sets strategies per campaign; ga-ads supplies the creative.",
 rules="""- A new campaign type is a hypothesis with a kill criterion written at launch (budget, time, and the metric that ends it).
- PMax never carries a small local lead-gen budget alone (corpus consensus).
- Any campaign that starts serving gets the 48-hour serving check (status, keywords, geo, budget vs planner range, billing, conversions recording).
- Local Services Ads eligibility and verification (Google's own background checks) are human steps for Mike; the skill stages, never signs.
- Enabling any campaign is spend: Gate-D.""",
 checklist=["Type chosen by job; inbound/outbound order respected",
            "PMax, if used, has complete asset groups, signals and a written purpose",
            "Budget map shows money per type with the reason",
            "Success metric named per type",
            "Kill criteria written for each new type",
            "Location targeting set to the real service area",
            "48-hour serving check scheduled at launch",
            "Jev `plan.readiness` run on the campaign plan"],
 subs=[
  ("pmax-playbook.md", "running Performance Max without losing the plot", """# Sub-skill: PMax playbook

1. Precondition: conversion tracking proven (ga-tracking) and a feed (retail) or full asset set (lead gen) ready. PMax with thin assets is a waste machine.
2. Build asset groups per theme or offer, not one catch-all; write headlines and descriptions as a set (ga-ads rules apply).
3. Audience signals: seed with first-party visitors, converters and themed search themes; signals guide, they do not target.
4. Brand defence: if brand runs as its own Search campaign, use brand exclusions in PMax so it cannot cannibalise and inflate its own numbers.
5. URL exclusions and page feeds: keep PMax off pages that cannot convert.
6. Judge PMax on value and lead quality, not impressions; read asset-group reporting and replace non-serving assets on a monthly cadence, not daily thrash.
7. Budget stays bounded until it proves qualified conversions; scaling follows ga-budget rules."""),
  ("local-campaigns.md", "local and service-area campaign mechanics", """# Sub-skill: local campaigns

1. Set location targeting to the real service area (metro/DMA or documented radius), with the presence vs presence-interest option chosen deliberately; never default-in the whole country.
2. Phone-first reality: call extensions, call reporting on, and account-level call detail configured (ga-tracking).
3. Service-area businesses: ad schedule aligned to when someone can answer the phone; a lead that hits voicemail is a wasted click.
4. Local Services Ads (where eligible): the verification and Google-guarantee steps are human steps for Mike; stage the paperwork and stop.
5. Geo bid adjustments only after enough local conversion data exists; small local accounts rarely have the volume to tune by city.
6. The 48-hour serving check is mandatory for local launches (see ga-local-b2b): status, low-search-volume keywords, geo starvation, budget vs planner range, billing, conversions recording."""),
 ]),

"ga-bidding": dict(
 title="bidding strategies and the discipline around learning",
 desc="Bidding for Google Ads: manual vs smart bidding, the strategy ladder (max clicks, max conversions, tCPA, tROAS, portfolio), conversion-volume prerequisites, learning periods, bid adjustments and seasonality. USE WHEN choosing or changing a strategy, when CPA swings mid-month, or when someone wants to change bids daily.",
 outcome="revenue-gtm: every campaign has a bidding strategy matched to its data volume and goal, with a change protocol that does not fight the learning system",
 judgments="keep, cut or change this bid setting, is this spend justified",
 rubric="spend.continue",
 when="Use after conversion tracking is proven and campaigns are built. Not for structure (ga-structure) or keyword selection (ga-keywords).",
 procedure="""1. **Data first**: strategy choice follows conversion volume. Thin data (a few conversions/month) earns manual CPC or max clicks with a ceiling; consistent volume (~30+ conversions per month per campaign) earns tCPA; value-varied businesses with revenue data earn tROAS. Corpus consensus: conversion data is the fuel; smart bidding without it is guessing.
2. **Ladder up, never jump**: manual/clicks -> max conversions -> tCPA (at target or above current CPA) -> tROAS. Skipping rungs strands accounts in learning.
3. **Set targets at reality**: tCPA starts at or above the trailing actual CPA; an aspirational target strangles delivery. Raise targets only as results earn it.
4. **Learning-period discipline**: after any strategy/target/structure change, leave the campaign alone for ~1-2 weeks. Daily intervention restarts learning and manufactures volatility (corpus consensus).
5. **Bid adjustments** only where the system still allows them (device, location, time where supported); smart bidding absorbs most signals - adjust the inputs (budget, conversion quality, targets), not micro-bids.
6. **Portfolio strategies** when several campaigns share a goal and should share pacing.
7. **Jev**: any strategy change through `spend.continue` with the account evidence row; DEFERRED means no change.""",
 handoff="`bidding-plan.md`: strategy per campaign with data-volume rationale, targets and their basis, change protocol. ga-budget uses the plan to set scaling rules.",
 rules="""- Never change strategy, targets and budget in the same week; one variable at a time or the learning data is garbage.
- Never chase daily CPA noise; read at the decision cadence (ga-reporting weekly, plan monthly).
- Bid changes that alter spend exposure are Gate-D.
- If conversions are not recording, the bidding conversation is postponed - fix ga-tracking first (corpus consensus).
- Dated manual-bid-era tactics are flagged as dated and not re-imported.""",
 checklist=["Strategy per campaign matched to conversion volume",
            "Targets set at/above trailing actuals with basis shown",
            "Change protocol written (one variable, learning window)",
            "Portfolio vs individual strategy decided with reason",
            "Conversion tracking confirmed recording before any smart bidding",
            "Jev `spend.continue` run on each strategy change request"],
 subs=[
  ("bid-strategy-ladder.md", "choosing and moving up the bidding ladder", """# Sub-skill: bid-strategy ladder

1. Count conversions per campaign for the trailing 30 days from the account (not from memory).
2. Assign by volume: 0-5 conversions -> manual CPC or max clicks with a CPC ceiling; 5-30 -> max conversions (no target); 30+ and stable -> tCPA; revenue-tracked and value-varied -> tROAS.
3. Move up a rung only after two stable weeks at the current rung; document the move and date in `bidding-plan.md`.
4. When moving to tCPA, set the target at trailing CPA + 10-20% headroom; tighten only after the campaign beats it for a week.
5. If delivery collapses after a move, revert to the prior rung - reverting is not failure, thrashing is.
6. Never stack a strategy change with a budget increase; the two interfere and the read is ruined."""),
  ("learning-periods-and-changes.md", "the change protocol that stops fighting the learning system", """# Sub-skill: learning periods and changes

1. Keep a one-page change log (date, campaign, what changed, why, expected effect). Change history verifies it (ga-reporting).
2. After any bid-strategy, target or structural change: hands off for ~1-2 weeks except blocking issues (disapprovals, tracking failure, runaway spend).
3. Blocking-issue intervention is allowed mid-learning: pause disapproved ads, fix broken tracking, cap runaway budgets. Everything else waits.
4. Judge effects at the right window: weekly for serving health, 2-4 weekly for CPA/ROAS decisions; same-period comparisons only.
5. Seasonality adjustments and data exclusions are for known events (promotions, outages), not for explaining ordinary variance.
6. If two people operate the account, one owns changes per week; parallel operators create learning loops that never converge."""),
 ]),

"ga-ads": dict(
 title="ad copy and assets that match the query and the page",
 desc="Ad creation for Google Ads: responsive search ads, headlines and descriptions from theme and offer, pinning policy, asset coverage (sitelinks, callouts, structured snippets, call, image, price, promotion), ad strength and policy safety. USE WHEN writing or rewriting ads, before launch, or when ad strength or disapprovals block delivery.",
 outcome="revenue-gtm: every ad group carries an RSA whose headlines match the theme and the landing page, with full asset coverage and zero policy risk",
 judgments="which ad copy wins, does this ad pass",
 rubric="ad.search",
 when="Use for every ad before launch and at each creative refresh. Not for landing pages (ga-landing) or keyword themes (ga-keywords).",
 procedure="""1. **Write from the theme and the offer**: headlines cover the theme (query language), the outcome, the proof or differentiator, and the CTA. Descriptions expand the promise and prequalify.
2. **Message match is the spine**: ad headline ≈ landing page H1 ≈ keyword meaning. The `ad.search` rubric exists exactly for this (query match, named pain, finished outcome, specificity, trust, differentiation, CTA prequalification, message match).
3. **Pinning policy**: pin only where a message MUST appear (e.g. regulatory or offer name); over-pinning strangles rotation and drops effective coverage. Prefer strength through variety.
4. **Asset coverage is part of the ad**: sitelinks (with descriptions), callouts, structured snippets, call asset for lead gen, images, price/promotion where real. Assets are free SERP real estate and a trust surface.
5. **Ad strength is a compass, not a law**: do not stuff junk headlines to chase "Excellent"; do not ignore "Poor" where the theme is narrow.
6. **Policy safety**: no unprovable claims, no trademark misuse, no prohibited content; financial/health claims need substantiation (pmm ads for local B2B: policy safety is a scored axis).
7. **Jev**: every new ad through `ad.search` with the full input set; iterate until it clears or record DEFERRED.""",
 handoff="`ad-sets.md`: per theme - RSA headlines/descriptions, pinning decisions, asset inventory, Jev verdict ids. ga-landing mirrors the winning message; ga-reporting reads the results.",
 rules="""- Every number in an ad (prices, discounts, counts) is true on the landing page the day it serves.
- Never promise what the landing page does not deliver; message match is a hard gate, not a style preference.
- Disapprovals are fixed the day they appear; a disapproved ad is a hole in the account.
- New ads enter through experiments or clear rotation logic, never wholesale replacement on a live learning campaign.
- Ad copy decisions are drafts; publishing/serving remains Gate-D through Mike.""",
 checklist=["Headlines cover theme, outcome, proof, CTA",
            "Message match verified ad-to-page (H1 alignment)",
            "Pinning minimal and justified",
            "Asset coverage complete for the campaign type",
            "Every ad number true on the landing page today",
            "Policy check passed (claims, trademarks, prohibited content)",
            "Jev `ad.search` run per new ad; decision id recorded"],
 subs=[
  ("rsa-blueprint.md", "building a responsive search ad that can actually rotate", """# Sub-skill: RSA blueprint

1. Inventory the theme's language (from ga-keywords mining): the exact phrases searchers use.
2. Draft 8-12 headlines (25-30 chars each) across four buckets: theme match, outcome/benefit, proof/differentiator, CTA. At least three distinct messages per bucket so combinations stay coherent.
3. Draft 2-4 descriptions (up to 90 chars) that expand one promise each and prequalify the caller (who it is for).
4. Pin at most one headline per position and only with a stated reason (compliance, brand). Record the reason in `ad-sets.md`.
5. Check every combination: do any two pinned or high-weight headlines contradict or read as nonsense together? Fix before launch.
6. Run the finished RSA through Jev `ad.search` with the target query and landing page first-screen facts; iterate on the weakest axes."""),
  ("asset-and-extension-checklist.md", "the asset inventory every campaign should carry", """# Sub-skill: asset and extension checklist

1. Sitelinks: 4+ per campaign with descriptions, pointing at real pages (services, pricing/entry, about/proof, contact).
2. Callouts: short trust/USP phrases (response time, guarantee, years, credentials) - each true today.
3. Structured snippets: the service catalogue header/values; Google's list headers only.
4. Call asset for lead-gen campaigns with a tracking number; schedule it to business hours if nobody answers otherwise.
5. Image assets: brand-true photos or graphics at required sizes; no text-heavy images.
6. Price and promotion assets where the offer has a real, current price; never a promotion without an end date the account respects.
7. Review cadence: monthly, replace assets that never serve; keep the policy check attached to every new asset."""),
 ]),

"ga-landing": dict(
 title="landing pages that pay the ad's promise",
 desc="Landing pages for Google Ads: message match, first-screen facts, offer clarity, forms, speed, mobile integrity and trust evidence. USE WHEN launching to a new page, when clicks convert poorly, or when quality score or ad relevance flags the page.",
 outcome="revenue-gtm: every ad group lands on a page whose first screen states the same promise as the ad, with one clear action and honest proof",
 judgments="does this page pay the ad's promise, which page variant wins",
 rubric="website.buyer",
 when="Use before launch and whenever a well-clicked theme converts poorly. Not for ad copy itself (ga-ads) or tracking (ga-tracking).",
 procedure="""1. **First-screen facts**: H1 restating the query's promise, the offer with its entry point, one primary CTA, and who it is for - visible without scrolling on mobile.
2. **Message match audit**: for each ad group, compare query -> ad headline -> page H1. Discontinuity is the first thing to fix; it wastes every click.
3. **One page, one action**: the primary CTA is singular (call, form, booking); secondary links exist but never compete visually.
4. **Form reality**: ask only what qualification truly needs; every extra field costs conversions. Phone-first pages for local services offer click-to-call above the fold.
5. **Speed and mobile**: the page loads fast on 4G and does not shift under the thumb; run the budget page test (payload caps, LCP) before pointing spend at it.
6. **Trust and honesty**: real proof (named, permissioned), real prices where possible, no invented reviews; anti-slop: no generic stock-hero fluff (the `website.buyer` rubric scores trust, offer clarity, conversion architecture and anti-genericity for exactly this).
7. **Jev**: page through `website.buyer`; the weakest axes become the fix list. DEFERRED blocks launch claims.""",
 handoff="`page-audit.md` or the live page URL: message-match table, first-screen facts, CTA, fix list by priority. ga-ads mirrors the page's winning lines back into headlines.",
 rules="""- The ad may never promise a step the page does not contain (no "instant quote" to a contact form that quotes nothing).
- No fake scarcity, fake reviews, or fabricated credentials; trust axes fail these hard.
- Tracking on the conversion event lives here too (ga-tracking owns the mechanism; this stage owns the placement).
- Every claim on the page is dated-checked before a flight starts; stale prices are bugs.
- Page changes on a live flight are experiments, not silent swaps.""",
 checklist=["First screen: promise, offer/entry, CTA, audience visible on mobile",
            "Query-to-ad-to-H1 match verified per ad group",
            "One primary CTA; secondary links do not compete",
            "Form fields minimised; click-to-call for phone-first",
            "Speed/mobile sanity checked on real mobile",
            "Proof elements real and permissioned; anti-slop pass",
            "Jev `website.buyer` run; fix list produced"],
 subs=[
  ("message-match.md", "the query-to-ad-to-page continuity audit", """# Sub-skill: message match audit

1. Export the top themes with their sample queries (ga-keywords).
2. For each theme, write the three lines a searcher sees in sequence: query, ad headline, page H1. Place them side by side in `page-audit.md`.
3. Flag mismatches: different service name, different promise, jargon translation loss, offer missing on the page.
4. Fix direction: change the page first when the ad matches the query (the page is usually the weak link); change the ad when the query is being stretched by matching.
5. Re-run the audit after each fix; message match is a standing test, not a one-time cleanup.
6. Watch the ad relevance and landing page experience columns as secondary evidence, but trust the side-by-side read over Google's opaque scores."""),
  ("form-and-speed-basics.md", "forms, first screens and speed checks that do not need a dev team", """# Sub-skill: form and speed basics

1. Count form fields; every field past name + contact + one qualifier is suspect. Justify each one or cut it.
2. Put the form or click-to-call where the decision happens (after proof on long pages; immediately on short local pages).
3. Thank-you page or event firing confirmed for every submit path (coordinate with ga-tracking before launch).
4. Speed: run Lighthouse on a throttled mobile profile; fix image weight and third-party scripts first. LCP above ~2.5s is a paid-traffic bug.
5. Mobile integrity: no overlapping sticky bars covering the CTA; inputs trigger the right keyboards; tap targets big enough.
6. Honest empty states and error messages; a failed submit that silently eats a lead is worse than a slow page."""),
 ]),

"ga-budget": dict(
 title="budget discipline, scaling and real experiments",
 desc="Budget and testing for Google Ads: daily budget math, limited-by-budget reads, scaling rules, shared budgets, campaign experiments, and the review loop that keeps or cuts spend. USE WHEN setting or changing budgets, when scaling a working campaign, or when designing a test.",
 outcome="revenue-gtm: every budget has arithmetic behind it, every scale-up has a trigger, and every experiment has a pre-registered read and a kill criterion",
 judgments="keep, cut or change this spend, is this test worth running",
 rubric="spend.continue",
 when="Use whenever money is allocated or moved and before any experiment. Not for bid mechanics (ga-bidding) or creative (ga-ads).",
 procedure="""1. **Budget as math**: monthly ceiling / 30.4 = daily; daily x expected CPC = expected clicks; clicks x conversion rate x close rate = expected deals. If the chain cannot plausibly reach one customer, the budget is a donation - fix the plan (ga-strategy) first.
2. **Limited-by-budget is information**: a campaign capped daily is telling you demand exceeds funding. Decide deliberately: raise budget (with the arithmetic), narrow targeting, or accept the cap - never ignore the flag.
3. **Scaling rules**: raise budgets in steps (corpus practice: ~10-20% at a time, wait out the learning window), only when CPA/ROAS beats target for a sustained window; one change at a time.
4. **Shared budgets** only for campaigns with one goal and one pacing need; never across brand and prospecting.
5. **Experiments are pre- drafts**: hypothesis, metric, minimum read window, sample-size reality check (small budgets can't reach significance - use directional reads and say so), kill criterion, and the exact decision rule before launch. Experiments run as Google Ads experiments/drafts where possible, not as live A/B chaos.
6. **Monthly spend review**: each campaign gets keep/cut/pause through Jev `spend.continue` on its evidence row; DEFERRED keeps last month's state and escalates.
7. Every budget move is Gate-D: Mike approves; the parent operator acts.""",
 handoff="`budget-plan.md`: per-campaign daily/monthly with arithmetic, scaling triggers and steps, experiment register with kill criteria. ga-reporting feeds the monthly review.",
 rules="""- No spend action (enable, raise budget, extend flight) without Mike's explicit approval (Gate-D). Staging is free; spending is not.
- Never run a test without its written decision rule and kill criterion.
- Budget changes and bidding changes never ship the same week (one variable).
- With small budgets, honest reporting includes the sample-size limit; directional reads are labelled directional.
- Never let a flight reach its end date at $0 and report it as a test (prior skill lesson; live reads settle state, not intent).""",
 checklist=["Daily/monthly figures with the arithmetic shown",
            "Limited-by-budget flags decided (raise / narrow / accept)",
            "Scaling steps and triggers written",
            "Shared budgets only within one goal",
            "Experiment register entries complete: hypothesis, metric, read window, kill criterion",
            "Monthly keep/cut review scheduled with Jev `spend.continue` rows",
            "All spend moves routed to Mike (Gate-D)"],
 subs=[
  ("budget-limits-and-scaling.md", "reading budget caps and scaling without wrecking delivery", """# Sub-skill: budget limits and scaling

1. Read `Limited by budget` and lost-impression-share (budget) columns weekly; log which campaigns are capped and why it does or does not matter.
2. For each capped campaign decide: fund more (arithmetic first), narrow the theme/geo so the current budget buys better traffic, or accept the cap deliberately.
3. Scaling steps: +10-20% budget at a time with a full learning window between steps; watch CPA/ROAS at each step and stop at the first sustained miss.
4. Never scale a campaign that has not proven conversion quality; scale follows proof, not hope.
5. Pausing is a budget decision too: write the reason and the re-entry condition before pausing.
6. Keep the whole-account view: money moved into one campaign is money moved out of another; state the trade."""),
  ("experiment-playbook.md", "designing Google Ads experiments that can actually answer", """# Sub-skill: experiment playbook

1. Write the hypothesis as a sentence with a direction ("tROAS at 300 will hold CPA while lifting volume").
2. Name the one metric that decides, and the guardrail metric that vetoes (e.g. lead quality).
3. Reality-check the sample: expected conversions per variant during the read window. If the account cannot buy enough conversions, the test is a decoration - shorten the question or gather more data elsewhere.
4. Use Google Ads experiments (drafts) for bid/structure tests and ad variations for creative; live-world A/B only where the platform cannot split.
5. Pre-register the decision rule and kill criterion in the experiment register before launch; after launch, no rule changes.
6. Read at the pre-set window, record the outcome (including "no readable difference"), and roll the winner or the rollback in one deliberate step."""),
 ]),

"ga-reporting": dict(
 title="reporting, optimization cadence and honest reads",
 desc="Reporting and optimization for Google Ads: the weekly cadence, search-term and asset reads, change-history forensics, attribution honesty, lead-quality feedback and flop diagnosis. USE WHEN running the weekly or monthly review, when numbers disagree with the CRM, or when a campaign underperforms.",
 outcome="revenue-gtm: every report is a live read with a date, every optimization has a recorded reason, and every result claim survives the attribution honesty check",
 judgments="is this performance signal real, what caused this result",
 rubric="signal.performance",
 when="Use weekly (serving health + mining) and monthly (money decisions). Not for setting strategy (ga-strategy) or building tests (ga-budget).",
 procedure="""1. **Weekly cadence** (one session, recorded): serving status and disapprovals; search terms mining (ga-keywords); ad and asset health; budgets/caps; conversions recording check. Same day fixes for anything blocking.
2. **Monthly money review**: spend, cost per qualified lead, lead quality from the CRM, by campaign. Each row gets keep/cut/pause via Jev `spend.continue` (ga-budget owns the decision, this stage owns the evidence).
3. **Live reads only**: numbers are read from the account (or the live dashboard) with the date stamped. Never copy a figure from an old report into a new one (prior skill lesson: written records disagreed; only the live read was right).
4. **Attribution honesty**: name the attribution model and window whenever comparing periods; a model change makes before/after comparisons dishonest until restated.
5. **Change history forensics**: when results move, the first suspect is the change log (including Google's own auto-applied changes). Correlate before theorising about the market.
6. **Flop diagnosis**: classify each miss (tracking, message match, offer, bid/data volume, competition, budget) through Jev `signal.performance`; DEFERRED goes to the human review list.
7. **Lead quality feedback loop**: closed-won/lost outcomes flow back to keyword and geo decisions (ga-local-b2b).""",
 handoff="`report-<week>.md` / `review-<month>.md`: live-read numbers with dates, fixes made, open items, decisions requested from Mike. ga-budget's monthly row depends on this evidence.",
 rules="""- Every reported number carries its source (account view, CRM, dashboard) and read date. A number without provenance does not ship.
- Never report intent as state: "we ran ads" claims must match account state (enabled, serving, spend).
- Result claims are classified (attributable? sample size?) before they enter any Mike-facing summary or client report.
- Optimization changes are recorded the same session with reasons; unrecorded changes make forensics impossible.
- Auto-applied recommendations are reviewed, not blindly accepted; note which are on.""",
 checklist=["Weekly session done and logged with date",
            "Search-term mining completed with actions recorded",
            "Conversions recording verified live",
            "Monthly review rows prepared for Jev `spend.continue`",
            "Attribution model/window stated on every comparison",
            "Change history checked for every material swing",
            "Lead-quality feedback loop updated from the CRM"],
 subs=[
  ("weekly-optimization-cadence.md", "the one-hour weekly account session", """# Sub-skill: weekly optimization cadence

1. Status sweep: campaigns, ads, keywords - anything Paused, Disapproved or `Eligible (Limited)` gets named with its limit. Fix or escalate the same day.
2. Search-term mining (ga-keywords): negatives added with rationale; theme candidates logged.
3. Creative read: ads with zero impressions (fix coverage/pinning), assets not serving, ad-strength collapses.
4. Money read: capped budgets, lost impression share, CPA/ROAS vs target by campaign.
5. Conversions check: at least one conversion action recording this week; Google prompting "Set up conversion tracking" is an incident, not a tip.
6. Log it all in `report-<ISO week>.md` with the read timestamps; end with one line: what changes next week and what waits."""),
  ("change-history-and-forensics.md", "reading the account's history before theorising", """# Sub-skill: change history and forensics

1. Open change history filtered to the swing window; list every human and auto-applied change (bids, budgets, status, targeting, ads, conversions).
2. Correlate: which changes precede the swing, and did the swing start inside a learning window after one of them?
3. Check the outside world second: auctions, seasonality, competitor offers - only after the account's own log is ruled out.
4. For CRM-level swings (good clicks, bad leads), pull search terms x geo x time-of-day against closed-won/lost data before blaming the ads.
5. Write the diagnosis as a classification (tracking / message match / offer / bid-data / competition / budget) with evidence; vague causes are not diagnoses.
6. Auto-applied changes: review the auto-recommendations log; disable categories that fight the strategy."""),
 ]),

"ga-local-b2b": dict(
 title="local B2B service accounts on small budgets",
 desc="Local B2B and service-business application: the $1-50/day reality, calls and forms as the conversion truth, vertical-specific pages, brand defence, what NOT to run at small scale, the 48-hour serving check and lead-quality loops. USE WHEN planning or auditing a local service or B2B account on a small budget, and before any local spend decision.",
 outcome="revenue-gtm: a small-budget account that spends only on proven inbound intent, tracks calls and forms as truth, and catches non-serving campaigns within 48 hours",
 judgments="is this account ready to spend, does this local build pass, is this spend justified",
 rubric="ad.search",
 when="Use for local service and B2B accounts at small budgets ($1-50/day), from plan through post-launch checks. Not for large multi-market builds (ga-structure owns general architecture).",
 procedure="""1. **Tracking before campaigns** (absorbed doctrine R2/R3): call leads AND form submits tracked and testable first; account-level call tracking, thank-you-page form tracking. A budget is wasted without this.
2. **Campaign roles named**: brand defence (worth running even when it feels redundant), inbound search (people already looking - the first claim on budget), outbound/display (most expensive, most frustrating, last resort) (absorbed doctrine R7).
3. **PMax is not the first home of a small local budget** (absorbed doctrine R4). Local lead gen starts on inbound search with themes and negatives (R5).
4. **Keyword-signal reality** (R1/R5): structure for intent and message match; broad match only with negatives and multiple themed keywords per group. No SKAG rebuilds (R6 - the 2019 advice is dated).
5. **Geo and call-detail settings are part of the build** (R8): explicit location targeting to the real service area; phone tracking set at account level.
6. **48-hour serving check** (post-launch lesson): read the account live at 48 hours and day 5; fix the first failing check the same day (status/limits, low-search-volume keywords, geo starvation, budget vs planner range, billing, conversions recording). If nothing can be fixed today, pause and say so.
7. **Small-scale honesty**: a test budget buys a few clicks a day; the measurement plan is calls and form fills per dollar, never impressions. Expectations are written before launch.
8. **Jev**: build/audit doc through `ad.search`; DEFERRED blocks "ready to spend".""",
 handoff="`local-build.md`: roles table, tracking proof, themes + negatives, geo settings, budget math, expectations, 48-hour check scheduled. ga-reporting takes the post-launch reads.",
 rules="""- This stage absorbs `pmm-google-ads-local-b2b` as its parent material (its R1-R8 doctrine and the 48-hour serving check are restated here as procedure and laws); that skill file stays at `~/.aside/u/0/skills/user/pmm-google-ads-local-b2b/SKILL.md` and is never forked into a second copy.
- Every spend, bid, geography or enablement change is Gate-D through Mike; sub-agents never touch budgets or live status.
- Phone leads are a primary conversion for local service; never run a call-focused business on form-only tracking.
- Never report "we ran ads" unless the account shows serving and spend; state claims are live-read (lesson LS22: two written records disagreed; only the live read was right).
- Dated doctrine (SKAGs, exact-match surgery) stays flagged and unexecuted.
- Local Services Ads verification and any sign-up/verification step is a NEEDS-MIKE item; stage documents only.""",
 checklist=["Call + form conversions proven firing before any spend",
            "Campaign roles named: brand / inbound / outbound",
            "Inbound search gets first claim on budget; PMax not carrying it all",
            "Negative lists in place before any broad match",
            "Location targeting and call detail verified per the real service area",
            "Budget math and expectations written (calls/forms per dollar)",
            "48-hour + day-5 serving checks scheduled",
            "Jev `ad.search` run on the build doc; Gate-D filed for spend"],
 subs=[
  ("small-budget-limits.md", "what a $1-50/day budget can and cannot do", """# Sub-skill: small-budget limits

1. Write the arithmetic honestly: daily budget / realistic CPC = clicks per day; clicks x conversion rate = leads per week. At $10-30/day this is single-digit leads weekly, often less.
2. Choose one geo and one service theme first; breadth at small budgets manufactures zero data everywhere instead of real data somewhere.
3. Exclude display, video and prospecting from the first flight entirely; they are last-resort budget for accounts that already convert inbound.
4. Set expectations in the plan: what result would justify continuation (cost per qualified lead band), what ends the test (kill criterion).
5. If the arithmetic cannot plausibly buy one customer per month, do not run ads; put the budget into the landing page or the offer first and say so.
6. Never stretch a small budget by chasing volume with broad match and no negatives; that converts money into junk leads fastest."""),
  ("local-b2b-lead-quality.md", "the lead-quality loop for service and B2B accounts", """# Sub-skill: local B2B lead quality

1. Define what a qualified lead IS (service fit, area, budget/timeline) in writing before launch; the whole loop hangs on this definition.
2. Capture every lead's source data: campaign, ad group, keyword/search term, geo, time - into the CRM or a simple log when there is no CRM.
3. Weekly: mark leads qualified / junk / uncontactable; junk patterns feed negatives (ga-keywords) and geo/schedule decisions (ga-campaigns).
4. Close the loop monthly: cost per QUALIFIED lead replaces cost per lead in every money decision; raw CPL flattering junk is a trap.
5. Call recordings or notes reviewed for message-match reality: what callers expected vs what was sold.
6. When lead quality drops while volume holds, suspect the query stretch first (search terms), then the ad promise, then the offer - in that order."""),
 ]),

}
