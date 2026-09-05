---
name: great-hc-11-motion-design-yaml
lane: design-ux
exemplar_of: hC-11-motion-design.yaml
description: "Reference exemplar — functional dashboard motion bound to duration/easing tokens, profiled at the frame budget, and paired with reduced-motion behavior and implementation parameters."
---

# hC-11 motion design — dashboard state transition

## Input

Specify the filter-to-results transition, metric-update feedback, and error-banner entrance for the renewal dashboard. Every animation must serve orientation, feedback, or continuity; the reference device target is 60fps.

## Output

`artifacts/motion/dashboard-refresh/motion-spec.yaml` records trigger, purpose, duration token, easing token, stagger, sequence order, and fallback for each animation. The implementation table maps the three motions to CSS or GSAP parameters. `perf/` contains the DevTools trace; `captures/` pairs 1x and 0.25x reviews with full and reduced-motion variants.

## Acceptance

```console
$ node tokens/validate.mjs tokens/tokens.json
# expected: exit 0; every referenced duration and easing token resolves
$ grep -rEn 'animation|transition' artifacts/motion/dashboard-refresh/ --include='*.css'
# expected: animated properties are transform/opacity or have paint-cost evidence
$ ./bin/rig-capabilities goal-spec --stem hC-11-motion-design
# expected: verdict OK
```

The performance capture meets the declared dropped-frame budget. `prefers-reduced-motion: reduce` has a specified, captured fallback for every motion; no large parallax, flashing over 3/s, or unpausable loop over five seconds appears. Each capture filename matches a motion-spec key and each implementation parameter equals its resolved token value.