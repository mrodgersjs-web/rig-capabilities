---
name: great-hc-10-brand-identity-yaml
lane: design-ux
exemplar_of: hC-10-brand-identity.yaml
description: "Reference exemplar — a distinguishable brand identity operationalized as rules, licensed assets, contrast-safe tokens, and an explicit guardian verdict rather than a moodboard."
---

# hC-10 brand identity — operator analytics

## Input

Create the identity system for an operator analytics product entering a field of monochrome SaaS competitors. The open lane must be demonstrated against ten captured competitors, then expressed in logo, color, type, voice, and imagery rules.

## Output

`artifacts/brand/operator-analytics/` contains `platform.md`, ten competitive captures and `patterns.md`, `guidelines.md`, local licensed font evidence, `asset-manifest.yaml`, the six-dimension pre-publish checklist, and `theo-verdict.md`. The manifest hashes named logo variants; the guideline includes clearspace, minimum size, misuse examples, contrast ratios, fallback stacks, voice do/don't pairs, and banned imagery clichés.

## Acceptance

```console
$ node tokens/validate.mjs tokens/tokens.json
# expected: exit 0 after brand.* token additions, with no duplicate key
$ git diff tokens/tokens.json
# expected: only reviewed brand-tier additions traceable to the identity system
$ shasum -a 256 -c artifacts/brand/operator-analytics/assets.sha256
# expected: every listed asset reports OK
$ ./bin/rig-capabilities goal-spec --stem hC-10-brand-identity
# expected: verdict OK
```

All approved text pairs meet at least 4.5:1 contrast. A shuffled thumbnail test records reviewer, method, and misidentification count; asset names match the declared regex; all fonts have license paths; and Theo's pass or veto is present with concrete revision notes when applicable.