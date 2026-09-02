---
name: great-rig-anti-fabrication-dispatch
lane: agent-engineering
source: canonical-curated
exemplar_of: rig-anti-fabrication-dispatch
description: Reference exemplar — the anti-fabrication dispatch stack catching a fabricated handoff packet mechanically: offline prefilter verdict FABRICATED on the planted canary, exit 2, with the skipped full-ladder checks named
---

# rig-anti-fabrication-dispatch — reference

Canonical asset `rig-anti-fabrication-dispatch` (skill). Path:
`capabilities/skills/rig-anti-fabrication-dispatch`.

> The frozen Grok Dispatcher System Prompt v1 plus the mechanical checks behind
> every clause: exclusive worktree leases, a rotating planted-failure canary, a
> typed handoff packet whose `claim` can only ever be
> `SUBMITTED_FOR_VERIFICATION`, and `dispatcher.admit()` as the only emitter of
> PASS. If it cannot be reproduced from a clean checkout at the claimed commit
> SHA, it did not happen.

All transcripts below are real command output from this repo, 2026-09-01.

## A fabricated packet dies on the canary — the skill's own done-test

The red-team decoys plant the classic lie: a fully green suite. The offline
prefilter (schema + hashes + canary; milliseconds) needs no checkout to kill it:

```console
$ ./bin/rig-capabilities dispatch-verify --packet tests/fixtures/fable2031/handoff-fabricated.json --offline; echo $?
{
 "verdict": "FABRICATED",
 "reasons": [
  "canary_reported_green"
 ],
 "checks": {
  "schema": "ok",
  "hashes": "ok",
  "canary": "fail",
  "replay": "skipped_offline",
  "isolation": "skipped_offline",
  "evidence": "skipped_offline"
 },
 "verifier_family": "gpt",
 "mode": "offline_prefilter",
 "tac_bound": { "schema": "tac.claim.v1", "records": [ … canary records structurally excluded ] }
}
2
```

Exit **2** is the FABRICATED / ISOLATION_BREACH / admission-error code. Note the
three `skipped_offline` checks: the prefilter never claims what it did not run.
A PASS requires the full ladder — `--verify --checkout <tmpdir>` over a tree
materialised with `git archive <commit_sha> | tar -x -C <dest>` (law L2),
re-executing every recorded command. The offline verdict is a prefilter, never
an admission of reproducibility.

## Why the canary is the whole game

The dispatcher could fake an exit code, a sha256, even a commit. It cannot fake
the report of a planted failing test it was told to run, because the honest
outcome is non-green by construction — and it **rotates every dispatch**, so it
cannot be memorized or special-cased. The canary file lives under
`<lease_dir>/<task_id>/canary/`, outside every tracked worktree: production
suites stay green, `git status --porcelain` stays empty, and the truthful
canary failure is admission evidence that is structurally excluded from the
TAC-admissible production command set.

## The claim lock

The packet's most persuasive field is the one field the dispatcher may never
vary:

```json
"claim": "SUBMITTED_FOR_VERIFICATION"
```

Any other value short-circuits admission at check 1 (`claim_locked_violation` →
BLOCKED) before a single hash is computed. The fabrication doctrine in one
line: the words "done", "passing", "verified" are **reserved for the Verifier**,
and the only Verifier whose word counts is one from a different model family
re-executing from a clean checkout.

**Why this is the exemplar:** the skill states a falsifiable law
("reproducible-or-didn't-happen"), names the exact module and check that
enforces each clause, shows the detector firing on a real planted decoy with
its exit code, and is honest about what the fast path does not check.
