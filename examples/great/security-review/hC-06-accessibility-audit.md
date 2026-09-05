---
name: great-hc-06-accessibility-audit-yaml
lane: security-review
exemplar_of: hC-06-accessibility-audit.yaml
description: "Reference exemplar — a WCAG 2.2 AA audit combining route-wide automation with keyboard, VoiceOver, focus, contrast, zoom, and reduced-motion evidence."
---

# hC-06 accessibility audit — signup flow

## Input

Audit `/signup`, `/verify-email`, and `/welcome` at WCAG 2.2 AA. The critical flow is account creation through the first welcome action; automated findings alone are insufficient.

## Output

`artifacts/a11y/signup/` contains `scope.yaml`, one axe JSON per route, `keyboard-log.md`, `sr-log.md`, 200%/320px and reduced-motion captures, and `report.md`. Each finding includes its WCAG success criterion, severity, evidence path, reproduction steps, and a `verified by` command or manual assistive-technology check. Form errors record actual versus expected VoiceOver announcements.

## Acceptance

```console
$ npx axe http://localhost:3000/signup --save artifacts/a11y/signup/axe/signup.json
# expected: scan artifact saved; violations summarized by impact
$ node scripts/contrast-audit.mjs /signup /verify-email /welcome
# expected: every rendered text/background pair has a measured ratio and failures name the 4.5:1 or 3:1 threshold
$ grep -rn 'outline: *none\|outline: *0' src --include='*.css'
# expected: every hit maps to a replacement focus style or a report finding
$ ./bin/rig-capabilities goal-spec --stem hC-06-accessibility-audit
# expected: verdict OK
```

Keyboard logs reconcile tabbed and DOM-interactive counts with zero traps. Screen-reader evidence covers each critical step, input and labeled-input counts match, and every critical/serious issue has a remediation ticket plus a deterministic re-test criterion.