---
name: app-mobile-build
description: "App Studio sub-skill, stage 7 (mobile): build and verify iOS and Android apps in either lane - Expo/React Native or Flutter - with simulator work run from an Orca terminal, compile-time flags proven from the shipped bundle, real-device or simulator screens as the only visual evidence, and test accounts cleaned up. Paid for in the TransformFit QA and screenshot runs."
tags: [rig, app-studio, sub-skill, mobile, expo, react-native, flutter, ios, android]
metadata:
  parent: app-studio
  tier: sub
  stage: mobile
  extends: "tg-expo-mobile-ai, react-native-architecture, dart-flutter-patterns, flutter-production-build, mobile-ios-design, mobile-android-design"
outcome: "A mobile build whose flags are proven from the bundle, whose screens were captured from the real app on a clean simulator or device, whose test accounts were deleted with deletion confirmed, and whose slice records carry app.stage-gate receipts."
activation: "Load for any iOS or Android build, simulator capture, mobile QA pass, or Flutter or Expo feature slice."
instruction: "Build and simulate from an Orca terminal, prove compile-time flags from the bundle, capture only real screens on a cold simulator, confirm the backend before automated sign-ups and clean up after, and gate each slice."
applies_when:
  env: "Orca terminal on the Mac for Xcode and simctl; EAS cloud for Expo builds; Aside for review only"
  runtime: "Flutter 3.x or Expo SDK with React Native"
  deps: "Xcode command line tools, xcrun simctl, flutter or eas CLI"
  params: "device UDID, bundle id, dart-define or app config per build"
  budget: "Xcode build about 45-60 s per run on the TransformFit worktree"
  scale: "one app, one device matrix at a time"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Pick the lane and run every build or simulator step from an Orca terminal.
  - Record and prove the compile-time flags of the exact bundle under test.
  - Capture real screens on a cold simulator with permission screens skipped.
  - Confirm the backend before automated sign-ups and delete every test account afterwards.
  - Gate each slice record with rig-s1gate app.stage-gate.
done_when:
  - "grep:capabilities/skills/app-mobile-build/SKILL.md:LA-15"
  - "grep:capabilities/skills/app-mobile-build/SKILL.md:LA-19"
  - "grep:capabilities/skills/app-mobile-build/SKILL.md:simctl"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - store submission and TestFlight release (app-ship-mobile, Gate-D)
  - posting marketing reels (a separate lane with its own approval)
  - editing the app's source from the QA seat when OMP owns fixes (TransformFit role split)
---

# app-mobile-build

JEV FIRST, binding on every mobile step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stage-gate` and `ui.design`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every mobile task: the `app-studio` meta-skill routes
stage 7 here and `app-studio-conductor` loads it from its routes table before the
stage's first action, and the `app-mobile-release` harness names it as doctrine. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 7 of 11. Main skills it extends: `tg-expo-mobile-ai`
(Expo lane), `react-native-architecture`, `dart-flutter-patterns`,
`flutter-production-build`, `mobile-ios-design`, `mobile-android-design`.
Main agents: `tg-mobile-builder`, `voltagent-mobile-app-developer`.

## Procedure

1. **Lane.** New app: Expo + Expo Router + EAS per `tg-expo-mobile-ai`. Existing Flutter
   app (TransformFit): stay on Flutter.
2. **Where it runs (LA-15).** CoreSimulatorService is unreachable from the Aside sandbox.
   Run simulator and Xcode work from an Orca terminal:
   `orca terminal create --worktree path:<worktree> --command "bash <script>"`.
3. **Flags are proven, not assumed (LA-19).** A tested TransformFit bundle had demo mode
   compiled ON, so 300 campaign screenshots exercised mock data. For Flutter web, count
   branch-unique string literals in `main.dart.js` (dart2js strips the dead branch when a
   `bool.fromEnvironment` flag folds). Record the `--dart-define` set with every build.
4. **Clean capture runs (LA-15, LA-17).** Cold `xcrun simctl shutdown` then `boot`,
   uninstall before each run, status bar override to 9:41 with battery discharging. On
   `/permissions/*` screens tap only "Not now" or "Skip for now": the primary button
   raises the real iOS prompt and stalls the flow. A leftover permission alert survived
   `simctl uninstall` and covered every shot of the next run.
5. **Real screens only (LA-16).** Capture with `xcrun simctl io <udid> screenshot`
   while an integration test drives the real app. Golden-test renders and the web build
   at phone size are not the app. Pixel metrics are not visual QA; someone looks.
6. **Test accounts (LA-18).** Confirm which backend the build talks to first: the
   TransformFit local web build wrote 14 real production accounts. Delete each one and
   poll the deletion status until the user returns 404; without polling, 14 of 14
   delete jobs sat pending past 90 s.
7. **Source is not render (LA-23).** A "frozen button" read from source sat in a
   demo-only branch; find the enclosing conditional and confirm on screen before filing.
8. **Gate** each slice record with `app.stage-gate`.

## Evidence

memory/episodic/2026-09-27.md#L1475, #L1478, #L1467, #L1480;
memory/projects/transformfit-qa.md#L18, #L20.
