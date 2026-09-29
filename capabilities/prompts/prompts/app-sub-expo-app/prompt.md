---
id: app-sub-expo-app
version: 2
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: build the Expo lane with its three preflight checks and simulator captures from Orca
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: expo app build
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons LA-15 LA-17 TG-21 TG-22 LA-44 LA-45 LA-49 | uncalibrated
tier: sub
parent: app-studio-mobile
stage: mobile
audience: builder
lessons: LA-15 LA-17 TG-21 TG-22 LA-44 LA-45 LA-49
jev_gate: app.prompt
jev_decision: 121881
content_sha256: 6c30b4d669adcea421434be3bd07b56abcbaeb88d2ad0c8dedb084cf83edea15
---

# Expo app (App Studio sub prompt, v2)

Contract
- id: app-sub-expo-app | version: 2 | tier: sub | parent: app-studio-mobile | stage: mobile | audience: builder
- inputs: {{STACK}}
- output: an Expo app with expo-router screens matching the screen map, and a preflight table in the mobile record
- lessons carried (each one is an instruction to follow):
  - LA-15: Run simulator work from an Orca terminal (CoreSimulatorService is unreachable from the Aside sandbox) and cold shutdown, boot and uninstall before each capture run.
  - LA-17: Tap Not now or Skip on permission screens during automated runs and clear leftover system alerts with a cold simulator restart.
  - TG-21: Expo: point the dev API at the Wi-Fi LAN IP, register the Android package and SHA-1 for Google sign-in, and pick APK (device) or AAB (store) on EAS. (TubeGuruji videos: 2n96HAqcG_w, MbiAwAp3lCA, cxto0P5DSYU)
  - TG-22: Put a floating action button beside the ScrollView (absolute position), never inside the scrolled content. (TubeGuruji videos: bpP7PKuEjgI, c0AOwKlAz9I)
  - LA-44: Import every module for the runtime that executes it: no window or document in React Native, client hooks only in files marked 'use client', env read the way the bundler exposes it, and check which surface a component is imported from before fixing an undefined-component error.
  - LA-45: After adding a native module, a config plugin, or a native or bundler config change, run expo prebuild and rebuild (or restart with the cache cleared for env and bundler config) and confirm the change on a device; a hot reload is not evidence the change is live.
  - LA-49: Before calling a screen done, render it with zero records (every element and ref access guarded) and, on mobile, open each form with the keyboard up and prove no field or button is hidden.
- gates: library gate app.prompt on this text; output gate app.stage-gate on the mobile record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: `npx expo export` exits 0 and each done-screen has a capture from a cold-booted simulator run from Orca
- stop: report BLOCKED: simulator unreachable when simulator commands fail in this sandbox (LA-15); never submit to a store; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. Preflight (TG-21): the dev API points at the Wi-Fi LAN IP, not localhost; Google sign-in has the Android package and SHA-1 registered; EAS builds APK for devices and AAB for the store.
2. A floating action button sits beside the ScrollView with absolute position (TG-22).
3. Captures run from an Orca terminal after a cold simulator boot (LA-15); dismiss permission dialogs with Not now (LA-17).
4. No window or document in React Native code; use the platform navigation API and expo-status-bar (LA-44; creators CH-JSM-01, CH-NJD-04).
5. After adding a native module or a config plugin, run expo prebuild and rebuild; restart with the cache cleared after env or bundler config changes (LA-45; CH-NJD-02).
6. Forms sit in KeyboardAvoidingView with safe-area insets: test each with the keyboard up and each list with zero records (LA-49; CH-NJD-01).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
