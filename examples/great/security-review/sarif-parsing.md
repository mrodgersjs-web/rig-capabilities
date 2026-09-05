---
name: great-sarif-parsing
lane: security-review
exemplar_of: sarif-parsing
description: >-
  A severity-correct SARIF reduction that joins results to rule defaults, preserves full paths while deduplicating, and emits stable file-line evidence for CI.
---

# SARIF parsing — inherited severity without lost findings

## Input

Process `results.sarif` from CodeQL. The fixture contains a result with no `result.level`; its referenced rule declares `defaultConfiguration.level: error`. Two tools also report the same fingerprint, while two different `login.py` paths share a basename.

## Output

Use the asset's standard-library helper rather than reading `.level` directly:

```console
$ PYTHONPATH=capabilities/skills/sarif-parsing/resources python3 -c 'from sarif_helpers import load_sarif,extract_findings,deduplicate,sort_by_severity; fs=sort_by_severity(deduplicate(extract_findings(load_sarif("results.sarif")))); [print(f"{f.file_path}:{f.start_line} [{f.level}] {f.rule_id}: {f.message}") for f in fs]'
src/auth/login.py:42 [error] py/sql-injection: User-controlled data reaches SQL execution
src/admin/login.py:42 [warning] py/weak-hash: Weak digest selected
```

The CodeQL result inherits `error` from the rule, the fingerprinted duplicate is removed, and the two distinct directory paths remain distinct.

## Acceptance

```console
$ python3 -m unittest discover -s capabilities/skills/sarif-parsing/resources -p 'test_sarif_helpers.py'
...
OK
```

The command exits 0. Any parser that defaults the missing CodeQL result level to `warning`, deduplicates by basename, or drops a finding without a stable key fails acceptance.
