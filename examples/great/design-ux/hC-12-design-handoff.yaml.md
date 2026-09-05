---
name: great-hc-12-design-handoff-yaml
lane: design-ux
exemplar_of: hC-12-design-handoff.yaml
description: "Reference exemplar — a byte-frozen account-settings design transferred with complete inventory, token mapping, state matrices, responsive rules, and dual sign-off."
---

# hC-12 design handoff — account settings R1

## Input

Handoff the approved account-settings flow to the web implementation owner. Freeze the source export as revision R1; cover profile, security, notifications, billing, and their linked confirmation/error flows.

## Output

`artifacts/handoff/account-settings/` contains `FREEZE.txt`, `inventory.yaml`, hashed exports under `assets/`, annotation coverage, `token-map.yaml`, state and breakpoint matrices, `copy-deck.yaml`, `open-questions.yaml`, walkthrough notes, and the dual-signed checklist. Each copy string has a stable ID, character limit, and truncation rule. Post-handoff changes re-enter as R2 with a new freeze hash.

## Acceptance

```console
$ shasum -a 256 -c artifacts/handoff/account-settings/assets.sha256
# expected: every SVG and raster variant reports OK
$ ./bin/rig-capabilities goal-spec --stem hC-12-design-handoff
# expected: verdict OK
```

The inventory count matches the frozen source, annotation coverage is 100%, and every design value maps to a code token or an owned token request. Each interactive component covers default, hover, active, focus, disabled, loading, empty, and error states. Responsive behavior states concrete reflow constraints. `blocking: true` count is zero, and both design and build sign-off lines are named and dated.