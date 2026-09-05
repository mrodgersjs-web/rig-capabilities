---
name: great-hc-07-mobile-design-yaml
lane: design-ux
exemplar_of: hC-07-mobile-design.yaml
description: "Reference exemplar — an iOS account-summary flow proven across device sizes, safe areas, thumb reach, dynamic type, dark mode, and failure states."
---

# hC-07 mobile design — account summary

## Input

Design the account summary and transaction detail flow for iOS using the pinned Apple HIG. The device matrix is iPhone SE, iPhone 15, and iPhone 15 Pro Max; both light and dark appearances are in scope.

## Output

`artifacts/mobile/account-summary/platform.md` names the guideline version and device matrix. `touch-audit.md` records every target's measured size, adjacent spacing, thumb-zone overlays, and system-gesture conflicts. `states.md` covers loading, offline, empty, and error states plus the asset budget. `manifest.yaml` lists every capture with sha256, including default and largest accessibility text sizes.

## Acceptance

```console
$ grep -R 'color\.alias\|surface\.' artifacts/mobile/account-summary/dark/ --include='*.css'
# expected: dark surfaces resolve through semantic tokens; no inverted-hex treatment
$ shasum -a 256 -c artifacts/mobile/account-summary/captures.sha256
# expected: every matrix capture reports OK
$ ./bin/rig-capabilities goal-spec --stem hC-07-mobile-design
# expected: verdict OK
```

All iOS targets measure at least 44x44pt with at least 8pt between adjacent controls; safe-area overlays show no interactive content under the notch or home indicator. The largest text size preserves critical labels without truncation, every data screen has four resilience states, and no desktop-only hover or right-click affordance survives review.