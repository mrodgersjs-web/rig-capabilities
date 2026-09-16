# Chunked offload through PAIR — decisions and measured reality

Date: 2026-09-15. Every number below came from a command run on this box; anything unmeasured
is labelled. Read the two corrections first — they change what "offload" should even mean here.

## Correction 1: the 128GB box is not inference-bound

The stated goal was "limit the work done on the 128GB so we can run more terminals". Measured:

| Measure | Value |
|---|---|
| Installed / used / unused | 128 GiB · 102G used · 24G unused |
| Memory-pressure headroom | 94% · zero compression, zero swap |
| CPU idle | 68.84% |
| **All local model-serving/routing processes** | **0.697 GiB RSS combined** |
| Agent executables (18 OMP runtimes, 13 TTY shells, 58 node procs) | ~11.35 GiB |
| Browser/Electron | ~18.93 GiB |

Local inference is already ~0.7 GiB — it is not what is consuming the box. Offloading
*inference* therefore buys almost nothing in RAM. What consumes the box is **orchestration
sprawl**: agent runtimes, shells, and browsers, roughly 30 GiB between them.

So the 10x lever is not "move model calls off-box" (they are already off-box: PAIR's own
ledger shows 29/29 recent requests scheduled on remote nodes, 0 local). The lever is:

1. **Move agent *loops*, not just model calls.** An OMP/Codex runtime deciding steps locally
   costs ~0.6 GiB each; the inference it triggers costs ~0. `~/.rig/node-ops` already ships
   agent work to remote nodes over SSH — that plane, not PAIR, is where terminal headroom
   comes from. It is currently DEGRADED (100 queued, `ready_count=0`, controller state
   DEGRADED) and dispatches remote **Codex CLI**, not PAIR.
2. **Cap concurrent local runtimes.** 18 OMP runtimes is the measurable footprint; that is a
   policy decision, not an engineering one.

## Correction 2: PAIR routes, it does not chunk — and it has no backpressure

PAIR at `127.0.0.1:11435` is a bundled `ollama-proxy` 0.26.2 under `nvpair-ui-broker` 0.40.2.
NVIDIA's own division of labour is "Hermes decomposes / PAIR routes / Ollama executes".

Verified behaviour:

- `/v1/models` 200 with 17 models; `/api/tags` 200; `/api/ps` 200; embeddings 200 (dim 768).
- `/health`, `/metrics`, `/stats` are **real 404s** — never use `/health` as a rollout probe.
- `/v1/responses` is **not model-aware**: `qwen3:4b` 404s there while working on
  `/v1/chat/completions`. Any client must pin Chat Completions.
- **No queue, no max-concurrency.** Requests are forwarded immediately; PAIR only retries
  upstream 429s across owners. Backpressure is the caller's job — that is why
  `rig-chunk dispatch` owns a semaphore (`--max-inflight`, default 4) and exponential backoff.
- Measured parallelism: 6 concurrent requests across 6 models, 6/6 HTTP 200, wall 28.3s vs
  82.1s serial (**2.9x**), no 429.
- Placement is **provable**: `workloads-history.json` records `originatedFrom` and
  `scheduledOn` node UUIDs per request. `cluster/members.json` names 7 members.
- PAIR is **loopback-only**. A remote worker cannot reach this Mac's 11435; it must call its
  own local PAIR, which then places the request. This dictates worker topology.

## Decision: model choice IS node choice

PAIR places a request on a node that owns the model. There is no "run this on the 96GB" flag,
so the only placement lever a client has is **which model it asks for**. `rig-chunk` therefore
resolves work class -> model -> observed owning nodes, and grades each choice:

- `offload-proven` — PAIR has scheduled this model on a remote node before.
- `local-only` — every observation ran here; fanning it out would be a lie. **Refused** unless
  `--allow-local-only`.
- `unproven` — never observed; allowed, but `verify` decides after the run.

Current inventory: 7 offload-proven models, 0 local-only. Note `rig-128gb` also owns
`qwen3.8:27b` and `qwen3-coder:30b`, so naive dispatch of those can land back on this box —
which is exactly what `verify` catches.

## Decision: the criticality gate is fail-closed toward Mike

Design and critical work stays local by construction. A chunk is held local if it touches
design authority (design/architecture/API surface/schema/migration/rename/naming convention),
the control plane (approval/permission/budget/retry policy/idempotency/kill switch/Gate-D),
an outward effect (publish/deploy/push/send/payment/delete/revoke/rotate), a security boundary
(credential/secret/token/private key/PII/PHI), or the instruction surface (doctrine/AGENTS.md/
system prompt) — or if it is irreversible, has `failure_cost >= 0.5`, or **has no acceptance
check** (work nobody can verify cannot be delegated). A chunk missing the fields needed to
judge it is REFUSED, never quietly fanned out.

Scope matters: design patterns are matched against the *work* (title + prompt) only, while
effects/controls/secrets are matched in the acceptance text too. First cut scanned everything
and held a chunk whose acceptance read "single word naming a color" as an API-naming decision
— a gate that trips on prose keeps everything local and defeats the purpose.

Carrier selection is **not** re-implemented: `rig-chunk` calls
`/Users/rig128gb/.rig/bin/rig-owner-router`, the executable form of
RIG_OWNER_ROUTING_DOCTRINE.md. A missing router reports `review-required`, never a guess.

## Lane status, honestly separated

| Lane | State | Evidence |
|---|---|---|
| **PAIR direct** (`rig-chunk plan/dispatch/verify`) | **WORKING** | `run` exit 0; 2/2 dispatched; `OFFLOAD_PROVEN`; chunks landed on RIG-36GB-Mac-Studio and RIGs-MacBook-Pro; design chunk held local |
| **Pydantic AI typed** (`chunk_agent.py`) | **WORKING** | Validated `Answer(color='Red')` in 7.5s through PAIR; history row 86 -> RIGs-MacBook-Pro |
| **Temporal durable** (`chunk_temporal.py`) | **EXECUTES; NOT DEPLOYED** | Ephemeral smoke: 2/2 activities, `all_remote: true`. Workers must move to remote nodes — activation is Gate-D |
| **Kestra scheduled** (`workflows/kestra/rig-chunk-fanout.yaml`) | **DORMANT — blocked** | Plane executes nothing: 27 enabled schedules in `main.rig`, **0 executions in 7 and 90 days**; PROCESS tasks run in-container against unmounted host paths |

Environment fix required and applied: no interpreter had both SDKs (`~/.hermes/.../venv` has
`pydantic_ai` but an incompatible `openai` — `pydantic_ai 2.22.0` imports `Moderation` from
`openai.types.chat.completion_create_params`, absent in `openai 2.24.0`; `~/.rig/meta-harness/.venv`
has `temporalio` and no `pydantic_ai`). Created `~/.rig/state/venvs/chunk-lane`
(`pydantic-ai-slim 0.8.1`, `openai 2.48.0`, `temporalio 1.18.2`) rather than mutating live envs.

## Recommendations, in order of payoff

1. **Repair the node-ops agent plane before adding anything.** It is the only plane that moves
   *agent* work off-box, and it is DEGRADED with 100 queued / 0 ready. Fixing it converts
   directly into terminal headroom; PAIR offload does not.
2. **Deploy one Temporal worker on a remote node** (`chunk_temporal.py worker`), using that
   node's own PAIR. Today all three live queues poll from this Mac, so Temporal currently adds
   local load. Requires the lane venv on the node. Gate-D to activate.
3. **Do not register the Kestra flow until the plane executes.** 27 schedules with 0 executions
   in 90 days is decorative green. Fix the container/host-path mismatch (mount the repo + reach
   host `11435`) or install a Kestra remote worker on a node. Then enable one flow and prove
   an execution before adding more.
4. **Never trust `/health` on PAIR** (404) and never read placement from config — read
   `workloads-history.json`. `rig-chunk verify` exits 2 on `UNPROVEN`, which is the correct
   default: absence of evidence is not offload.
5. **Cap local OMP runtimes.** 18 live runtimes is the measured cost; no amount of inference
   routing addresses it.

## Known limits of what was built

- `verify` matches history rows by `(model, start-time window)`, not by a request id PAIR does
  not return. Concurrent identical-model dispatches inside the same window can therefore be
  matched to each other's rows; the verdict per chunk stays correct (all matched rows are
  checked against the local UUID) but per-chunk attribution is not unique.
- PAIR flushes `workloads-history.json` *after* the HTTP response, so `verify` polls for up to
  `settle_s` (15s). A first read immediately after dispatch reports a false `UNPROVEN`; this
  was observed and fixed, not assumed.
- `rig-chunk` does not decompose prose into chunks. The mission JSON declares chunks; splitting
  a goal into units remains a judgment call and deliberately stays with Mike.
