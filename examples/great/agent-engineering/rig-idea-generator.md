---
name: great-rig-idea-generator
lane: agent-engineering
source: canonical-curated
exemplar_of: rig-idea-generator
description: Reference exemplar — the V3.1 gates rejecting buzzword copy and accepting a mechanism-dense idea, each gate tested by forcing its exact threshold pair, seeded MAP-Elites replay, and an ASR that excludes the questions a machine cannot judge
---

# rig-idea-generator — reference

Canonical asset `rig-idea-generator` (skill, pointer). Implementation:
`capabilities/skills/rig-lattice-system/rig_lattice/idea/`.

> Creativity is not randomness. Creativity is controlled deviation that
> remains useful, appropriate, and provable.

## What good looks like

The two failure modes the module exists to refuse, both from the CLI:

```
$ rig-lattice idea score --title "AI-powered synergy platform" \
    --content "Our best-in-class end-to-end solution leverages cutting-edge
    AI to unlock growth and revolutionize your business with seamless
    world-class results." --claims 3
verdict: reject
failed_gates: ['generic_usefulness', 'final_acceptance']
  generic_usefulness: deviation 0.00 < 0.4 with generic penalty 1.00 >= 0.85
  and proof density 0.12: median language with no receipts; nothing to revise
```

```
$ rig-lattice idea score --title "Deterministic BMS router replaces
    model-guessed mode selection" --content "<mechanism-dense body>" \
    --context "RIG coding agents on enterprise refactors" \
    --sources 5 --claims 4 --mechanisms 4
verdict: accept
acceptance: creativity ✓ deviation ✓ appropriateness ✓
            usefulness ✓ proof_density ✓ generic_penalty ✓
```

## Each gate is tested at its own threshold pair

A gate that has never been shown to bite is decoration. Every gate is
exercised by forcing the exact pair the build card names, so the *gate* is
under test rather than a fixture's happenstance score:

| gate | forced condition | action |
|---|---|---|
| anti-randomness | `novelty 0.90 > 0.85`, `appropriateness 0.50 < 0.55` | **reject** |
| anti-randomness (boundary) | `novelty == 0.85` exactly | **pass** — `>` is not `>=` |
| generic-usefulness | `usefulness 0.75 > 0.70`, `deviation 0.35 < 0.40` | **revise** |
| generic-usefulness (saturated) | `generic_penalty 1.0`, `proof_density 0.0` | **reject** |
| theater | `deviation 0.85 > 0.80`, `proof_density 0.55 < 0.60` | **revise** |
| final acceptance | each of six thresholds, one at a time, `−0.01` | **fails, names the dimension** |

Precedence is tested too: an input that trips both a reject gate and a revise
gate returns `reject`.

## The geometric mean is the honest part

```
C = [N_vendi · U · Q_hybrid · S_bayesian]^(1/4) · D · ε · R · V · I · B
    / [G · K · T]
```

The four primary terms enter as a geometric mean, so one dead dimension
collapses the score — an idea cannot buy its way past a zero with volume on
the other three. The divisors floor at 0.25 so no input can zero the result
either.

## Proxies are declared, not hidden

Two of the fifteen sub-formulas need machinery that does not exist offline.
Rather than quietly approximating, every score reports what was substituted:

| term | card specifies | shipped proxy |
|---|---|---|
| `N_vendi` | `exp(H(eigenvalues(K)))` over embeddings | normalized max n-gram distance to corpus |
| `S_bayesian` | `D_KL(P_post ‖ P_prior)` | corpus-contradicting claim count, normalized |

```python
score.proxies → ("N_vendi: n-gram distance to corpus stands in for Vendi
                  eigen-entropy over embeddings", ...)
```

## Determinism and replay

```
$ rig-lattice idea score --title t --content c --json  (twice) → byte-identical
$ rig-lattice idea grid --candidates ideas.json --seed 7 (twice) → identical
$ rig-lattice idea grid --candidates ideas.json          → error: seed required
```

`seed` is a required keyword argument, not an optional one with a clock
fallback — a quality-diversity run that cannot replay is an anecdote.

## The ASR refuses to flatter itself

The 25-question stack carries 21 automatable checks and 4 that need human
judgement. The 4 are **excluded from the denominator** and counted separately:

```json
{"asr": 0.7619, "survived": 16, "scored": 21, "manual": 4,
 "total_questions": 25,
 "note": "4 of 25 questions need human judgement and are excluded from the
          denominator, not counted as survived"}
```

A rate of 16/21 reported as 16/21 is worth more than 20/25 obtained by
counting unjudgeable questions as passes.

## Why it is not a brainstorming tool

The RIG delta: the private `rig-creative-booster` package is gone (both owners
404). The vendored bridge's fallback was a hand-tuned weighted sum with its
own accept threshold that **disagreed** with the build card's gates — a bundle
with two threshold sets cannot tell you whether an idea passed. That stub is
deleted; the V3.1 core rebuilt from the card is the offline default, and the
optional package import still wins if a clone ever surfaces
(`booster_available() → "package" | "builtin"`).

Verified: `tests/test_idea_gates.py` — 40 tests over gates, scoring bounds,
MAP-Elites replay, and the ASR denominator.
