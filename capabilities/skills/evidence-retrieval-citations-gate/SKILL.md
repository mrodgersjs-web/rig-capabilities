---
name: evidence-retrieval-citations-gate
description: >-
  Use when an agent must pull evidence from the capability corpus and every
  returned claim has to be backed by a source that actually exists. Three jobs,
  one checker: `retrieve` ranks corpus docs for a query with BM25 (IDF-weighted,
  deterministic tie-break); `gate` resolves every cited source id on every
  returned row against an INDEPENDENT registry — a returned claim whose citation
  does not resolve is exit 2, and the registry is loaded from a separate file so
  a planted id cannot self-vouch; `benchmark` proves the ranker earns its keep by
  beating a keyword-overlap baseline on mean reciprocal rank over a labelled
  probe set, exit 2 if it does not. Stdlib only, no network, no model, no writes.
allowed-tools: Bash Read
owner: rig-intelligence
domain: Retrieval / evidence integrity
status: Draft
outcome: >-
  agent-engineering: retrieved evidence is ranked, beats a keyword baseline on a
  measured probe set, and cannot return a claim whose citation does not resolve
  in an independent registry — retrieval that cites nothing real is refused
done_when:
  - cmd:python3 capabilities/skills/evidence-retrieval-citations-gate/retrieve.py benchmark --matrix capabilities/skills/evidence-retrieval-citations-gate/fixtures/corpus.json --probes capabilities/skills/evidence-retrieval-citations-gate/fixtures/probes.json --hit-floor 0.6; test $? -eq 0
  - cmd:python3 capabilities/skills/evidence-retrieval-citations-gate/retrieve.py gate --matrix capabilities/skills/evidence-retrieval-citations-gate/fixtures/corpus.json --registry capabilities/skills/evidence-retrieval-citations-gate/fixtures/registry.json --query "harness state memory"; test $? -eq 0
  - cmd:python3 capabilities/skills/evidence-retrieval-citations-gate/retrieve.py gate --matrix capabilities/skills/evidence-retrieval-citations-gate/fixtures/corpus_bogus_citation.json --registry capabilities/skills/evidence-retrieval-citations-gate/fixtures/registry.json --query "lesson trigger mandated check"; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/evidence-retrieval-citations-gate/retrieve.py gate --matrix capabilities/skills/evidence-retrieval-citations-gate/fixtures/corpus_no_citation.json --registry capabilities/skills/evidence-retrieval-citations-gate/fixtures/registry.json --query "lesson trigger mandated check"; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/evidence-retrieval-citations-gate/retrieve.py benchmark --matrix capabilities/skills/evidence-retrieval-citations-gate/fixtures/corpus.json --probes capabilities/skills/evidence-retrieval-citations-gate/fixtures/probes_bad_gold.json --hit-floor 0.6; rc=$?; test $rc -eq 2
  - file:capabilities/skills/evidence-retrieval-citations-gate/retrieve.py
great_example: examples/great/agent-engineering/evidence-retrieval-citations-gate.md
quality_floor: 0.6
---

# evidence-retrieval-citations-gate

THE LAW: **retrieved evidence is ranked, measured against a baseline, and every
returned claim's citation resolves in an INDEPENDENT registry — or it is
refused.** Three failure modes this closes, each a `cmd:` that must go red on a
plant:

1. **Unranked recall.** Returning documents in corpus order, or by raw keyword
   overlap, is not retrieval. `benchmark` computes BM25 MRR and keyword-overlap
   MRR over a labelled probe set and exits 2 unless BM25 strictly beats the
   baseline (measured: **0.8333 > 0.7130**, hit@1 0.667 over 9 probes). A ranker
   that cannot outscore set-overlap is not earning its complexity.

2. **Self-vouching citations.** The first draft built the citation registry from
   the same rows it was checking, so a planted bogus id was added to the
   registry and passed — the gate could never go red. `gate` now loads the
   registry from a SEPARATE file (`fixtures/registry.json`, 62 real source ids);
   a returned row citing `arXiv:9999.99999-FABRICATED` is exit 2.

3. **Uncited claims.** A returned row with an empty citation list is exit 2 — a
   retrieval result with no evidence is worse than no result.

## Commands

| command | contract |
|---------|----------|
| `retrieve --matrix C --query Q [-k 5]` | BM25 top-k with each row's cited ids |
| `gate --matrix C --registry R --query Q` | exit 2 if any returned citation is not in R |
| `benchmark --matrix C --probes P --hit-floor F` | exit 2 if BM25 does not beat keyword MRR or hit@1 < F |

Exit codes: 0 clean / 1 usage-or-file-missing / 2 contract violation. BM25 uses
a deterministic id tie-break, so a query returns the same ranking every run.

## Done-tests (planted failures are permanent regression cases)

Five `cmd:` forms plus the checker `file:`: benchmark GREEN (beats baseline),
gate GREEN (registry resolves), gate RED on a bogus citation, gate RED on a
missing citation, benchmark RED on a probe whose gold is not in the corpus. The
out-of-band plant (disable the beats-baseline clause → a tie passes → gate
blind) is proven in the reference exemplar.

## Provenance

Corpus is RIG's own derived capability analysis (name + mechanism + rig_delta,
id-only citations — not creator transcript text). Registry ids are the 18 video
/ 24 arXiv / 20 oss sources of the Discover AI increment. No creator text ships.
