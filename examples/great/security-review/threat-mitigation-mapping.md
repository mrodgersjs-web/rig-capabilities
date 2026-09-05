---
name: great-threat-mitigation-mapping
lane: security-review
exemplar_of: threat-mitigation-mapping
description: >-
  A risk-treatment matrix that gives each named threat layered preventive, detective, and corrective controls with owners, validation methods, and residual-risk decisions.
---

# Threat mitigation mapping — controls that can be tested

## Input

Map three accepted threat statements: SQL injection in checkout, stolen administrator sessions, and ransomware on the order database. Each threat includes likelihood, impact, affected asset, and an accountable owner; generic labels such as “improve security” are rejected.

## Output

The matrix maps every threat across layers and control types. For SQL injection: parameterized queries and server-side validation are preventive application controls; database anomaly alerts are detective data controls; credential rotation and incident containment are corrective. Each row records implementation owner, evidence path, test command or exercise, target date, and residual risk. The session highlights any threat with only one control as a critical gap.

The canonical asset contract is executable from the repository:

```console
$ ./bin/rig-capabilities test threat-mitigation-mapping
{
 "id": "threat-mitigation-mapping",
 "pass": true,
 "ran": 2,
 "unrunnable": 0
}
```

## Acceptance

- Every input threat has at least one preventive, one detective, and one corrective treatment, distributed across at least two control layers.
- Every control has an owner and a concrete validation method; untested controls remain planned, never “effective.”
- `./bin/rig-capabilities test threat-mitigation-mapping` exits 0 and reports `pass: true`.
