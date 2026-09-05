---
name: great-hc-09-onboarding-flow-yaml
lane: design-ux
exemplar_of: hC-09-onboarding-flow.yaml
description: "Reference exemplar — an activation-first onboarding flow with a measured time-to-value path, honest progress, recoverable steps, consent separation, and runnable funnel instrumentation."
---

# hC-09 onboarding flow — first project created

## Input

Redesign onboarding so activation is the `project_created` event, fired only after a user names a project and saves its first task. Target median time-to-first-value is under 180 seconds with at most four required steps.

## Output

`artifacts/onboarding/first-project/activation.yaml` defines the event, target rate, source, step timings, and longest bottleneck. `flow.md` gives each step a completion signal, skip/defer/save recovery, permission timing, and separately untoggled consent choices. `events.yaml` specifies `step_entered`, `step_completed`, and `step_abandoned` payloads and includes the funnel query. The post-onboarding screen has a populated empty-state CTA.

## Acceptance

```console
$ shasum -a 256 -c artifacts/onboarding/first-project/captures.sha256
# expected: every screen in the four-step list reports OK
$ ./bin/rig-capabilities goal-spec --stem hC-09-onboarding-flow
# expected: verdict OK
```

The timeline totals no more than 180 seconds and every required step is value-delivering or legally required. No step dead-ends: abandonment preserves state or offers a declared exit. The event names in the funnel query exactly match `events.yaml`; control and one variant name a hypothesis and guardrail; and legal, privacy, and marketing choices remain separate and off by default.