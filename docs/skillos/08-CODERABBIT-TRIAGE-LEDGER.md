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
