# SkillOS provenance — clean-room, non-copy

Tessl is a **behavior benchmark**, not a source tree to fork.

## License wall

`tesslio/cli` is public GitHub but contains only `README.md` + `LICENSE.md`.
The license states:

> Copyright 2025 Tessl. All rights reserved.
> This software is proprietary to Tessl and is subject to Tessl's Terms of Service.
> Unauthorized reproduction or distribution is prohibited.

Source: https://github.com/tesslio/cli/blob/main/LICENSE.md

**RIG must not** clone, vendor, decompile, or reimplement from Tessl CLI internals.
No Tessl source, prompt text, rubric JSON, or eval harness code enters this repo.

## Allowed inputs (behavior only)

| Source | Use |
|---|---|
| https://docs.tessl.io (published docs) | product/behavior facts, cited |
| `tessl --help` and subcommand help on a locally installed binary | observed CLI surface |
| https://tessl.io and `/registry` public pages | marketplace behavior |
| Public MIT tesslio repos that are **actions, tiles, or examples** (not the CLI) | observed packaging *shapes* (SKILL.md, evals/, tile.json) — describe, do not copy files |
| RIG's own `rig-capabilities` tree | implementation substrate |

## Disallowed

- Forking `tesslio/cli`
- Reusing Tessl review rubrics, judge prompts, or eval sandbox code
- Publishing RIG assets *to* Tessl as the upgrade path
- Naming RIG APIs as Tessl clones (`tessl review` → not a verb we copy)

Independent specs in this folder are the only implementation contract.

## Claim rule

Every Tessl fact in `01-TESSL-BENCHMARK.md` carries a URL. Unsourced Tessl claims are dropped.
