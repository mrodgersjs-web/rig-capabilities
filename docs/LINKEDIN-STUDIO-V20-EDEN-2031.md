# RIG LinkedIn Studio — v0 → v20, Eden, and the 2031 direction

Status: IMPLEMENTATION DESIGN, not an implementation or activation approval. Prepared 2026-09-04. Builder: MiMo v2.5 Pro; independent verifier must use another model family. Scope of this session: inspect, design, and run a loopback-only preview. No content was published, scheduled, sent, or changed in Eden.

## 1. Decision and done contract

Build a **buyer-evidence-to-qualified-conversation operating system**, not another post generator. Eden is the research and collaborative editorial workspace; LinkedIn Studio is the operator, state, evidence, approval, and handoff surface. Existing GTM machinery owns commercial records and approved execution. One logical publishing authority, never two schedulers for the same content revision.

The requested Studio v0–v20 numbers below are implementation milestones. They are **not** the existing app's package version (End Studio V10), the company's 2031 v0–v10 capability ladder, model versions, or calendar years.

Planning deliverable is complete when it contains: observed v0 evidence; explicit strategy authority; all ten layers with contracts, ownership, failure semantics and adversarial acceptance; Eden's existing structure and actual capability limits; a dependency-ordered twenty-slice MiMo handoff; and a working safe preview. Implementation completion additionally requires the scenario under §10, independent verification, and explicit approval for any live action. A complete plan is not a working v20 product.

### Current commercial authority versus horizon

| Subject | Controlling decision | Source / status |
|---|---|---|
| Current ICP | Owner-operators/professional-services founders in law, dental/DSO, CPA, home services, specialty clinics, where the founder is the bottleneck | S1, Mike-locked current offer |
| Entry offer | RIG Operating Audit, $7,500: diagnosis → 90-day plan → readout | S1; do not use retired $2.5K/$3.5K entry SKUs |
| Ladder | Optional $10K Blueprint → $25–50K implementation → $5–10K/month managed operating layer | S1; one-time fees are not ARR |
| Exception | HED-class $40K assessment through procurement/PO/SOW | S1; not the cold-entry checkout |
| Booking CTA | https://calendly.com/rodgersintelligence/rig-audit | S1; use booking, not an unverified payment link |
| Near-term aspiration | $10M ARR by June 2027 | S5, historical strategy target, not a forecast of success or current revenue |
| Operating direction | Strategy first, AI second, automation third; forward-deployed work finances reusable capability | S4; proposed product names do not amend S1 pricing |
| 2031 thesis | Private Enterprise Twin OS on commodity edge compute | S2 explicitly calls this an “own forecast” |

There is no verified completed single Fable “2031 GTM strategy” synthesis in the inspected evidence. `docs/DONE-CONTRACT-2031.md` describes intended work; its Gate-D session record is blocked, and `/tmp/fable-2031-result.json` was not found by the strategy scout. Do not claim Fable approved this design. Use the authority split above, not a fabricated consolidated canon. July revenue/call figures in S5 are historical; September actuals remain unknown until read from commercial systems.

The forecast's phase gates are retained, not flattened into “ship by year”: 2026 H2 requires ten signed audits and twelve consecutive positive-convergence weeks; ten audits yielding zero contracts refutes the ladder. 2027 requires independently verified certification and closing contracts. 2028 requires client #10 materially cheaper than #1 and at least one crystallized workflow per engagement. 2029 requires a Vendor Death Drill. 2030 allows Studios to propose goals, with Mike gating them. 2031 requires org-scale operation, A_t ≥0.8, one operator. These are company gates, **not claims this LinkedIn project alone can satisfy**. [S2]

## 2. Observed v0 and scope boundary

### Repository boundary

- Editorial UI: `/Users/rig128gb/Desktop/rig-linkedin-studio/end-studio-v10` (hereafter `UI/`). Next 14.2.5, React 18.3.1, TypeScript, Zod 3.23.8, Zustand, Tailwind, Vitest. `app/page.tsx` renders Mission Control; `src/lib/` holds contracts/engine state.
- Existing editorial/engagement engines and data also live under `/Users/rig128gb/Desktop/rig-linkedin-studio`. Preserve them until a named caller is migrated and independently verified.
- `/Users/rig128gb/Developer/rig-gtm-studio-v2` (hereafter `GTM/`) supplies the RIG studio corpus/catalog visible in Eden and commercial integration candidates. It is not permission to duplicate its CRM, scheduling, or memory ownership.
- Developer `rig-linkedin-studio-luca/cockpit-v2` is a different Traject cockpit. Do not put this LinkedIn build there. Prior `traject-v20-future-back` artifact paths under Desktop did not resolve; do not treat that plan as a LinkedIn baseline.
- Generic A1/A2/A3/A4 Python guidance from the builder skill is an architectural reference, not verified current UI code. Preserve the **existing Zod/TypeScript boundary**; do not impose a second Pydantic source of truth on this app.
- The existing Python domain owners are reuse targets, not automatically proven services: `rig_linkedin_studio/storage.py` is filesystem campaign storage; `campaign_ledger.py` is a SQLite **engineering-turn** ledger at `~/.jake/rig.db`, not a sales/content ledger; `approval_queue.py` is an Atlas JSONL request queue whose resolution does not execute actions. Scout-identified additional owners: `workflows/evidence_synthesizer.py`, `rig_linkedin_studio/proof_generator.py`, `publishing/publisher.py`, `analytics/store.py`. Audit their actual contracts at the owning slice; do not port their business logic wholesale into TypeScript.

### Actual startup evidence

Pinned dependencies were absent. Installed the existing lockfile with `npm ci --ignore-scripts --no-audit --no-fund`; no source or lockfile edit was intended. The install warned that Next 14.2.5 is vulnerable. Preview remains loopback-only; upgrading to a current patched compatible release is a v1 prerequisite before deployment, not something silently bundled into this planning session.

Running service: `linkedin-studio-plan-preview`, `./node_modules/.bin/next dev -p 3410 -H 127.0.0.1`, with `NEXT_TELEMETRY_DISABLED=1`. Browser verified `http://127.0.0.1:3410/`, title `End Studio V10`, Mission Control. Screenshot: `../.lavish/linkedin-studio-v0.png`. Root `start.sh`/`run.sh` were deliberately not used because they can start schedulers or other operational processes. No workflow Run control was invoked.

### Behavioral gaps, not cosmetic debt

| Observed surface | Evidence | Consequence / first repair |
|---|---|---|
| 15 workflow definitions displayed; zero run/proof records in this fresh process | Mission Control; `UI/src/lib/workflows.ts` | Definitions are not completed workflows or historical performance |
| Workflow execution creates `[dry-run draft]`, simulated transitions, and path strings without writing those artifacts | Baseline scout inspection of `UI/src/lib/engine.ts`; all `WORKFLOWS` are `dry_run` | No provider workflow is exercised; simulated proof must be labeled, not promoted |
| Approval POST mutates a flag; workflow POST accepts request-supplied owner | Scout inspection of `UI/app/api/{approvals,workflows/[id]/run}/route.ts` | Authenticate and authorize server-side; a request string is not Mike |
| `/api/health` always says OK; terminal emulates allowlisted commands | Scout inspection of health route and `UI/src/lib/terminal.ts` | Separate process liveness from readiness; label terminal as simulation |
| Runs, proofs and approvals are process-global arrays | `UI/src/lib/store.ts:3–28` | Restart loses state; persist before approving anything |
| “live” derives from environment-variable presence | `UI/src/lib/integrations.ts:6–80` | Configured ≠ authenticated ≠ reachable ≠ exercised; replace status semantics |
| UI shows gates 10/13, two failing | Mission Control | Not production readiness; most pass conditions are hardcoded booleans |
| Gate 00, 01, 02, 03, 05–08, 10–11 pass without fresh executable evidence | `UI/src/lib/gates.ts:26–46` | Remove fabricated green; `unknown` until evidence for the exact revision exists |
| Approval lacks exact target/time/media/revision/expiry binding | `UI/src/lib/schemas.ts:63–76` | A draft-level approval is insufficient to authorize an external action |
| LinkedIn and Archon are blocked in current status code | `UI/src/lib/integrations.ts:64–79` | Keep blocked until proven; never relabel an unsupported integration as live |
| Console mixes publishing, jobs, recruiter and acquisition surfaces | Browser navigation | Prioritize LinkedIn commercial path; leave unrelated job/recruiter flows untouched |

### Eden: observed, not imagined

Workspace: https://app.eden.so/w/rodgemd1-s-workspace/home. The populated `RIG GTM Studio` space is https://app.eden.so/w/rodgemd1-s-workspace/spaces/e4dcb178-f056-4238-a440-e2ec03d27997. Its canvas showed existing corpus notes for LinkedIn How-To and Recall lanes (GTM, CRO, brand-writing, communication, LinkedIn engagement, presentation, agent-patterns, video-scripts), plus Skills, Agents & Harnesses, Contracts & Gates, and Examples. Provenance cards retain Recall card IDs, source URLs where available, and 2026-09-02 capture dates. Some cards have `source_url: null`; do not manufacture URLs.

Sidebar also showed `Weekly strategy`, `RIG Known Expert OS`, `RIG OS — Jake Vault x Memory OS`, `LI swipe`, `Welcome to Eden`, `My Ideas (renamed)`. Their existence is observed; their complete contents and stable IDs were not inventoried. Reuse and link rather than create another parallel workspace.

The Custom AI catalog displayed **36** assistants; a DOM count found **31 showing zero connected sources**. Five displayed sources: Creator Deep Dive (6), RIG Known Expert OS (2), RIG GTM Studio Brain (1), RIG Operator (5), Thought Partner (7). Counts describe catalog UI, not completeness or quality of all knowledge. Several zero-source summaries are visibly malformed. Exclude unreviewed assistants from the Studio execution allowlist; do not delete or bulk-rewrite them.

RIG GTM Studio Brain was inspected through Overview and Configure. It has one source labeled `RIG GTM Studio board — skills, corpus, examples, contracts`, workspace access `Connected sources`, and **no routines**. Its instructions already require pattern/card grounding, prefer patterns supported by ≥2 creators, mark early signals, cite Recall card titles, avoid invented video-duration evidence, and keep drafting separate from Gate-D publication. Extend this definition after approved revision-safe editing, not by replacing it with a blank assistant. Snapshot text: `../.lavish/eden-studio-brain-observed.txt`.

Eden MCP tools were not available in this session's mounted inventory. OAuth, pagination, writes, scheduler connections and analytics entitlement were **not exercised**. Browser inspection succeeded after delayed navigation/reload; transport click success was not treated as page success. We did not enter Publish or call analytics, since the first analytics request can enable tracking.

## 3. Systems model: intervene at the constraint

Boundary: source observation → buyer problem → evidenced campaign → approved release → conversation → qualified booking → commercial outcome → verified learning. Exclude delivery of client projects themselves, billing execution, and unrelated employment workflows.

| Stock | Unit / inflow / outflow | Delay or constraint | Authoritative owner |
|---|---|---|---|
| Buyer-relevant evidence | Valid claim records; accepted observations in, retraction/expiry out | Provenance review and permission to disclose | RIG evidence ledger; Eden source locator |
| Campaign work in progress | Active briefs; admitted campaigns in, shipped/killed out | Mike review time, available real proof | Studio campaign state |
| Approved release queue | Exact content revisions; approvals in, receipt/revocation out | Timezone, media, publisher availability | RIG release ledger |
| Unresolved engagement | Threads needing response; observed replies in, resolved/declined out | Observation lag, staffed service window | GTM relationship owner; Studio projection |
| Qualified conversations | Deduplicated qualified threads; qualification in, closed/disqualified out | Buyer timing; not every comment is intent | GTM commercial record |
| Reusable demonstrated mechanisms | Verified mechanism cards; proof-backed promotion in, invalidation out | Outcome maturation, independent verification | Existing memory/capability owners |

**R1, desired reinforcing loop:** specific buyer evidence → credible useful content → relevant replies → discovery evidence → sharper buyer model → more specific content. A reply is feedback, not revenue.

**B1, capacity-balancing loop:** more output → more review/reply work → slower follow-through → fewer qualified bookings → lower admitted WIP. Stop admission when unresolved work exceeds staffed capacity; do not respond by adding generators.

**R2, failure loop:** pressure for output → generic claims → poor-fit engagement → weak learning → pressure for output. This is a hypothesis, not an observed time series.

**B2, control loop:** source contradiction/provider uncertainty → quarantine and human review → corrected claim/state → release resumes. It must remain fast enough that staff do not bypass it.

**R3, long-term compounding:** verified client mechanism → safe anonymized proof → trust and better-fit calls → successful engagement → reusable mechanism. Do not infer this loop is functioning from a larger knowledge corpus.

Proposed bottleneck hypotheses: (H1) buyer evidence/intake and follow-through, not drafting capacity, limit commercial outcomes; (H2) duplicated orchestration and unsourced assistant inventory increase noise; (H3) truth-bearing status and persistence are prerequisites for trusting automation. H1 needs linked content→thread→booking observations; H2 needs actor/queue inventory; H3 is directly supported by source-code gaps. Reject H1 if qualified traffic is sufficient but booking friction or offer mismatch dominates; then fix intake or offer rather than content.

**Leverage order:** Meadows 6 information/feedback → 5 rules/WIP and release authority → 3 goal alignment. Reject a rank-12 “increase posting volume” intervention until capacity and qualified conversion are measured. The systems studio ran GREEN for the complex-context frame and RED for a deliberate `disorder` input. Runs are in S8. These prove procedural checks discriminate, not that H1/H2 are empirically true. The canned fourteen-day simulation uses synthetic starting stocks and response rates; its 0.106 versus 1.998 inbound outputs are **not a RIG forecast, target, or expected lift**.

Initial operating policy (proposed defaults, not canonical measured optimum): one primary ICP problem and at most three active campaign briefs per weekly review; no higher publication floor; admit a post only if review and follow-through capacity exist. Observe early response at 24h/72h, commercial path at 7/30 days, delayed outcomes separately. Start reply SLA at 90 minutes **inside explicitly staffed windows**, retain event time and observed time, and measure coverage; no promise of 24/7 five-second replies. Automatic acknowledgements are sends and remain gated.

Canonical weekly review follows Strategy → Research → Design → Execution → Learnings. C_t and A_t are read from the existing capability register/verdict machinery, not recoded in the Studio. Require `ΔC_t > 0`, `ΔA_t ≥ 0`, and the real booked-qualified-conversations condition; missing denominator, MAD=0, unclassified >10%, or missing evidence is `unknown`/blocked, not zero or PASS. The source contains tension between “information weeks count” and a strict improvement gate: retain useful information as a learning artifact, **do not waive the weekly gate**. Three weeks of rising C_t with zero bookings triggers weight/offer review; three FAIL weeks triggers loop review; a verifier that never blocks for four weeks requires independent replay. [S2,S3]

## 4. Shared data and trust contracts

Extend `UI/src/lib/schemas.ts` using existing Zod and naming conventions. The fields below are proposed additions, not current APIs. All authoritative records carry `schema_version`, stable ID, `revision`, UTC creation/update times, owner, classification, provenance and trace/run IDs where applicable. Money is integer minor units plus currency; duration/time units are explicit; timestamps contain timezone/offset. Unknown values are nullable with `status` and `reason`; `0` means an observed zero. UTC storage does not replace the provider's IANA scheduling timezone.

- **StrategyContract**: `strategy_id`, `revision`, `authority_source`, `authority_hash`, `status` (current/forecast/proposed/superseded), `valid_from`, `icp_ids`, `offer_ids`, `goal_metric`, `horizon`, `non_goals`, `gate_refs`.
- **AccountSignal**: `signal_id`, `account_id`, role, observed problem/trigger, `source_ref`, `observed_at`, `expires_at`, `fit_reason`, `intent_evidence`, `qualification_status`, opt-out/suppression reference. No inferred health, ethnicity, personality or financial distress.
- **EvidenceRecord**: `evidence_id`, provider/workspace/item locator, source revision, URL or explicit missing-URL reason, capture/event time, content hash, bounded excerpt/quote offsets, claim type (fact/inference/assumption/forecast/preference), reliability basis, falsifier, source ACL, license, disclosure permission, retention class, superseded/retracted link.
- **CampaignBrief**: `campaign_id`, strategy revision, ICP/problem/offer/CTA refs, evidence IDs, content role (diagnosis/mechanism/proof/objection/field-note), hypothesis, intended buyer response, owner, timebox, WIP state, experiment reference.
- **ContentRevision**: `content_id`, revision, campaign/brief hash, text, format, claim-span→evidence links, media IDs/hashes/alt text, source-pattern attribution, model/prompt/skill versions, generation mode (real/manual/simulation), quality verdict references.
- **HandoffManifest**: RIG object ID/revision, Eden workspace/item/row ID and remote revision, direction, base hash, payload hash, accepted hash, operation key, cursor, state (proposed/applied/conflict/failed), receipt time. A board's space ID is not a workspace ID.
- **ReleaseIntent**: one ID bound to `content_id`+revision, exact account/platform, media hashes, `scheduled_at_utc`, timezone, executor, approval reference, expiry and action hash. State: dormant → awaiting_approval → approved → dispatching → scheduled/posted; ambiguous outcome → reconcile_required; rejected/expired/revoked/failed remain explicit. `approved` is never a publication receipt.
- **EngagementEvent / CommercialOutcome**: provider event ID, actual platform post ID, thread/contact/account refs, received/observed time, classification and reason, qualification/booking/deal IDs, lifecycle dates, cancellation/disqualification, attribution evidence and confidence. Deduplicate before aggregating.
- **CapabilityObservation**: provider/tool/account scope, configured/auth/reachable/exercised booleans or unknowns, permitted operation class, observation time/TTL, latency/error class, evidence ref. No secrets in observations.

**Storage and domain choice:** keep Next as presentation/thin request adapters and place business execution in the existing Python domain boundary, without granting legacy modules unearned release authority. Reuse only verified aggregate-specific contracts: `storage.py` owns campaign file locations; `campaign_ledger.py` owns engineering-turn history; `approval_queue.py` owns Atlas request history, not action authorization; evidence/proof/analytics modules are reuse candidates until their slice verifies them. ReleaseIntent/outbox owns missing transactional release state, and the executor selected and verified at v13 alone dispatches. `publishing/publisher.py:41–75` currently ignores scheduling/media parameters, returns a local ID and a browser-call boolean, while `get_post_status:104–118` reads local SQLite—not LinkedIn. It does not qualify as a verified executor. Use Python stdlib SQLite for missing Studio-owned records, preferably an appropriate existing store after schema/ownership inspection; otherwise one narrowly scoped DB under the configured data directory. Never overload engineering-turn tables or create a competing Atlas approval authority. Prefer an existing supervised domain entrypoint; if none fits, add one bounded JSON stdio dispatcher, not a network service. Zod validates the UI wire contract; shared fixtures keep the domain invariant aligned. CRM, memory and the capability register remain external owners referenced by IDs.

**Ownership:** Eden owns original research material and its human edits. RIG owns accepted evidence snapshots, strategy contracts, content revisions, quality decisions, release authority and execution receipts. GTM/CRM owns qualification, bookings and deals. Capability register owns C_t/A_t. Memory OS owns durable promoted knowledge. Projections can be stale but cannot become a second source of truth.

**Missing authentication boundary:** the current approval API has no authenticated actor or verified Gate-D adapter. Creating that boundary is an explicit v2 target, not presumed infrastructure. First reuse an installed operator identity service only if its issuer/audience/session verification is actually established. Otherwise implement the local single-operator pairing contract in the MiMo packet §3: human-initiated OS-owner pairing, hashed expiring server sessions, fixed server-assigned actor/role/scope, exact Origin/Host and CSRF checks, and no payload-supplied authority. v12 adds exact `APPROVE <run_id>` against the stored immutable action hash, expiring one-use nonce and atomic decision consumption. The mounted `gate_d_check({request_id})` is only a pending-request inventory, not proof of approval. A canonical Gate-D backend may replace the local decision authority only after its authenticated, hash-bound receipt contract is verified and a single-authority cutover is approved. Never mirror “approved” flags as a second authority.

**Revision rules:** a changed claim, body, media, account, platform or time invalidates prior release approval. Uniqueness on `(provider, external_event_id)` and on the logical active release for `(content_id, revision, account_id, platform)` prevents duplicate ingestion/dispatch. Intent and outbox are inserted atomically; there is no credible exactly-once guarantee across a provider network, so unresolved writes enter reconciliation rather than automatic resending.

## 5. Ten implementation-ready layers

### L01 — Strategy and outcome contracts

**Outcome:** every admitted campaign answers “which current buyer problem, offer, desired response, and authoritative strategy revision?” Owner: Mike for commercial decisions; strategy steward prepares; independent verifier checks authority. Depends on runtime persistence and evidence identity, not a generative agent.

**Implementation:** extend schemas and the existing acquisition/personal-brand workflow inputs; add a Strategy view to the existing shell. Import S1 current commercial fields and S2 horizon gates into separate records. Hash sources and require explicit acceptance of a changed current contract. Resolve all quote/CTA rendering from offer IDs; no copied prices in prompts. Add a strategy conflict queue; show current/proposed/forecast in text, not only color. Historical campaigns keep the authority revision under which they were made.

**Eden handoff:** `Weekly strategy` receives an approved, source-linked weekly decision brief; `RIG GTM Studio` points to it. Proposed strategy ideas from Thought Partner return as proposals, never overwrite S1. No automatic modification of prices, audiences, payment links, or goals.

**Acceptance:** given a draft quoting the retired $3.5K audit, admission is RED; replacing it with the current offer reference is GREEN. Given 2031 forecast language, it stays labeled forecast and cannot become a current capability claim. Changing an offer revision marks dependent unfinished drafts for review without rewriting published history.

**Failure/rollback:** source unavailable or conflicting → block commercial claims, permit research-only work. Restore the previous accepted strategy revision locally; do not retroactively alter approvals or external copy. Versions v4/v9/v20.

### L02 — Audience and account intelligence

**Outcome:** select buyers by observed problems and relevant roles, not creator popularity. Owner: GTM account/relationship owner (Darius lane), with research support. Depends on L01 and L04.

**Implementation:** reuse client/relationship surfaces and existing GTM IDs; add AccountSignal read model. Distinguish company, person, creator and target account. Store trigger, problem, role, source age, disqualifier and missing information; use explainable predicates before any scoring model. Start one weekly ICP/problem cohort; keep broader source material searchable without treating all eight legacy verticals as current priority. Unknown identity or ambiguous name remains unresolved; do not merge on display name alone.

**Eden handoff:** Creator Deep Dive supplies structure/outlier research; GTM supplies buyer qualification. Creator follower count/outlier score never grants ICP fit. Approved cohort brief links selected research cards and existing account IDs, not private CRM contact dumps. Tables use typed select/date/item/url fields if the live schema supports them.

**Acceptance:** an extremely viral non-ICP creator cannot enter the qualified buyer queue; an in-scope owner with a sourced problem can enter the research queue but not become a booked conversation. Duplicate profile URLs resolve to one identity; opted-out contacts remain suppressed through import and merge. A stale signal shows its age and loses admission eligibility rather than disappearing.

**Failure/rollback:** unresolved identities → review; lost CRM connection → visibly stale read projection, no writes or inferred zero pipeline. Reversible local cohort selection; no contact activation. Versions v5/v14.

### L03 — Eden knowledge operating system

**Outcome:** make the populated workspace usable by Studio without a second corpus or uncontrolled assistant fleet. Owner: Eden workspace steward for layout/content, RIG adapter for manifests. Depends on L04 IDs and L10 persistence; conceptual source inspection can precede these.

**Workspace design:** retain `RIG GTM Studio` as corpus/catalog hub, `Weekly strategy` as current decisions, `RIG Known Expert OS` as editorial judgment, `RIG OS — Jake Vault x Memory OS` as scoped memory pointers, and `LI swipe` as craft examples. Link existing items by ID. Within the GTM hub, add views/boards only when discovery shows no equivalent: Intake; Buyer Problems; Evidence & Mechanisms; Campaign Briefs; Draft Review; Published Receipts; Experiments & Learnings. Existing contracts/skills/examples/Recall-lane notes remain reference sections; do not rearrange or delete them during import.

**Table contract:** campaign rows contain RIG ID, title, stage select, ICP/problem selects, owner, due date, evidence item refs, Studio review URL, RIG revision, last synced date, conflict state. Evidence rows contain source item, capture date, source type, admissibility, rights, retraction status. Only shared draft fields are editable from Eden; approval, sent/posted and revenue cells are read-only projections of RIG/CRM receipts. If table read pagination limits or schema cannot express a field, retain the authority in RIG and link the manifest; never truncate silently.

**Assistant plan:** use Creator Deep Dive for research, Thought Partner for hypotheses, GTM Studio Brain for corpus-grounded draft/script work, Known Expert OS for editorial critique, RIG Operator for voice. These are provisional role assignments, not proof that each assistant is safe. Load exact definitions and attached source catalogs before admission. No new assistant is needed for v1. Review the 31 zero-source assistants' complete definitions before any promotion; zero sources alone is a risk flag, not proof of uselessness. Do not bulk-delete. Narrow connected sources, keep cross-chat voice/memory off unless explicitly requested, and deny external publishing in the Studio tool policy even if a prompt says “draft only.”

**Workflow:** discover live MCP tools and workspace ID → enumerate bounded pages/boards/tags/AIs → record locators and revisions → select permitted material → preview import diff → accept into RIG evidence → draft against accepted IDs → stage a proposed Eden review update → approve the workspace change → apply with concurrency guard → read back. The browser-only path is operator-assisted intake with explicit item URL and excerpt; label it non-automated, never claim MCP sync passed.

**Automation limits:** documented hosted MCP is `https://mcp.eden.so/mcp` with OAuth. Workspace search is saved material, not a representative ranking. Use social research tools for outliers. MCP exposes no AI image/carousel generation and no portable SKILL.md/legacy skill/prompt/identity import. Custom AI definitions, sources and tables have revision rules; routines observed in the app are not a verified callable MCP automation API. Brain currently has no routines; add none until a single scheduler owner is selected. The scheduler's account connections/timezone and this account's paid capabilities remain unverified. First `eden_get_analytics` can activate tracking; require explicit approval for first activation. Media upload yields public URLs: disclosure approval precedes upload.

**Acceptance:** repeated read/import yields one evidence identity; changed remote note raises a conflict without overwriting the human edit; embedded table markers survive a note round trip; unknown workspace cannot fall back to another account. An adapter without mounted/authenticated tools reports unavailable. A “top creator posts” query routed to saved-card filtering fails review. All outward Eden calls remain unreachable in preview mode.

**Failure/rollback:** `auth-expired` → client reconnect/refresh, then one retry; validation error → fix fields, not blind retry; row conflicts → reread and explicit merge; interrupted import → resume saved cursor. Never delete original Eden items to undo an import. Deactivate the local mapping or retain the last accepted snapshot. Versions v6/v7/v8/v18.

### L04 — Evidence and memory contracts

**Outcome:** every factual content claim has inspectable lineage and permission to disclose. Owner: evidence steward; memory owner alone promotes durable knowledge. Depends on L10 storage and current schema conventions.

**Implementation:** extend ProofRecord into a verifier-bound result, distinct from evidence sources; add EvidenceRecord and claim-span links to content. Store bounded immutable source snapshots with hashes and retention; cite source title/locator and timestamp. Classify fact/inference/assumption/forecast/preference. Contradictory claims coexist in a register until resolved; copied repetition is not independent corroboration. Record pattern structure separately from creator-owned story, numbers and wording. Model confidence is not source reliability or a calibrated probability.

**Eden handoff:** retain original item ID, board/workspace scope, captured remote revision and Recall card ID. A card title alone is not sufficient support for a numeric claim. A null URL remains null with provenance through the Recall card. Export approved mechanism summaries and links, not entire private conversations, client files or raw vault notes. Use the existing scoped Memory OS; no blind bidirectional vault replication.

**Acceptance:** a number with no supporting excerpt is RED; a retracted source invalidates affected pending drafts and approvals. Public output using private-only evidence is blocked even if accurate. Duplicate copies of one source do not satisfy “two independent sources.” A permitted original claim survives rendering and is inspectable from the claim to its exact snapshot.

**Failure/rollback:** retain source loss/retraction state and downstream impact; stop new claims from stale sources but preserve historical provenance. A repair supersedes, never silently edits, the prior record. Versioned scoped memory promotion requires a receipt; unavailable memory sink leaves a local pending artifact, not a fake synced state. Versions v3/v7/v11/v19.

### L05 — Editorial and campaign planning

**Outcome:** plan one coherent buyer journey rather than a daily assortment of formats. Owner: editorial lead; Mike accepts strategic changes. Depends on L01/L02/L03/L04.

**Implementation:** extend existing personal-brand/article workflow definitions and Content surface with CampaignBrief. Each brief binds a wound/problem, mechanism, evidence, offer, buyer response and stop condition. Recommended sequence: problem recognition → useful diagnosis → mechanism demonstration → legitimate proof → objection clarification → invitation when appropriate. Do not require every post to pitch. Field notes must be real observations; examples are labeled examples. Cross-format reuse must preserve claim lineage, not just text.

**Eden handoff:** weekly planning happens in `Weekly strategy`; shared campaign rows link to Studio briefs. Brain can suggest drafts from selected cards. Known Expert OS evaluates whether the content teaches a buyer something non-generic. Human notes entering from Eden become brief proposals, not hidden instructions to the workflow.

**Acceptance:** admission rejects an orphan draft with no current strategy/problem/evidence; the fourth active brief is blocked under the initial three-brief WIP policy unless Mike explicitly changes capacity. A killed campaign leaves its reason and receipts. A buyer objection can generate a new evidence-linked brief without creating an unsolicited outbound action.

**Failure/rollback:** unresolved source or strategy conflict pauses affected briefs only. Do not fill calendar holes with fabricated numbers, irrelevant trends or automatic publishing. Versioned weekly plan can be superseded while prior editorial decisions remain auditable. Versions v9/v10/v16.

### L06 — Creative production and quality

**Outcome:** distinct operator-voice work with truthful substance and measurable craft, not arbitrary score chasing. Owner: content producer; separate editor/evidence verifier. Depends on accepted briefs, claim ledger and model adapter.

**Implementation:** route existing drafting/quality engines before adding generators. Produce text, optional image/carousel/video brief and alt text as one ContentRevision. Keep native media generation in an existing approved image/video lane; Eden MCP is not that lane. Choose a source pattern, preserve its mechanism, replace all creator-owned substance. Limit candidate generation initially to three alternatives; select with reasons and retained rejects. Human Mike experience never comes from a model inventing “I did X.”

**Quality order:** disclosure/IP and unsupported-claim hard gates → ICP/mechanism relevance → voice/originality/editorial judgment → actual format limits/accessibility → independent release-readiness verdict. Use the existing single Deviation Service rather than reimplementing forty engines. Numerical craft scores remain advisory until calibrated against held-out human labels and outcomes. Template “≥2 numbers, ≥1 question, no image = kill” is not a universal truth: importing it would incentivize fabrication and needless media; only apply a campaign-specific rule with provenance and a reason. A useful text-only LinkedIn post remains valid.

**Eden handoff:** Brain drafts; Operator proposes voice refinements; Known Expert OS critiques. A source-linked draft and critique enter Studio as untrusted proposals. Neither assistant can sign its own quality gate or approve its output. Eden in-app media creation is a manual optional step, with asset rights and final hashes recorded before review.

**Acceptance:** a polished draft with an invented customer result is RED despite high craft score; copied creator numbers are blocked. A truthful text-only post can pass. Any revision after quality verification invalidates that verdict. Missing alt text blocks relevant image release; invalid/corrupt media cannot pass merely because a URL exists.

**Failure/rollback:** provider outage preserves the last accepted draft; no silent substitute model or template labeled generated. Exhausted repair loop stops after three attempts with specific defects for Mike. Reverting draft content creates a new revision rather than resurrecting a stale approval. Versions v10/v11.

### L07 — Distribution and relationship workflows

**Outcome:** one approved release and human-accountable follow-through. Owner: RIG release controller; the executor selected and verified at v13 executes; GTM relationship owner manages replies. Incumbent queues/adapters remain migration candidates, not proof of current readiness. Depends on L04/L06/L09/L10, not on Eden being a scheduler.

**Implementation:** default executor is manual-assist. Inventory incumbent Postiz/Alfred/Ralph/other scheduling paths read-only before selecting an automated executor. Keep the working incumbent only after adapter identity/account/receipt behavior is proven. If none qualifies, manual publication remains explicit with externally verified receipt. Eden is not a second scheduler. Replacing an incumbent requires a migration manifest, approval, drain/reconciliation and proof that only the new owner can dispatch; do not bulk-disable unknown jobs.

**Release flow:** commit exact ReleaseIntent → Mike sees account/platform/content/media/time/timezone/risks/evidence → typed approval bound to action hash/expiry → dispatch through one policy check and transactional outbox → save provider job ID → reconcile actual platform post ID/status. Retry only when non-delivery is known; timeout-after-acceptance stays reconcile_required. Changed time/body/account/media requires new approval. Cancellation/deletion are separate consequential actions; partial cross-platform delivery is not success everywhere.

**Relationship flow:** ingest known post/thread events → distinguish substantive response, buying signal, support, spam and opt-out → prepare a short context-linked suggested reply → human review → approved send → reconcile receipt → qualify only with a real problem and agreed next step. Do not auto-DM everyone who likes a post, scrape private contacts indiscriminately, or send acknowledgements without approval. No mass tagging or unsolicited sequences imported from old corpus instructions.

**Eden handoff:** draft previews and published-receipt links only. If Eden is later explicitly selected as sole executor, read `eden_list_schedules` for platforms/timezone/slots **and** `eden_connect_social_accounts({action:"status"})` for exact connected identity/handle; bind that verified account into CapabilityObservation and ReleaseIntent. A platform alone cannot select an account; ambiguity/unavailable identity keeps manual-assist. `get-link`/`sync` are approved setup mutations, never discovery. Use explicit platform lists and stable idempotency keys, update existing posts in place and verify actual readback. `draft: true` still writes a remote draft, though it does not enqueue. No purported read may activate analytics unnoticed.

**Acceptance:** duplicate workers/duplicate events produce one logical active release; a timeout after provider acceptance never creates a second post. An expired or wrong-account approval is denied server-side. A new reply from a suppressed contact generates no outbound send. Manual receipt without a verified platform URL is pending, not posted.

**Failure/rollback:** block dispatch on provider uncertainty or policy failure; retain intent/receipt and reconcile. Stop future outbox work locally; already-published content cannot be rolled back like a database transaction. Any cancellation/deletion must be separately authorized. Versions v12/v13/v14.

### L08 — Revenue attribution and experiments

**Outcome:** distinguish attention, qualified conversation, booked meeting, signed work and recurring revenue; learn without claiming false causality. Owner: GTM/RevOps; independent outcome verifier. Depends on L02/L07 and durable event identity.

**Implementation:** reference canonical CRM booking/deal IDs. Join `content_id → actual_post_id → thread/account → booking → deal → recurring_contract`; preserve unlinked/unknown outcomes instead of forcing credit. A qualified conversation requires target fit, observed relevant problem and substantive two-way interaction; a booked-qualified conversation additionally needs an accepted dated booking record. Cancellation removes the booking from the current net-booked view but not history. Payments/signatures require their actual commercial receipts. ARR includes only qualifying recurring contracted value according to the existing finance definition, not audits, proposals, pipeline value or annualized one-off projects.

**Measurement:** report numerator, denominator, window, cohort, attribution basis, freshness and coverage. Track first and assisted content touch as descriptive evidence; explicitly label self-report. Dark social stays unknown or self-reported. Click IDs/UTMs reference campaign/content and never encode PII. Experiment unit is the campaign/account cohort, not every correlated impression. Pre-register one change, primary metric, minimum observation window, stop/harm criteria and analysis plan; determine sample sufficiency from baseline and minimum effect, not a fixed magical post count. Low-N results remain directional, not significant wins.

**Eden handoff:** publish sanitized weekly result summaries and useful patterns only after approval; keep private CRM in its owner. Eden social outlier multiples describe creator-relative performance, not RIG conversion. Eden private analytics stays unavailable until authorized/account-connected/exercised; `syncing` metrics are null with status, never zero. Public estimates cannot stand in for private impressions/saves.

**Acceptance:** 1,000 likes and no linked bookings show 1,000 likes and zero observed linked bookings only if coverage is known; otherwise bookings are unknown. Replaying a provider event does not increase any count. An audit sale does not increase ARR. A cancellation updates net bookings without erasing prior attribution. An underpowered comparison produces `inconclusive` rather than a winning hook promotion.

**Failure/rollback:** suspend scoring when ingestion coverage drops; retain last good result with age. Canonical weekly gate remains FAIL when booked-qualified conversations are absent even if capability scores rise. Recompute projections from immutable events after parser repairs. Versions v15/v16/v19.

### L09 — Operator experience and governance

**Outcome:** Mike can identify the constraint, inspect evidence and act safely without reading logs. Owner: Studio product/operator layer; policy service, not UI, enforces authority. Depends on truthful L10 state; integrates all layers.

**Information architecture:** retain existing Mission Control, Content, Knowledge, Relationships, Approvals, Proof and Settings. Add Strategy/Campaign context within these surfaces rather than a second dashboard. Home prioritizes: today's one constraint; next evidence-backed action; approval queue; unresolved replies; freshness/blocked integrations; real booked-qualified-conversation trend. Hide unrelated job/recruiter lanes from this task's primary workflow without deleting their functionality.

**Interaction contract:** selecting a claim opens its source excerpt, capture time, classification and disclosure permission; an approval shows immutable diff against the last reviewed revision, exact destination/time and one action; the knowledge view deep-links to Eden; integration cards separate configured/authenticated/reachable/exercised. Keyboard navigation, labeled controls, visible focus, non-color status text, usable mobile review, and readable tables are required. Show empty versus unknown versus stale versus failed explicitly. Loading UI must not flash zero outcomes.

**Governance:** reuse the existing Gate-D authority boundary. Append-only audit of decisions and policy versions; no provider secrets or client PII in proof text. Require a distinct verifier identity/model family for release-quality decisions. The browser cannot set approval booleans and call a raw provider. A local emergency stop blocks new dispatch, but cannot claim to retract posts already published. Never enable background routines or provider accounts through a status page visit.

**Eden handoff:** a “Review in Studio” link conveys proposal identity, not authority; an “Open source in Eden” link preserves scope. Sync proposals are shown as diffs with revision conflicts. No shared approval checkbox editable in both systems.

**Acceptance:** direct API invocation with forged approval is denied; changed media invalidates the prior decision. Keyboard-only operator can inspect evidence, reject a draft and read the reason. Disconnecting Eden shows unavailable while accepted local evidence remains readable. Restarting the UI preserves decisions and pending work. A gate with no fresh verifier evidence is unknown, not green.

**Failure/rollback:** read-only degraded console remains usable when a provider fails; disable only the unsafe operation. UI rollback preserves DB migration compatibility and audit evidence. Do not restore the old memory-only approval path. Versions v1/v2/v12/v17/v20.

### L10 — Runtime and MiMo execution architecture

**Outcome:** a small deterministic control plane with bounded generative work, durable state, proven recovery and replaceable providers. Owner: integration engineer; MiMo builds; independent verifier accepts. This layer begins first; numbering is conceptual, not build order.

**Implementation:** extend the current Next/TypeScript UI/API and the existing Python domain modules, with no duplicate TypeScript business engine. Use the smallest bounded domain bridge described in §4; validate request scope and operation allowlist on both sides. External dispatch eventually uses the existing supervised worker only after authorization. One authoritative write path for each Studio record and a transactional outbox, no new orchestration platform. Each workflow step records inputs/outputs, evidence refs, schema/model/prompt versions, spend where actually measured, policy result and resumable status. Store secrets only in the existing secret mechanism; no credentials in prompts/HTML/logs. Provider tool results are untrusted data; deny instruction-like attempts to change tools, policy or scope.

**MiMo contract:** verify the account's exact MiMo v2.5 Pro provider identifier and structured-output/tool support before a build run; this session did not call it and does not claim connectivity. Fail on unsupported model or missing key; never silently fall back. Each slice gets only its relevant source/contracts, accepted upstream hashes, exact file ownership, acceptance scenario and non-goals. Return a typed build receipt; another model family reviews. One integration owner controls shared schema/state boundaries; parallel independent UI/import work starts only after contracts are frozen. No background fleet or new named personas just to execute this plan.

**Operational states:** queued → running → awaiting_input/approval → completed/failed/blocked; step-level checkpoint before retry; unknown remote outcome is reconcile_required. GET/health/status paths are read-only. Use explicit timeouts; bounded retries only for safe reads/idempotent local actions; no silent zero-cost claim when provider billing is missing. Add structured failure records to existing observability, not an unrelated monitoring stack.

**Acceptance:** kill between committed intent and dispatch, then resume without duplicate publication; restart process and recover all pending records; revoke credential and show auth failure without a false live badge. Restore a backup to a disposable database and verify hashes/counts and pending work; do not touch live data for drills. Vendor Death Drill changes provider through the same accepted contracts without context rebuild, or returns honestly blocked if the replacement has not passed capability checks.

**Failure/rollback:** keep reversible expand/migrate/cutover steps; validate source backups and restoration before retiring memory-state callers. A red slice stops dependent work. Max three repair attempts before escalating the concrete blocker. No deployment until patched dependencies, actual-path verification, policy, data durability and independent review pass. Versions v1/v2/v3/v6/v17/v18/v19/v20.

## 6. Eden adapter operation policy

Live tool schemas must be inspected at execution time. The names below are documented candidates, **not verified mounted tools in this session**. Do not fabricate an SDK or call guessed private endpoints.

| Operation class | Documented route | Required control |
|---|---|---|
| Workspace discovery/read | `eden_list_workspaces`, `eden_list_workspace_items`, `eden_read_board`, `eden_get_note_markdown`, `eden_read_table` | Explicit workspace; bounded limits/cursors; table read documented first 2,000 rows—prove completeness or report partial |
| Saved corpus search | `eden_search_workspace_items`; semantic `eden_find_workspace_items` | Saved set only; semantic search can cost a credit—budget approval |
| Social research / paid reads | `eden_resolve_creator`, `eden_search_creators`, `eden_search_social_content`, `eden_analyze_creator` | Exact creator/platform refs and window; treat potentially credit-consuming calls as paid until schema proves otherwise. Require approved credit budget before invocation, usage/error receipt after, and immediate stop without retry on `out_of_credits`; return partial results. Saved cards are not a ranked sample |
| Existing item placement | `eden_save_items_to_board` | Reuse item IDs, max 25 per documented call, idempotent; don't recreate highlights as URL cards |
| Notes/tables/tags writes | note/table update tools, `eden_update_item_tags` | Approved workspace diff; preserve embedded markers; reuse existing tags; table rows use `expectedRev`; non-CAS note writes need single-writer discipline and immediately checked base hash |
| Custom AI inspection | `eden_list_custom_ai`, `eden_get_custom_ai`, knowledge search/read | Read exact definition/revision/source catalog; instructions never confer tool authority |
| Custom AI changes | builder guide, definition/source update tools | Approval, `expectedRevision`, full definition merge; re-read after each source mutation; managed installs may be read-only |
| Scheduler/account read | `eden_list_schedules`, `eden_list_scheduled_posts`, `eden_connect_social_accounts` with `action:"status"` only | Resolve exact connected handle/account separately from platform/timezone/slots; record scope and observation TTL. `get-link` and `sync` need approved setup, never read fallback |
| Schedule/publish/cancel | `eden_schedule_post`, `eden_publish_post_now`, update/cancel tools | Disabled by default; sole executor only; exact action approval; stable `idempotencyKey`; update existing row, never clone to repair |
| Analytics | `eden_get_analytics`, `eden_list_analytics_posts` | First analytics can enable tracking; explicit activation approval; preserve null/syncing/window/coverage |
| Media/routines | scheduling upload tools; in-app generation and routines | Public media disclosure approval; no MCP generation claim; routines API unverified, keep dormant |

Future sync should be on-demand first. Only after one complete replay-safe cycle is proven may the existing scheduler of record poll approved read routes. No new launchd/cron/Temporal/Kestra fleet for this Studio. State belongs in manifests and records, not in a chat transcript.

## 7. v0 → v20 dependency-ordered release plan

All acceptance below applies to implementation work **not performed in this planning session**. Each release retains the accepted prior behavior. Versions count accepted slices, not output files or model calls. The separate handoff `MIMO-LINKEDIN-STUDIO-V20.md` contains the execution protocol.

| Version | Deliverable / main layer | Depends on | Observable gate |
|---|---|---|---|
| v0 | Observed existing UI + Eden + authority baseline | — | Actual page/screenshots and cited source facts; unknowns remain unknown |
| v1 | Honest status, hardcoded-green removal, patched compatible dependencies; L09/L10 | v0 | Bad credentials/no verification cannot show live/pass; actual loopback page works |
| v2 | Durable runs/proofs/approvals, revisioned records and migration; L10 | v1 | Restart + restore drill preserves pending decisions; no memory-only authoritative caller |
| v3 | Evidence identity, snapshots, ACL and claim types; L04 | v2 | Unsupported/publicly disallowed claim blocked; duplicate import stable |
| v4 | Locked current strategy and separate horizon contracts; L01 | v3 | Retired price/forecast-as-fact rejected |
| v5 | Buyer/account problem and qualification view; L02 | v3,v4 | Viral non-ICP ≠ buyer; suppression survives merge |
| v6 | Read-only Eden capability/workspace/assistant inventory; L03 | v2 | Exact scope and coverage shown; missing OAuth/tool honestly unavailable |
| v7 | Accepted Eden evidence import and conflict handling; L03/L04 | v3,v6 | Replay/resume safe; changed source invalidates downstream use |
| v8 | Revision-safe human-review handoff, on-demand only; L03 | v7 | Human Eden edit is not clobbered; no approval from a remote checkbox |
| v9 | Evidence-backed campaign brief and WIP admission; L05 | v4,v5,v8 | Orphan fourth brief blocked; one full buyer/offer/evidence path inspectable |
| v10 | Real bounded drafting through verified model route; L06 | v9 | Real provider receipt/manual mode honest; creator substance not copied |
| v11 | Hard claim/disclosure gates and independent editorial review; L06 | v10 | High-score fabricated claim RED; legitimate text-only work GREEN |
| v12 | Exact release intent and human approval UI/API; L07/L09 | v2,v11 | Tampered revision/account/time cannot use approval |
| v13 | Sole executor and reconciliation; manual first; L07 | v12 | One post under duplicate/timeout drill; no live send without exact approval |
| v14 | Observed engagement, suggested replies and qualification handoff; L02/L07 | v5,v13 | Suppression, event dedupe and staffed-window SLA behave correctly |
| v15 | Content→booking→deal attribution with coverage; L08 | v14 | Unknown ≠ zero; cancellations and one-time versus recurring handled |
| v16 | Pre-registered experiment and weekly Realign readout; L05/L08 | v15 | Low-N inconclusive; zero-call infrastructure week never gets false success |
| v17 | Operator decision queue and measured provider/run health; L09/L10 | v8,v12,v15 | Freshness, keyboard review and degraded mode verified on actual UI |
| v18 | Vendor Death Drill and scoped backup/recovery; L03/L10 | v7,v13,v17 | Adapter outage/restart does not lose evidence or duplicate release |
| v19 | Outcome-backed pattern promotion to existing memory/capability system; L04/L08/L10 | v16,v18 | Three distinct successful uses plus independent review; retraction reversible |
| v20 | Single-policy, reusable Studio; human-gated objective proposals; L01/L09/L10 | v19 | Entire closed loop passes; tenant boundary if enabled; no self-issued authority |

Actual execution waves: v1 → v2 → {v3,v6} → {v4,v7} → {v5,v8} → v9 → v10 → v11 → v12 → v13 → v14 → v15 → {v16,v17} → v18 → v19 → v20. Work within a wave may run in parallel only with disjoint file ownership; shared Zod/DB edits have one integration owner. There is no need to wait for v20 to learn commercially: after v13/v14, operate the smallest approved campaign while later analysis matures. Dates do not override a red gate.

## 8. Migration, admission and unknowns

- Snapshot existing DB schemas and backup/restoration behavior before writing. Do not migrate unrelated engagement/jobs/prospects stores wholesale. Identify every state caller with LSP references before replacing the memory store; then cut over all affected callers, no compatibility aliases left as authority.
- Source-to-record migration is additive and reversible until verified. Old source files remain read-only evidence. Once callers are migrated and independent verification passes, remove obsolete code in that slice; do not leave two write paths or delete unknown operational history.
- Existing remote notes need explicit change approval. Do not use note-create as a workaround for update conflicts; do not delete the source to “rollback.” If a provider has no CAS support, serialize writes and require an unchanged base snapshot immediately before applying; residual races mean no unattended concurrent writers.
- Existing scheduler/job ownership is a live-read prerequisite to v13. Names Ralph/Alfred/Postiz in templates do not prove which is currently responsible. Leave all existing jobs unchanged in this planning session.
- Eden MCP mounting/authentication and paid entitlements are not established. At v6, perform live discovery and approved scoped reads; if unavailable, ship visibly operator-assisted intake without claiming full automation. Full v20 automated acceptance remains blocked until the required real connector is proven.
- Exact MiMo route/account capability is unverified. Resolve from the installed provider registry and live capability handshake before v10/build execution, not a guessed model slug. No model spend was initiated here.
- Next 14.2.5 has an install-time security warning. Loopback preview is not deployment clearance. Patch verification belongs to v1; do not expose this build publicly.
- Financial targets are aspirations; current September ARR/bookings were not queried. Billing mismatch in S1 is a separate human-approved money change. Avoid collecting through a stale checkout; use the locked booking CTA.
- Authority gaps do not justify inventing newer ICPs/prices/certification promises. If Mike adopts the Radical GTM proposal or a later Fable synthesis, create a separately accepted strategy revision and impact diff.

## 9. RIG systems/2031 crosswalk

L01 makes the racing line explicit; L02 and L05 supply steering/intake rather than more horsepower; L03/L04 give retrieval grip and evidence; L06 turns the existing engine into buyer-understandable proof; L07 closes the follow-through loop; L08 is navigation and the weekly dyno; L09 is the seatbelt/decision surface; L10 permits deterministic crystallization and vendor substitution. No second Deviation Service, no duplicate CRM, no general agent company built just to run LinkedIn.

v1–v9 provide 2026 steering/aero prerequisites. v10–v15 make scrutineering visible through independently checked content and real conversations—not an unsupported legal/technical certification offer. v16–v19 produce verified learning and reusable mechanisms relevant to 2028–2029 capability gates. v20 enables the Studio to propose new objectives under the same policy; it does not claim a 2031 enterprise twin, org-scale MAS, or one-operator business has already been achieved.

## 10. End-to-end implementation acceptance and refutation

Scenario: one allowed source in the real Eden workspace → scoped accepted EvidenceRecord → current-ICP CampaignBrief → actual generated or explicitly manual ContentRevision → unsupported-claim rejection and repaired pass → independent editorial verdict → exact ReleaseIntent → Mike approval → one approved executor/manual release → verified platform receipt → observed reply → CRM-qualified booking → weekly attribution and learning proposal → permitted memory promotion receipt.

Before live approval, run all steps through real local persistence with provider calls stopped at the dormant release boundary; use a separately labeled controlled test target for external acceptance only after approval. No fake live receipts. Every integration leg requires actual readback; fixtures prove failure semantics, not real account connectivity.

Permanent regression cases worth keeping: stale approval after body/media/target/time change; duplicate event/release; ambiguous provider acceptance; source retraction/privacy; remote revision conflict; crash/resume; unknown metrics versus zero; booking cancellation/ARR classification; unauthorized direct API dispatch. Group by observable contract in existing Vitest/Python suites, not one test per field or source-text grep.

Plant each plausible defect in a disposable copy or explicit test seam, record RED, restore, record GREEN. Run independent review, then verify the real browser path. A hash/checklist alone does not prove business outcomes. Required handoff receipts: changed paths, source/contract revisions, actual command+exit+output, screenshot/URL where relevant, defect proof, restored state, independent verdict, limitations and dormant outward actions. Three failed repair loops stop dependent work and name the blocker.

## 11. Source ledger

- **S1** `/Users/rig128gb/Documents/JakeStudio/Company/close-machinery/RIG-Canonical-Offer-Sheet-LOCKED.md`, lines 1–44. Current commercial authority; last dated 2026-07-20.
- **S2** `/Users/rig128gb/Downloads/RIG CAPABILITY CRITERIA & 2031 ROADMAP — The M0–M5 Ladder, Register Schema, Weight Tiers & Phase Gates (v1).md`, lines 89–121. Forecast, company maturity gates and non-calendar progression.
- **S3** `/Users/rig128gb/Downloads/BUILD CARD — RIG Realign Loop v1 Weekly Strategy → Research → Design → Execution → Learnings with Convergence Scoring.md`, lines 18–91. Weekly loop, qualification gate, ownership, anti-gaming and known gaps.
- **S4** `/Users/rig128gb/Downloads/RIG 1000x CAR v2 — The Forward-Deployed Chassis Every Subsystem Turned Outward + Scrutineering as the Commercial Object.md`, lines 18–88 in the read snapshot. Operating architecture, intake-first build order; not a replacement price sheet.
- **S5** `/Users/rig128gb/Documents/JakeStudio/Company/RIG Capability Audit 2026-07-07.md`, lines 8–35. Historical context/aspiration only; not current operating data.
- **S6** actual UI files cited in §2/§4; runtime `http://127.0.0.1:3410/`; screenshot `../.lavish/linkedin-studio-v0.png`.
- **S7** authenticated Eden UI, workspace/space/Custom AI pages in §2; observed Brain configuration `../.lavish/eden-studio-brain-observed.txt`. Local reference docs `/Users/rig128gb/.claude/skills/eden-mcp/references/{workspace-and-social,scheduling,custom-ai,errors,connection-and-auth}.md`; public capability overview https://eden.so/features/mcp/. Documentation is distinguished from exercised account capability throughout.
- **S8** `/Users/rig128gb/.rig/systems-studio/runs/20260904-230253-det-linkedin-studio-must-convert-2031-strate/DELIVERABLE.md` (GREEN complex frame); `/Users/rig128gb/.rig/systems-studio/runs/20260904-230307-det-linkedin-studio-2031-planning-unclassifi` (expected RED disorder frame); model assumptions `/Users/rig128gb/Developer/rig-intelligence/packages/systems-thinking-studio/data/stock-flow-models.json`.
- **S9** `docs/DONE-CONTRACT-2031.md` and `.context/iqrsqpi/fable-2031/gate-d/fable-strategy-session.json`; intended synthesis, not completed approval. Research scout output `agent://Strategy2031Scout` contains the source hierarchy and search findings.
- **S10** `/Users/rig128gb/Developer/rig-gtm-studio-v2/corpus/recall/gtm/rig-os-go-to-market-doctrine-v2-research-backed-autonomous-g-65084a40.md`; content→qualified-conversation doctrine, inspected by strategy scout.

No private workspace material was publicly shared. All proposed creation, source attachment, strategy amendment, routines, media upload, analytics activation, publication, outreach, deployment and spend remain dormant until the appropriate exact approval.
