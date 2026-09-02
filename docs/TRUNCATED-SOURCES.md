# TRUNCATED-SOURCES — three of nine cards end mid-content at source

Tails below were re-read from disk on 2026-09-01 before writing this file. The ledger is
cross-checked by `corpus.detect_truncation()` (P2) and by
`tests/fable2031_corpus.py::TruncationLedgerTests`: a mismatch in either direction — a row in one
place and not the other, an `end_anchor` cell that disagrees with
`data/fable2031/source_inventory.json`, or a byte count that disagrees — fails the test. Byte
counts are `stat` output, matching `/tmp/fable2031-source-inventory-facts.json`.

**Anchor semantics.** `end_anchor` is the line that *marks* the truncation: the last content line
before the cut, or, when the cut sits mid-document and a structural marker immediately follows it,
that marker. Card 9 is the marker case — the cut is Phase 11's one-line objective and `## Sources`
comes immediately after it, so the anchor is `## Sources`, not the `- [website](…)` bullet that
survives under that heading. Cards 1 and 6 are cut at EOF, so their anchors are the last content
line on disk.

| source_path | bytes | end_anchor | missing_content | recovery_route |
|---|---|---|---|---|
| `/Users/rig128gb/Downloads/PROMPT PACK — Full-Corpus Scrape → Grok Extraction → Fable 5.1 Capability Map (2031 Design Chain).md` | 991 | `\| QNA \|` | Remainder of the "Source systems to sweep" table after the `` `\| QNA \|` `` row, and — per the card's own title — the Grok extraction prompts and the Fable 5.1 capability-map prompts of the 2031 design chain that never appear on disk. | Recall; else `/Users/rig128gb/.rig/bin/riglake-mount-ensure` then search `~/mnt/RIGLake` for a longer exact-title copy |
| `/Users/rig128gb/Downloads/RIG GAP REGISTER v1 — Every Missing Capability, Ranked by Blast Radius × Revenue Proximity (Worst-Harness-First Fix Order).md` | 1505 | `**3. No capability register.**Z` (gap 3's text ends `No capability register.` with a bare `Z` appended on the same line) | Everything after gap 3: the stray-terminated remainder of gap 3, gaps 4+ of Tier 1, and every lower tier the title promises ("Every Missing Capability"). | Recall; else `/Users/rig128gb/.rig/bin/riglake-mount-ensure` then search `~/mnt/RIGLake` for a longer exact-title copy |
| `/Users/rig128gb/Downloads/RIG Known Expert OS — 12-Phase Master Prompt for a Forward-Deployed AI Strategist & Engineer.md` | 20559 | `## Sources` | Phase 11 body after its objective line; Phase 12 in full; Gates 11 and 12 | Recall; else `/Users/rig128gb/.rig/bin/riglake-mount-ensure` then search `~/mnt/RIGLake` for a longer exact-title copy |

## Observed tails (verbatim, re-read 2026-09-01)

**Card 1 — PROMPT PACK (27 lines).** Under `## Source systems to sweep`: line 22 `| System | Content |`,
line 23 `| --- | --- |`, line 24 `| QNA |` — a table row truncated mid-row — then lines 25–27 are blank.
The final non-blank line is exactly `| QNA |`. `QNA` is never "corrected" or promoted to the
four-letter form it would become. That spelling is deliberately absent from this file — the
cross-check test fails if it ever appears in it — and a recovered copy must be re-hashed from
disk, never guessed into the four-letter spelling.

**Card 6 — GAP REGISTER (22 lines).** `## Tier 1 — Structural. Blocks all monetization. (w = 5)`
lists gaps 1 and 2, then line 19 is `**3. No capability register.**Z` — the bold gap-3 heading text
followed immediately by a bare `Z` on the same line — then lines 20–22 are blank. Nothing after gap 3
exists on disk.

**Card 9 — Known Expert OS (530 lines).** Line 514 `### Gate 10`, line 522 `# Phase 11 — Turn the
system into the RIG offering`, lines 524–525 `## Objective` / `Translate the validated expertise
into a bounded offer.`, line 529 `## Sources`, and line 530 (final line)
`- [website](https://www.youtube.com/watch?v=vl6GDCbMi4I)`. Gate headers found on disk run
`### Gate 1` (:165) through `### Gate 10` (:514) only. Phase 12 is absent entirely.

The recorded anchor is `## Sources` — the marker proving Phase 11's body is gone — and **not** the
Sources bullet at line 530. `corpus.detect_truncation()` returns that heading for this card, and
`data/fable2031/source_inventory.json` records it.

## Synthesis prohibition and the tag trap

No Phase 11 body, no Phase 12 content, no Gate 11/12 criterion, and no promotion of `QNA` to its
four-letter form may ever be synthesised for these cards. If a longer exact-title copy cannot be
recovered from Recall or
`~/mnt/RIGLake`, the cards stay `TRUNCATED_AT_SOURCE`; only directly evidenced content is scored,
the Phase-11 offering row stays pinned at `maturity_M0_5: 0`, and `GATES[11]`/`GATES[12]` stay
`KeyError`s rather than authored substitutes.

Corpus selection must never rely on a `Build Cards` tag filter: cards 1 and 6 carry `tags: []`, and
card 9's tags are `"RIG/brand"`, `"AI GTM"`, `"personal/career"`, `"Harness Design"` — none is
`Build Cards`, so a tag-only filter selects **zero** of the three truncated cards. Manifest
membership (`data/fable2031/source_inventory.json`) wins over tags, guaranteeing all nine cards —
including every truncated one — enter the corpus.
