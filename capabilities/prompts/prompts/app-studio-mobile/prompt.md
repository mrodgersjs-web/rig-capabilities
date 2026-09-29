---
id: app-studio-mobile
version: 1
status: draft
updated: 2026-09-28
task: App Studio mobile stage prompt: build the Expo or native lane and show it running on a clean simulator driven from Orca
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: expo mobile app react native lane
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: main
parent: app-studio-meta
stage: mobile
audience: builder
lessons: LA-15 LA-16 LA-17 LA-18 LA-19 LA-22 TG-21 TG-22
jev_gate: app.prompt
jev_decision: 119519
content_sha256: dc01b94a5e4f0dca676c5df7e6c6fb7da06f7161a12ccdebe03737355a29d307
---

# Stage 7: mobile (App Studio main prompt, v1)

Contract
- id: app-studio-mobile | version: 1 | tier: main (stage) | parent: app-studio-meta | stage: mobile | audience: builder
- inputs: {{STACK}}, spec.md screen map
- output: a mobile build plus captures from a cold-booted simulator, recorded in .app-studio/stages/mobile.md
- lessons carried (each one is an instruction to follow):
  - LA-15: Run simulator work from an Orca terminal (CoreSimulatorService is unreachable from the Aside sandbox) and cold shutdown, boot and uninstall before each capture run.
  - LA-16: Use screenshots of the real app on a device or simulator and have a person or vision judge actually look; golden-test renders and pixel metrics are not visual QA.
  - LA-17: Tap Not now or Skip on permission screens during automated runs and clear leftover system alerts with a cold simulator restart.
  - LA-18: Confirm which backend the build talks to before automated sign-ups, then delete every created test account and poll deletion status until the user is gone.
  - LA-19: Prove the shipped bundle's compile-time flags from the bundle itself (for example dart2js dead-branch string counts) before trusting any QA run against it.
  - LA-22: Check in-app account deletion (Apple 5.1.1(v)), purchases that transact (3.1.1), metadata the app can back (2.3.1), no dead buttons (Play IN_APP_EXPERIENCE) and live crash reporting before submission.
  - TG-21: Expo: point the dev API at the Wi-Fi LAN IP, register the Android package and SHA-1 for Google sign-in, and pick APK (device) or AAB (store) on EAS. (TubeGuruji videos: 2n96HAqcG_w, MbiAwAp3lCA, cxto0P5DSYU)
  - TG-22: Put a floating action button beside the ScrollView (absolute position), never inside the scrolled content. (TubeGuruji videos: bpP7PKuEjgI, c0AOwKlAz9I)
- gates: library gate app.prompt on this text; output gate app.stage-gate plus ui.design on the captures (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: the app installs on a cold-booted simulator, each done-screen has a capture from it, and any test accounts created are deleted with the deletion confirmed
- stop: report BLOCKED: simulator unreachable from the Aside sandbox when simulator commands fail here; the capture run moves to an Orca terminal (LA-15); deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-expo-app

Question this stage answers: does the real app on a clean simulator or device do what the spec says?

1. Build with app-sub-expo-app and run its preflight (TG-21).
2. Simulator work runs from an Orca terminal; cold shutdown, boot and uninstall before each capture run (LA-15).
3. Dismiss permission dialogs with Not now or Skip during automated runs (LA-17).
4. Confirm which backend the build talks to before automated sign-ups, then delete every test account and poll until it is gone (LA-18).
5. Prove compile-time flags from the shipped bundle itself before trusting a QA run (LA-19).
6. Store-policy items (account deletion, purchases, metadata, crash reporting) are checked before any submission request (LA-22).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
