---
name: app-teardown
description: "App Studio sub-skill, intake-spec source lane (reference-app teardown): reverse-engineer an app Mike uses (MacroFactor today, many more to come) into a per-row trace ledger in the TARGET app's repo, and hold a coverage gate that fails until every captured row has a build or a reasoned decision behind it. Captures come from the phone side (jev-phone: WebDriverAgent text tree, no Mac mouse), help-center docs, and the builder's gap audit; Jev routes rows to landed commits; the builder records VERIFIED evidence per slice. Use for 'reverse engineer this app', 'scrape every screen of X', 'teardown', 'parity with X', 'merge features from these apps into mine', or when a capture exists but nothing ties it to a build."
tags: [rig, app-studio, sub-skill, intake, teardown, reverse-engineering, parity, trace, jev-phone]
metadata:
  parent: app-studio
  tier: sub
  stage: intake-spec
  lane: reference-app teardown
  extends: "app-intake-spec, jev-phone, jev-ultrafast, typesafe-jev, app-verify-evidence, app-close-and-learn"
outcome: "For each source app -> target app pair: a sourced ledger (docs + device screens + audit items), Jev routing of rows to landed commits, builder evidence per slice, and `trace.py coverage` exiting 0 only when every row is VERIFIED, EXISTS, SKIP-with-reason, or a screen MAPPED to done rows."
activation: "Load whenever Mike points at an existing app as the reference for one of his apps, before any spec is written from it, and whenever a builder asks what is left of a parity effort."
instruction: "Register the pair, capture from docs and the phone side, import everything into the target repo's ledger, route with Jev (triage, not proof), hand the builder the ledger rules, and never call parity done unless coverage exits 0."
applies_when:
  env: "macOS host with Orca; target repo is a git worktree; iPhone on USB for device capture"
  runtime: "python3 stdlib (trace.py, jev-phone); WebDriverAgent via Xcode for iOS captures"
  deps: "~/Developer/jev-phone; rig-s1gate; keychain item com.rig.env.TYPESAFE_API_KEY (never printed)"
  params: "source app name + platform, target app key, target repo path, builder slice commit pattern"
  budget: "capture about 5-6 s per new screen once WDA is up; Jev routing about 4 s per 350 rows"
  scale: "one ledger per source->target pair; many sources may feed one target"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Register the pair in ~/Desktop/Projects/app-teardowns/registry.json.
  - Build the doc map from the help center's collection pages (sourced rows).
  - Capture the device screens with jev-phone (watch first on a real account; crawl only after --dry-run).
  - Import map, audit and runs into <target repo>/docs/parity/trace/TRACE.jsonl.
  - Route rows to landed commits with trace.py link (Jev, p >= 0.9) and reopen any route the builder's notes contradict.
  - Give the builder docs/parity/trace/README.md; slices record VERIFIED evidence; the stage closes only on coverage exit 0.
done_when:
  - "cmd:python3 capabilities/skills/app-teardown/scripts/test_trace.py"
  - "cmd:python3 capabilities/skills/app-teardown/scripts/plant_trace.py"
  - "file:capabilities/skills/app-teardown/scripts/trace.py"
out_of_scope:
  - copying a competitor's proprietary copy, assets, exercise/food databases or brand (behaviour only)
  - intercepting a competitor's network traffic or decompiling its binary
  - deciding a target app's product scope (Mike) or any outward release step (Gate-D)
---

# app-teardown

JEV FIRST, binding on every step: typed judgments (which commit implements a row, is a tap
navigation or a mutation, is this screen the same as that one) go to Jev through the paths below
BEFORE any frontier LLM call. When no judge answers: DEFER. DEFERRED is never a pass, never
"built", never "safe to tap". A required signal passes only above 0.9.

Sub-skill of `app-studio`, the reference-app lane of stage 1 (`app-intake-spec` owns the spec
format; this skill owns capture, the ledger and the coverage gate). Every row keeps its source,
so the spec rows cite a doc URL, a screen PNG, or an audit line.

## The loop, per source app

```
capture (docs + phone) -> import -> route (Jev) -> build (App Studio 3-9) -> record -> gate
```

| Step | Command | Output |
|---|---|---|
| 0 register | edit `~/Desktop/Projects/app-teardowns/registry.json` | source app, platform, framework, target repo, builder, slice grep |
| 1 docs | WebFetch `<help>/en/collections/<id>` (one fetch lists every article) | capability map, one sourced row per behaviour |
| 2 device | `jev-phone doctor` -> `watch` (you tap) or `crawl --dry-run` -> `crawl` | run folder: PNG + exact text tree per screen, clickable viewer |
| 3 import | `trace.py import-map / import-audit / import-run` | `<target repo>/docs/parity/trace/TRACE.jsonl` |
| 4 route | `trace.py link --repo <target> --grep "<slice pattern>" --min-p 0.9` | BUILT (unverified) rows with commit + jev evidence |
| 5 build | builder follows `docs/parity/trace/README.md` | slices record VERIFIED rows with commit + test |
| 6 gate | `trace.py coverage --ledger ... --repo <target>` | exit 0 done, 1 open rows, 2 bad evidence |
| view | `trace.py render --out ~/Desktop/Projects/app-teardowns/<pair>` | TRACE.md + trace.html (served at :8947/teardowns/) |

`T=~/Developer/rig-capabilities/capabilities/skills/app-teardown/scripts/trace.py`,
`J=~/Developer/jev-phone/bin/jev-phone`. Simulator/device commands run in an Orca terminal.

## Statuses and the evidence the gate re-checks

| Status | Needs | Counts as done |
|---|---|---|
| OPEN | nothing | no |
| TRIAGED | priority must/should/could | no |
| PLANNED | ticket or slice | no |
| BUILT | a commit that exists in the target repo | no (needs proof) |
| VERIFIED | commit + a test file or screen that exists | yes |
| EXISTS | file/test evidence in the target repo (it was already there) | yes |
| SKIP | a reason (8+ chars) | yes |
| MAPPED | covers=[ids] (screens, composite audit items) | only when every covered row is done |

Imports never overwrite a decision already recorded on a row.

## Decision routing (inventory, first match wins)

| Decision | Route | Why |
|---|---|---|
| evidence exists (commit in repo, test path, screen file) | CODE | deterministic |
| which landed commit implements a row | JEV (`trace.py link`, choice over commits + NONE, p >= 0.9) | bounded set, answer consumed by code |
| is a tap navigation or a mutation (live account) | CODE rules, then JEV batch per screen (`jev-phone`) | fail closed |
| writing spec rows / acceptance checks from screens | SYSTEM 2 (app-intake-spec) | generation |
| building the feature | SYSTEM 2 builder (App Studio stages 3-9) | generation |
| product scope (e.g. nutrition in TransformFit), release | HUMAN (Mike, Gate-D) | owner decision |

## Capture lessons (earned 2026-09-28, MacroFactor Workouts -> TransformFit)

1. **iPhone Mirroring cannot run in the background.** It only takes real HID mouse events while
   its window is frontmost, so a Mirroring driver steals focus and the cursor every tap and
   measured about 53 s per screenshot (77 in 68 min). Drive the phone from the phone side:
   WebDriverAgent (XCUITest) reads the app's accessibility tree and taps inside the device.
2. **Flutter apps expose their text to XCUITest** (MacroFactor and TransformFit are Flutter):
   exact strings in 45-76 ms; OCR of 354-px Mirroring grabs garbles small text.
3. **The capture target is Mike's live account.** Code blocks switches, sliders, text fields,
   switch rows and action-verb labels; Jev judges the rest; undecided = skip. Calibrated 16/19
   with 0 unsafe taps on MacroFactor rows. Take a Data Export before any crawl; start with `watch`.
4. **Health data stays home.** Hosted Jev gets digit-masked labels only; OpenJev (Mike's box)
   may see full text.
5. **UIKit trees include what a sheet covers**; only tap elements in the top presented layer,
   with their centre in the safe area. Skip prose (commas, trailing period, more than 5 words).
6. **Jev routing is triage, not proof.** It sent "superset creation pre-workout" to the
   supersets commit; the builder's slice notes said pre-workout pairing was not in it. Routed
   rows land as BUILT, and a builder note beats a route.
7. **Sandbox mechanics**: CoreSimulator/CoreDevice need an Orca terminal; the Aside sandbox kills
   background jobs at the next tool call; `file://` is blocked in the browser (serve on a port);
   check a port is free before binding (8100 and 8931 were taken on this Mac).
8. **Test builds can auto-run sign-up.** A Flutter build compiled from an integration test
   (`IntegrationTestWidgetsFlutterBinding` in `kernel_blob.bin`) runs its test on launch; grep
   the build before launching it anywhere near production.

## Many apps, one target

One ledger per source->target pair in the target repo; the registry lists every pair. Several
sources feeding one target (e.g. MacroFactor + another tracker -> TransformFit) stay separate
ledgers; merge by capability at planning time (Jev "same capability?" over row pairs), never by
deleting rows. A row only leaves the queue through a status with evidence.

## Files

- `scripts/trace.py` ledger + gate (stdlib); `scripts/test_trace.py` 8 gates;
  `scripts/plant_trace.py` 5 planted failures that must turn the suite red.
- `~/Developer/jev-phone` capture engine (README there): WDA client, crawler, watcher, viewer.
- `~/Desktop/Projects/app-teardowns/registry.json` every source->target pair.
- First pair: `tf-macrofactor-parity/docs/parity/trace/` (437 rows, 2026-09-28).
