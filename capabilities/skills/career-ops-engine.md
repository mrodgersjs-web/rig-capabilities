---
name: "career-ops-engine"
description: "Score and tailor against a job posting with the adopted career-ops engine (MIT, 78.6K stars) instead of free-handing it. RIG Jobs stays the ledger."
---

# career-ops-engine — the scoring/tailoring engine behind RIG Jobs

Adopted 2026-10-29. Upstream `career-ops-hq/career-ops` @ ef9006f, v1.38.0, MIT, 78,676 stars, pushed the day of adoption. Clone: `~/Developer/adopted/career-ops-hq/career-ops` (74 MB, deps installed, `node doctor.mjs` passes).

## What it is for, and what it is not

It answers one question well: **does this specific posting fit Mike, 1-5, and what does the tailored packet look like.** That is the per-role resume doctrine (`doctrine/job-resume-per-role.md`) turned into a machine.

It is **not** the record of what was applied. RIG Jobs (:3211, `jf_roles` 190 in queue, 613 Gmail-confirmed applications, 18 interviews) stays the single ledger. career-ops has its own `data/pipeline.md` and `output/` inside the clone - scratch, never a source of truth, and never synced outward.

## How to call it

```bash
cd ~/Developer/adopted/career-ops-hq/career-ops
node doctor.mjs                      # 3 warnings while cv.md is still staged empty
node openai-eval.mjs --help          # direct-API evals; --url takes an OpenAI-compatible base
```

Local models, no spend: `OPENAI_BASE_URL=http://127.0.0.1:18811/v1` (sglang `qwen3.8-flash-next-uncensored`, the same router OpenOutreach and OpenSDR already use). Do not add a paid key without Mike's word.

## The two gates before first use

1. **`cv.md` is deliberately empty.** It must be filled from the Mike-approved working resume (`~/.rig/live/aside-work/resume-artifacts/r_q8z4jgd3/`) and read by him, because every job resume is his own approval floor - a generated draft does not satisfy that. The engine will happily write a plausible resume out of a wrong cv.md, which is the failure this gate exists for.
2. **Nothing submits.** career-ops' own README makes the same promise Mike does: it drafts, **you press Submit**. `config/profile.yml`, `modes/_profile.md` and `portals.yml` are still the shipped example templates - placeholder content, so treat anything they imply as unset.

## Do not

- Do not run `npx @santifer/career-ops init` until the install shape is decided; it writes into `~/.claude`, which the Aside skill surface shares.
- Do not start `npm run ui` (8 web deps missing) or the `cops` docker wrapper - no Docker daemon here.
