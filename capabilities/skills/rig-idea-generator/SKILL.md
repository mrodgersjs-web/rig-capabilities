---
name: rig-idea-generator
description: "Deterministic idea evaluation and generation — the V3.1 Master Creativity Function with its four gates (anti-randomness, generic-usefulness, theater, final acceptance), the 25-niche MAP-Elites quality-diversity grid, the 25-question adversarial survival stack, DES² rigor amplifiers, and the 16-framework collision catalogue. Use when asked to score or generate ideas, check whether an idea is generic or merely random, run the creativity gates, produce an idea menu, or collide two innovation frameworks. Pointer skill: the implementation lives in the rig-lattice-system payload."
allowed-tools: Bash Read Grep
owner: rig-intelligence
domain: Agent engineering / creative intelligence
status: Stable
verified_by: jake
verified_on: 2026-09-02
acl: public
relates_to: rig-lattice-system, rig-deviation-engines
outcome: "agent-engineering: an idea gets a reproducible accept/revise/reject with the failing gate named, so novelty that is merely random and usefulness that is merely median are both refused before anyone builds them"
done_when:
  - file:capabilities/skills/rig-lattice-system/rig_lattice/idea/booster.py
  - cmd:capabilities/skills/rig-lattice-system/bin/rig-lattice idea score --title "AI-powered synergy platform" --content "Our best-in-class end-to-end solution leverages cutting-edge AI to unlock growth and revolutionize your business with seamless world-class results." --claims 3 --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['verdict'] in {'accept','revise','reject'}; assert d['verdict']=='reject', d['verdict']; assert 'generic_usefulness' in d['failed_gates'] or 'anti_randomness' in d['failed_gates']"
  - cmd:python3 -c "import sys; sys.path.insert(0,'capabilities/skills/rig-lattice-system'); from rig_lattice.idea import QUESTIONS, N_NICHES, AMP_PRODUCT_MAX; assert len(QUESTIONS)==25; assert N_NICHES==25; assert abs(AMP_PRODUCT_MAX-6.552)<1e-3"
  - cmd:python3 -c "import sys; sys.path.insert(0,'capabilities/skills/rig-lattice-system'); from rig_lattice.idea import MethodologyLibrary; assert len(MethodologyLibrary().get_all())==16"
great_example: examples/great/agent-engineering/rig-idea-generator.md
quality_floor: 0.7
---

# RIG Idea Generator

> Creativity is not randomness. Creativity is controlled deviation that
> remains useful, appropriate, and provable.

This skill is a **pointer**: the implementation is `rig_lattice/idea/` inside
`capabilities/skills/rig-lattice-system/`.

## activation

Fires on: "score this idea", "is this idea any good", "run the creativity
gates", "generate ideas", "give me an idea menu", "is this generic", "is this
just random", "collide two frameworks", "what's the adversarial survival rate".

## instruction

Score first, generate second. `rig-lattice idea score` runs the V3.1 Master
Creativity Function over the idea's *declared* fields — sources, claims,
mechanisms, corpus — and then the four gates, returning
`accept | revise | reject` with the failing gate named. Two failure modes are
refused by construction: **random novelty** (novel but contextless) and
**generic usefulness** (practical but median). To generate rather than judge,
`rig-lattice idea grid --candidates FILE --seed N` fills a 25-niche
quality-diversity grid and returns the elite per niche; the seed is required so
a run replays byte-identically.

No LLM sits in the scoring loop. The same idea always scores the same.

## applies_when

```yaml
env: any POSIX shell; no network
runtime: python3 >= 3.11
deps: stdlib only
params:
  title / content / context: the idea text
  sources / claims / mechanisms: counts of the idea's receipts
  corpus: file of reference lines to measure novelty against
  seed: REQUIRED int for the MAP-Elites grid — runs must replay
budget:
  A1: $0.00   # the whole scoring path is deterministic
scale: 25 niches x mutations_per_candidate per grid run; scoring is O(text)
```

## permissions

Bash Read Grep

## flow

1. **Score.** `rig-lattice idea score --title T --content C --sources n
   --claims n --mechanisms n [--corpus PATH]`.
2. **Read the gate that failed**, not the number. Each gate reports the exact
   threshold pair that tripped it.
3. **Revise against that gate**: anchor the novelty (name the audience), break
   the median (cut buzzwords, add a mechanism), or back the deviation (cite
   sources, name mechanisms).
4. **Re-score.** The verdict change is the proof.
5. **Generate alternatives** when a single idea keeps failing:
   `idea grid --candidates F --seed N` for the 25-niche menu.
6. **Stress-test the survivor** with the 25-question stack — the survival rate
   reports how many *automatable* questions passed and how many need a human.

## done_when

- a buzzword-only idea returns `reject` with `generic_usefulness` or
  `anti_randomness` in `failed_gates`
- a mechanism-dense, sourced idea returns `accept` with all six acceptance
  thresholds met
- two runs of the same input are byte-identical
- `idea grid --seed N` twice produces identical output
- `len(QUESTIONS) == 25`, `N_NICHES == 25`, `AMP_PRODUCT_MAX == 6.552`

## out_of_scope

- **Writing the idea for you.** This scores and diversifies; it does not draft
  prose. Generation is structural (niche + operator), not generative.
- **The private `rig-creative-booster` package.** Absent; both known owners
  404. The V3.1 core here is the offline default. If a clone appears the bridge
  prefers it automatically and reports `engine="package"`.
- **Claiming embedding-grade novelty.** Two of the fifteen sub-formulas use
  documented offline proxies (see below). The proxies are reported in every
  score's `proxies` field, never hidden.

## The Master Creativity Function (V3.1)

```
C(idea) = [ N_vendi · U · Q_hybrid · S_bayesian ]^(1/4)
          · D(portfolio) · ε(execution) · R(reversibility)
          · V(vessel) · I(instinct) · B(bad_idea_residue)
          / [ G(generic) · K(cost) · T(time_to_value) ]
```

The four primary terms enter as a geometric mean: one dead dimension collapses
the score, so an idea cannot buy its way past a zero.

**Declared proxies.** Where the card specifies machinery unavailable offline,
the substitution is named in the module and in the output:

| term | card specifies | offline proxy |
|---|---|---|
| `N_vendi` | `exp(H(eigenvalues(K)))` over an embedding similarity matrix | normalized max n-gram distance to the supplied corpus |
| `S_bayesian` | `D_KL(P_post ‖ P_prior)` | count of claims contradicting the corpus's modal claim, normalized |
| `G` third term | cliché embedding distance | folded into the n-gram overlap term |

## The four gates

| gate | condition | action |
|---|---|---|
| anti-randomness | `novelty > 0.85 and appropriateness < 0.55` | **reject** — random, not creative |
| generic-usefulness | `usefulness > 0.70 and deviation < 0.40` | **revise** — useful but median |
| generic-usefulness (saturated arm) | `deviation < 0.40 and generic_penalty ≥ 0.85 and proof_density ≤ 0.2` | **reject** — median language, no receipts, nothing to revise |
| theater | `deviation > 0.80 and proof_density < 0.60` | **revise** — needs mechanism specificity |
| final acceptance | `creativity ≥ 0.78, deviation ≥ 0.80, appropriateness ≥ 0.65, usefulness ≥ 0.70, proof_density ≥ 0.60, generic_penalty ≤ 0.15` | **accept** when all six clear |

Reject outranks revise outranks accept.

## MAP-Elites (25 niches)

Axes: Novelty (5 bins) × Time-to-Value (5 bins). Mutation operators are the
transform sets vendored in `innovation.py` — SCAMPER's 7 verbs and Synectics'
4 analogies — plus 10 Oblique Strategies, drawn from `random.Random(seed)`.
Selection keeps the highest-scoring elite per niche.

## Adversarial Survival Rate (25 questions)

Four groups: pre-ideation (6), during-ideation (6), post-ideation (7), hostile
skeptic (6). 21 carry a deterministic check; **4 are marked `manual=True` and
excluded from the denominator**, with the count reported. A question a machine
cannot honestly judge is never counted as survived.

## DES² amplifiers

Five rigor multipliers whose product caps at **6.552**: mechanism map (1.5) ×
source per claim (1.4) × falsification pre-registration (1.6) × specificity
(1.3) × Brier calibration (1.5).

## Collision catalogue

`MethodologyLibrary` carries 16 innovation frameworks (TRIZ, SCAMPER,
Synectics, Biomimicry, ...). `combine(m1_id, m2_id)` interleaves two into a
hybrid — that is what "collision" means outside engine 06.

## Invocations

```bash
SKILL=capabilities/skills/rig-lattice-system

# score an idea
$SKILL/bin/rig-lattice idea score \
  --title "Deterministic BMS router" \
  --content "Route by threshold gate because a model in the decision path is not reproducible." \
  --context "RIG coding agents on enterprise refactors" \
  --sources 3 --claims 2 --mechanisms 4 --json

# 25-niche menu, replayable
$SKILL/bin/rig-lattice idea grid --candidates ideas.json --seed 7 --json

# adversarial survival rate
python3 -c "import sys; sys.path.insert(0,'$SKILL'); \
  from rig_lattice.idea import run_stack; \
  import json; print(json.dumps(run_stack({'title':'t','content':'c'})['asr']))"

# collide two frameworks
python3 -c "import sys; sys.path.insert(0,'$SKILL'); \
  from rig_lattice.idea import MethodologyLibrary; \
  print(MethodologyLibrary().combine('triz','biomimicry')['name'])"
```
