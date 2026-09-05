---
name: rig-capabilities-corpus
description: Run the deterministic card-corpus scanner over the nine fable-2031 source cards — manifest-first selection, dedup, rule classification, structural truncation — and honour the 10% unclassified halt.
argument-hint: "[scan|classify|truncation] [--root <path>]"
allowed-tools: Read, Bash
category: meta
outcome: "meta: evidence selection is a manifest decision, not a model opinion, and a truncated card stays truncated rather than being completed"
done_when:
  - file:capabilities/commands/rig-capabilities-corpus.md
  - grep:capabilities/commands/rig-capabilities-corpus.md:TRUNCATED_AT_SOURCE
  - cmd:test 1 -eq $(python3 -c 'from rig_capabilities.corpus import corpus_report as C; r = C(roots=["tests/fixtures/fable2031/corpus"]); print(1 if r["ok"] and r["unclassified_rate"] <= 0.10 else 0)')
  - cmd:test 1 -eq $(python3 -c 'from rig_capabilities.corpus import gate_corpus_refusal as G; print(1 if G(".")[0] else 0)')
  - cmd:test 3 -eq $(python3 -c 'import json; from pathlib import Path; d = json.loads(Path("data/fable2031/source_inventory.json").read_text()); print(sum(1 for c in d["cards"] if c["status"] == "truncated_at_source"))')
  - cmd:python3 -m unittest tests.fable2031_corpus
great_example: capabilities/commands/rig-capabilities-corpus.md
acl: public
quality_floor: 0.7
---

# rig-capabilities-corpus

No model sits in the classification path. The scanner enumerates what is **declared**, then reads
it: `data/fable2031/source_inventory.json` is the nine-card source manifest (`id`, absolute `path`,
`sha256`, `bytes`, `status`, `end_anchor`), and `data/fable2031/classify_rules.json` is ordered
data where the first match wins.

Selection rule — and the trap it closes: a file is in-corpus when its path is in the manifest
**or** its frontmatter `tags` contain `Build Cards`, and manifest membership wins. It has to: cards
1 and 6 carry `tags: []` and card 9's tags are `"RIG/brand"`, `"AI GTM"`, `"personal/career"`,
`"Harness Design"` — none is `Build Cards`, so a tag-only filter selects **zero** of the three
truncated cards, i.e. it would drop the weakest evidence first.

Verb surface: `corpus scan|classify|truncation` are the operator verbs (each takes `--root`
repeatable, and a `--json` shape); the `done_when` checks below call the module entry points
directly, so they verify the same code the verbs wrap on any checkout. Quote the run, never the
intention — a missing verb answers `invalid choice` from argparse, which is a gap to report, not a
result to call green.

1. **Scan** (`corpus scan [--root <path>]`; module `scan_corpus(roots, manifest)`). Reports `raw`,
   `unique`, `duplicates`, `contradiction_variants`, per-root `{root, present, cards}`, and the card
   list. Card identity is `card_key`: the frontmatter `title:` when present, else the file stem with
   a trailing ` (N)` copy suffix stripped. The arithmetic is an identity —
   `raw == unique + duplicates + contradiction_variants` — and byte-equal bodies under one key are
   duplicates while divergent bodies under one key are contradiction variants, never silently
   merged. The primary copy is the longest body, then the newest `updatedAt`, then the smallest
   path. An absent root reports `present: false, cards: 0` and never shrinks a denominator.
2. **Classify** (`corpus classify`; module `classify(card, rules)`). Ordered rules over
   `title`/`tags`/`body`; first match supplies `subsystem`, `studio`, `type` from the register's own
   vocabularies. No match stays `unclassified: true, reason: "no_rule_matched"` — an honest
   unclassified is preferred to a guessed placement, because a wrong placement makes a capability
   look owned.
3. **Truncation** (`corpus truncation`; module `detect_truncation(text) -> (bool, anchor)`).
   Structural only: an unterminated pipe-table row, a sentence mark with a stray character glued to
   it, a line ending on a connector, or a cut immediately followed by a structural marker. The
   anchor names the mark, never the content that follows it.

## The halt: 10%, and what it refuses

`UNCLASSIFIED_HALT_RATE = 0.10` over `unclassified / unique` — the unique cards actually scanned.
Past it, `corpus_report` returns `ok: false` and `convergence.score_week` raises `CorpusRefusal`:
**no week gets scored on a register the classifier cannot place.** `unique == 0` is
`ok: false, reason: "empty_corpus"` — never a division, never a pass. The denominator is never a
rhetorical figure like "~453 Build Cards".

The hermetic `certify` gate reads only the committed snapshot
`tests/fixtures/fable2031/corpus-manifest.json`, whose arithmetic is explicit: 22 files → 20 unique
keys → 19 classified, 1 unclassified = `0.05` (halt 0.10), 1 truncated card, 1 duplicate pair, 1
contradiction variant. `gate_corpus_refusal('.')` prints
`rate=0.0500 unclassified=1/20 halt=0.1 source=tests/fixtures/fable2031/corpus-manifest.json`.
A planted snapshot at 0.15 turns that gate RED; the planted variant is the proof the gate is not
theatre.

## The three TRUNCATED_AT_SOURCE cards — and what is forbidden about them

| card | bytes | status | `end_anchor` | what is missing |
|---|---|---|---|---|
| PROMPT PACK — 2031 Design Chain | 991 | `truncated_at_source` | `\| QNA \|` | the rest of the sweep table, and the Grok-extraction / Fable-5.1 mapping prompts the title promises |
| RIG GAP REGISTER v1 | 1505 | `truncated_at_source` | `**3. No capability register.**Z` | everything after gap 3, whose heading ends with a bare `Z` glued to it |
| RIG Known Expert OS | 20559 | `truncated_at_source` | `## Sources` | the Phase 11 body after its one-line objective, Phase 12 entirely, and Gates 11 and 12 |

`docs/TRUNCATED-SOURCES.md` is the ledger; `tests/fable2031_corpus.py::TruncationLedgerTests` fails
if the ledger, the inventory, and `detect_truncation` ever disagree in either direction.

Prohibited, without exception: synthesising a missing region; "correcting" the three-letter sweep
row to the four-letter brand it would become; authoring a Phase 11 body, a Phase 12, or Gate 11/12
criteria that do not exist on disk; promoting a truncated card's claim to a scored capability row;
or quietly preferring the tag filter because it looks cleaner. A recovered copy must be re-hashed
from disk. A card stays `TRUNCATED_AT_SOURCE` until a longer copy is hashed back in, and the
absence of a `Build Cards` tag is never a reason to drop one.

## Honest state as of 2026-09-01 (quote this, not optimism)

- **The live scan does not clear the halt today, and says so.** Over `~/Downloads` alone
  `corpus_report` returns `raw 1988, unique 419, classified 330, unclassified 89,
  unclassified_rate 0.212411, truncated 3, ok false, reason "unclassified_rate_exceeded"` — the
  halt is binding on live roots, which is the seam working, not a bug to route around.
  `~/mnt/RIGLake` is mounted and its walk dies with `TimeoutError: [Errno 60]` deep inside
  nested package trees; `realign` carries that as `unclassified_rate_unreported`, which blocks PASS
  rather than reading an unknown rate as zero. Use `--root tests/fixtures/fable2031/corpus`
  (module: `roots=[...]`) for a deterministic, sub-second, repo-only run.
- **A card count is not a booking.** Nothing this scanner reports is revenue:
  `data/fable2031/bookings-2026-W36.json` counts **zero** records because no
  `qualification_evidence_path` resolves to a file on disk, so the week the corpus feeds is
  `BASELINE_ONLY` and **no convergence improvement may be claimed** from any corpus number. There
  is no booked conversation and no revenue figure on this disk, and no sentence in this command
  treats one as existing.
