---
name: great-semgrep-rule-creator
lane: security-review
exemplar_of: semgrep-rule-creator
description: >-
  A test-first taint rule whose vulnerable and safe cases are both executable, with AST inspection preceding the smallest one-rule YAML detector.
---

# Semgrep rule creator — tainted eval

## Input

Detect Flask query input reaching Python `eval`, but do not flag a literal expression or input passed through the approved `sanitize` function. Create exactly `flask-eval-taint/flask-eval-taint.yaml` and `flask-eval-taint/flask-eval-taint.py`; the test file starts with `ruleid` and `ok` annotations before the rule exists.

## Output

The rule uses `mode: taint`, `request.args.get(...)` as a source, `eval(...)` as a sink, and `sanitize(...)` as a sanitizer. AST inspection confirms the source and sink shapes before pattern authoring:

```console
$ semgrep --dump-ast -l python flask-eval-taint/flask-eval-taint.py
...
$ semgrep --test --config flask-eval-taint/flask-eval-taint.yaml flask-eval-taint/flask-eval-taint.py
1/1: ✓ All tests passed
```

A planted change deleting `pattern-sanitizers` makes the safe sanitized case fail, demonstrating that the negative fixture constrains precision rather than decorating the file.

## Acceptance

- The directory contains one YAML rule and one language test file.
- `semgrep --test --config flask-eval-taint/flask-eval-taint.yaml flask-eval-taint/flask-eval-taint.py` exits 0.
- Both vulnerable and safe variants are present; no `todook`, `todoruleid`, or `languages: generic` annotation is used.
