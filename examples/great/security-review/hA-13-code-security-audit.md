---
name: great-hA-13-code-security-audit-yaml
lane: security-review
exemplar_of: hA-13-code-security-audit.yaml
description: Reference exemplar for a scanner-plus-manual security audit whose findings include exploit paths, reproduction status, and dispositions.
---

# hA-13-code-security-audit.yaml — great example

## Input

Audit a diff touching authenticated HTTP routes, file parsing, and a database sink. Enumerate every entry point and trust boundary, then select the five riskiest source-to-sink paths for manual review. A scanner hit is a candidate until the code trace reproduces it or records it as theoretical.

## Output

The audit stores `.rig/security/surface.md`, `.rig/security/boundaries.md`, raw SAST/SCA/secret reports, five traces in `.rig/security/taint-traces.md`, an authorization review with negative cases, and a deduplicated `.rig/security/FINDINGS.md`.

```console
$ semgrep --config p/owasp-top-ten --json --output .rig/security/semgrep.json .
# expected: valid JSON; every hit appears in the findings register or has a disposition

$ gitleaks detect --report-format json --report-path .rig/security/gitleaks.json --redact 100
# expected: no live credential; a live hit is a stop-tier result

$ ./bin/rig-capabilities goal-spec --stem hA-13-code-security-audit
# expected: the canonical scanner-plus-manual harness resolves
```

## Acceptance

- Five manual traces name source, code path, sanitizer or absence, sink, and verdict.
- AuthN/AuthZ review covers the auth path and three mutating endpoints with negative tests.
- Each finding has severity, exploit path, file:line, reproduction status, and fix-or-track disposition.
- Every critical/high issue is fixed with a regression test or tracked with owner and due date; findings are not sent without Gate-D.
