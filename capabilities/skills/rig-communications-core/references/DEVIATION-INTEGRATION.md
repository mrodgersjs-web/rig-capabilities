# Deviation Integration (v13)

## Engine-to-surface map

Canonical source: `rig_comms/surfaces.py` — each `Surface.engines` tuple names
its RIG Deviation Engines (40-engine registry, ids 1–40). Print live:
`python3 -m rig_comms surfaces`. Assignment rationale: each surface gets one
anti-gravity engine (escape the median), one evidence engine (anchor claims),
one surface-specific mechanism engine.

## Polar cards (low pole → high pole)

| surface | low pole (generic) | high pole (deviated) |
|---|---|---|
| emails | feature list + CTA | the reader's Tuesday-9am problem named W-number style, one mechanism, one ask |
| linkedin | insight + hashtag | wound hit + specific number + loop the reader must close |
| substack | 2,500-word essay | argument that survives the 25-question stack, receipts woven without bragging |
| songs | rhyme scheme | euphoria protocol — tension/release mapped to W3–W8, no cliché pair left |
| film-scripts | dialogue exchange | visual mechanism — the shot carries the wound, not the line |
| specs | requirement list | invariants + failure modes + explicit out-of-scope, zero adjectives (FORGE) |
| code | working function | boring, correct, tested — deviation budget ZERO |
| prompts | instruction paragraph | constraint lattice: role + done-test + refusal conditions |
| novels | plot summary | scene-level voltage; chapter-end Zeigarnik loops |
| resumes | responsibility bullets | outcome verbs with numbers that survive fabrication gate |
| research | literature list | evidence synthesis with per-claim source weight (WITNESS) |
| love-notes | — | private lane: no machine deviation, no scoring, exit 3 (LOCKED) |

## Corpus baselines (the median we deviate FROM)

`data/comms/baselines.json` — deterministic medians from the local
writing-craft corpus (refresh: ). Current: 25
transcripts, median 2,184 words / 14-word sentences (screenwriting-film
surface only; remaining 7 surfaces DATA_GAP until the YouTube block lifts).
Anti-median rule: a draft whose sentence-length distribution peaks at the
surface median IS the median — push it or reject it.

## Deviation budget (agent contract, not a fake number)

- linkedin/substack: ≥5 σ-ladder variants, keep max-RIG-L; target rung per
  `surfaces.py` `sigma_target`
- emails/specs: 3 variants
- code/prompts: 0 — correctness first, declared honestly
- **Honesty**: `sigma_target` is metadata in the gate envelope
  (`meta.sigma_status: META`), NOT a fabricated numeric score. Real σ units come
  from `rig-lattice` scoring of an artifact against its baseline; the stack
  never fakes that mapping.
