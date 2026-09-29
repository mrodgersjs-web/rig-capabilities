# App Studio prompt family

The prompts live in the RIG prompt library (`capabilities/prompts`, registry `registry.json`), filed
2026-09-28 as drafts (`score: null`, uncalibrated). Composition contract:
`capabilities/prompts/composition/app-studio.md`. Bench composer: `~/Desktop/Projects/rig-app-studio/bench/render_prompt.py`
(library mode by default, `--legacy` for the A/B baseline) with firing rules in `bench/prompt-rules.json`
and its selftest `bench/prompt-selftest.py`. The hierarchy's `prompts` kind is checked by
`scripts/validate_hierarchy.py` V9; `--plant prompt_orphan` must exit 2.

Counts: 1 meta, 15 main (11 stage + 4 role), 31 sub. Versions and filing decisions are in the inventory below
(registry `version` and `jev.decision_id`).

## Library gate

Rubric `app.prompt` (`capabilities/harnesses/s1gate/rubrics/app.prompt.json`, advisory, uncalibrated; created
2026-09-28 because no existing rubric judged prompts). Fixtures: `fixtures/app.prompt.md` PASS (decision 119507),
`fixtures/app.prompt.bad.md` ESCALATE with contract 0.12 and leak 0.74 (decision 119508). A prompt is filed only
with verdict PASS and contract_stated, evidence_done, lessons_actionable and stop_rules above 0.9. The kind
`app.prompt` is not yet registered in `work-criteria.json` (another owner).

## Inventory

| id | tier | parent | stage | audience | lessons carried | JEV app.prompt |
|---|---|---|---|---|---|---|
| app-studio-meta | meta | none | all | all | LA-03, LA-21, LA-28, LA-29, LA-31, LA-34, LA-35, TG-06, TG-24 | v1 PASS 119516 |
| app-studio-builder | main (role) | app-studio-meta | all | builder | LA-03, LA-07, LA-21, LA-25, LA-32, TG-06, TG-07, TG-08, BENCH-01, BENCH-04, BENCH-05 | v2 PASS 121868 |
| app-studio-verifier | main (role) | app-studio-meta | verify-qa | verifier | LA-02, LA-05, LA-06, LA-09, LA-20, LA-21, LA-24, LA-25, LA-27, LA-29, LA-34 | v2 PASS 121053 |
| app-studio-ui-judge | main (role) | app-studio-meta | design-ux | ui-judge | LA-15, LA-16, LA-17, LA-23, TG-10, TG-30 | v1 PASS 119521 |
| app-studio-lesson-filer | main (role) | app-studio-meta | operate-learn | lesson-filer | LA-28, LA-30, LA-34 | v1 PASS 119514 |
| app-studio-intake-spec | main (stage) | app-studio-meta | intake-spec | builder | TG-01, TG-02, LA-16, LA-35, BENCH-01, BENCH-04 | v2 PASS 121869 |
| app-studio-architecture-stack | main (stage) | app-studio-meta | architecture-stack | builder | LA-01, LA-07, LA-32, TG-03, TG-29, BENCH-05, LA-48, LA-51 | v2 PASS 121870 |
| app-studio-design-ux | main (stage) | app-studio-meta | design-ux | builder | TG-02, TG-10, TG-11, TG-30, LA-16, LA-23 | v1 PASS 119515 |
| app-studio-scaffold-setup | main (stage) | app-studio-meta | scaffold-setup | builder | LA-01, LA-02, LA-03, LA-25, LA-33, TG-12 | v1 PASS 119518 |
| app-studio-backend-data | main (stage) | app-studio-meta | backend-data | builder | LA-24, TG-16, TG-20, LA-42, LA-43, LA-50 | v2 PASS 121935 |
| app-studio-web-frontend | main (stage) | app-studio-meta | web-frontend | builder | LA-09, LA-10, LA-11, LA-23, LA-25, TG-14, TG-27, BENCH-02, LA-36, LA-37 | v3 PASS 121885 |
| app-studio-mobile | main (stage) | app-studio-meta | mobile | builder | LA-15, LA-16, LA-17, LA-18, LA-19, LA-22, TG-21, TG-22 | v1 PASS 119519 |
| app-studio-ai-features | main (stage) | app-studio-meta | ai-features | builder | LA-07, TG-03, TG-05, TG-17, TG-18, TG-25, TG-26 | v1 PASS 119510 |
| app-studio-verify-qa | main (stage) | app-studio-meta | verify-qa | builder | LA-20, LA-21, LA-24, LA-34, TG-23, TG-29 | v1 PASS 119522 |
| app-studio-ship-release | main (stage) | app-studio-meta | ship-release | builder | LA-11, LA-12, LA-13, LA-14, TG-12, TG-13, TG-15, TG-23, LA-38 | v2 PASS 121936 |
| app-studio-operate-learn | main (stage) | app-studio-meta | operate-learn | builder | LA-26, LA-28, LA-34 | v1 PASS 119517 |
| app-sub-spec-md | sub | app-studio-intake-spec | intake-spec | builder | TG-01, BENCH-01, BENCH-04 | v2 PASS 121866 |
| app-sub-acceptance-checks | sub | app-studio-intake-spec | intake-spec | conductor | LA-08, LA-20, TG-04, BENCH-02 | v1 PASS 119525 |
| app-sub-stack-md | sub | app-studio-architecture-stack | architecture-stack | builder | LA-01, LA-07, LA-51, BENCH-01, BENCH-05 | v2 PASS 121867 |
| app-sub-named-fallbacks | sub | app-studio-architecture-stack | architecture-stack | builder | LA-07, TG-03, LA-39 | v2 PASS 121872 |
| app-sub-saas-skeleton | sub | app-studio-design-ux | design-ux | builder | TG-02, TG-10, TG-30, LA-49 | v2 PASS 121883 |
| app-sub-sandbox-rules | sub | app-studio-scaffold-setup | scaffold-setup | builder | LA-01, LA-02, LA-03, LA-25, LA-32, LA-33, LA-51 | v2 PASS 121884 |
| app-sub-next-webpack-scaffold | sub | app-studio-scaffold-setup | scaffold-setup | builder | LA-01, TG-12 | v1 PASS 119541 |
| app-sub-json-store | sub | app-studio-backend-data | backend-data | builder | LA-24, TG-20 | v1 PASS 119536 |
| app-sub-demo-user-auth | sub | app-studio-backend-data | backend-data | builder | LA-07, TG-16 | v1 PASS 119528 |
| app-sub-clerk-auth | sub | app-studio-backend-data | backend-data | builder | LA-07, TG-14, TG-15, TG-16 | v1 PASS 119527 |
| app-sub-drizzle-neon | sub | app-studio-backend-data | backend-data | builder | LA-01, LA-06, TG-19 | v1 PASS 119531 |
| app-sub-quota-gate | sub | app-studio-backend-data | backend-data | builder | LA-08, TG-04, LA-47, LA-46, LA-07 | v2 PASS 121937 |
| app-sub-durable-job | sub | app-studio-backend-data | backend-data | builder | LA-05, TG-05, TG-25 | v1 PASS 119533 |
| app-sub-ssr-first-paint | sub | app-studio-web-frontend | web-frontend | builder | TG-14, BENCH-02, LA-36, LA-44 | v2 PASS 121871 |
| app-sub-next-build-time | sub | app-studio-web-frontend | web-frontend | builder | LA-09, LA-11, LA-14 | v2 PASS 121049 |
| app-sub-expo-app | sub | app-studio-mobile | mobile | builder | LA-15, LA-17, TG-21, TG-22, LA-44, LA-45, LA-49 | v2 PASS 121881 |
| app-sub-llm-feature | sub | app-studio-ai-features | ai-features | builder | LA-07, TG-17, TG-26, TG-29 | v1 PASS 119538 |
| app-sub-verify-md | sub | app-studio-verify-qa | verify-qa | builder | LA-21, LA-24, LA-41 | v2 PASS 121880 |
| app-sub-gate-d-hold | sub | app-studio-ship-release | ship-release | builder | LA-12, TG-23 | v1 PASS 119535 |
| app-sub-deploy-gotchas | sub | app-studio-ship-release | ship-release | builder | LA-11, LA-13, LA-14, TG-13, TG-15, TG-19, TG-27, TG-28, LA-46 | v2 PASS 121882 |
| app-sub-lesson-candidates | sub | app-studio-operate-learn | operate-learn | builder | LA-28 | v1 PASS 119537 |
| app-sub-feature-slice | sub | app-studio-builder | all | builder | TG-06, TG-07, TG-08, TG-09, TG-11, TG-24, LA-40, LA-48 | v2 PASS 121873 |
| app-sub-stage-record | sub | app-studio-builder | all | builder | LA-21, LA-34, BENCH-03 | v1 PASS 119551 |
| app-sub-done-md | sub | app-studio-builder | all | builder | LA-07, LA-21 | v1 PASS 119530 |
| app-sub-planted-failure | sub | app-studio-verifier | verify-qa | verifier | LA-27 | v1 PASS 119543 |
| app-sub-assertion-lint | sub | app-studio-verifier | verify-qa | verifier | LA-20, LA-34 | v1 PASS 119526 |
| app-sub-persistence-readback | sub | app-studio-verifier | verify-qa | verifier | LA-05, LA-24 | v1 PASS 119542 |
| app-sub-real-screen-capture | sub | app-studio-ui-judge | design-ux | ui-judge | LA-15, LA-16, LA-17, LA-23 | v1 PASS 119545 |
| app-sub-typed-lesson | sub | app-studio-lesson-filer | operate-learn | lesson-filer | LA-28, LA-30 | v1 PASS 119552 |
| app-sub-error-states | sub | app-studio-web-frontend | web-frontend | builder | LA-37, LA-21 | v1 PASS 121938 |
| app-sub-observability | sub | app-studio-ship-release | ship-release | builder | LA-38, LA-37 | v1 PASS 121939 |

## TG lessons (typed, from tubeguruji-doctrine and the 11 tg-* skills)

Each row is an instruction; video ids are the ones the source skill cites (transcripts under
`data/corpora/how-to/build-craft/tubeguruji/<id>.txt`).

| id | slug | instruction | TubeGuruji videos | source | carried by |
|---|---|---|---|---|---|
| TG-01 | demo-first | Write the finished app down as a click-through (every screen, its one action, the observable result) before the first file. | zcYM_Gqoph4, Dsw0pMnblWg, zrdbOx0eGtM | tubeguruji-doctrine law 1 | app-studio-intake-spec, app-sub-spec-md |
| TG-02 | skeleton-is-product | Build the repeatable skeleton (landing, auth gate, sidebar dashboard, input form with quota, generation with progress, artifact view/share, credits gate); vendors are swaps behind it. | zcYM_Gqoph4, zjwj21wzs4U | tg-saas-skeleton | app-studio-intake-spec, app-studio-design-ux, app-sub-saas-skeleton |
| TG-03 | free-tier-first | Choose each vendor by its free tier first and name the paid upgrade; pay only when the product forces it. | ciXiibK7Gds, cxto0P5DSYU | tg-free-tier-engineering | app-studio-architecture-stack, app-studio-ai-features, app-sub-named-fallbacks |
| TG-04 | quota-at-creation | Enforce a quota in the one creation path per action, as a token bucket, DB counter or entitlement flag, and hit the deny path before calling it done. | zcYM_Gqoph4, ciXiibK7Gds, s28yOCBVgGw, rdaSPdCkoFQ | tg-quota-gates | app-sub-acceptance-checks, app-sub-quota-gate |
| TG-05 | durable-jobs | Never run a long multi-step AI job in the request; run it as durable steps with a status record. | -h1O73T0jmo, 6niOEjus2Vg, kxM_oEMn3IM, 31-Qfr2Pc5Q | tg-durable-ai-pipelines | app-studio-ai-features, app-sub-durable-job |
| TG-06 | plan-review-gate | Write the plan first and check it against the spec before implementing; an unreviewed plan never becomes code. | kxM_oEMn3IM, 31-Qfr2Pc5Q, O_f55bWzsik | tg-agentic-build-workflow | app-studio-meta, app-studio-builder, app-sub-feature-slice |
| TG-07 | paste-exact-error | Feed the exact error text (message, file, line) into the next fix attempt instead of restating the goal. | 5VK8rc3GXdc | tg-agent-prompt-craft | app-studio-builder, app-sub-feature-slice |
| TG-08 | one-feature-named-vendors | Work one feature per slice; name the vendor, the files touched and the observable result expected before writing code. | kxM_oEMn3IM, sxn2GPQjJgc | tg-agent-prompt-craft | app-studio-builder, app-sub-feature-slice |
| TG-09 | docs-plus-parameters | When integrating an SDK, work from the vendor's own integration docs plus the product parameters (limits, plans) in one pass. | -h1O73T0jmo | tg-agent-prompt-craft | app-sub-feature-slice |
| TG-10 | real-data-not-lorem | Seed and render coherent real data (names, amounts, dates), never lorem ipsum, on every generated surface. | tJmN2XduBVk | tg-agent-prompt-craft | app-studio-ui-judge, app-studio-design-ux, app-sub-saas-skeleton |
| TG-11 | component-scope-edits | Change the smallest component that fixes the issue; do not regenerate the page. | tJmN2XduBVk, c9qA-uhysIY | tg-ai-media-pipeline | app-studio-design-ux, app-sub-feature-slice |
| TG-12 | build-locally-first | Run the production build locally and fix it from the build log before any deploy request. | -AVtkiG0laE | tg-deploy-gotchas | app-studio-scaffold-setup, app-studio-ship-release, app-sub-next-webpack-scaffold |
| TG-13 | env-redeploy-no-cache | After any env change, redeploy without the build cache and confirm the new value is live. | zrdbOx0eGtM, s28yOCBVgGw | tg-deploy-gotchas | app-studio-ship-release, app-sub-deploy-gotchas |
| TG-14 | public-root-route | Keep / (and every public page) in the auth middleware's public-route list; a deployed landing page that demands sign-in is a shipped bug. | zjwj21wzs4U | tg-deploy-gotchas | app-studio-web-frontend, app-sub-clerk-auth, app-sub-ssr-first-paint |
| TG-15 | oauth-prod-config | Before real users: production OAuth origins and redirect URIs, the Clerk production instance, and both login and logout redirect URLs. | fh1s6UbzJ7k, hCSX5zSb3b4, saoW6BaNamc, zrdbOx0eGtM | tg-auth-wiring | app-studio-ship-release, app-sub-clerk-auth, app-sub-deploy-gotchas |
| TG-16 | ownership-authz | Gate every mutation on record ownership, not only on being signed in. | P6dha4Sq8gQ | tg-auth-wiring | app-studio-backend-data, app-sub-demo-user-auth, app-sub-clerk-auth |
| TG-17 | prompt-to-json | Have the model return JSON for a declared schema, validate it, and render or reject it; never render unvalidated model text as structure. | UgLN9O930vE, s28yOCBVgGw | tg-ai-media-pipeline | app-studio-ai-features, app-sub-llm-feature |
| TG-18 | two-stage-generation | Generate the expensive config once and apply themes or variants to it without regenerating. | c9qA-uhysIY | tg-ai-media-pipeline | app-studio-ai-features |
| TG-19 | prod-starts-empty | Expect production data stores and job dashboards to start empty; swap dev deployment URLs and keys for production ones. | fh1s6UbzJ7k, UgLN9O930vE, b_4Z_QpEd2Q | tg-durable-ai-pipelines | app-sub-drizzle-neon, app-sub-deploy-gotchas |
| TG-20 | strictmode-duplicates | Make writes idempotent: React StrictMode runs effects twice in development and duplicated rows follow. | zlZ_7VTfxUs | tg-deploy-gotchas | app-studio-backend-data, app-sub-json-store |
| TG-21 | expo-preflight | Expo: point the dev API at the Wi-Fi LAN IP, register the Android package and SHA-1 for Google sign-in, and pick APK (device) or AAB (store) on EAS. | 2n96HAqcG_w, MbiAwAp3lCA, cxto0P5DSYU | tg-expo-mobile-ai | app-studio-mobile, app-sub-expo-app |
| TG-22 | fab-sibling | Put a floating action button beside the ScrollView (absolute position), never inside the scrolled content. | bpP7PKuEjgI, c0AOwKlAz9I | tg-expo-mobile-ai | app-studio-mobile, app-sub-expo-app |
| TG-23 | prod-verification-bar | A rendered page is not a working deploy: sign in, create one artifact, fire one webhook and run one job on the production URL. | zrdbOx0eGtM, zjwj21wzs4U | tg-deploy-gotchas | app-studio-verify-qa, app-studio-ship-release, app-sub-gate-d-hold |
| TG-24 | reproduce-before-fix | Reproduce a failure and capture its exact output before changing code. | zlZ_7VTfxUs, zjwj21wzs4U, qop_fAoayWI | tubeguruji-doctrine law 8 | app-studio-meta, app-sub-feature-slice |
| TG-25 | per-step-progress | Render per-step progress for every pipeline from the job's own status record. | ciXiibK7Gds, kxM_oEMn3IM, 6niOEjus2Vg | tg-durable-ai-pipelines | app-studio-ai-features, app-sub-durable-job |
| TG-26 | llm-client-module | Create the LLM client in one util module and import it; route user-chosen models through one gateway. | sXRDL-EPtrM, fOtjNm3JoAE | tg-ai-media-pipeline | app-studio-ai-features, app-sub-llm-feature |
| TG-27 | remote-images-config | Whitelist remote image hosts in next.config and restart the server; config does not hot-reload. | OTTZEwWN4l4 | tg-deploy-gotchas | app-studio-web-frontend, app-sub-deploy-gotchas |
| TG-28 | webhooks-local | Webhooks never reach localhost: use a tunnel in development and seed demo credits directly. | O_f55bWzsik | tg-deploy-gotchas | app-sub-deploy-gotchas |
| TG-29 | corpus-security-gap | The corpus skips tests and security (keys in source lUMIj6I9fR8, RLS disabled bpP7PKuEjgI): add tests with assertions and keep keys and access rules on. | lUMIj6I9fR8, bpP7PKuEjgI | tubeguruji-doctrine known gaps | app-studio-architecture-stack, app-studio-verify-qa, app-sub-llm-feature |
| TG-30 | per-mutation-feedback | Every mutation gives visible feedback (toast), every list has an empty state and a skeleton loader, and render guards wait for data. | zlZ_7VTfxUs, YwcyE1XlUZU | tg-saas-skeleton | app-studio-ui-judge, app-studio-design-ux, app-sub-saas-skeleton |

## BENCH lessons (App Bench evidence, 2026-09-28; candidates for LA entries)

| id | instruction | evidence | carried by |
|---|---|---|---|
| BENCH-01 | Write .app-studio/spec.md and .app-studio/stack.md before the first source file. | both builders skipped them on 2026-09-28 and intake-spec and architecture-stack did not advance (runs 6415a483, 9cfde8ad) | app-studio-builder, app-studio-intake-spec, app-sub-spec-md, app-sub-stack-md |
| BENCH-02 | Server-render the app name and primary content of every contract page so a raw GET without JavaScript proves the page. | a working app failed its home-page check on 2026-09-28 because the raw HTML lacked the expected text (run 6415a483, P1) | app-studio-web-frontend, app-sub-acceptance-checks, app-sub-ssr-first-paint |
| BENCH-03 | Record a receipt or `not applicable: <reason>` for every fired lesson in the stage record. | fired lessons LA-06 and LA-09 had no receipt in either run on 2026-09-28 and the lesson validator exited 2 | app-sub-stage-record |
| BENCH-04 | Give every feature id in spec.md a Done looks like line: the screen or route, the one action, and the observable result. | bench stage gates held intake-spec with app.spec done_looks_like at 0.29 when spec.md lacked it (Fork T measurement, 2026-09-28) | app-studio-builder, app-studio-intake-spec, app-sub-spec-md |
| BENCH-05 | Name the lane on stack.md's first line (Lane: web SaaS, mobile app, ...) and say why the stack fits it. | bench stage gates held architecture-stack with app.stack lane_named at 0.26-0.28 when the lane was only implied (Fork T measurement, 2026-09-28) | app-studio-builder, app-studio-architecture-stack, app-sub-stack-md |

## Channel lessons (CH-<CODE>-NN)

Filed 2026-09-28 (Y3 merge): each row is a source of a consolidated LA-36..LA-51 lesson a prompt carries. Procedure: `capabilities/prompts/composition/app-studio-channel-lessons.md`.
V9 resolves a cited CH id only through a row here and checks the source line exists.

| id | instruction | videos | source lesson | carried by |
|---|---|---|---|---|
| CH-CDS-02 | validate the database URL at boot and throw when it is missing, so a misconfigured environment fails loudly at start instead of at the first query | OcqWu_kasck | capabilities/skills/youtube-codesistency/references/lessons.jsonl#CH-CDS-02 | app-sub-named-fallbacks |
| CH-CDS-04 | an Express global error handler must declare the next parameter (four arguments) or Express treats it as normal middleware and never routes errors to it | q3HE1dFiJBI | capabilities/skills/youtube-codesistency/references/lessons.jsonl#CH-CDS-04 | app-studio-backend-data |
| CH-CWA-01 | components whose first render depends on browser-only state must gate on a mounted flag (or use suppressHydrationWarning / skipHydration), because the server render cannot know that state | ffJ38dBzrlY | capabilities/skills/youtube-code-with-antonio/references/lessons.jsonl#CH-CWA-01 | app-sub-ssr-first-paint |
| CH-CWA-03 | a cookie set with secure:true silently breaks login on http://localhost and logout in production; make the flag depend on NODE_ENV | dllIBXa0nlE | capabilities/skills/youtube-code-with-antonio/references/lessons.jsonl#CH-CWA-03 | app-sub-deploy-gotchas |
| CH-CWA-08 | a file using usePathname/useRouter/useSearchParams must carry 'use client', or the build fails with 'this React hook only works in a client component' | 6fXNWBFPfRM | capabilities/skills/youtube-code-with-antonio/references/lessons.jsonl#CH-CWA-08 | app-sub-ssr-first-paint |
| CH-CWA-10 | handle each webhook event type with its own payload shape; one shared parse shape for all events is a silent data-loss bug | S-4DrLHtL1s | capabilities/skills/youtube-code-with-antonio/references/lessons.jsonl#CH-CWA-10 | app-sub-quota-gate |
| CH-CWA-12 | run the production build mid-build, not at the end; a failed build at that point is almost always a type or lint error, not a runtime bug | CAr02YlEJUc | capabilities/skills/youtube-code-with-antonio/references/lessons.jsonl#CH-CWA-12 | app-sub-feature-slice |
| CH-GXD-01 | install error monitoring in the first scaffold commit, before features, and prove one induced error reaches the dashboard | Snw0b-PMhsU | capabilities/skills/youtube-galaxies-dev/references/lessons.jsonl#GXD-01-error-monitoring-first | app-sub-observability |
| CH-GXD-03 | test purchases on a real device or the store sandbox; a simulator run is not evidence the store integration works | XaMUNPzwFwo | capabilities/skills/youtube-galaxies-dev/references/lessons.jsonl#GXD-03-iap-needs-real-device | app-sub-quota-gate |
| CH-GXD-05 | run documentation snippets as written and diff them against the installed versions before adopting; docs code is not assumed to work | W9bbVJwCyqo | capabilities/skills/youtube-galaxies-dev/references/lessons.jsonl#GXD-05-docs-snippets-drift | app-sub-feature-slice |
| CH-JSM-01 | never reference window.location, document, or other web globals in React Native code; grep the bundle for those identifiers and replace with the platform navigation API | 4nVoLX2taFg | capabilities/skills/youtube-javascript-mastery/references/lessons.jsonl#CH-JSM-01 | app-sub-expo-app |
| CH-JSM-02 | on npm ERESOLVE or dependency mismatch, re-run the install with --legacy-peer-deps and record which package forced it, instead of hand-editing versions | 41lfYQhUzRs | capabilities/skills/youtube-javascript-mastery/references/lessons.jsonl#CH-JSM-02 | app-sub-sandbox-rules |
| CH-JSM-03 | never throw on a missing environment variable at module import time; validate env inside the code path that needs it, or importing the file from anywhere kills unrelated routes | I1V9YWqRIeI | capabilities/skills/youtube-javascript-mastery/references/lessons.jsonl#CH-JSM-03 | app-sub-named-fallbacks |
| CH-JSM-05 | for a single-page app, add the catch-all rewrite to index.html (dot-asterisk -> /index.html 200) in the host config before deploying, or deep links 404 in production | ek7hmv5PVV8 | capabilities/skills/youtube-javascript-mastery/references/lessons.jsonl#CH-JSM-05 | app-sub-deploy-gotchas |
| CH-JSM-06 | never let one failed fetch blank a whole screen; guard the conditional render and console.log the error instead of replacing the list with an error state | 8vIDZO_w7lY | capabilities/skills/youtube-javascript-mastery/references/lessons.jsonl#CH-JSM-06 | app-sub-error-states |
| CH-JSM-08 | package thrown errors inside the page UI; a raw error popup that replaces the whole app is a release blocker, not a nice-to-have | I1V9YWqRIeI | capabilities/skills/youtube-javascript-mastery/references/lessons.jsonl#CH-JSM-08 | app-sub-error-states |
| CH-JTC-01 | pick one package manager for the project, prove install + build work with it, and record why before adding another | 06g6YJ6JCJU | capabilities/skills/youtube-josh-tried-coding/references/lessons.jsonl#JTC-01-one-package-manager | app-sub-sandbox-rules |
| CH-JTC-04 | prove the payment provider key is loaded in the runtime that calls it before debugging router code; a linked-router error is usually a key-loading error | vEQlN17miq8 | capabilities/skills/youtube-josh-tried-coding/references/lessons.jsonl#JTC-04-provider-key-before-code | app-sub-named-fallbacks |
| CH-LMA-05 | every Express middleware must end with next() on the pass-through path, or the request hangs and no later handler or error handler runs | csUM7yfiaMw | capabilities/skills/youtube-lama-dev/references/lessons.jsonl#CH-LMA-05 | app-studio-backend-data |
| CH-LMA-07 | form payloads arrive as strings; coerce and validate the declared type in the schema, or the parse fails on input the user correctly typed | rNSzejRkHcg | capabilities/skills/youtube-lama-dev/references/lessons.jsonl#CH-LMA-07 | app-studio-backend-data |
| CH-LMA-09 | check response.ok on every fetch and throw on failure, or the UI renders an empty page that looks like a valid empty result | DpYE5zPDRVQ | capabilities/skills/youtube-lama-dev/references/lessons.jsonl#CH-LMA-09 | app-sub-error-states |
| CH-NJD-01 | wrap forms in KeyboardAvoidingView with the right offset and respect the safe-area inset, or the keyboard covers the input and the field looks detached from the screen edge | CC0H9xz29JI | capabilities/skills/youtube-notjust-dev/references/lessons.jsonl#CH-NJD-01 | app-sub-expo-app |
| CH-NJD-02 | after adding a native module or an Expo config plugin, run npx expo prebuild and rebuild the app; a dev-server restart does not pick up native changes | CC0H9xz29JI | capabilities/skills/youtube-notjust-dev/references/lessons.jsonl#CH-NJD-02 | app-sub-expo-app |
| CH-NJD-04 | use the StatusBar exported by expo-status-bar, not the React Native one, or the bar renders black-on-black and disappears on themed screens | rIYzLhkG9TA | capabilities/skills/youtube-notjust-dev/references/lessons.jsonl#CH-NJD-04 | app-sub-expo-app |
| CH-PYG-02 | start the dev server and drive one real request with the network tab open; a running server is not a working feature | pb_jYgSqGh0 | capabilities/skills/youtube-piyush-garg/references/lessons.jsonl#PYG-02-drive-one-real-request | app-sub-verify-md |
| CH-SSG-02 | reproduce on first load AND after client navigation, then fix the mismatched value at its source (one date/number formatter) instead of suppressing the error | 7DVdVGm7Ht8 | capabilities/skills/youtube-sonny-sangha/references/lessons.jsonl#SSG-02-ssr-client-mismatch | app-sub-ssr-first-paint |
| CH-SSG-03 | name the invalidation for every cached read: after a write, the next read must return the new value, proven with a second request | PoMEGxNLwFc | capabilities/skills/youtube-sonny-sangha/references/lessons.jsonl#SSG-03-stale-cache-invalidation | app-studio-backend-data |
| CH-SSG-06 | run the charge path twice with the same idempotency key and assert exactly one charge; every tool-called payment function must be idempotent | OZLdtusYmzw | capabilities/skills/youtube-sonny-sangha/references/lessons.jsonl#SSG-06-idempotent-charge | app-sub-quota-gate |
| CH-SSG-12 | drive the built feature in a real browser session and record the interaction, instead of declaring it works from code reading | KHFUtD9go1E | capabilities/skills/youtube-sonny-sangha/references/lessons.jsonl#SSG-12-verify-in-real-browser | app-sub-verify-md |
| CH-TRV-03 | prove one failing request surfaces in both the API and the client with its request context captured, not just a console line | NKiTlo_dgb8 | capabilities/skills/youtube-traversy-media/references/lessons.jsonl#TRV-03-error-both-ends | app-sub-observability |
| CH-TRV-04 | treat a build that passes with lint warnings as not clean: fix or explicitly waive each warning before shipping | 5zR1ZE5aqho | capabilities/skills/youtube-traversy-media/references/lessons.jsonl#TRV-04-lint-warning-is-not-clean | app-sub-feature-slice |
| CH-TRV-08 | no error is swallowed to keep a demo moving: every catch fixes, rethrows, or logs with enough context to act | oIx7ObcfdlU | capabilities/skills/youtube-traversy-media/references/lessons.jsonl#TRV-08-no-suppressed-errors | app-sub-error-states |
| CH-TRV-10 | guard every element/ref access against the empty state and test the screen with zero records | QsH8FL0952k | capabilities/skills/youtube-traversy-media/references/lessons.jsonl#TRV-10-empty-state-element-guard | app-sub-saas-skeleton |

## Composed-prompt checks

- A full composed builder prompt (49 to 53 KB) timed out System One (decisions 119669, 119675: failing closed,
  no answers). That is DEFERRED, not a verdict; the library texts it is built from each passed on their own.
- The task-filled sections judged on their own: builder section PASS 119687 (tg-expense-tracker) and 119688
  (tg-ai-form-builder), meta section PASS 119683 and 119685.
- The legacy render (A arm) judged by the same rubric: ESCALATE 119676 (contract 0.27, lessons 0.47).

## Seam for channel-derived lessons

Lessons mined from the JSMastery-like build channels enter as new `app-sub-*` prompts with a parent among
the 15 main prompts (and as TG-style rows in a table here keyed by their own prefix), each with video-id
evidence, a JEV app.prompt PASS before filing, a rule in `bench/prompt-rules.json`, and a row in
`scripts/build_hierarchy.py` PROMPTS. The lesson filer (`app-studio-lesson-filer`) owns that path.
