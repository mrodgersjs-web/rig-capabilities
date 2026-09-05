---
name: great-hc-05-design-token-build-yaml
lane: design-ux
exemplar_of: hC-05-design-token-build.yaml
description: "Reference exemplar — one canonical token source producing deterministic CSS and Tailwind outputs, then replacing a real component literal without visual drift."
---

# hC-05 design token build — semantic status colors

## Input

Add `color.alias.status.warning` and its dark-mode value to `tokens/tokens.json`, preserving the global/alias/component tier convention. Generate the declared web targets and migrate the alert banner from its duplicated hex value to the alias.

## Output

The run leaves validated source tokens, `dist/tokens/tokens.css`, `dist/tokens/tailwind.tokens.js`, an entry in `tokens/CHANGELOG.md`, and before/after alert-banner captures under `artifacts/token-build/status-warning/`. The generated-file review maps each output delta to `color.alias.status.warning`; the literal sweep records any intentional exceptions.

## Acceptance

```console
$ node tokens/validate.mjs tokens/tokens.json
# expected: exit 0 with no collision or missing type/tier
$ node tokens/build.mjs && sha256sum dist/tokens/* > /tmp/t1 && node tokens/build.mjs && sha256sum -c /tmp/t1
# expected: exit 0; every generated file reports OK
$ npm test -- tokens
# expected: exit 0 with no unexplained snapshot delta
$ ./bin/rig-capabilities goal-spec --stem hC-05-design-token-build
# expected: verdict OK
```

The component uses the built token, not a new parallel constant; source and output token counts reconcile. A visual comparison of the real alert banner reports no unintended change, and the residual `grep -rEo '#[0-9a-fA-F]{6}' src --include='*.tsx' --include='*.css'` results are mapped to tokens or exception-listed.