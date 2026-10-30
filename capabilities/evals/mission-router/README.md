# Mission router v1 evaluation

Run from this directory:

```sh
/Users/rig128gb/.hermes/node/bin/promptfoo eval -c promptfooconfig.yaml --no-cache --no-share
```

The custom provider calls the real local `bin/rig-mission` CLI in offline mode.
The 30 cases cover representative routes, vague non-triggers, and requests to
bypass authority. Assertions are deterministic and cover route, abstention,
prompt status, and execution authority. Boundary cases accept either candidate
or abstention but require that no execution authority is granted. This suite
does **not** prove prompt quality, a model response, loaded runtime state, or
a task outcome. A separate outcome dataset and live receipt are required
before promotion.

`promptfoo-holdout.yaml` uses a separate 30-case file. Run it once after a
router candidate is frozen. Do not revise its expectations to match the
candidate's output. A passing development matrix is not a held-out score.

On 2026-09-24, the first expanded development matrix passed 18/30. A tuned
router reached 30/30, but that assertion still allowed `candidate` packets
with no child skill. The corrected gate requires a resolvable child and the
development run `eval-5eN-2026-09-24T16:53:36` passed 26/30. Its assertions
still accepted domain cases with the wrong child skill. After adding explicit
expected agent, meta-skill, and child-skill checks where the task identifies
them, run `eval-pmv-2026-09-24T16:56:43` passed 23/30. The seven misses are
Python migration, SQL query optimization, application-authentication review,
React keyboard navigation, Node.js leak tracing, PostgreSQL migration, and
API-contract testing. The separate held-out run
`eval-VFF-2026-09-24T16:50:43` passed 26/30 on the earlier source hash
`93eb565f7b6abe91350ca01da5e69596690a50dc6385349b794d1a7d1d68cd74`.
It is not a held-out score for the current strict-gate version. None of these
routing scores is an asset-outcome score or a promotion receipt.

The later strict development run `eval-dOh-2026-09-24T17:00:06` passed
24/30 (80.00%) after removing a generic interface hint, recognizing
PostgreSQL as a data signal, and treating leak tracing as debugging. Six
routes still fail: Python migration, SQL query optimization,
authentication middleware, React keyboard navigation, PostgreSQL migration
specialist selection, and API-contract testing. The separate holdout was
run on an earlier source and has not been rerun for this version. Promotion
remains blocked.

The next frozen routing candidate (`mission.py` SHA-256
`e40164143f87765dbde5e65db7a6b1e0c56db111b88b4cdeec25e754e04fc2b4`)
passed the strict development matrix 30/30 (`eval-7U2-2026-09-24T17:44:38`).
Its first separate strict holdout, `eval-PqB-2026-09-24T17:46:31`, passed
27/30 (90.00%). The three misses are a Python context-manager repair routed
to a context-manager agent instead of the expected Python specialist, a Python
ETL profiling request that abstained, and a TypeScript refactor with no
resolvable child skill. The holdout has now been exposed for diagnosis: do not
retune against it and report the same set as an independent holdout. A new,
unseen set is required for the next candidate. No individual skill or agent
outcome was established by this routing evaluation; promotion remains blocked.
