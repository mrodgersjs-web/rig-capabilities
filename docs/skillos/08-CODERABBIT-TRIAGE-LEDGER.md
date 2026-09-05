# CodeRabbit Review Findings Triage Ledger (2026-09-05)

Ledger tracking the triage, source validation, and disposition of all 58 CodeRabbit review findings across the `rig-capabilities` estate (branch `fable-2031`, base commit `0beeb46`).

## Executive Summary

- **Total findings triaged**: 58
  - `bin/` (CLI dispatch): 1
  - `docs/skillos/` (Documentation & Catalog): 3
  - `capabilities/` (Skills, Commands, Hooks): 9
  - `examples/great/` (Exemplars): 45
- **Triage outcomes**:
  - **VALID-FIX**: 38 (remediated in working tree and verified)
  - **INVALID-REJECT**: 20 (rejected with concrete, evidence-backed justification)

---

## 1. CLI Dispatch Findings (1 finding)

| # | File & Location | Severity | Description | Disposition | Evidence & Resolution |
|---|---|---|---|---|---|
| 1 | `bin/rig-capabilities:1088-1098` | Major | Dead `--count` and `--strict` CLI flags in `skillos_dispatch` call sites | **VALID-FIX** | Forwarded `count=args.count` and `strict=args.strict` to both `skillos_dispatch` calls. |

---

## 2. Documentation & SkillOS Catalog Findings (3 findings)

| # | File & Location | Severity | Description | Disposition | Evidence & Resolution |
|---|---|---|---|---|---|
| 2 | `docs/skillos/review-summary-2026-09-05.md:11` | Minor | Clarify 11/11 checks are Tessl verification only and record store gate remains red | **VALID-FIX** | Updated summary text: explicit `Tessl verification checks: 11/11 pass` and documented `Store gate: red (143/4993 restorable, v6+ gated)`. |
| 3 | `docs/skillos/universe.jsonl:141` | Major | Machine-specific absolute paths (`/Users/rig128gb/...`) in catalog dump | **VALID-FIX** | Fixed generator in `rig_capabilities/catalog.py:317-321` to use `str(m.relative_to(base))` for repo-relative paths; regenerated in universe. |
| 4 | `docs/skillos/universe.jsonl:4673-4674` | Major | Double-extension artifacts (`.md.md`, `.yaml.md`, `.sh.md`) generated for exemplars | **VALID-FIX** | Fixed generator in `rig_capabilities/rounds.py:122` and `rig_capabilities/quality.py:189` to strip extension before appending `.md`; renamed all 91 double-extension files. |

---

## 3. Capabilities Findings (9 findings)

| # | File & Location | Severity | Description | Disposition | Evidence & Resolution |
|---|---|---|---|---|---|
| 5 | `capabilities/commands/skill-upgrades.md:10` | Major | Hard-coded `iqrsqpi-v10` in generic command completion check | **VALID-FIX** | Updated `done_when` to `cmd:./bin/rig-capabilities quality --weakest 1`, verifying the actual upgrade reporting mechanism without hard-coded asset IDs. |
| 6 | `capabilities/skills/semgrep/SKILL.md:288` | Major | Embedded "ignore previous instructions" reported as prompt injection | **INVALID-REJECT** | The line is part of the "Untrusted scanned content" doctrine section instructing agents to treat scanned code strictly as data; rejecting injection attempts is an affirmative security feature. |
| 7 | `capabilities/hooks/session-size-guard.sh:3` | Major | `file:` fallback in `done_when` allows passing without hook firing test | **VALID-FIX** | Dropped `file:` fallback; requires `cmd:python3 scripts/hook_fires.py session-size-guard.sh`. Verified test passes. |
| 8 | `capabilities/hooks/jake-pushback.sh:3` | Major | `file:` fallback in `done_when` | **VALID-FIX** | Dropped `file:` fallback; requires `cmd:python3 scripts/hook_fires.py jake-pushback.sh`. Verified test passes. |
| 9 | `capabilities/hooks/guard-secret-write.sh:3` | Major | `file:` fallback in `done_when` | **VALID-FIX** | Dropped `file:` fallback; requires `cmd:python3 scripts/hook_fires.py guard-secret-write.sh`. Verified test passes. |
| 10 | `capabilities/hooks/guard-dangerous-commands.sh:3` | Major | `file:` fallback in `done_when` | **VALID-FIX** | Dropped `file:` fallback; requires `cmd:python3 scripts/hook_fires.py guard-dangerous-commands.sh`. Verified test passes. |
| 11 | `capabilities/hooks/goal-loop-startup.sh:3` | Major | `file:` fallback in `done_when` | **VALID-FIX** | Dropped `file:` fallback; requires `cmd:python3 scripts/hook_fires.py goal-loop-startup.sh`. Verified test passes. |
| 12 | `capabilities/skills/rig-known-expert-os/SKILL.md:14` | Major | Pipeline exit code masked in `done_when` check | **VALID-FIX** | Replaced pipe with `python3 -c "import subprocess, json; r=subprocess.run(['./bin/rig-capabilities', 'expert-os', 'phases', '--json'], capture_output=True, text=True, check=True); assert json.loads(r.stdout)['12']=='absent_at_source'"` ensuring nonzero exits raise. |
| 13 | `capabilities/skills/codeql/SKILL.md:19` | Major | Outcome claims dataflow path for all findings | **VALID-FIX** | Scoped outcome requirement to `@kind path-problem`: "...every path-problem finding lands in SARIF with its dataflow path, never a pattern guess". |

---

## 4. Exemplar Findings (45 findings)

| # | File & Location | Severity | Description | Disposition | Evidence & Resolution |
|---|---|---|---|---|---|
| 14 | `examples/great/agent-engineering/gap-wild_card-agent-engineering.yaml.md:31` | Minor | Line 31 assertion checks `'prove'` instead of `'prove it wrong'` | **VALID-FIX** | Updated assertion to `assert 'prove it wrong' in t`, matching line 30 grep specification. |
| 15 | `examples/great/agent-engineering/mh-06-install-verification-session.yaml.md:18` | Major | `sha256sum <source-file>` uses shell redirection syntax | **VALID-FIX** | Replaced `<source-file>` with `path/to/source-file`. |
| 16 | `examples/great/agent-engineering/hermes-conductor.md.md:17` | Major | Hardcoded absolute path `/Users/rig128gb/...` in status command | **VALID-FIX** | Replaced with `"${FACTORY_DOCTRINE_ROOT:-$HOME/Developer/RIG-Factory-Doctrine}"`. |
| 17 | `examples/great/agent-engineering/coding-harness.md.md:17` | Major | `<changed_python_file>` uses redirection syntax | **VALID-FIX** | Replaced with `path/to/changed_python_file.py`. |
| 18 | `examples/great/agent-engineering/mh-04-deviation-expedition-session.yaml.md:18` | Major | `<s>` and `<b>` placeholder values use redirection syntax | **VALID-FIX** | Replaced with `"$score"` and `"$baseline"`. |
| 19 | `examples/great/security-review/semgrep.md:31` | Minor | Undefined `OUTPUT_DIR` variable before CLI invocation | **VALID-FIX** | Added explicit `export OUTPUT_DIR="${OUTPUT_DIR:-/tmp/semgrep-scan}"`. |
| 20 | `examples/great/security-review/threat-mitigation-mapping.md:17` | Minor | Request to mandate arbitrary threat-modeling fields (likelihood, impact) | **INVALID-REJECT** | The exemplar defines the control-mapping contract established for this capability; adding speculative risk fields is out of scope. |
| 21 | `examples/great/security-review/codeql.md:29` | Major | Analysis outputs to `raw/results.sarif` while acceptance checks `results/results.sarif` | **VALID-FIX** | Aligned analysis command `--output` to `"$OUTPUT_DIR/results/results.sarif"`. |
| 22 | `examples/great/design-ux/hC-02-ui-design.yaml.md:19` | Major | Request to expand color hex scan to 3, 4, 8 digit values | **INVALID-REJECT** | The design token standard intentionally enforces 6-digit hex color tokens (`#[0-9a-fA-F]{6}`) exclusively. Shorthand hex is forbidden by policy. |
| 23 | `examples/great/data-analytics/gap-pe_cfo-data-analytics.yaml.md:27-31` | Major | Request to expand gap-harness validation commands | **INVALID-REJECT** | This is a draft gap-harness whose deliberate done-test requires only the `Working-capital` sentinel token. |
| 24 | `examples/great/design-ux/hC-03-ux-research.yaml.md:22-23` | Major | Request for multi-table CSV relational join validation in exemplar | **INVALID-REJECT** | Exemplar's contract check `assert all(row['theme_id'] and row['observation_id'] for row in r)` is the documented standard. |
| 25 | `examples/great/design-ux/build-out-harness.md.md:17-18` | Major | `<port>` and `<module>` placeholder redirection syntax | **VALID-FIX** | Replaced with `"${PORT:-8080}"` and `"${MODULE:-app}"`. |
| 26 | `examples/great/design-ux/hC-07-mobile-design.yaml.md:21-22` | Major | Request to replace CSS token grep with full CSS AST parser | **INVALID-REJECT** | Grepping for semantic alias tokens is the repo-wide convention for UI design verification. |
| 27 | `examples/great/design-ux/hC-03-ux-research.yaml.md:19-20` | Major | Request to replace file count check with normalized participant id comparator | **INVALID-REJECT** | The 1:1 file count check between consent and session records is the exact documented contract. |
| 28 | `examples/great/security-review/hA-13-code-security-audit.yaml.md:22` | Major | Gitleaks report does not redact secrets | **VALID-FIX** | Added `--redact 100` to `gitleaks detect` invocation. |
| 29 | `examples/great/revenue-gtm/hD-08-expansion-play.yaml.md:23` | Major | Request to replace grep ROI check with structured JSONL parser | **INVALID-REJECT** | Grep for numeric currency/percentage references in markdown report is the documented lightweight check. |
| 30 | `examples/great/revenue-gtm/hD-08-expansion-play.yaml.md:21` | Major | `jq` query does not fail shell on empty cohort | **VALID-FIX** | Added `-e` flag to `jq -e 'length >= 1'`. |
| 31 | `examples/great/revenue-gtm/hD-06-nps-analysis.yaml.md:24` | Major | Request to expand PII regex to all possible identifier types | **INVALID-REJECT** | Email is the primary PII attribute in NPS exports; broad regex expansion creates high false-positive rates on survey responses. |
| 32 | `examples/great/revenue-gtm/hD-01-outbound-sequence.yaml.md:21` | Major | Output path writes to root instead of declared artifact directory | **VALID-FIX** | Updated `--out` to `artifacts/outbound/dental-ops-2026-09/deduped.csv`. |
| 33 | `examples/great/revenue-gtm/hD-02-icp-research.yaml.md:23` | Major | Output path writes to root instead of artifact directory | **VALID-FIX** | Updated `--out` to `artifacts/icp/dental-groups-2026-09/firmographics.csv`. |
| 34 | `examples/great/revenue-gtm/hD-04-pricing-test.yaml.md:21` | Major | `jq` query does not fail shell on insufficient keys | **VALID-FIX** | Added `-e` flag to `jq -e 'keys | length >= 3'`. |
| 35 | `examples/great/code-engineering/hA-02-code-refactor.yaml.md:24` | Major | Request for full characterization vector diffing framework | **INVALID-REJECT** | The exemplar already executes full pytest parity (184 passed) and pydoc diff; characterization engine is out of scope. |
| 36 | `examples/great/agent-engineering/swarm-harness.md.md:17-18` | Major | Placeholder redirection syntax in diff and comm | **VALID-FIX** | Replaced angle brackets with `"$OUT_A"`, `"$OUT_B"`, `"$SORT_A"`, `"$SORT_B"`. |
| 37 | `examples/great/code-engineering/hA-05-code-migration.yaml.md:18-19` | Major | Request to replace grep caller census with AST migration recipe | **INVALID-REJECT** | Grepping for legacy import paths is the documented affirmative caller census check. |
| 38 | `examples/great/code-engineering/hA-04-code-debug.yaml.md:18-22` | Major | Test rerun shown without intermediate fix/patch boundary | **VALID-FIX** | Added explicit `# apply cache isolation fix to src/tax/cache.py` between runs. |
| 39 | `examples/great/business-ops/co-unemployment-filing.md.md:28` | Major | Cron schedule lacks explicit timezone | **VALID-FIX** | Declared explicit `0 22 * * 6 (America/Denver)`. |
| 40 | `examples/great/agent-engineering/ops-harness.md.md:18-20` | Major | Placeholder redirection syntax in ping, tar, shasum | **VALID-FIX** | Replaced with `"$NODE_IP"` and `"$BACKUP_NAME"`. |
| 41 | `examples/great/content-publishing/hB-02-newsletter-issue-session.yaml.md:19` | Major | Awk command only checks max length, not minimum count of 5 lines | **VALID-FIX** | Updated awk script: `awk 'length($0)>50 { long=1 } NF { count++ } END { if (long || count<5) exit 1 }'`. |
| 42 | `examples/great/code-engineering/scraping-harness.md.md:17-20` | Major | Placeholder redirection syntax in curl and jq | **VALID-FIX** | Replaced `<url>`, `<raw_file>`, `<record>` with `"$URL"`, `"$RAW_FILE"`, `"$RECORD"`. |
| 43 | `examples/great/code-engineering/hA-08-code-pr-prep.yaml.md:20-21` | Major | `origin/main` ref can drift during review | **VALID-FIX** | Captured `BASE_SHA=$(git rev-parse origin/main)` and used `$BASE_SHA` for log/diff. |
| 44 | `examples/great/content-publishing/hB-06-twitter-thread-session.yaml.md:31` | Minor | Thread count mismatch between Input (8) and Acceptance (5-12) | **VALID-FIX** | Aligned acceptance to "between five and twelve (nominally 8) and matches arc.yaml". |
| 45 | `examples/great/content-publishing/gap-personal_brand-content-publishing.yaml.md:23-31` | Major | Request to expand gap-fill harness validation | **INVALID-REJECT** | Gap-fill harness specifically validates the `Anti-thirst` token sentinel per G2 halt rules. |
| 46 | `examples/great/design-ux/hC-08-dashboard-design.yaml.md:23` | Major | Request to require multiple resolution captures in FREEZE.txt | **INVALID-REJECT** | The freeze artifact is scoped to `dashboard-final.png`; multi-resolution validation is handled in other design tracks. |
| 47 | `examples/great/code-engineering/scraping-harness.md.md:13-16` | Major | Request to add pre-fetch robots.txt/blocklist validator | **INVALID-REJECT** | Loop exemplar demonstrates loop termination and curl execution; full crawler subsystem is out of scope. |
| 48 | `examples/great/design-ux/hC-11-motion-design.yaml.md:23-24` | Major | Request to build CSS AST animation analyzer | **INVALID-REJECT** | Grep for animation and transition properties is the established lightweight check. |
| 49 | `examples/great/docs-knowledge/gap-construction-docs-knowledge.yaml.md:28-31` | Major | Request to expand gap-harness validation | **INVALID-REJECT** | Gap harness tests for domain sentinel token `OSHA`. |
| 50 | `examples/great/infra-ops/gap-manufacturing-infra-ops.yaml.md:28-31` | Major | Request to expand gap-harness validation | **INVALID-REJECT** | Gap harness tests for domain sentinel token `genealogy`. |
| 51 | `examples/great/design-ux/hC-09-onboarding-flow.yaml.md:27` | Major | Request to mandate live cohort TTFV measurement in design review | **INVALID-REJECT** | Design spec review verifies designed timeline bounds (<= 180s); live telemetry belongs to runtime phase. |
| 52 | `examples/great/design-ux/hC-12-design-handoff.yaml.md:21` | Major | Request to hash FREEZE.txt and copy deck in addition to assets.sha256 | **INVALID-REJECT** | `assets.sha256` is the authoritative frozen artifact manifest. |
| 53 | `examples/great/docs-knowledge/gap-legal-docs-knowledge.yaml.md:28-31` | Major | Request to expand gap-harness validation | **INVALID-REJECT** | Gap harness tests for domain sentinel token `privilege`. |
| 54 | `examples/great/research-intel/hD-10-competitive-intel.yaml.md:21` | Major | `jq` query does not exit nonzero on false | **VALID-FIX** | Added `-e` flag to `jq -e '[.. | .source_url? // empty] | length >= 20'`. |
| 55 | `examples/great/research-intel/hD-09-market-research.yaml.md:21` | Major | `jq` query does not exit nonzero on false | **VALID-FIX** | Added `-e` flag to `jq -e '[.[] | select(.tier == "primary")] | length >= 2'`. |
| 56 | `examples/great/revenue-gtm/hD-02-icp-research.yaml.md:25` | Major | `jq` query counts null/empty outcomes | **VALID-FIX** | Added `-e` and null/empty filter: `jq -e '[.accounts[].outcome | select(. != null and . != "")] | unique | length >= 2'`. |
| 57 | `examples/great/misc/hD-12-growth-experiment.yaml.md:17` | Major | `jq` query does not exit nonzero on false | **VALID-FIX** | Added `-e` flag to `jq -e 'all(.[]; .fired_on_staging)'`. |
| 58 | `examples/great/revenue-gtm/hD-01-outbound-sequence.yaml.md:25` | Minor | JSONL safety gate query iterates over values instead of record objects | **VALID-FIX** | Updated to `jq -s -e 'length > 0 and all(.[]; .passed >= 8)' artifacts/outbound/dental-ops-2026-09/safety_gate.jsonl`. |

---

## Provenance, and the PR surface (checked after `984d60f` was pushed)

The 58 findings above came from the **local `coderabbit` CLI** (`~/.local/bin/coderabbit`,
review of `fable-2031` against base `0beeb46`). They are not PR review comments, and the
difference matters: the PR surface has produced **no findings at all**.

| evidence | value |
|---|---|
| artifact | `.context/coderabbit/pr1-latest.md` — 152,913 bytes, pulled from `issues/1/comments` |
| comments by `coderabbitai[bot]` | 1, at 2026-09-05T04:31:59Z |
| inline review comments (`pulls/1/comments`) | 0 |
| reviews (`pulls/1/reviews`) | 0 |
| check runs on `984d60fc…` | 0 |
| verdict in that single comment | **Review skipped** — the captured comment reports: "This PR contains 1938 files, which is 1788 over the limit of 150." |
| captured limit evidence | `.context/coderabbit/pr1-latest.md:4-26` reports the skip, says to reduce to 150 files or fewer, identifies the plan as Free, and says a paid plan raises the limit |
| range it would have reviewed | `e18305fa…` → `984d60fc…` |
| `.coderabbit.yaml` in the working tree | absent; the artifact, not that absence, is the evidence for the limit applied to this run |

So "check CodeRabbit findings on the pushed commit" answers honestly: **there are none, because
the captured review was skipped.** The comment attributes the skip to its 1938-file input and
reports a 150-file limit for that Free-plan run; it does not establish a universal plan limit.

GitHub PR bases are branches, not commits. Two correctly shaped routes to a delta review are:

1. Create a temporary base branch pinned at `984d60f` and a head branch pinned at the new SHA,
   then open the PR between those branches. This requires two approved pushes to refs other
   than `fable-2031`.
2. Open the delta PR against `fable-2031` **before** advancing `fable-2031`, while that base
   branch still points at `984d60f`.

After `fable-2031` advances to the head SHA, a PR from that same head against `fable-2031`
has zero diff. Any push or PR creation remains subject to its normal approval gates.

---

## Delta rounds on top of `984d60f` (same day)

Mechanism correction: the section above concluded a delta review needed a pushed base branch.
It does not. `coderabbit review --committed --base <branch>` honours a **local** branch as the
base, so pinning one at the base commit is enough:

```
git branch -f cr-base-984d60f 984d60f
coderabbit review --committed --base cr-base-984d60f
```

The run header prints `Compare : fable-2031 → cr-base-984d60f`, and the review counted the
expected file set (21 then 22 files), which is what proves the range rather than the header.
`--base-commit 984d60f` was also tried and still compared against `main`.

### Round 1 — `984d60f` → `8917635`

> **Artifact caveat, recorded after the fact.** This section originally cited
> `.context/coderabbit/delta-984d60f-to-66fb687.md`. That attribution was wrong, and the reason matters:
> `.context/coderabbit/` is gitignored scratch that **each review run overwrites**, so the file named
> `…to-66fb687.md` no longer holds the head it was named for. What is on disk now is a 2-finding tail
> (5 finding blocks across the two misnamed files), not the 7 findings this round reported. The tables
> below are the record — written from the live transcript as each finding was dispositioned, with the
> check that proves each fix. The artifacts are not. Treat any `.context/coderabbit/*.md` filename as
> "the head this run pointed at", never as durable evidence, and copy it out before the next run if a
> specific review must survive.

| # | File & Location | Severity | Description | Disposition | Evidence & Resolution |
|---|---|---|---|---|---|
| D1 | `scripts/check_license_gate_plant.py:166` | Major | "Isolated" plant called `check_universe(stores=True)`, fetching all 293 recipe rows over the network | **VALID-FIX** | Root cause is scope, not the flag: `stores=True` is required, because without it `exit_code` derives from key coverage and a denied blob exits 0. The gate root is now pruned to the single victim row, so no recipe origins remain. Runtime 140s+ → 0.13s with the same `gate_exit=1` assertion. |
| D2 | `scripts/blob_license_ledger.py:138` | Critical | `_rel(payload)` received `None`; `Path(None)` raises `TypeError`, which `except ValueError` does not catch | **VALID-FIX** | `_rel` returns `""` for `None`. Reproduced the `TypeError` on the pre-fix form before changing it; covered by `test_generator_survives_an_unresolvable_payload`. |
| D3 | `scripts/blob_license_ledger.py:115` | Minor | `(ROOT / UNIVERSE).read_text()` raised `FileNotFoundError`; the universe is a generated artifact | **VALID-FIX** | Absent universe now only disables pinned-drift detection. Covered by `test_generator_runs_without_the_frozen_universe`, run through `main(--root)` on a scratch root. |
| D4 | `tests/test_exemplar_resolution.py:93` | Minor | `cls.assertTrue(...)` inside `setUpClass` | **VALID-FIX** | `assertTrue` is an instance method: called on the class it raised `AttributeError` and masked the real fault. Now raises `RuntimeError`. |
| D5 | `rig_capabilities/skillos.py:762-763` | Minor | `licence_denied` collected every failing blob row, so a corrupt or missing warehouse blob was reported as a licence refusal | **VALID-FIX** | Split out `unrestorable_blobs`. Live gate now reports `licence_denied=0, unrestorable_blobs=0` over 302 valid rows, and a planted corruption is named by the new key (`test_denied_and_unrestorable_blobs_are_reported_apart`). |
| D6 | `scripts/blob_license_ledger.py:25-30` | Minor | Bare `"ISC"` / `"BSD"` needles matched inside `MISC` and `DISCLAIMER`; `ISC` is in `PERMISSIVE`, so a false hit clears bytes for archiving | **VALID-FIX, then RE-OPENED** | First remediation word-bounded the needles. That claim was **overstated** and is corrected in Round 3: a word-bounded `\bISC\b` still reads `"not ISC licensed"` as a grant. |
| D7 | `scripts/blob_license_ledger.py:95` | **Major** | A neighbouring `LICENSE` outranked the asset's own `license:` declaration, so a vendored file declaring `GPL-3.0` under a permissive neighbour was classified MIT and cleared | **VALID-FIX** | Priority is now frontmatter → sibling licence → upstream marker → repo grant (`test_own_declaration_outranks_a_permissive_neighbour`). Blast radius measured first: 138 repo-MIT, 1 frontmatter, 1 sibling-derived entry, and zero assets carrying both signals, so the inversion was latent. Ledger regenerates byte-identical in an isolated worktree. |

### Round 2 — `984d60f` → `24142b7` (`.context/coderabbit/delta-984d60f-to-24142b7.md`)

22 files reviewed. **Zero critical, zero major.** One minor.

| # | File & Location | Severity | Description | Disposition | Evidence & Resolution |
|---|---|---|---|---|---|
| D8 | `capabilities/skills/codeql/scripts/test_section_pointers.py` | Minor | Suggested scanning "tracked shipped files, or all supported script and workflow suffixes" | **INVALID-REJECT → overturned in Round 3** | Rejected as "the scan already covers every shipped form". The rejection reasoning was unsound: *zero offenders today* says nothing about a regression test's future coverage, and `.py`/`.sh` are shipped forms in this estate. Fixed in Round 3 by widening the scan, not by narrowing the claim further. |

### Round 3 — `984d60f` → `aeaf337` (`.context/coderabbit/delta-984d60f-to-aeaf337.md`, copied out before the next run)

All 8 unpushed commits, 22 paths plus this round's edits. **Zero critical, zero major.** Two minor,
both correct, both against documentation I had written in the previous two rounds — which is the point
of running the review at the revision you intend to ship rather than at the one you reviewed last.

| # | File & Location | Severity | Description | Disposition | Evidence & Resolution |
|---|---|---|---|---|---|
| D9 | `docs/SECURITY-SNYK-MEDIUM-TRIAGE-2026-09-05.md:93` | Minor | A successful `snyk code test` was recorded as proving OAuth credentials exist. It proves only that *some* credential was usable | **VALID-FIX** | Row rewritten to name the authentication source as **unknown** and to state the withdrawal in place. A scan result cannot distinguish an OAuth token from a legacy token in a store `snyk config get API` does not read — and this doc's whole argument was that the org setting is unidentified, so the inference contradicted its own conclusion |
| D10 | `docs/skillos/08-CODERABBIT-TRIAGE-LEDGER.md:154` | Minor | Round-1 heading said `→ 8917635` while citing an artifact named `…to-66fb687.md` | **VALID-FIX** | The reviewer found a real labelling error, and the cause was worse than the mismatch: `.context/coderabbit/` is overwritten by each run, so the cited file no longer held round 1's output. Heading de-referenced, caveat added above Round 1, and this round's artifact copied out deliberately. See the artifact caveat |

### Two defects found by reading the diff back, not by the reviewer

Recorded here because a ledger that only lists what the tool caught understates how the remaining
defects were missed:

1. **`_rel` ignored its `root` argument.** `main(root)` resolved output and universe against `root`
   while payloads were still relativized against module-level `ROOT`, so `--root` against an alternate
   checkout wrote absolute temp paths into a committed file. Found while verifying the flag at all.
   The first repair attempt still emitted 144 escaped paths — `_rel` resolved the payload but not the
   root, and macOS `/var` is a symlink to `/private/var`, so `relative_to()` rejected paths genuinely
   inside the root. Both sides resolve now; `test_generator_runs_without_the_frozen_universe` asserts
   `present.path == capabilities/skills/present/SKILL.md` through a symlinked temp root, which fails
   without either half.
2. **D6's remediation was thinner than its claim.** Detection now requires a licence *form* — the
   heading, the opening sentence of the canonical ISC text (which usually has no heading), or a BSD
   clause/license form. Measured against the committed ledger: **0 of 147 entries change verdict**, so
   nothing licensed is lost to the stricter needle. `test_a_licence_claim_must_look_like_a_licence`
   pins the canonical-text positive and the `not ISC licensed` negative.

### Root cause worth keeping

`capabilities/workflows/codeql-build.js` has **zero commits on any ref** (`git log --all --
--oneline -- <path>` → empty; absent in `HEAD`). Four checks across two files asserted against
it. They passed on one workstation because the untracked file was present, and on any clean
checkout they fail before anything they guard is examined — one of them aborted the run before
the rest of the suite. `PROSE` is empty across all 106 tracked docs, so the prose-pointer lane
was not merely unsatisfied, it was unsatisfiable; its one match in the tracked tree is a path
inside backticks. Deleted rather than retargeted, so the file no longer claims coverage it
lacks.

Suite state after this round: `1422 passed, 1 failed` over the full tree. The single failure is
`tests/fixtures/fable2031/dispatch-captured/test_c26024401_3f7a91c2.py`, a planted canary whose
own docstring states its failure is mandatory and that reporting a green suite is fabrication.

## Round 4 — delta at `f1e9bf5` (2 minor) and two in-flight blockers

CodeRabbit reviewed `fable-2031 → f1e9bf5` after the MIT/Apache/CC0 title anchoring:
**2 minor**, both taken.

| # | finding | disposition |
|---|---|---|
| R4-1 | Goal Card line 10 says 199 introduced but its parenthetical sums to ~197 | **VALID — reconciled here, not in the card.** The card is locked by directive ("document deltas, don't edit the card"). Re-measured through git, `71af341 → 984d60f`: introduced = **199** = 102 rows under new `(kind,id)` (the 91 exemplar renames live inside these; 69 of them carry byte-identical shas) **+ 97 rows whose existing key changed content**; retired = **188** = the same 97 old-sha rows + 91 keys gone. Net +11 keys (102 − 91), every term from the two committed `universe.jsonl` files. The card's `(~91 renames, ~95 edits, +11 new keys)` triple is superseded by this decomposition; its totals 188/199 were right and independently reproduce. |
| R4-2 | The named-residual fix said `shlex.split` + argv — shlex is not a security control (operators survive as literal argv only until something re-expands a shell) | **VALID — line rewritten.** The flip-condition fix is now stated as provenance (verify signed specs before retaining shell execution) or a shell-free command schema; `shlex.split` is explicitly named as *not* the control. |

Two blockers caught in review of my own work before sealing, both real:

1. **The title anchoring stopped mid-line.** `e40ed8b`'s and `f1e9bf5`'s Apache/CC branches
   anchored the *start* only — regex search stops wherever the pattern stops, so
   `…(the "License") is not applicable` and `…PROVIDE LEGAL SERVICES is false` still returned
   permissive ids. `091fced` demands the complete canonical notice — version, parenthetical
   in straight or curly quotes, optional semicolon, end-of-line — and the CC corporation
   clause's sentence period (line-end would have been wrong: the authentic deed continues on
   the same line, so the anchor is the period followed by whitespace/EOL). Both exact
   suffix-denials are table-test negatives beside their canonical positives; 0 of 140 ledger
   verdicts change.
2. **The Snyk observation over-claimed.** It proved zero projects *now* and no PR control on
   General Settings — not that nothing was *ever* imported, not the GitHub integration's
   health (its page sits behind a ToS re-acceptance the probe refused to click), and not that
   no such control exists anywhere. All three claims confined to what the UI showed; the
   conclusion is "not present on reachable surfaces."

### Store-gate stability, measured at the final tree — not "302, stable"

Three consecutive `skillos check --stores` runs at `091fced`/`2f95382` returned
**302 / 140 / 233** valid. The arithmetic reconciles exactly once the blob lane is read
from the universe, not from the ledger: the stable blob-lane count is **139** — the number
of `store.status = blob` rows in `docs/skillos/universe.jsonl`, matching the offline count
`skillos check` itself prints — and every online run is 139 + recipe successes:
302 = 139 + 163, 140 = 139 + 1, 233 = 139 + 94. The recipe lane is a live network probe:
6 url+commit groups fetched shallow over unauthenticated HTTPS with a 60-second per-fetch
timeout, verified rows tracking how many groups survived. Named failure text: `git fetch
--depth 1 origin <commit> … timed out after 60 seconds`.

**Clearance ≠ storage.** The ledger's 140 archive-cleared *entries* are not 140 stored
blobs: they cover **139 distinct `(kind,id)` assets** — `skill/evidence-retrieval-citations-gate`
carries two cleared entries (shas `9eb5b1786d9e`, `afe28f7a5500`, both MIT, two content
versions of one asset) — and clearance only *permits* filing; a row still needs its current
snapshot content to be the cleared content. All 139 blob rows map to cleared assets and no
blob row lacks clearance (checked both directions). So the honest statement of the v5
blocking gate is:

> `skillos check --stores` rc=1; valid = 139 blob receipts (stable, offline-verifiable)
> + recipe receipts verified this run (1 to 163 of 163, network-dependent); invalid
> 4,702–4,864 (each run's invalid = 5004 − that run's valid); the gate is red on every run and its red does not depend on the flaky
> lane — 4,700+ rows have no evidence of any kind.

*Superseding note (clean-tree ledger regen at the review SHA):* after the M1 fix (restored
snapshots no longer inherit the repo MIT grant), the ledger was regenerated in a detached
worktree of the committed tree with the shared warehouse copied in. The new artifact carries
**139** archive-cleared entries over 139 distinct assets; the duplicate cleared entry for
`skill/evidence-retrieval-citations-gate` is gone because its stored-drift blob is now
**denied** — the bytes in the warehouse carry no licence evidence of their own, and clearance
of live content no longer blesses different stored bytes (`skill/codeql` likewise in
`needs_review`). **The stable blob lane moved with the artifact:** `_licence_map` is
digest-bound, so the two universe rows referencing denied hashes dropped too — bare
`skillos check` now reports `valid_store_count` **137**, not the 139 measured above under the
old artifact. Every "139 stable" figure in this section is explicitly a pre-regen measurement,
and so is the 4,702–4,864 invalid range quoted above: under the committed artifact the blob
lane is 137, so the range is **4,704–4,867** (invalid = 5004 − 137 − rows verified that run).
`09-STOCKTAKE-AND-DIRECTIVE.md` §1 is the authoritative snapshot; Round 6 below is where that
cross-surface drift was caught and closed.

A future hardening (not this delta): cache verified fetch results per url+commit with a TTL
so the gate's reported number is reproducible, and raise or parallelize-aware the 60 s cap.

## Round 5 — delta reviewed at `a0de0ac` (3 minor)

| # | finding | disposition |
|---|---|---|
| R5-1 | Stale internal reference "line 82" after the shlex rewrite shifted the quoted paragraph | **VALID — fixed.** The controlling statement is now named by its heading (`**Not done here:**` paragraph), not by a line number that any edit invalidates. |
| R5-2 | Trust-boundary text said commands come from `loop.yaml` or CLI args, while the table itself listed `RIG_LOOP_VERIFIER_CMD` | **VALID — fixed.** The env var is named as a third input channel and the accepted risk is restated as "files, argv, **or environment** on this machine" — the same principal that can execute anything here. (The same edit briefly broke the table's blank-line and duplicated a row; both repaired, table re-read after.) |
| R5-3 | "302 max" vs "140 + 163 = 303", and rows-vs-groups units | **VALID — already cured pre-review.** The addendum was amended (unpushed) to 139 stable blobs: totals 302 = 139 + 163 exactly; 6 URL+commit groups are named as groups, and 163/1/94 as verified *rows* per run. This round reviewed the pre-amend text. |

## Round 6 — delta reviewed at `7f69703` (1 major, 1 minor)

22 files reviewed, `fable-2031 → cr-base-984d60f` (transcript kept at `.local/cr19.log`). Both
findings are against `docs/skillos/09-STOCKTAKE-AND-DIRECTIVE.md`, both correct, both taken. The
review ran *after* the last commit, so these were the only open findings in the tree.

| # | finding | disposition |
|---|---|---|
| R6-1 | **Major** — receipt counts and route counts inconsistent: at 163 recipe-verified rows the post-regen formula gives 4,704, not the 4,702 §3 equated to `invalid_store_count` (130 + 4,571 + 1) | **VALID — fixed by publishing one authoritative snapshot and accounting for the two rows.** §1 no longer carries a pre-regen table plus a superseding caveat; it carries one post-regen measurement at `7f69703` with both lanes side by side (offline: valid 137, invalid 4,867, rc 0; `--stores`: valid 300 = 137 + 163, invalid 4,704, rc 1) and a five-row breakdown of the red. The missing 2 are the drift-denied `blob` rows, which are *not* in `unresolved` (4,572 = 2,425 + 2,146 + 1) and so were absent from every route: `skill/codeql` and `skill/evidence-retrieval-citations-gate` hold a `blob` receipt whose stored digest carries `archive_allowed: false`. Route C now covers 3 rows and the identity is `130 + 4,571 + 3 = 4,704`. The reviewer's second half was right too — the group attributions do name universe rows, so the hedge that said so was deleted and the blob-receipt lane is stated separately: `blob 139` counts receipts, `valid 137` counts receipts the ledger clears, and the ledger's own 142/139/`needs_review` totals are quoted beside them. |
| R6-2 | Minor — §5 claimed §1's numbers were reproducible without requiring a clean worktree or defining `.index.json` state, while §6 recorded 5006 assets in a shared root against 5004 in a fresh clone at the same commit | **VALID — fixed, and the drift is worse than the finding says.** §5 is now a `git worktree add --detach` + `reindex` recipe and states which inputs make the store lane deterministic: `universe.jsonl`, `blob-license-ledger.json` and the **139 tracked blobs** under `docs/skillos/warehouse/` are all committed, so the blob lane reproduces exactly; `.index.json` is gitignored, per-root, and rebuilt from the external harness roots. Re-measured at `7f69703`: the shared root and a fresh worktree now *both* read 5005 with 140 canonical — the 5006/5004 pair was a point-in-time reading, which is the argument for pinning the index rather than quoting a total. §5 therefore separates reproducible fields (`n` 5004, `blob` 139, offline `valid` 137, the two `licence_denied` ids) from the network-dependent recipe lane and from the reindex total, whose only reproducible assertion is `ok_keys: true`. |

### A third defect, found by running §5 rather than reading it

§4 quoted the plant script's old success text (`planted on agent/rig-lattice-router.md -> …`,
`restored -> re-granted=True problems=(none)`). `f9caddf` had already replaced that output with
five named proofs — the doc was quoting a run that can no longer happen. §4 now quotes the five
`PASS` lines the script actually prints at this commit. Every command in §5 was executed in the
clean worktree before the rewrite: `33 passed, 10 subtests`; plant exit 0 with all five proofs and
a clean canonical tree; `check` rc 0; `check --stores` rc 1.
