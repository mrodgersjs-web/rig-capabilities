---
name: app-ship-mobile
description: "App Studio sub-skill, stage 10b (ship-release, mobile): prepare an iOS or Android release that survives store review - account deletion that completes, purchases that transact, metadata the app can back, no dead buttons, live crash reporting, flags proven from the release bundle, real screenshots - then hold the submission at Gate-D for Mike."
tags: [rig, app-studio, sub-skill, ship, mobile, app-store, play-store, testflight, gate-d]
metadata:
  parent: app-studio
  tier: sub
  stage: ship-release
  extends: "app-store-ship, flutter-store-deployment, flutter-production-build, tg-expo-mobile-ai, gate-d-loop"
outcome: "A mobile release record with each store-policy item checked and cited, an app.ship receipt with store_policy above 0.9, and a Gate-D request held for the submission."
activation: "Load when a mobile app approaches TestFlight, internal testing, or store review, or when store metadata, screenshots, or purchase flows are being prepared."
instruction: "Run the store-policy preflight against the real build, prove the release flags, capture real screenshots, write the release record, gate it with app.ship, and hold the submission at Gate-D."
applies_when:
  env: "Orca terminal for Xcode and simctl; EAS or Gradle for builds; App Store Connect and Play Console owned by Mike"
  runtime: "Flutter or Expo/React Native release builds"
  deps: "app-store-ship for the submission mechanics; a verify record from app-verify-evidence"
  params: "bundle id, version and build number, store listing copy, screenshot set"
  budget: "store review cycles are days; preflight is hours"
  scale: "one app, one release"
permissions:
  - fs.read
  - fs.write
  - bash
  - gate-d-required:publish
  - gate-d-required:purchase
flow:
  - Run the store-policy preflight on the real release build.
  - Prove the release build's compile-time flags from the bundle.
  - Capture real screenshots on a clean simulator or device.
  - Write the release record and gate it with rig-s1gate app.ship.
  - Hold the submission at Gate-D and record the request id.
done_when:
  - "grep:capabilities/skills/app-ship-mobile/SKILL.md:LA-22"
  - "grep:capabilities/skills/app-ship-mobile/SKILL.md:5.1.1"
  - "file:capabilities/harnesses/s1gate/rubrics/app.ship.json"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - pressing submit in App Store Connect or Play Console (Mike's action)
  - buying developer accounts or in-app purchase tiers
  - writing store copy that claims features the build does not have
---

# app-ship-mobile

JEV FIRST, binding on every ship-release (mobile) step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.ship`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every ship-release (mobile) task: the `app-studio` meta-skill routes
stage 10 here and `app-studio-conductor` loads it from its routes table before the
stage's first action, and the `app-mobile-release` harness names it as doctrine. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 10 of 11 (mobile half). Main skills it extends:
`app-store-ship`, `flutter-store-deployment`, `flutter-production-build`,
`tg-expo-mobile-ai` (EAS lane), `gate-d-loop`. Sub-process: `app-mobile-release`.

## Store-policy preflight (LA-22)

Measured on TransformFit source (memory/projects/transformfit-qa.md#L36, #L30):

| Item | Store rule | What failed there |
|---|---|---|
| In-app account deletion | Apple 5.1.1(v) | deletion was a TODO; later, deletion completed only when its status was polled (LA-18) |
| Purchases transact | Apple 3.1.1 | four membership screens showed snackbars instead of transacting |
| Metadata the app can back | Apple 2.3.1 | the site claimed an AI body scan while the camera plugin was absent |
| No dead buttons | Google Play IN_APP_EXPERIENCE | the repo already cited a prior Play rejection for dead buttons |
| Crash reporting live | ships blind otherwise | six consecutive Sentry TODOs |

Each row gets a proof line from the real release build, not from source.

## Procedure

1. Run the preflight table above against the release build on a clean simulator or device.
2. **Flags (LA-19).** Prove the release bundle's compile-time flags (demo mode OFF).
3. **Screens (LA-16, LA-17).** Store screenshots come from the real app via
   `xcrun simctl io <udid> screenshot` on a cold simulator with the 9:41 status bar.
4. **Build where it can run (LA-15).** Xcode from an Orca terminal; Expo through EAS.
5. **Release record + gate.** `.app-studio/release.md` then `rig-s1gate check app.ship`.
6. **STOP at Gate-D** for TestFlight, internal testing, or store submission; record the id.
7. After approval and submission, confirm the build is visible in App Store Connect or
   Play Console before calling the release done.
