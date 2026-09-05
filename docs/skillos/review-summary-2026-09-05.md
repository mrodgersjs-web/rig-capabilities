# Canonical review summary — 2026-09-05

Tracked, sanitized companion to `.context/tessl-review-batch/` (run IDs only, no credentials).

## Tessl accounting

- Canonical assets: **140**; review records: **280** (terminal: 280)
- Supported (skill): **29** → security 29/29 completed, quality 29/29 completed, **failed 0**
- Unsupported (non-skill) records: **222**
- Quality score (completed): min 66, max 99, mean 85.86
- Verification checks: **11/11 pass**

## Accepted security findings

- `iqrsqpi-v20` MEDIUM W011 — Third-party content exposure detected (indirect prompt injection risk).
- `semgrep` MEDIUM W011 — Third-party content exposure detected (indirect prompt injection risk).

Accepted (inherent untrusted-content exposure): `iqrsqpi-v20`, `semgrep`

## Supported-skill runs (id · sha · security run · quality run · quality score)

| skill | catalog sha | security run_id | quality run_id | score |
|---|---|---|---|---|
| adversarial-verification-loop | `892216101095` | 01a06f90-1066-7201-be38-9526cf0fd081 | 01a06f90-4eaf-70ba-ab37-9d879c5f1f48 | 82 |
| codeql | `0f016f6d34c0` | 01a06fa5-80c5-7673-815b-454ad2371cb0 | 01a06fa5-807c-7133-bc17-6a957b1a58cd | 92 |
| differential-review | `249fb79d2a5a` | 01a06fa5-8087-73d3-9d03-c311a1179a7a | 01a06fa5-9ffd-7029-b7eb-42cfe943d10d | 78 |
| evaluator-forge-from-exemplars | `1da9c311c67c` | 01a06f93-e5f4-7066-b95b-85b4284c178c | 01a06f94-ba9f-77d4-8462-10c60e960acd | 88 |
| evidence-retrieval-citations-gate | `afe28f7a5500` | 01a06f93-f810-744f-904b-9122cb8cfc8c | 01a06f94-c0a6-734b-99a4-0d0f43a04389 | 91 |
| experience-lesson-records | `665e2e4aada6` | 01a06f93-fb18-75b9-85fd-ad6f9341e4aa | 01a06f94-c097-7788-9baa-775fcb20f2c8 | 91 |
| gamma-trace-record-and-failure-attribution | `27c3a35b35f3` | 01a06f93-fbc5-737f-93db-6843806a160b | 01a06f95-ad2c-7283-861e-fcfb866a0061 | 85 |
| gate-d-loop | `f90143d5deaa` | 01a06f94-0a54-7314-831b-a74f3e9118fb | 01a06f95-b56b-770d-a85f-84769b19f7a0 | 82 |
| git-push-safety-loop | `66ba95592c26` | 01a06f94-0eb5-7336-a775-6c707fc3708d | 01a06f95-df86-7261-a8af-cc58b7772dab | 90 |
| iqrsqpi-v10 | `85254b508fcd` | 01a06fa5-a13b-7246-8ff8-8e423ac77548 | 01a06fa5-b3b4-741e-9c94-e161f370cc2d | 88 |
| iqrsqpi-v11 | `c00ee555ba9f` | 01a06f94-1ef7-7596-82fb-d0565535700b | 01a06f96-96cd-757a-abdf-a74ef68f9413 | 86 |
| iqrsqpi-v20 | `0d9feab80109` | 01a06fa6-9091-75f1-bba7-b7856852a085 | 01a06fa6-a60c-74ca-be3a-6bcdf344ce34 | 76 |
| iqrsqpi-v20-slice | `f75f7b7e3dc6` | 01a06f94-2eb8-73c2-880e-2812239379b3 | 01a06f96-d839-7663-9ddf-9b8ec9ae6d7e | 80 |
| north-star-lock-loop | `9a048d11c80b` | 01a06f94-33e6-7257-9a6d-abb29c1d20fa | 01a06f97-3e2d-753c-ad7c-e4ae7028dd3c | 82 |
| phase-discipline-loop | `ea048f0c8b77` | 01a06f94-401f-7409-9870-e284c48046b0 | 01a06f97-a179-7450-8c9f-fd920dd42840 | 81 |
| proof-loop | `72e90bde04ab` | 01a06f94-46ab-743c-a88c-f436f4717c8e | 01a06f98-09a6-718e-96cb-17acecc76fa6 | 83 |
| rig-agent-team | `ed17961b4a04` | 01a06fa6-b4e0-758c-9349-dfaf7e4f1514 | 01a06fa6-c9d3-73af-9361-1ad23fdf953c | 81 |
| rig-anti-fabrication-dispatch | `c0c073e30841` | 01a06fa7-41d7-775a-b3ff-9bc9bc8e8264 | 01a06fa7-53e1-7506-afa1-767fdfce36e2 | 91 |
| rig-deviation-engines | `0d8344825802` | 01a06f94-5896-76ab-ba3a-70f03e29e019 | 01a06f98-3ffd-7226-a4d9-ae4c082e5612 | 91 |
| rig-idea-generator | `6cbaa13a9ec3` | 01a06f94-5ef3-74b6-83c6-c36d9d6273cb | 01a06f98-aeeb-76b7-b94f-a606059e76bb | 91 |
| rig-known-expert-os | `95ce3146b14a` | 01a06fa7-69d9-7191-90b1-e075079577e6 | 01a06fa7-8589-7073-bbd9-9feac07e232e | 86 |
| rig-lattice-system | `66a8dcb66802` | 01a06f94-78ee-7596-8ec1-357c37c611c8 | 01a06f99-8242-7067-87c7-8edaa2ad8f0b | 90 |
| rig-office-docs | `adbbeed8ebe8` | 01a06fa8-12dc-7339-9141-49d10082626e | 01a06fa8-1486-75b9-ac39-c0404fa8c573 | 99 |
| sarif-parsing | `90f213ac3160` | 01a06fa8-2540-7192-995c-9537240b1c98 | 01a06fa8-3758-7148-86d1-2acc438bd699 | 88 |
| security-threat-model | `49b92c9cbb58` | 01a06fa8-a056-7788-a433-7df413284ddc | 01a06fa8-b361-75a4-bbc2-9f7fcb07e9ea | 90 |
| semgrep | `b64f86b73e09` | 01a06fa9-3486-74a9-be5c-96116f036c45 | 01a06fa9-4672-7720-ba03-f7f68542893a | 94 |
| semgrep-rule-creator | `eedecc390ca1` | 01a06fa9-6430-70a0-bb95-d27ba0ce7ad5 | 01a06fa9-7424-740f-a4a5-4912b974e261 | 91 |
| skill-upgrades | `63afa4691041` | 01a06f94-9ce9-704d-a2e4-923bddbc833d | 01a06f99-dbc7-7399-9491-234bd0d0c017 | 77 |
| threat-mitigation-mapping | `c3403b1fc27a` | 01a06fa9-7618-7582-abe5-24378e92b0f4 | 01a06fa9-87be-7414-a072-f6d1db1407fc | 66 |

## Snyk (local CLI)

- `snyk code test --org=rodgemd1` exit 1: **272 findings — 0 high, 26 medium, 246 low** (untriaged; not a clearance)
- `snyk test` (deps): no supported manifests (stdlib-only)
