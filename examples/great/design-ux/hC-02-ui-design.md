---
name: great-hC-02-ui-design-yaml
lane: design-ux
exemplar_of: hC-02-ui-design.yaml
description: Reference exemplar for a token-only responsive UI with complete interaction states, measured contrast, breakpoint captures, review, and a frozen artifact.
---

# hC-02-ui-design.yaml — great example

## Input

Design a settings workflow from a brief naming the user, job-to-be-done, success metric, and constraints. Review three comparable interfaces for transferable patterns, then load the project's allowed color and type tokens before creating the surface. No ad-hoc hex or orphan font size is accepted.

## Output

The implementation uses the 8px spacing grid and produces captures at 375, 768, and 1440 pixels. `states.md` accounts for default, hover, active, focus, disabled, loading, empty, and error states for every interactive component, with tab order and visible focus annotations. Theo's pass/veto review is stored beside the artifacts.

```console
$ grep -rEo '#[0-9a-fA-F]{6}' artifacts/ui/settings/ --include='*.css' --include='*.html' | grep -vFf tokens/allowed-hex.txt
# expected: empty output; every color comes from the token source

$ node scripts/contrast-check.mjs artifacts/ui/settings/
# expected: exit 0 with body >=4.5:1 and large text/UI chrome >=3:1

$ sha256sum artifacts/ui/settings/final.html
# expected: digest is copied into FREEZE.txt with a version stamp
```

## Acceptance

- Brief and reference notes exist before design work, with patterns extracted rather than copied.
- All three breakpoint screenshots exist and show the same complete workflow.
- State matrix, focus order, and contrast evidence cover every interactive element.
- Aesthetic review has a recorded verdict, and the final HTML/export hash matches the frozen version.
