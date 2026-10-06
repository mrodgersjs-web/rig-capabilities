# Website evidence contract v2

Schema id: `rig.site-evidence.v2`. This is an acceptance repair candidate, not a certified site or a new harness. The canonical implementation lives in `jev-site-gate/scripts/`; the client capability delegates to it. Install both existing capabilities together only after outcome and independent review gates permit promotion. Coordinate any production `_tools` propagation with its current writer.

## Shadow checks without workspace writes

Use `python3 capabilities/skills/jev-site-gate/scripts/gate.py <slug> --root <input-workspace> --verifier-key <authorized-public-key> --dry-run` for a shadow check. The existing client-mirror wrapper forwards the same arguments. This mode emits one JSON report to stdout with `dry_run: true`, exits 0 for PASS or 1 for evidence/quality failure, and never creates evidence directories or replaces the workspace's gate result. Argument refusal exits 2. The RUNNING invalidation and terminal result writes remain unchanged for legacy invocations without `--dry-run`.

`--dry-run --portfolio <slug...>` propagates the mode to every child. `--airtable-record` is rejected before evaluation in dry-run mode. No output-path option exists: `--output` is rejected, including existing files, symlinks, hardlinks, workspace aliases and new paths. This avoids output alias races rather than trying to permit selected paths. Shell redirection is caller-owned and outside the CLI's guarantee; never redirect stdout into the input workspace. Capture stdout through the supervising process into a separate handoff artifact only when authorized.

Dry-run is not offline mode or acceptance authority. Existing HTTPS GET and hosted-Jev checks still run when signed evidence reaches them; synthetic tests mock those boundaries and make no provider requests. Trust, signatures, criteria and exit behavior are not relaxed. No deployment, publish, send, Airtable write, credential change or permanent trust enrollment is authorized by this flag. Current empty production trust still rejects C00.

## Trust and privacy

The current `TRUSTED_VERIFIERS` mapping is empty. Production acceptance fails closed. A caller-provided public key never grants operator authority. No permanent key, trust enrollment, credential change or new signer is created by this repair. Existing trust roots found for desktop package signing or retired Orca sessions are not website-QA authority and must not be borrowed. Any future mapping must identify an existing approved QA signer by public-key SHA-256, verifier id and family, through reviewed source/configuration change. Test fixtures patch temporary in-memory trust; their signatures prove contract behavior only.

An independent verifier must own the actual browser run and inspect its outputs before signing. Signing builder assertions is not independent QA. Require a different builder/verifier id and family, and authenticate the verifier against the approved key mapping. Do not sign partial, missing, stale, fabricated or builder-only observations. RSA SHA-256 detached signatures are verified with installed OpenSSL; Python Pillow verifies and decodes PNGs. Missing dependencies cause FAIL, never acceptance. Do not put signing private keys or provider secrets in sites, captures, notes, logs or ProofPackets.

Signed bytes are `evidence/verifier-receipt.json`; detached signature is `evidence/verifier-receipt.sig`. A real authorized verifier can use the existing signer infrastructure to produce this format. These instructions do not authorize key creation or trust installation. Supply the already-authorized public key through `--verifier-key`, outside the entire builder workspace.

## Offering admission

`offering.json` contains:

- `schema`, `offering_id` matching the site slug and receipt, and `brand_owner_id` matching the client id.
- `client`: stable `id`, actual `name`, `identity_kind` (`client` or `user-named-project`), and `identity_source` with site-relative `path`, `sha256`, JSON-pointer `locator`. A private project additionally needs `authority: mike-direct` supported by actual user evidence, independently verified. TransformFit can use that route. No public domain is required for a private concept.
- `solution`: stable `id`, concrete `mechanism`, `problem`, `status` (`proposed` or `verified`) and existing `source_ids`. Preserve uncertainty. Displaying the site does not establish engagement, authorization to publish, or a verified business outcome.
- `sources`: at least three distinct pain-source ids with exact native `record_id`, raw `record_locator` JSON pointer, `run_id`, `kind` (`socialfetch` or `airtable`), `scope` (`client` or `category`), exact `quote`, bound raw `artifact` and `run_receipt`. The record locator must resolve to the actual id in the same raw record as the quoted field. Duplicate native records or raw record locators cannot count as distinct sources. Each artifact/run reference contains `path`, `sha256`, JSON-pointer `locator`. The located run must contain matching `run_id`, `provider`, `status: success`, and the raw `response_sha256`. At least one actual SocialFetch chain is required for this mission. Empty/blocked scans cannot establish it. A category source cannot be attributed to a client's customer.
- `pinterest`: exact `pin_url`, local `image_path`, `image_sha256`, raw `index_source` locator and a visually observed `visual_decision`. Include actual extraction provenance and label partial/RSS coverage honestly. Do not impose cached counts as admission policy. A caption-derived color claim is not visual inspection.
- `references`: three to five distinct `mirror` captures and at least three `award` captures with exact `url`, matching `capture_url` and bound PNG `artifact`. Generated production images and original pin references remain distinguishable.

Every displayed pain card must have an exact, distinct source record and quote. The independent receipt has `source_reviews[source_id]` with `client_id`, `solution_id`, `relevant: true` and a concrete applicability `rationale`. Missing or unrelated evidence is a rejection, not a prompt to invent data. RIG/RI-branded entries cannot count for the client mission.

Quote locators resolve to string fields inside the native id's owning record object, never a collection or ancestor container. Distinct id fields in the same raw object still count as one record. JSON-pointer escapes must be valid; array indices use canonical nonnegative decimal spelling (`0`, `1`, etc.), so `/pains/00` cannot alias `/pains/0`.

## Independent receipt and capture

The receipt contains `schema`, `offering_id`, `url`, UTC `captured_at`, `build_sha256`, `session_id`, authenticated `verifier: {id, family}`, distinct `builder: {id, family}`, `artifacts: {relative_path: sha256}`, `source_reviews`, and `captures`.

Bind all inputs consumed by the gate: offering, demand/claims/critique, seven phase documents, raw source/run and pin files, browser observations, tool trace, actual Lighthouse report, structured critique, Miro export/ledger, build and deployment evidence, and all PNGs. SHA-256 build identity covers every file under `app/` except dependency/cache directories `node_modules`, `.git`, `.next`; include the final built files in that tree. Symlinks and path escapes are refused. The approved verifier must establish that the reviewed served deployment has these build bytes; HTTP 200 alone cannot establish build identity.

Receipt and capture must be no more than 24 hours old and never future-dated. Lighthouse `fetchTime` must be within one hour of the receipt. Capture entries for `evidence/desktop-1440.png` and `evidence/mobile-390.png` contain matching `url`, `build_sha256`, `captured_at`, and `viewport` `[1440,900]` or `[390,844]`. Decode actual PNG pixels; full-page height may exceed the viewport. A padded file or a tiny valid image fails.

`probe.json` is the independent served-page observation, with `url == vercel_url == receipt.url`, actual DOM measurements and the existing hero/pain/CTA/links/font fields. Add `images_complete: true` only after all images finished loading. Boolean/infinite measurements are invalid. Bind the navigation/session used for the measurements.

`browser.json` contains matching `url`, `build_sha256`, `session_id`, empty `runtime_errors`, and:

- `scroll` and `three_d`: actual target `selector`, named `mechanism`, at least two input/state samples at **each** width 390 and 1440; each sample has `viewport_width`, actual `input.scroll_y` and observed `state`. Scroll positions and target states must change within each viewport. For 3D, show changed target state while all other controls (including pointer position) remain fixed, isolating the scroll response. Pointer-only tilt is supplemental evidence and cannot prove 3D scrolling. Do not fill records from source comments, library names, preview videos or assumed effects.
- `three_d.kind` can be `css3d` or `webgl`. Genuine CSS 3D records computed `state.transform` values as finite 16-entry `matrix3d(...)` with nonzero depth components. WebGL records actual `rendered_frames >= 2`, `fallback_tested: true` and `fallback_usable: true`. Verify intentional scene composition and observed depth/rotation at the declared scroll/pointer positions. A canvas is not mandatory; static perspective is insufficient.
- Scroll state must include actual computed `opacity` and/or a finite computed `transform` matrix. WebGL state must include an observed finite 16-value `world_matrix` and/or `view_projection_matrix` for the scene/camera. Capture ids, timestamps, frame counters and other metadata are ignored when comparing target states. A static target cannot pass by changing capture metadata.
- Measured field names must remain consistent across samples. Compare numeric values, not serialized spellings; `0` and `0.0` are equal. Computed `none`, 2D and 3D identity transforms normalize to the same matrix. At least one measured component must change by more than `0.00001`.
- `reduced_motion`: one desktop and one mobile observation with `emulated: reduce`, actual `motion_suppressed`, `content_visible` and `cta_click_succeeded` all true. An alternative that hides the page fails.
- `cta`: one desktop and one mobile record of `visible`, `enabled`, `hit_target`, `click_succeeded`, `expected_effect_observed`, all true; `clock_origin: navigationStart`, finite `clickable_ms` from 0 to 1000. Visibility timing after tab open is not a click test.

`tool-trace.json` has the same `session_id` and real execution events including navigation, scroll, pointer, reduced-motion, CTA click, screenshot and Lighthouse. Preserve actual event payloads/capture ids in the trace; the verifier checks them against artifacts. A manually authored trace is not performance measurement. The gate validates identity/event coverage but cannot determine truth without an authenticated independent capture authority.

`lighthouse.json` is the **unmodified actual report**, with matching `requestedUrl` and `finalDisplayedUrl`, `fetchTime`, `configSettings.formFactor: mobile`, version, nonempty audits and no runtime error. The gate computes category scores from this file; copied probe values are ignored. Minimum performance 80, accessibility 90. Lighthouse alone does not establish complete accessibility.

`critique.json` has authenticated `verifier_id`, score from 8 to 10, exact `screenshot_hashes`, and specific `findings` for desktop, mobile, keyboard, images and reduced-motion. Each finding has `area`, observed `observation`, `severity`; every blocker needs `resolved: true` and a bound `retest_artifact`. Human-readable critique prose cannot grant a pass or an award claim.

## Actual Miro execution

Use Mike's existing board `uXjVEez017g=`. New process frames are setup, not execution. Reconcile the authoritative native board export and its crosswalk before claiming each stage ran. Do not invent native item ids from phase names.

`miro-export.json` contains `board_id`, UTC `captured_at`, actual `source_tool`, `capture_id`, and exported `items` with original `id`, `content`, observed `offering_id`, `phase`, and linked `artifact_hashes`. Preserve the native source export/capture used for normalization in the receipt. Export within 24 hours of the final receipt, after recorded phase completion.

`phase-ledger.json` contains matching `offering_id`, `board_id`, ordered `phases` (discover, define, gate, diverge, develop, deliver, measure), and `divergence`. Each phase has `status: completed`, responsible `worker`, correct `previous`, strictly increasing UTC `completed_at`, bound `artifacts` and real `item_ids`. Linked Miro content must identify that offering and phase, with matching artifact hashes.

Required phase artifacts include the phase's nonempty Markdown plus:

- Discover: offering, demand, raw pin index.
- Define: claims.
- Gate: `brief-gate.json` with actual hosted-Jev decisions for `promise-pain` and `single-cta`, each with `decision_id`, `model`, `provider: hosted-jev`, finite score at least 0.85 and at most 1. Preserve the actual request/response evidence in bound artifacts.
- Diverge: three different rendered PNG directions; each maps to a real pin and mirror URL. Record `selected_direction` and source-linked `selection_rationale`.
- Develop: `build-manifest.json` with the matching immutable `build_sha256`.
- Deliver: `deployment.json` with matching URL/build, actual status 200 and capture id. An authorized private/local preview is valid evidence; this contract grants no deployment/publication permission.
- Measure: probe, browser, Lighthouse, desktop/mobile screenshots and structured critique.

Deleting/changing a phase artifact after acceptance invalidates the rerun. Source checks are lint, actual artifacts and trusted independent verification decide acceptance. This repair currently rejects every production acceptance request because no approved website-QA trust root has been established.

## Evidence limits and promotion

The behavioral unittest suite exercises signed synthetic fixtures and re-signed semantic failures. It is not a pinned held-out evaluation of agent outputs, live browser QA, different-family GEV or D85 certification. Require the existing `skill-upgrades` source-bound outcome screen (at least 30 held-out tasks, score above 0.90, zero hard-block failures), an independent verifier and applicable build gates before promotion. The user's overnight client deadline does not convert missing evidence into a pass.
