---
name: tg-expo-mobile-ai
description: >
  Pillar skill for the React Native/Expo lane of the TubeGuruji corpus —
  Figma-first mobile builds, Expo Router navigation, mobile AI features via APIs,
  EAS APK/AAB builds, Firebase App Distribution, and the mobile-only gotchas
  (localhost, SHA-1, slug, ScrollView/FAB positioning).
tags: [rig, doctrine, react-native, expo, mobile, tubeguruji]
metadata:
  source: "corpus — cxto0P5DSYU (EAS APK/AAB, slug trap, App Distribution), MbiAwAp3lCA (Google SHA-1), 2n96HAqcG_w (localhost/LAN IP), bpP7PKuEjgI + c0AOwKlAz9I (FAB/ScrollView), zMMcxWORZvg (HyGraph schema in GUI, e-learning), FJm3eKT9L9s (Nile serverless Postgres), HlR15YZM7fg (gamified AI course app, agent-built), UgLN9O930vE (Convex AI diet planner, 21.6k words), OBxf8JDjNCQ (zero-to-production course)"
  extracted: "2026-09-25"
  parent: tubeguruji-doctrine
outcome: "A full-stack React Native app built on the skeleton, building to APK/AAB via EAS and distributed to testers, with the corpus' mobile-only failure modes pre-checked."
activation: "Load when the build targets iOS/Android via React Native/Expo, when an Expo build fails, or when porting a web AI SaaS pattern to mobile."
instruction: >
  Keep the same skeleton stages as web; swap the toolchain (Expo Router,
  Nativewind/Tailwind, EAS). Start from the Figma prototype the corpus walks
  first. Treat localhost, OAuth fingerprints, and slug/app-name equality as the
  three pre-flight checks before any build.
applies_when:
  env: "local repo + Expo/EAS account + device or emulator"
  runtime: "React Native + Expo (Expo Router); Android/iOS device"
  deps: "expo, expo-router, nativewind (or RN styles), hosted DB (Firebase/Supabase/Convex/Neon/HyGraph), auth provider"
  params: "slug == app name; ~30 free EAS builds/month; APK profile for testers, AAB for Play Store"
  budget: "free tiers carry dev; EAS free queue can wait ~60 min (1MqozxAvmsc)"
  scale: "single app; TestGroup-scale distribution via App Distribution"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Walk the Figma prototype first; the corpus builds RN apps design-first (zMMcxWORZvg, xMtTnGCZSx8).
  - Scaffold with Expo + Expo Router; stack/tab navigation with NavigationContainer conventions (0O4HsoG1ZuY, VOFJ1wBJcUo).
  - Wire auth early (Firebase/Google or Clerk social) with the OAuth pre-flight: package name in app.json + SHA-1 fingerprint in Google Cloud (MbiAwAp3lCA).
  - Fetch from the hosted DB via the central API module; remember localhost fails on device — use the machine's Wi-Fi LAN IP (2n96HAqcG_w).
  - Build feature screens with FlatList sliders, skeleton/empty states, toasts; keep the FAB OUTSIDE the ScrollView as a sibling with position:absolute (bpP7PKuEjgI, c0AOwKlAz9I — identical fix in two unrelated courses).
  - Add AI features as API calls from the app to your backend or the provider (LhKguWePLp0 RN→Next.js backend; ZcZu1NYx-WE on-device Gemini calls; P4D20QVX7Aw image AI via APIs).
  - Build with EAS: verify `slug` equals the app name or the build fails (cxto0P5DSYU); APK profile for direct installs, AAB for Play Store; bump the version on rebuild without changing the package name (2ua_Eu0LhcI).
  - Distribute via Firebase App Distribution: drag the APK, invite testers by link, watch per-tester download analytics (cxto0P5DSYU, 0-NwPCCzXv0).
done_when:
  - "grep:capabilities/skills/tg-expo-mobile-ai/SKILL.md:SHA-1"
  - "grep:capabilities/skills/tg-expo-mobile-ai/SKILL.md:slug"
  - "grep:data/corpora/how-to/manifest.jsonl:cxto0P5DSYU"
out_of_scope:
  - native module development (Kotlin/Swift), custom build plugins
  - App Store / Play Store publishing itself (deferred in the corpus too — "payment module at 10K views", zMMcxWORZvg)
  - pushes/publishes without Gate-D
quality_floor: "A mobile build claimed working without an install on a real device is RED — the corpus standard is APK on a phone, demonstrated."
---

# React Native / Expo Lane

## Design-first, always

The RN lane starts from a Figma prototype walked on screen before code
(zMMcxWORZvg opens on the prototype; xMtTnGCZSx8 is explicitly "from Figma
design"; the education-app series begins with frames). Carry the same discipline:
prototype → walk → build.

## The three pre-flight checks (all corpus-paid failures)

1. **localhost does not work on device** — API base URL must be the dev machine's
   Wi-Fi LAN IP from network settings (2n96HAqcG_w).
2. **Google sign-in needs the manual OAuth client**: Android package name in
   `app.json` AND SHA-1 fingerprint in the Google Cloud OAuth client; "you will
   not find the single video" covering it (MbiAwAp3lCA).
3. **EAS slug must equal the app name** or the build errors; ~30 free builds/month
   on the EAS free tier; APK for devices, AAB for the Play Store (cxto0P5DSYU).

## Layout gotcha worth memorizing

The FAB-floating-over-scrolling-list problem has one corpus answer, found
independently in two courses: ScrollView wraps ONLY the list content; the FAB is a
sibling positioned with `position:absolute; bottom:0` (bpP7PKuEjgI, c0AOwKlAz9I).

## Backend rotation mirrors web

Firebase/Firestore + Storage (c0AOwKlAz9I, xJQjeOeYq1o, yIrIZmKT-Qk via Strapi+MySQL),
Supabase with FK relations (bpP7PKuEjgI), Convex with dev→prod URL swap
(UgLN9O930vE), Nile serverless Postgres with a serverless-deployed API "so you
don't need to pay for a server" (FJm3eKT9L9s), HyGraph CMS with the schema built in
the GUI (`user enrolled course` model with reference + completed-chapter component,
zMMcxWORZvg 02:43).

## Mobile AI features are API calls, not on-device models

- RN client → Next.js backend → provider (Bard chatbot, LhKguWePLp0).
- Provider calls from the app (Gemini travel planner, ZcZu1NYx-WE).
- Image AI entirely via APIs inside RN (upscale, background removal, text-to-image,
  P4D20QVX7Aw).
- AI generation with JSON-spec prompts and a shared prompt file (diet planner:
  `prompt.jsx`, model-name constant, 3 variants as JSON, UgLN9O930vE).
- A coding agent can even run the APK build and fix it mid-course (HlR15YZM7fg,
  DEUi_8e7GLk — CleanBot builds and repairs the APK).

## Distribution

Firebase App Distribution is the corpus' free beta channel: drag the APK in, invite
testers by link, see per-tester download analytics (0-NwPCCzXv0: "one of the best
ways to distribute your application for free"; cxto0P5DSYU). On rebuild: bump the
version, never change the package name (2ua_Eu0LhcI).
