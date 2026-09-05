---
name: great-semgrep
lane: security-review
exemplar_of: semgrep
description: >-
  An approved, telemetry-off Semgrep plan executed by the canonical runner, with every failed, skipped, and zero-coverage ruleset carried into the report before SARIF merge.
---

# Semgrep — approved plan to auditable SARIF

## Input

Scan `/work/checkout` in `run-all` mode after explicit approval of `rulesets.json`. The plan includes language rules plus the required applicable third-party repositories. The target and output directory are absolute and fixed before execution.

## Output

The runner owns command generation so every scan has `--metrics=off`, correct language includes, and the approved ruleset list:

```console
$ bash capabilities/skills/semgrep/scripts/run-scans.sh \
    --target /work/checkout \
    --output-dir /work/checkout/static_analysis_semgrep_1 \
    --mode run-all \
    --rulesets /work/checkout/static_analysis_semgrep_1/rulesets.json \
    --jobs 4
```

It writes `scans.json`, per-unit JSON/SARIF under `raw/`, then the asset's merge step produces the consumer artifact:

```console
$ uv run --no-project capabilities/skills/semgrep/scripts/merge_sarif.py "$OUTPUT_DIR/raw" "$OUTPUT_DIR/results/results.sarif" --scans "$OUTPUT_DIR/scans.json"
```

## Acceptance

```console
$ jq -e '.failed == [] and .skipped == [] and .coveredNothing == []' "$OUTPUT_DIR/scans.json"
true
$ jq -e '.version == "2.1.0" and (.runs | type == "array")' "$OUTPUT_DIR/results/results.sarif"
true
```

If any list is nonempty, the scan may still be useful, but the report names every entry and never presents the run as complete.
