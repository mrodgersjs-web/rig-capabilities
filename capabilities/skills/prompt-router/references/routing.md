# Prompt routing table

_Generated from `registry.json` by `node tools/route.mjs --write-routing`. Do not hand-edit._

Registry updated: 2026-09-28 | prompts: 144

## app-studio

- **app-studio-ai-features** v1 [draft] - App Studio ai-features stage prompt: ship LLM features that validate model replies and run without paid keys through named fallbacks
  - triggers: ai feature in the app, llm feature with fallback
- **app-studio-architecture-stack** v2 [draft] - App Studio architecture-stack stage prompt: record the stack the task names, what builds in the sandbox, and a named fallback per paid vendor
  - triggers: app stack decision, write stack.md
- **app-studio-backend-data** v2 [draft] - App Studio backend-data stage prompt: implement the API contract, storage, auth, quotas and jobs with executed proof per endpoint
  - triggers: api contract endpoints, backend data layer for the app
- **app-studio-builder** v3 [draft] - App Studio builder prompt: build one app to its contract in the current folder and write the mission record the verifier reads
  - triggers: bench builder prompt, app builder prompt, builder for this app task
- **app-studio-design-ux** v1 [draft] - App Studio design-ux stage prompt: map the screens onto the SaaS skeleton with real data and plan real captures for judging
  - triggers: app screen map, design the app screens
- **app-studio-intake-spec** v2 [draft] - App Studio intake-spec stage prompt: pin what the app is, its source, its done-screens and its contract in spec.md
  - triggers: app intake spec, write the app spec
- **app-studio-lesson-filer** v1 [draft] - App Studio lesson filer prompt: turn each new build failure into a typed lesson and patch the owning sub-skill in the same session
  - triggers: file the lesson, typed lesson from this failure, lessons into skills
- **app-studio-meta** v2 [draft] - App Studio meta prompt: run an app build mission through 11 JEV-gated stages with one builder, a separate verifier and Gate-D stops
  - triggers: app studio mission, build this app end to end, app studio meta prompt
- **app-studio-mobile** v1 [draft] - App Studio mobile stage prompt: build the Expo or native lane and show it running on a clean simulator driven from Orca
  - triggers: expo mobile app, react native lane
- **app-studio-operate-learn** v1 [draft] - App Studio operate-learn stage prompt: record the failures hit during the build as lesson candidates with exact evidence
  - triggers: lessons from this build, operate and learn stage
- **app-studio-scaffold-setup** v1 [draft] - App Studio scaffold-setup stage prompt: get a first slice to build, serve and answer curl inside the Aside sandbox
  - triggers: scaffold the app, first slice builds and serves
- **app-studio-ship-release** v2 [draft] - App Studio ship-release stage prompt: prepare a complete release request and hold it at Gate-D
  - triggers: ship the app, release request held at gate-d
- **app-studio-ui-judge** v1 [draft] - App Studio UI judge prompt: judge real captured screens of a built app against its spec and done-screens
  - triggers: judge the app screens, ui judge screenshots, visual qa of the built app
- **app-studio-verifier** v2 [draft] - App Studio verifier prompt: grade a finished app build against acceptance checks the builder never saw, through rig-testlab and the mutation gate
  - triggers: verify the app build, hidden acceptance checks, app bench verifier
- **app-studio-verify-qa** v1 [draft] - App Studio verify-qa stage prompt: self-verify every contract line from a fresh production build and write verify.md
  - triggers: self verify the app, write verify.md
- **app-studio-web-frontend** v3 [draft] - App Studio web-frontend stage prompt: every contract page returns real server-rendered content from the production build
  - triggers: web frontend pages, server rendered pages for the app
- **app-sub-acceptance-checks** v1 [draft] - App Studio sub-prompt: author executable acceptance checks for an App Bench task that the builder never sees
  - triggers: author acceptance checks, bench task acceptance
- **app-sub-assertion-lint** v1 [draft] - App Studio sub-prompt: lint a test runner for assertion verbs and hardcoded pass literals before quoting its counts
  - triggers: assertion verbs lint
- **app-sub-clerk-auth** v1 [draft] - App Studio sub-prompt: wire Clerk with public routes, ownership checks and a demo-user fallback when keys are absent
  - triggers: clerk auth wiring
- **app-sub-demo-user-auth** v1 [draft] - App Studio sub-prompt: a seeded demo user as a named auth stub with ownership checks on every mutation
  - triggers: demo user auth stub
- **app-sub-deploy-gotchas** v2 [draft] - App Studio sub-prompt: the after-approval deploy checklist distilled from shipped-broken deploys
  - triggers: deploy gotcha checklist
- **app-sub-done-md** v2 [draft] - App Studio sub-prompt: the DONE.md close-out the verifier reads first
  - triggers: done.md close out
- **app-sub-drizzle-neon** v1 [draft] - App Studio sub-prompt: Drizzle ORM over Neon or PGlite with the pg-proxy row contract proven before wiring
  - triggers: drizzle neon postgres, pg proxy drizzle
- **app-sub-durable-job** v1 [draft] - App Studio sub-prompt: run long AI work as durable steps with a status record and per-step progress
  - triggers: durable background job, multi step pipeline progress
- **app-sub-error-states** v1 [draft] - App Studio sub-prompt: keep a failed request from blanking a screen with section error states, response.ok checks and no swallowed errors
  - triggers: section error states
- **app-sub-expo-app** v2 [draft] - App Studio sub-prompt: build the Expo lane with its three preflight checks and simulator captures from Orca
  - triggers: expo app build
- **app-sub-feature-slice** v2 [draft] - App Studio sub-prompt: brief and build one feature per slice with named vendors, files and an observable result
  - triggers: one feature per slice
- **app-sub-gate-d-hold** v1 [draft] - App Studio sub-prompt: a complete release request that stays HELD until Mike approves
  - triggers: gate-d release request
- **app-sub-json-store** v1 [draft] - App Studio sub-prompt: a JSON-file store with atomic writes that boots from an empty folder
  - triggers: json file store
- **app-sub-lesson-candidates** v1 [draft] - App Studio sub-prompt: record each failure hit during the build as a lesson candidate with exact evidence
  - triggers: lesson candidates section
- **app-sub-llm-feature** v1 [draft] - App Studio sub-prompt: an LLM feature with a JSON schema contract, one client module and a named fallback
  - triggers: gemini feature with fallback, llm json schema feature
- **app-sub-named-fallbacks** v2 [draft] - App Studio sub-prompt: env-gate each paid vendor behind a named fallback so the app runs with no keys
  - triggers: named fallback for paid api
- **app-sub-next-build-time** v2 [draft] - App Studio sub-prompt: rebuild and restart after changing public files or NEXT_PUBLIC values, and confirm it by fetch
  - triggers: next public build time
- **app-sub-next-webpack-scaffold** v1 [draft] - App Studio sub-prompt: scaffold Next.js App Router with webpack builds and Tailwind v3 so it builds in the Aside sandbox
  - triggers: next.js webpack scaffold
- **app-sub-observability** v1 [draft] - App Studio sub-prompt: error capture for API and client with request and session context, proven by an induced error before any release request
  - triggers: error monitoring before release
- **app-sub-persistence-readback** v1 [draft] - App Studio sub-prompt: check each persisted record through a second path and show background work runs with a forced-due fixture
  - triggers: persistence readback check
- **app-sub-planted-failure** v1 [draft] - App Studio sub-prompt: show a check can go red by planting a defect with byte-movement proof
  - triggers: planted failure proof
- **app-sub-quota-gate** v2 [draft] - App Studio sub-prompt: enforce quotas and credits in the creation path, and make every charge and webhook idempotent in test mode with live keys at Gate-D
  - triggers: quota gate limit
- **app-sub-real-screen-capture** v1 [draft] - App Studio sub-prompt: capture real screens from the production build or a cold simulator for the UI judge
  - triggers: capture real screens
- **app-sub-saas-skeleton** v2 [draft] - App Studio sub-prompt: map the app onto the seven-part SaaS skeleton with real data and per-mutation feedback
  - triggers: saas skeleton screens
- **app-sub-sandbox-rules** v2 [draft] - App Studio sub-prompt: the Aside sandbox rules for native binaries, process control, ports and Python
  - triggers: aside sandbox rules
- **app-sub-spec-md** v2 [draft] - App Studio sub-prompt: the .app-studio/spec.md format the verifier and the app.spec gate use
  - triggers: spec.md format
- **app-sub-ssr-first-paint** v2 [draft] - App Studio sub-prompt: server-render each contract page's name and primary content so the server HTML alone shows the page
  - triggers: server rendered first paint
- **app-sub-stack-md** v2 [draft] - App Studio sub-prompt: the .app-studio/stack.md format the app.stack gate reads
  - triggers: stack.md format
- **app-sub-stage-record** v1 [draft] - App Studio sub-prompt: the .app-studio/stages/<stage>.md format with Evidence and lesson receipts that app.stage-gate reads
  - triggers: stage record evidence block
- **app-sub-typed-lesson** v1 [draft] - App Studio sub-prompt: write one typed lesson line for the App Studio ledger that validates and fires
  - triggers: typed lesson format
- **app-sub-verify-md** v2 [draft] - App Studio sub-prompt: the .app-studio/verify.md self-verification format
  - triggers: verify.md format

## code

- **independent-read-only-review** v1 [draft] - Independent read-only review of a landed fix: bugs, security, violations, run the check, no source writes
  - triggers: independent review, read-only review, always recheck, review this fix, pass with exact evidence
- **independent-verification-sidecar** v1 [draft] - Design green-path and red-path tests for a harness without editing files
  - triggers: verification sidecar, propose red-path tests, green path red path, propose gates not edit, independent test design
- **worktree-unit-spec-packet** v1 [draft] - Parallel worker packet: isolated worktree, read the spec in full, run tests and paste real output, commit
  - triggers: worktree worker prompt, isolated track handoff, assign track, builder spec in full, sealed unit of work

## coding

- **coding-mission-outcome** v1 [draft] - Implement and verify a bounded coding change from a hash-bound mission packet
  - triggers: Python parser, coding mission, implement code, fix an API bug, regression test

## gtm-outreach

- **off-linkedin-distribution-push** v1 [draft] - Off-LinkedIn distribution push for a live post: execute what is executable, name the exact blocker for the rest
  - triggers: push this post off linkedin, cross post distribution, execute the lanes, exact blocking report, off-platform amplification
- **read-only-icp-outreach-targets** v1 [draft] - Read-only prospect selection from the existing network using primary sources, no sending
  - triggers: find outreach targets, who should i email, prospect list no sending, target selection read only, best network prospects

## job-search

- **job-receipt-reconciliation** v1 [draft] - Read-only application receipt reconciliation in a bounded window, sqlite readonly only
  - triggers: reconcile application receipts, new application evidence, check submissions read only, receipt check, application ledger audit
- **job-search-state-audit** v1 [draft] - Full audit of job-search state: materials, moves today, resume and LinkedIn and saved-jobs alignment
  - triggers: job search audit, full audit of what we have, moves today, job strategy alignment, step back on the job search

## ops-automation

- **nightly-memory-consolidation** v1 [draft] - Nightly Memory OS consolidation: set the memory budget, run consolidation, record what changed
  - triggers: nightly memory consolidation, consolidate memories, memory budget, memory os maintenance, run the consolidation
- **ops-fleet-reliability-sweep** v1 [draft] - Read-only fleet reliability sweep reporting only new breakage since the last report
  - triggers: reliability sweep, read-only report, watchdog report, fleet status, new failures, cron health
- **ops-heartbeat-heal-report** v1 [draft] - Run rig-heartbeat heal and write the VERDICT report with mandatory receipt
  - triggers: heartbeat, heal the fleet, ops health report, run the heartbeat, automation receipt, fleet receipt

## planning-strategy

- **decision-grade-morning-brief** v1 [draft] - Decision-grade morning brief sized for a phone, gathering read-only inputs before ranking decisions
  - triggers: morning brief, decision grade brief, brief for today, what needs deciding today, phone length brief
- **future-back-versioned-gtm-roadmap** v1 [draft] - Future-back versioned roadmap and GTM design for a program going from now to a named version
  - triggers: future back roadmap, design out v20, versioned upgrade plan, go to market plan, deep layers

## prompt-craft

- **pattern-few-shot-block** v1 [draft] - Add structured few-shot examples that hold style and decision boundaries
  - triggers: few shot examples, add examples, example block, match this style, show examples, decision boundary
- **pattern-prompt-chain-3step** v1 [draft] - Chain three single-purpose prompts: summarize, extract insights, create action items
  - triggers: prompt chaining, break it into steps, summarize then insights, action items from, chain of prompts, one shot failing
- **pattern-sectioned-prompt** v1 [draft] - Structure any task prompt into delimited sections: background, instructions, tool guidance, output description
  - triggers: section the prompt, structure the prompt, xml tagged prompt, background information instructions, output description, prompt layout
- **pattern-subagent-search-isolate** v1 [draft] - Isolate search in sub-agents so the lead agent only synthesizes and decides
  - triggers: sub agent research, isolate search context, lead agent synthesizes, research with subagents, delegate the search, context isolation

## research

- **linkedin-growth-2026-research** v1 [draft] - Research what works on LinkedIn now using outside sources only, no account writes
  - triggers: what is working on linkedin, research growth tactics, outside sources only, no account writes, current linkedin best practices
- **recall-product-inventory** v1 [draft] - Source-cited product and technical inventory of a named product in numbered coverage areas
  - triggers: reverse engineer this product, source-cited product inventory, technical inventory of, research the product, factual stack analysis

## rig-gtm

- **lead-triage-classifier** v0 [draft] - Classify an inbound message (LinkedIn/email) as client-lead, job-opportunity, vendor-spam, or other

## rig-hq

- **rig-hq-meta-career** v1 [draft] - Operating meta-prompt for Career: J7 pipeline, prep and follow-ups that convert screens into offers
  - triggers: career meta prompt, job search, applications, resume, interview prep, recruiters
- **rig-hq-meta-engineering-tac-os** v1 [draft] - Operating meta-prompt for Engineering (TAC OS): J12 build/code and J2 watch/verify with one builder, an independent verifier and stop-before-ship
  - triggers: engineering meta prompt, build this, fix this repo, verify the build, what is left to do, prove it is done
- **rig-hq-meta-growth-content** v1 [draft] - Operating meta-prompt for Growth & Content: J6 right-lane voice, queue and numbers across LinkedIn, Instagram and film
  - triggers: growth content meta prompt, linkedin lane, content queue, post this, hooks, video
- **rig-hq-meta-intelligence** v1 [draft] - Operating meta-prompt for Intelligence: J4 sourced recall and J5 visible process design
  - triggers: intelligence meta prompt, recall, remember this, push to memory os, design the process, research this
- **rig-hq-meta-office-of-the-ceo** v1 [draft] - Operating meta-prompt for Office of the CEO: J1 day triage, J3 approvals and gates, J10 voice capture, J13 unattended runs, plus the draft-only Jacob lane J9
  - triggers: office of the ceo meta prompt, what needs me today, triage the day, gate d approvals, run unattended
- **rig-hq-meta-ops-fleet-security** v1 [draft] - Operating meta-prompt for Ops, Fleet & Security: J11 model and node reliability, routing around failures, secret and dependency hygiene
  - triggers: ops fleet security meta prompt, model routing, node down, fallback lane, secret sweep, fleet health
- **rig-hq-meta-revenue** v1 [draft] - Operating meta-prompt for Revenue: J8 offers, pipeline and outreach toward the first paying RIG client, with cold-send safety gates
  - triggers: revenue meta prompt, gtm, outreach, pipeline, offers, first paying client
- **rig-hq-prompt-alfred-linkedin-cron** v1 [draft] - Role prompt for alfred-linkedin-cron: scheduled drafting pipeline that produces drafts on a cadence and never publishes
  - triggers: alfred cron, scheduled drafts, daily linkedin draft cycle
- **rig-hq-prompt-clara-customer-success** v1 [draft] - Role prompt for clara-customer-success: onboarding, health and expansion signals once a client exists
  - triggers: clara, customer success, onboarding, churn risk, expansion signal
- **rig-hq-prompt-daphne-avis** v1 [draft] - Role prompt for daphne-avis: chief-of-staff drafting of decisions, briefs and exact-value approval packets
  - triggers: daphne, draft the decision packet, approval packet, morning brief, chief of staff draft
- **rig-hq-prompt-darius-gtm** v1 [draft] - Role prompt for darius-gtm: revenue-motion owner — offers, pipeline and outreach toward the first paying RIG client
  - triggers: darius gtm, revenue motion, offers and pipeline, gtm plan
- **rig-hq-prompt-darius-sales** v1 [draft] - Role prompt for darius-sales: outbound prospecting, scoring and reply ops (drafts; sends gated)
  - triggers: darius sales, prospect list, cold email draft, reply draft, score these accounts
- **rig-hq-prompt-eleanor-finance** v1 [draft] - Role prompt for eleanor-finance: spend, budgets and cost-per-run with receipts
  - triggers: eleanor finance, spend report, budget cap, cost per run
- **rig-hq-prompt-george-application-engineering** v1 [draft] - Role prompt for george-application-engineering: app-layer slices — data, backend, integrations
  - triggers: george, backend slice, data layer, integration, api endpoint
- **rig-hq-prompt-iris-jr-os-intelligence** v1 [draft] - Role prompt for iris-jr-os-intelligence: estate knowledge — what RIG already knows, built and decided
  - triggers: iris jr, what does rig already have, estate inventory, prior art check
- **rig-hq-prompt-iris-sr-research** v1 [draft] - Role prompt for iris-sr-research: deep research with a 4-tier source map and per-claim weights
  - triggers: iris research, deep research, source this claim, research dossier
- **rig-hq-prompt-iris-strategy** v1 [draft] - Role prompt for iris-strategy: evidence discipline owner — recall first, sources always, maps that expose gaps
  - triggers: iris strategy, what do we already know, decision research, design the process
- **rig-hq-prompt-jacob-lane-draft** v1 [draft] - Draft-only prompt for Jacob's lane (J9): film, Hudl, recruiting and minor-lane content, held for Mike's yes every time
  - triggers: jacob lane, jacob film, hudl clip, pewaukee, jacob content draft
- **rig-hq-prompt-jordan-app** v1 [draft] - Role prompt for jordan-app: the single builder who writes code in the named worktree
  - triggers: jordan app, build the slice, implement the plan, fix in this repo
- **rig-hq-prompt-jordan-jr-ai-engineering** v1 [draft] - Role prompt for jordan-jr-ai-engineering: engineering orchestrator that scouts, plans, dispatches one builder and stops before ship
  - triggers: jordan jr, engineering orchestrator, scout and plan the build, dispatch the builder
- **rig-hq-prompt-julie-job-search** v1 [draft] - Role prompt for julie-job-search: application-first search owner — truthful packets, receipts, follow-ups
  - triggers: julie, job search, applications pipeline, apply to these roles
- **rig-hq-prompt-madison-recruiting** v1 [draft] - Role prompt for madison-recruiting: recruiter and agency sourcing, outreach drafts and follow-up cadence
  - triggers: madison, recruiters, agency outreach, recruiter message draft
- **rig-hq-prompt-marcus-film** v1 [draft] - Role prompt for marcus-film: film and short-video production briefs and cuts (draft side, published only with approval)
  - triggers: marcus film, video brief, short film, shot list, video cut
- **rig-hq-prompt-nadia-data** v1 [draft] - Role prompt for nadia-data: data pipelines, measurement and numbers with named sources
  - triggers: nadia, data pipeline, measurement, the numbers, dataset check
- **rig-hq-prompt-nico-instagram** v1 [draft] - Role prompt for nico-instagram: adapting proven assets into the Instagram lane without voice drift
  - triggers: nico instagram, instagram adaptation, repurpose to instagram
- **rig-hq-prompt-opal-product** v1 [draft] - Role prompt for opal-product: product scoping — outcome, acceptance, cut lines before a build starts
  - triggers: opal, scope this, acceptance criteria, cut line, what does done look like
- **rig-hq-prompt-otto-operations** v1 [draft] - Role prompt for otto-operations: fleet and model reliability — probe first, route around failures, receipt everything
  - triggers: otto operations, fleet health, lane died, model routing fix
- **rig-hq-prompt-pedro-partnerships** v1 [draft] - Role prompt for pedro-partnerships: partner sourcing and co-sell motions with measurable sourced revenue
  - triggers: pedro, partnerships, co-sell, partner outreach, channel partner
- **rig-hq-prompt-prime-jake-pai** v1 [draft] - Role prompt for prime-jake-pai: CEO-office orchestrator that routes, gates and remembers every run
  - triggers: prime jake, orchestrate the day, jake ceo, what needs mike
- **rig-hq-prompt-ralph-linkedin** v1 [draft] - Role prompt for ralph-linkedin: LinkedIn hooks, posts and comment drafts in the right lane voice
  - triggers: ralph linkedin, linkedin post draft, hooks, linkedin comment draft
- **rig-hq-prompt-steve-content** v1 [draft] - Role prompt for steve-content: content-engine owner with lane discipline across LinkedIn, Instagram and film
  - triggers: steve content, content engine, lane voice, content plan
- **rig-hq-prompt-theo-design** v1 [draft] - Role prompt for theo-design: design judgment on user-facing surfaces before and after implementation
  - triggers: theo, design review, ui surface, ux flow, visual check
- **rig-hq-prompt-vera-security** v1 [draft] - Role prompt for vera-security: secret-leak sweeps and dependency vulnerability triage with fail-closed redaction
  - triggers: vera security, secret sweep, vulnerability triage, credential hygiene
- **rig-hq-sub-j1-1-an-approval-sits-over-24h** v1 [draft] - Interrupt sub-prompt (J1): an approval sits over 24h — re-surface it at the top of Today with a recommendation
  - triggers: approval over 24h, stale approval, old gate request
- **rig-hq-sub-j1-2-a-day-is-overloaded** v1 [draft] - Interrupt sub-prompt (J1): a day is overloaded — cut to 3 items and park the rest
  - triggers: day overloaded, too much work, collapsing, cut the day down
- **rig-hq-sub-j1-day-triage** v1 [draft] - Recurring sub-prompt (J1): turn the morning noise into the short list that actually needs Mike
  - triggers: day triage, what do we accomplish today, what needs me, top 3 today
- **rig-hq-sub-j10-1-a-dictated-name-matches-nothing** v1 [draft] - Interrupt sub-prompt (J10): a dictated name matches nothing — test homophones before filing
  - triggers: unknown name in dictation, name matches nothing, homophone
- **rig-hq-sub-j10-voice-capture** v1 [draft] - Recurring sub-prompt (J10): file and route one dictated thought without losing it
  - triggers: file this, note this, capture this thought, route this note
- **rig-hq-sub-j11-1-a-lane-dies** v1 [draft] - Interrupt sub-prompt (J11): a lane dies — move work to the next probed lane and file a repair card
  - triggers: lane died, provider down, node offline
- **rig-hq-sub-j11-2-a-paid-account-runs-dry** v1 [draft] - Interrupt sub-prompt (J11): a paid account runs dry — catch it with a one-token probe and stop the spend
  - triggers: paid account dry, credits exhausted, quota out
- **rig-hq-sub-j11-model-route** v1 [draft] - Recurring sub-prompt (J11): set or repair a model/lane route with probe evidence
  - triggers: model route, route around the failure, fix the lane, fallback chain
- **rig-hq-sub-j12-1-a-gate-goes-red** v1 [draft] - Interrupt sub-prompt (J12): a gate goes red — re-prompt the same builder with the evidence, max 3, then Windshield
  - triggers: gate red, check failed, red verify, failing gate
- **rig-hq-sub-j12-2-a-lesson-matches-a-new-task** v1 [draft] - Interrupt sub-prompt (J12): a lesson matches a new task — make its check required on the run
  - triggers: lesson matches task, apply the lesson, lessons ledger hit
- **rig-hq-sub-j12-build-slice** v1 [draft] - Recurring sub-prompt (J12): build one checked plan slice with real check output
  - triggers: build slice, implement this plan, code this
- **rig-hq-sub-j13-1-a-loop-spends-past-its-cap** v1 [draft] - Interrupt sub-prompt (J13): a loop spends past its cap — pause it and ask Mike
  - triggers: budget cap exceeded, loop spending, runaway spend
- **rig-hq-sub-j13-2-a-routine-errors-3-times** v1 [draft] - Interrupt sub-prompt (J13): a routine errors 3 times — the breaker pauses it
  - triggers: routine errors, three failures, breaker trip
- **rig-hq-sub-j13-unattended-run** v1 [draft] - Recurring sub-prompt (J13): arm an unattended run with a deadline, kill switch and budget cap
  - triggers: run unattended, keep going until, 1000x turns, overnight run
- **rig-hq-sub-j2-1-a-builder-goes-silent** v1 [draft] - Interrupt sub-prompt (J2): a builder goes silent — read its log, name the death cause, relaunch once on a probed lane
  - triggers: builder silent, worker stalled, no output, build hung
- **rig-hq-sub-j2-2-a-claim-of-done-has-no-receipt** v1 [draft] - Interrupt sub-prompt (J2): a claim of done has no receipt — refuse it and file a Windshield card
  - triggers: done claim no receipt, unevidenced done, badge not work
- **rig-hq-sub-j2-3-a-model-drifts-to-flash** v1 [draft] - Interrupt sub-prompt (J2): a model drifts to Flash — pin the session back and log it
  - triggers: model drift, flash model, wrong model bound, route drift
- **rig-hq-sub-j2-verify-receipt** v1 [draft] - Recurring sub-prompt (J2): verify a claim of done independently and issue or refuse the receipt
  - triggers: verify done, prove it, is it done, independent verification
- **rig-hq-sub-j3-1-a-card-has-no-exact-values** v1 [draft] - Interrupt sub-prompt (J3): a card has no exact values — block it before it reaches Mike
  - triggers: card no exact values, vague approval card, missing values
- **rig-hq-sub-j3-2-same-kind-approved-5-times** v1 [draft] - Interrupt sub-prompt (J3): the same kind of action was approved 5 times — propose a standing yes
  - triggers: approved 5 times, standing approval proposal, repeated gate
- **rig-hq-sub-j3-approval-gate** v1 [draft] - Recurring sub-prompt (J3): one-tap approve/deny packets for outward actions with exact values
  - triggers: approval packet, gate d, approve or deny, outward action
- **rig-hq-sub-j4-1-an-answer-has-no-source** v1 [draft] - Interrupt sub-prompt (J4): an answer has no source — send it back for a cited retry
  - triggers: unsourced answer, no citation, claim without evidence
- **rig-hq-sub-j4-2-recall-api-lags-the-app-853-vs-2** v1 [draft] - Interrupt sub-prompt (J4): recall API lags the app (853 vs 21,987) — flag the gap and route to the app export
  - triggers: recall lag, recall api gap, memory index stale
- **rig-hq-sub-j4-recall-first** v1 [draft] - Recurring sub-prompt (J4): surface what is already saved and decided, with sources, before anything new
  - triggers: recall first, what do we already know, prior decision, saved knowledge
- **rig-hq-sub-j5-1-a-map-has-red-links** v1 [draft] - Interrupt sub-prompt (J5): a map has red links — file build cards to turn them green
  - triggers: red links, map gaps, unresolved links in the map
- **rig-hq-sub-j5-process-map** v1 [draft] - Recurring sub-prompt (J5): lay a fuzzy idea out as a visible, editable process map with its gaps named
  - triggers: process map, design it out visually, system map, canvas the process
- **rig-hq-sub-j6-1-a-post-takes-off** v1 [draft] - Interrupt sub-prompt (J6): a post takes off — repurpose it and ask about a boost
  - triggers: post took off, going viral, spike in impressions
- **rig-hq-sub-j6-2-the-calendar-runs-thin** v1 [draft] - Interrupt sub-prompt (J6): the calendar runs thin — fill next week, schedule only after Mike's yes
  - triggers: calendar thin, queue running out, fill the content calendar
- **rig-hq-sub-j6-3-comments-flood-in** v1 [draft] - Interrupt sub-prompt (J6): comments flood in — draft replies for Mike's yes
  - triggers: comments flooded, reply backlog, many comments
- **rig-hq-sub-j6-post-cycle** v1 [draft] - Recurring sub-prompt (J6): one content cycle — lane call, hooks, draft, gate
  - triggers: content cycle, write a post, draft this content, hooks for this
- **rig-hq-sub-j7-1-an-interview-gets-booked** v1 [draft] - Interrupt sub-prompt (J7): an interview gets booked — build the prep pack and run a mock
  - triggers: interview booked, interview prep, interview scheduled
- **rig-hq-sub-j7-2-screens-stop-converting** v1 [draft] - Interrupt sub-prompt (J7): screens stop converting — find the stage that leaks
  - triggers: screens not converting, stalled funnel, no callbacks
- **rig-hq-sub-j7-application-batch** v1 [draft] - Recurring sub-prompt (J7): one application batch — tailor, verify claims, receipt
  - triggers: application batch, apply to these roles, tailor the resume
- **rig-hq-sub-j8-1-a-prospect-replies** v1 [draft] - Interrupt sub-prompt (J8): a prospect replies — draft the answer and book the call only after Mike's yes
  - triggers: prospect reply, inbound reply, lead responded
- **rig-hq-sub-j8-2-a-week-passes-with-no-reply** v1 [draft] - Interrupt sub-prompt (J8): a week passes with no reply — change the offer or the list, not the volume
  - triggers: week no reply, dead sequence, no responses
- **rig-hq-sub-j8-gtm-motion** v1 [draft] - Recurring sub-prompt (J8): run one revenue motion step — offer, list, sequence or scorecard
  - triggers: gtm motion, revenue step, work the pipeline, offers and outreach
- **rig-hq-sub-j9-1-signed-in-handle-does-not-match** v1 [draft] - Interrupt sub-prompt (J9): the signed-in handle does not match — everything halts
  - triggers: handle mismatch, wrong account signed in, jacob handle assert failed
- **rig-hq-sub-j9-jacob-draft** v1 [draft] - Recurring sub-prompt (J9): produce one Jacob-lane draft and hold it for Mike
  - triggers: jacob draft, draft jacob clip, jacob lane artifact

## verification-probe

- **probe-connectivity-ack** v2 [draft] - One-shot connectivity check that echoes an exact ack literal and touches nothing
  - triggers: connectivity check, reply with exactly, echo, echo back, is this alive, alive, is it up, still responding, liveness, ping the agent, ack literal, just have it echo
- **probe-exec-raw-stdout** v1 [draft] - Run one exact command and return raw stdout, stderr and exit code with zero interpretation
  - triggers: run exactly this, raw stdout, no interpretation, prove the command ran, exec proof, exit code only
- **probe-repl-once** v1 [draft] - Connection test exercising exactly one repl call and reporting one observed value
  - triggers: connection test, repl exactly once, report the page title, one tool call, fresh observation
- **secret-scan-memory-probe** v1 [draft] - Scan memory for secrets and report presence without ever printing values
  - triggers: scan memory for secrets, credentials in memory, sensitive values check, memory secret audit, api keys check
- **stop-report-no-edits** v1 [draft] - Stop exploration now and return strongest findings with evidence, no edits
  - triggers: stop exploring, return strongest findings, wrap up with evidence, no edits just findings, timebox stop

## writing-content

- **linkedin-draft-no-publish** v1 [draft] - Draft a short LinkedIn post and print only, never publish or schedule
  - triggers: draft a short linkedin post, do not publish, two sentence post, print the draft only, draft only post

