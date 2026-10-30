---
name: swarm-harness
description: "RIG doctrine as a loop-skill — Swarm harness (GL-SW/GL-AD). Governed parallel-agent dispatch: identity lock, agent-count, angle uniqueness, convergence, synthesis, cross-family verify."
version: 11.1.0
outcome: "agent-engineering: Swarm harness (GL-SW/GL-AD) enforced as a gated loop with hooks"
done_when:
  - "cmd:python3 bin/rig-loop test swarm-harness"
  - "file:capabilities/skills/swarm-harness/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.7
metadata:
  loop_skill: v11
  doctrine_source: "capabilities/loops/swarm-harness.md"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill swarm-harness"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# Swarm harness (GL-SW/GL-AD) — loop-skill (v11 contract)

Source doctrine: `capabilities/loops/swarm-harness.md`

## Step 0 — activate (every harness)

```bash
rig-loop activate swarm-harness --intent "<one sentence>"
```

## Stages (each artifact + deterministic gate goes RED on its own)

| Stage | Artifact | What the gate refuses |
|---|---|---|
| `I1` Identity-lock | `intent.md` | No `## GOAL` / `## SWARM-TYPE` (must be `GL-SW` or `GL-AD`) / `## AGENTS` / `## FILE-OWNERSHIP` / executable `## DONE-TEST`. Nothing spawns before this. |
| `W` Wire-lease | `spawn.md` | Fewer than 3 rows of the form `- agent: <id> model: <pinned> writes: <paths>`; any `model:` containing **flash**; `spawn_confirmed` counter < 3. A worker with no named model, or two workers on one path, blocks here. |
| `D` Diverge | `divergence.md` | Fewer than 3 distinct `- angle:` lines; fewer than 3 files actually written by workers. Two workers on one angle is duplicated spend, not divergence. |
| `C` Converge | `convergence.md` | Missing `## Conflicts` / `## Agreement`, or zero named conflicts. A swarm that only agreed was never diverging. |
| `Y` Synthesize | `synthesis.md` | Claims that do not carry a `- [w:<worker>]` attribution; an empty `## Claims`. |
| `V` Verify | `verify.md` | No verdict from a **different model family** than the builder (`independent_verdict`), no planted failure proven RED→GREEN. Same-family approval is refused. |
| `P` Proof | `proof.json` | Unsealed run. |

## Why these gates and not softer ones (2026-09-29, measured)

34 pinned-model workers ran in one swarm today (22 Grok writers, 12 MiMo rival-family verifiers)
with no engine governing them. What that cost, and what each gate above now blocks:

- A `studio-corpus/laws/*.md` file was **wiped by a parallel write** → `W` demands one named writer per path.
- MiMo timed out and MiMo/Grok workers died **after returning an empty message**, leaving nothing on disk → `D` requires files actually written, and the worker brief must save every ~5 rows.
- An unqualified fallback silently routed to Blackwell **Flash** and died on `terminated` → `W` refuses a flash model by name.
- The citation existence gate passed 14,245 refs and still let through citations whose cited second does not state the law; only a **cross-family** judge caught it (92.0% precision over 1,175 judged, 45 re-anchored, 37 withdrawn, 12 laws deleted) → `V` refuses a same-family verdict and refuses a verifier that never went RED.

## Running it

```bash
rig-loop activate swarm-harness --intent "<one sentence>"   # then fill intent.md
rig-loop stage I1 pass && rig-loop counter spawn_confirmed --set 3 && rig-loop stage W pass
# ... D, C, Y, V each need their artifact; V needs: rig-loop verify --family <not the writer family>
rig-loop seal && rig-loop stage P pass
rig-loop test swarm-harness    # 6 cases, 3 planted failures proven RED
```

## Closing loop / kill switch

See loop.yaml. Escalate to Mike when the closing loop is exhausted.

## What the first live run taught (2026-09-29, run `swarm-harness-20260929T221343Z-6591c2`)

8 workers, 7 delivered, 1 stalled at 0 rows (12.5% worker loss), 42 candidate upgrades,
5 of 7 gates passed, **Verify parked** - and the reasons are mechanical, not philosophical:

1. **`rig-loop wire --harness` has no `aside` root** (claude/codex/hermes/omp/prime-agent only).
   An Aside-driven swarm emits no write telemetry, so `files_written_min` reads 0 while eight
   worker files are verifiably on disk. Diverge had to be `--force`d with the reason recorded.
   Fix: add an `aside` root or a `rig-loop files add <path>` register verb.
2. **`independent_verdict` accepts only those same five harness families**, so it cannot express
   the thing cross-family verification actually means on this machine: `grok-4.7` writers judged
   by `mimo-v2.6-pro` and vice versa. The gate is right; the family list is wrong.
3. **`rig-loop artifact <stage> <path>` replaces the stage artifact**, it does not append. Binding
   eight worker files to Diverge made the gate look for `## Angles` inside the last one.
4. **`stage <S> park` parks the whole run**, and `resume` takes a positional run id with no
   `--cwd`, unlike every sibling verb.
5. **A verifier brief that treats a mutable counter as a load-bearing claim manufactures false
   REFUTATIONS.** The rival-family pass over w7/w8 returned 8 SUPPORTED, 2 MISPLACED (step WORDS
   where the lattice needs step CODES - `quality`, `research`, `produce`) and 9 UNSUPPORTED, and
   most of the UNSUPPORTED rows were just a number that moved between dispatch and verdict
   ("waiting is 120 not 81", "Jev 17.4% not 15.2%", "db is 229,679,104 not 229,670,912"). Two
   refutations were substantive and stand: the 485 unconverted captions already had markdown
   siblings, and `harvest.sh` already dedupes by videoId. So a verifier brief must say:
   **cite the number you observed with its timestamp; a drifted number is a re-count, not an
   UNSUPPORTED; only a claim whose artifact does not exist or whose test cannot fail is refuted.**
