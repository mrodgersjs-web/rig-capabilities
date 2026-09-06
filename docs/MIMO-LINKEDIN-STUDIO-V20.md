# MiMo v2.5 Pro — LinkedIn Studio v0 → v20 execution packet

Status: READY FOR BUILD REVIEW; NOT AUTHORIZATION TO EXECUTE OUTWARD ACTIONS. Companion specification: `LINKEDIN-STUDIO-V20-EDEN-2031.md` in this directory. Read it before implementation. This packet is self-contained enough to select the next slice; the specification supplies source authority, shared field contracts and all ten layer acceptance cases.

## 1. Mission, scope and authority

Build the existing LinkedIn editorial Studio into a source-grounded, human-approved, buyer-conversation operating system. Use the existing populated Eden workspace. Preserve one publisher, one commercial truth owner, one approval authority. Correct v0's simulated execution and false readiness before adding features.

- Plan repository: `/Users/rig128gb/Developer/rig-capabilities`.
- Actual UI (`UI/`): `/Users/rig128gb/Desktop/rig-linkedin-studio/end-studio-v10`.
- Domain repository (`ROOT/`): `/Users/rig128gb/Desktop/rig-linkedin-studio`.
- Corpus/commercial reuse candidate (`GTM/`): `/Users/rig128gb/Developer/rig-gtm-studio-v2`.
- Eden: `rodgemd1-s-workspace`; known **space**, not workspace ID: `e4dcb178-f056-4238-a440-e2ec03d27997`.
- Do not edit Traject's `cockpit-v2`, turn this into a job-search app, start root startup scripts, create an assistant fleet, add a new scheduler, change prices/Stripe, publish/send/upload media, enable analytics, mutate Eden, deploy or push without exact applicable approval.
- Current commercial source: `/Users/rig128gb/Documents/JakeStudio/Company/close-machinery/RIG-Canonical-Offer-Sheet-LOCKED.md`. Audit $7,500; optional Blueprint $10K; implementation $25–50K; managed $5–10K/month. HED $40K is a separate procurement case. No Fable synthesis is verified complete; 2031 is a source-labeled forecast.

The planning session installed only the existing UI lockfile dependencies and launched a local preview. It did not implement any slice below. Never use this packet's existence as evidence that v1–v20 passed.

## 2. Provider and workspace preflight

Resolve the exact installed MiMo v2.5 Pro model route from the live harness/provider registry, then verify authenticated availability, structured-output schema support and the required tool behavior using an approved bounded request. The route is not established in this packet. Missing model/key/tool support means BLOCKED with the exact prerequisite; no silent substitution. Do not print credentials.

Confirm repository identity and the current worktree's user changes once at session entry. Prior scout saw moving/conflicting branch observations, so there is no frozen commit hash here. Use the existing Orca-managed lane if applicable; do not invent raw worktrees around an unknown `.git` pointer. Preserve unrelated work. Read applicable repository guidance. Use LSP references before modifying exported symbols; identify every caller before replacing state or contracts.

Eden's documented tool surface is not this account's verified tool inventory. At v6, discover mounted tools, read schemas and resolve explicit workspace/account IDs. Do not call `eden_get_analytics` during discovery: it can activate tracking. Read-only catalog/definition retrieval is separate from creating sources, saving drafts, research-credit spending or scheduling.

## 3. Frozen shared architecture

Keep Next as UI plus thin API boundary; reuse verified aggregate-specific Python contracts, not blanket legacy authority. `storage.py` owns campaign file access; `campaign_ledger.py` engineering-turn history; `approval_queue.py` Atlas request history only. Evidence/proof/analytics are slice-level reuse candidates. ReleaseIntent/outbox owns missing transactional release state; only the executor verified at v13 dispatches. `publishing/publisher.py` currently ignores scheduling/media inputs and calls a browser publisher, returning a local ID/boolean and local DB status; it is not production receipt proof. `UI/src/lib/schemas.ts` owns the Zod wire vocabulary, not a second publishing engine. Use Python stdlib SQLite for missing Studio records/outbox. CRM, memory and capability register are referenced, not copied.

Inspect/reuse these exact seams before writing adjacent code:

| Existing seam | Responsibility / required change |
|---|---|
| `UI/src/lib/integrations.ts`, `agents.ts`, `gates.ts`; `app/api/{integrations,health}/route.ts` | Remove environment-presence “live” and hardcoded “pass”; expose timestamped capability evidence |
| `UI/src/lib/schemas.ts`, `ids.ts` | Versioned wire contracts; canonical full action hash, revisions, explicit states, provenance; inspect current short-hash behavior before using for authority |
| `UI/src/lib/store.ts` | Replace volatile authoritative arrays after all callers are mapped; durable projection only |
| `UI/src/lib/engine.ts`, `workflows.ts`; `app/api/workflows/[id]/run/route.ts` | Replace simulated state walking with bounded domain calls; simulated runs remain unmistakably simulations, never proof |
| `UI/app/api/approvals/route.ts`, `src/lib/engine.ts` | Server-side identity/policy validation; exact action-hash approval; no request-controlled approver authority |
| `UI/app/api/proof/route.ts`, `src/lib/terminal.ts` | Real receipt/evidence rendering; label command emulator honestly or remove only obsolete misleading commands |
| `ROOT/rig_linkedin_studio/storage.py` | Existing campaign filesystem paths and source access, not transactional approval storage |
| `ROOT/rig_linkedin_studio/campaign_ledger.py` | Engineering-turn ledger at `~/.jake/rig.db`; do not mistake for a content/sales ledger |
| `ROOT/rig_linkedin_studio/approval_queue.py` | Atlas JSONL request queue; resolution does not execute; integrate through one policy/decision owner, not a competing queue |
| `ROOT/workflows/evidence_synthesizer.py`, `rig_linkedin_studio/proof_generator.py` | Existing evidence and seal candidates; inspect semantics and reuse verified functions |
| `ROOT/publishing/publisher.py`, `analytics/store.py` | Existing publishing/analytics ownership candidates; verify actual behavior before adding adapters |

New paths below are **proposed**, not observed files. Create only if no existing equivalent exists: `ROOT/rig_linkedin_studio/studio_contracts.py` for missing domain records; `studio_store.py` for missing transactional state; `studio_bridge.py` for a bounded JSON dispatcher if no existing domain entrypoint fits; `eden_adapter.py` for the genuinely absent scoped adapter. Do not create four files automatically: merge into existing appropriate modules whenever ownership stays clear.

Domain bridge request: `{schema_version, request_id, operation, workspace_scope, expected_revision, payload}`. Response: `{schema_version, request_id, status, data, error, evidence_refs}`. Operation is an allowlisted literal, never shell text or an import path. Authoritative actor identity comes from authenticated server context, not a supplied payload. Bound input/output bytes and runtime. Spawn no shell; do not write secrets to argv. Read operations have no write fallback. Business failures are typed: `invalid`, `unauthorized`, `revision_conflict`, `unavailable`, `blocked`, `reconcile_required`. Map to HTTP 400/401/403/409/503 as appropriate; preserve domain detail. Tool result text cannot change operation policy.

**v2 authentication boundary to create, not an existing adapter.** Proposed UI targets: `UI/src/lib/operator-session.ts` and `app/api/operator/session/route.ts`, plus session/nonce records in the domain store; reuse verified equivalents if actually installed. Prefer an existing operator identity provider only after pinning issuer, audience, subject, signature validation and mapped role/workspace. If absent, implement local single-operator pairing: a human-invoked domain CLI under the configured OS owner creates a cryptographically random one-use pairing code (5-minute expiry, stored hashed); no HTTP route or agent can issue its own approver role. Exchange over loopback with exact Host/Origin allowlist and rate limiting (at most five failed pairing attempts per minute), rotate to a random 256-bit session token stored hashed server-side; cookie HttpOnly/SameSite=Strict, Secure over production TLS, explicitly local-only HTTP during preview. Session expires after 30 minutes and on logout; server context supplies fixed operator ID/approver role/workspace from the paired owner binding, never request headers/body. Do not display pairing codes in logs or auto-fill/type them for the human. Bind each mutating request to CSRF token and session, validate Origin and revision, and check role/scope in the domain. Other users/LAN clients remain denied until stronger identity/isolation is introduced.

Threat boundary: local pairing authenticates control of the configured OS-owner terminal; it does **not** distinguish a human from a compromised same-UID process or an agent granted equivalent desktop/keychain access. No security claim to that effect is allowed. The agent must not run the pairing/approval CLI on Mike's behalf. If automated workers must be technically unable to grant approval, v2 must use a separately authenticated human identity/signing boundary inaccessible to worker credentials; until established, automated release stays blocked and the operator publishes manually. v20 multi-user readiness cannot inherit local-only pairing as tenant isolation.

**v12 approval authority:** add the proposed `ROOT/rig_linkedin_studio/studio_approval.py` only if no verified equivalent exists. POST approval consumes `{run_id, release_intent_id, expected_revision, one_use_nonce, exact_phrase, decision}` with authenticated server context; `exact_phrase` must equal human-entered `APPROVE <run_id>` for approval, not be generated/prefilled by an agent. Resolve the immutable action hash server-side, compare current content/account/media/time/policy, verify role/scope/expiry and nonce, then atomically consume nonce and record the hash-bound decision. Exact replay returns the existing receipt without another decision; altered replay is 409. Rejections never execute. The UI's current unauthenticated route is removed as an authority after callers migrate. The mounted `gate_d_check({request_id})` is documented pending-request inventory only, not a verification endpoint; no authenticated accepted-decision backend has been verified. If an existing canonical Gate-D backend is later proven, prefer it through an explicit one-authority cutover; do not dual-write approvals. Local operator authentication does not prove human intent by itself: the exact point-of-risk confirmation remains mandatory, and no background worker may issue it.

**Paid reads:** saved-corpus semantic search and social research may consume Eden credits. v6 makes no paid calls. Later slices require an explicit approved research budget before the first credit-consuming call, preserve actual usage/error receipts, and stop immediately without retry on `out_of_credits`, returning collected partial evidence. Unknown cost is not free. Do not use public research as an unapproved paid fallback for unavailable analytics.

Schema evolution is additive until all callers migrate. After verified cutover, remove obsolete write paths. Use shared JSON boundary fixtures to keep Python/TypeScript semantics aligned without maintaining duplicate business rules. SQLite transactions bind intent/outbox; uniqueness prevents duplicate logical releases, but network delivery still needs reconciliation. No exactly-once marketing claim.

## 4. Twenty slice cards

Each card inherits the full corresponding layer's acceptance/failure conditions. “Existing targets” are starting locators, not permission to ignore other callers revealed by LSP. “Acceptance” is behavior, not source-text assertions. Do not broaden a slice into unrelated refactoring.

### v1 — Truth before features
- Depends on v0. Layers L09/L10.
- Existing targets: integrations/agents/gates/health/terminal, current status components and pages, package manifest+lock.
- Change: separate configured/authenticated/reachable/exercised; attach observation time, evidence and unknown reason. Remove hardcoded green and fictional terminal-ledger claims. Label every simulated workflow/proof. Keep liveness separate from readiness. Upgrade to a current patched compatible Next release from vendor guidance; no major migration just to modernize.
- Acceptance: missing/invalid credentials never show exercised/live; a gate with no verifier evidence never passes; GET health does not trigger provider activation. Loopback Mission Control loads using the patched lock. Report unverified provider calls rather than inventing tests proving availability.
- Rollback: restore UI/package changes if upgrade fails; never reintroduce false production status as a fallback. Outward actions remain disabled.

### v2 — Durable control state
- Depends on v1. L10.
- Targets: store, engine, schemas, approval/proof APIs; verified Python ownership candidates; proposed operator-session/session API and domain session records in §3.
- Change: identity/scope-bound durable runs, proofs, decisions and events, schema migration version, atomic local transactions, bounded JSON bridge, and authenticated server actor context. Map all callers, migrate, remove memory authority.
- Acceptance: create a dormant run and pending decision, restart, read the same IDs/content; replay request yields one record. Restore disposable backup and compare records/hashes. Forged owner, unpaired/expired session, wrong workspace, bad Origin/CSRF and replayed pairing code are denied. No proof path exists only as a string.
- Rollback: reversible migration into a disposable copy first; validated backup; do not delete user history or turn JSONL and SQLite into dual authorities.

### v3 — Evidence identities
- Depends on v2. L04.
- Targets: existing evidence synthesizer/proof generator, schemas/domain records, Knowledge view.
- Change: source locators/revisions, hashes, claim type, excerpt, ACL/disclosure, expiry/retraction and source lineage. Distinguish source evidence from verification proof.
- Acceptance: fabricated number and private-only fact blocked; source replacement creates a new revision; repeated import does not duplicate; null URL remains explicitly missing.
- Rollback: invalidate imported mapping, retain source and history.

### v4 — Current strategy versus forecast
- Depends on v3. L01.
- Targets: schemas/domain store, existing acquisition/personal-brand workflow inputs, Strategy/Settings view.
- Change: import source-linked current offer, ICP, CTA and separate horizon record; strategy conflict queue and revision impact graph. Price renderers use current offer IDs.
- Acceptance: retired price and 2031 capability-as-current-claim RED; S1-correct claim GREEN; change causes draft review, not historical rewrite.
- Rollback: explicitly restore last accepted contract; no payment-system mutation.

### v5 — Buyer problem intelligence
- Depends on v3,v4. L02.
- Targets: existing relationship/client surface and GTM identifier mapping.
- Change: explainable account/person/creator distinctions, sourced problem triggers, qualification state, signal freshness and suppression references.
- Acceptance: popular creator is not a qualified buyer; stale signal visible; ambiguous identity unresolved; opt-out survives dedupe/merge.
- Rollback: revert cohort proposal, leave CRM source untouched.

### v6 — Actual Eden discovery
- Depends on v2. L03.
- Targets: integrations/settings/knowledge; new Eden adapter only after confirming absence.
- Change: inspect live tool schemas; explicit workspace resolution; paginated boards/items/tags/AIs inventory, capability/entitlement status and source counts. Bind existing GTM space and selected assistants by verified IDs. Read `eden_connect_social_accounts({action:"status"})` for exact connected handles/account identity, separately from `eden_list_schedules` platform/timezone data; store provenance/TTL. Never use `get-link` or `sync` as a read fallback.
- Acceptance: unavailable tools/auth are honest; unknown workspace never defaults elsewhere; catalog page count/partial coverage visible. No content/analytics/schedule/account write or paid research call occurs.
- Rollback: remove local connection mapping; do not disconnect another user's account or delete assistants.

### v7 — Source-preserving Eden import
- Depends on v3,v6. L03/L04.
- Targets: Eden adapter, evidence owner, import cursor/manifests, Knowledge view.
- Change: selective previewed import with base/accepted hashes, source ACL and scoped IDs; preserve notes/tables/Recall IDs rather than flattening everything into a text blob.
- Acceptance: interruption resumes; repeated import stable; changed/retracted source invalidates relevant pending claims; first-2,000-row limit cannot masquerade as complete table ingestion.
- Rollback: supersede local evidence import; never delete/rewrite originals.

### v8 — Eden ↔ Studio review handoff
- Depends on v7. L03.
- Targets: manifest/conflict records, existing content/knowledge APIs, Eden adapter.
- Change: on-demand proposed draft/campaign diff, approved remote write path, stable remote row/item refs and revision guards. Stage and inspect until exact workspace mutation approval exists.
- Acceptance: concurrent human edit raises conflict; table embedded markers survive; remote approval/revenue fields cannot confer RIG authority. Exact approved write is read back; without approval record blocked, not complete automated sync.
- Rollback: local proposal cancellation; any remote reversal requires its own approved diff.

### v9 — Campaign admission
- Depends on v4,v5,v8. L05.
- Targets: existing workflow/Content pages, campaign domain owner.
- Change: one primary ICP/problem per weekly plan; initially ≤3 active briefs; evidence/offer/response hypothesis/kill criteria. Add contextual strategy and Eden links in existing shell.
- Acceptance: no-source/no-strategy draft rejected; fourth brief blocked; killed campaign retains reason; current brief traverses to sources and offers.
- Rollback: supersede plan; do not auto-fill calendar gaps.

### v10 — Real bounded drafting
- Depends on v9 and verified model preflight. L06.
- Targets: engine's dry-run branches, existing drafting/quality functions, model integration.
- Change: actual schema-validated model call with source packet and prompt/model version; maximum three candidates initially. Explicit manual and simulation modes; no silent fallback. Preserve real source-pattern attribution.
- Acceptance: actual provider invocation receipt, or honest blocked status; no fabricated customer/Mike experience; malformed output fails; draft remains local/unpublished.
- Rollback: preserve last accepted revision and disclose provider failure.

### v11 — Independent content gates
- Depends on v10. L04/L06.
- Targets: quality/evidence/proof domain owners and approval-ready display.
- Change: claim/disclosure hard gates, editorial relevance/voice/originality judgment, media validation/alt text. Reuse existing Deviation Service, no copied rubric engine. Verdict binds exact draft/asset hashes and distinct verifier identity.
- Acceptance: polished false claim fails; factual text-only content can pass; content mutation invalidates verdict; self-review cannot sign independent approval.
- Rollback: leave draft unapproved; three failed repair cycles escalate exact defect.

### v12 — Exact approval contract
- Depends on v2,v11. L07/L09.
- Targets: approval/run APIs, schemas, v2 operator session boundary, proposed domain approval authority specified in §3, review page. No existing authenticated Gate-D adapter is assumed.
- Change: dormant ReleaseIntent with content/media/platform/account/time/timezone/action hash and expiry. Typed approval and authenticated actor; policy check on the server. No dispatch yet.
- Acceptance: direct unauthorized API, bad Origin/CSRF, expired approval, nonce reuse with changed payload and tampered content/time/account/media denied; exact idempotent replay returns the same receipt without execution; rejection persists; keyboard review works.
- Rollback: revoke intent; no claim of undoing an external action.

### v13 — One executor with reconciliation
- Depends on v12. L07.
- Targets: existing publisher, release outbox, receipt/status view.
- Change: read-only inventory incumbent schedulers and select sole executor only after account/receipt/drain/dispatch proof; manual-assist until proven. Atomic claim/dispatch, provider job ID and actual post ID, reconciliation on ambiguous delivery. Eden is disabled unless explicitly selected through approved cutover; refresh `eden_connect_social_accounts` action `status`, bind exact account identity and deny when identity is unavailable or mismatched. Connecting (`get-link`/`sync`) is separate approved setup.
- Acceptance: duplicate worker and timeout-after-acceptance cases yield one logical release and no blind resend. Test doubles prove failure paths only. One live test on approved destination is required for actual provider readiness; otherwise gate remains blocked.
- Rollback: stop new dispatch; reconcile existing jobs; cancel/delete only under separate approval.

### v14 — Human-accountable engagement
- Depends on v5,v13. L02/L07.
- Targets: incumbent engagement/relationship owners and Studio projection.
- Change: ingest deduped thread events with occurred/observed timestamps; staffed reply windows, suggested replies, qualification reason and suppression. Approved sends only.
- Acceptance: duplicate events do not inflate thread count; opt-out blocks sends; no bulk DM from likes; stale observation cannot pretend SLA success; receipt closes suggestion.
- Rollback: freeze new suggestions/sends, retain events and reconciliation queue.

### v15 — Commercial attribution
- Depends on v14. L08.
- Targets: existing analytics store and CRM read contracts, dashboard projections.
- Change: content/post/thread/booking/deal links, numerator/denominator/coverage/age, cancellation, source/assisted/self-report attribution and one-off versus recurring amount semantics.
- Acceptance: unknown not zero; dedupe; cancelled booking correct; audit sale not ARR; unsupported causal inference not presented as lift.
- Rollback: rebuild read projections from immutable events; source commercial records unchanged.

### v16 — Weekly experiments and Realign
- Depends on v15. L05/L08.
- Targets: weekly review/experiments, existing capability register/verdict adapter.
- Change: pre-registration, cohort/time window, minimum effect/sample reasoning, harm/stop rule; fetch rather than duplicate C_t/A_t. Useful information may persist even when strict weekly gate FAILS.
- Acceptance: low-N inconclusive; zero bookings cannot pass because infrastructure score rose; missing denominator/MAD=0 blocks; kill criteria visible.
- Rollback: suspend experiment; preserve prior evidence and labels.

### v17 — Operator decision and health surface
- Depends on v8,v12,v15. L09/L10.
- Targets: existing page shell, Mission Control, provider/run status, approvals/proof.
- Change: constraint-first home and action queue; source/diff inspection; measured health/freshness; empty/unknown/stale/failed distinctions; keyboard/mobile review. Do not add another cockpit.
- Acceptance: actual desktop/mobile browser path, keyboard evidence review/rejection, disconnected Eden and provider degradation readable; no fake zero flash.
- Rollback: UI-only revert compatible with durable state; do not restore false badges.

### v18 — Recoverability and Vendor Death Drill
- Depends on v7,v13,v17. L03/L10.
- Targets: bridge/provider policy, existing recovery utilities, store/manifest/outbox.
- Change: disposable DB restore; process interruption before/after outbox commit; credential expiry; replacement provider under unchanged contracts. No live node/scheduler destructive drill.
- Acceptance: recovery preserves IDs/revisions/pending decisions, no duplicate release; replacement must pass capability handshake or honestly block; no context rebuilt from memory alone.
- Rollback: restore verified backup in controlled scope; never overwrite live state with an unverified snapshot.

### v19 — Outcome-backed reuse
- Depends on v16,v18. L04/L08/L10.
- Targets: existing memory/capability promotion workflow and Studio review projection.
- Change: mechanism candidates require three distinct successful uses, provenance, outcome quality and independent promotion; preserve counterexamples. Prefer deterministic function only when behavior truly repeats.
- Acceptance: three copies of one success fail; unsourced high-scoring pattern fails; genuine qualified evidence can promote with a real sink receipt; later retraction propagates.
- Rollback: deprecate/promote correction through memory owner, never silently erase history.

### v20 — Reusable, policy-bound Studio
- Depends on v19. L01/L09/L10.
- Targets: existing policy boundaries, context packaging and closed-loop acceptance.
- Change: reusable scoped campaign template, explicit external account bindings, Mike-gated objective proposals; no new goal or tool authority self-issued by assistants. Enable multi-user/tenant operation only if required by the adopted scope and isolation is proven.
- Acceptance: entire source→brief→draft→gate→approved release→receipt→conversation→booking→learning path; cross-account access denied; missing actual connector prevents claiming automated v20. All ten layers covered; no duplicate owners/schedulers, no stale compatibility authority, no forged proof.
- Rollback: disable new goal admission and dispatch while preserving readable state; separately approve any external remediation.

## 5. Dependency waves and ownership

`v1 → v2 → {v3,v6} → {v4,v7} → {v5,v8} → v9 → v10 → v11 → v12 → v13 → v14 → v15 → {v16,v17} → v18 → v19 → v20`

One integration owner owns shared schema/DB/bridge changes. Do not let parallel agents both edit `schemas.ts`, migrations, store or policy. After those contracts freeze, independent provider-read/UI/detail slices can run in disjoint lanes and return patches. Parallel workers skip formatters, linters and project-wide tests mid-flight; integration owner runs validation once against the merged real tree. No worker can accept its own release gate. If shared mutation cannot be isolated, serialize it rather than invent an abstraction.

## 6. Verification and receipt protocol

At slice start, name the consumer-visible contract and a plausible defect that would violate it. Read the current test runner/config and reuse existing suites. UI verification is the actual page at loopback; provider verification needs authenticated readback; mock success never proves connectivity. Keep only meaningful boundary/regression tests, not field-copy, wording or wiring assertions.

At slice end:
1. Run the specific changed-path scenario, relevant existing tests and required build/type validation in the integration owner after edits settle.
2. Plant the named defect in a disposable copy/test seam, capture RED, restore, capture GREEN. Keep the behavior regression, not the mutation in production source.
3. Independent other-family reviewer inspects actual source/output and attempts the failure path. Maximum three repair loops, then concrete blocker; never keep generating a similar failed shape indefinitely.
4. Verify the actual UI/CLI/provider boundary after final correction. Read proof artifacts and hashes, not a claimed file path.
5. Update slice receipt and unresolved/outward dormant actions. Commit only the coherent accepted slice when authorized by the working session; no automatic push/deploy.

Proposed machine receipt (all values real; no placeholder completion packet):

```json
{
  "schema_version": 1,
  "slice": "v1",
  "status": "blocked|verified",
  "base_revision": "actual checkout revision",
  "changed_paths": [],
  "contract_hashes": {},
  "checks": [{"command": "actual command", "exit_code": 0, "output_path": "existing artifact"}],
  "refutation": {"defect": "named observable defect", "red_receipt": "existing artifact", "green_receipt": "existing artifact"},
  "actual_path": {"url_or_command": "actual exercised boundary", "evidence_path": "existing artifact"},
  "verifier": {"model_family": "different from MiMo", "verdict": "verified|feedback|blocked", "receipt": "existing artifact"},
  "outward_actions": {"state": "dormant", "pending_exact_approvals": []},
  "limitations": []
}
```

This is a schema illustration, not a submitted success receipt. If any required field has no evidence, status must remain blocked. Store receipts in the repository's existing proof/run convention discovered at preflight, not a second agent-memory silo.

## 7. First prompt to give MiMo

> Read `docs/LINKEDIN-STUDIO-V20-EDEN-2031.md` and this handoff from `/Users/rig128gb/Developer/rig-capabilities`. Implement **v1 only** in `/Users/rig128gb/Desktop/rig-linkedin-studio/end-studio-v10`; preserve existing user edits and identify current checkout first. Inspect the exact status/gate/health/terminal callers and package lock. Correct env-presence liveness, hardcoded green, simulated proof labels and the vulnerable Next dependency using the smallest compatible patch. Do not run root startup scripts, publish/send/schedule, modify Eden, enable tracking, change offers, deploy or push. Reuse current Zod/UI patterns, no new business engine. Run actual loopback UI plus meaningful regression checks after edits settle; prove a false-readiness defect fails, restore, and request independent other-family verification. Return the real receipt format in §6. If provider/model/version information is unavailable, state the precise blocker instead of inventing a fallback. Do not claim v2–v20 are implemented. Continue only through the next accepted dependency slice when the supervising session admits it.

## 8. Safe preview operations

Existing planning preview runs as supervised service `linkedin-studio-plan-preview` on `127.0.0.1:3410`. Inspect its status before starting another copy. The preview's original Next 14.2.5 remains security-warning affected until v1; no public host binding. Use only the locked local binary, not `npm exec` when `node_modules` is absent (it may offer an unpinned latest version).

From the UI directory, the explicit passive command is:

```sh
./node_modules/.bin/next dev -p 3410 -H 127.0.0.1
```

Services must use the harness's supervised service manager. Do not use `ROOT/start.sh`, `ROOT/run.sh`, a cron, or a tray app. Stop only the service you started. Opening a page is not approval to click Run, approve, send or publish.
