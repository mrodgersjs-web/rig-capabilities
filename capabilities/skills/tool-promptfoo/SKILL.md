---
name: tool-promptfoo
description: Author deterministic-first Promptfoo eval matrices for Design Harness providers, prompts, assertions, and CI gates.
outcome: "data-analytics: prompt and provider variants are compared on repeatable local assertions before any model-graded evaluation is trusted"
done_when:
  - cmd:/Users/rig128gb/.hermes/node/bin/promptfoo --version
great_example: "An echo-provider suite validates rendering and JSON/contains assertions offline, then the same config adds one explicit judge provider for semantic scoring."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: registry:promptfoo/promptfoo
---

# tool-promptfoo

## Role in our stack

Promptfoo 0.121.17 is an **Evaluation** CLI/library for declarative prompt, provider, and assertion matrices. Prefer deterministic assertions and local providers. Model-graded assertions require an explicit grader and approved data destination.

## Verified snippets

### 1. Parse an assertion

```javascript
import { AssertionSchema } from "promptfoo";
const assertion = AssertionSchema.parse({ type: "contains", value: "RIG" });
if (assertion.type !== "contains") throw new Error("parse failed");
```

Verified: `/Users/rig128gb/.hermes/node/bin/node /tmp/agentforge-snippets/promptfoo/verify.mjs 1` → exit 0.

### 2. Parse a test case

```javascript
import { AtomicTestCaseSchema } from "promptfoo";
const testCase = AtomicTestCaseSchema.parse({ description: "offline", vars: { name: "RIG" }, assert: [{ type: "contains", value: "RIG" }] });
```

Verified: `/Users/rig128gb/.hermes/node/bin/node /tmp/agentforge-snippets/promptfoo/verify.mjs 2` → exit 0.

### 3. Run an offline echo eval

```javascript
import { evaluate } from "promptfoo";
const result = await evaluate({ prompts: ["Hello {{name}}"], providers: ["echo"], tests: [{ vars: { name: "RIG" }, assert: [{ type: "contains", value: "RIG" }] }] }, { cache: false, writeLatestResults: false });
if (!result.results[0].success) throw new Error("eval failed");
```

Verified: `/Users/rig128gb/.hermes/node/bin/node /tmp/agentforge-snippets/promptfoo/verify.mjs 3` → exit 0.

## Pitfalls

- Use `--no-cache` while developing to avoid stale greens.
- Use `--no-share`; it disables result sharing but not configured provider calls.
- Set the grader provider explicitly for model-graded assertions.
- Do not transform away a raw-output contract violation such as fenced JSON.

## Planted failure

Change the deterministic assertion to an absent string; the result must be unsuccessful:

```javascript
const bad = { prompt: "Hello RIG", expected: "MISSING" };
if (!bad.prompt.includes(bad.expected)) throw new Error("RED: contains assertion failed");
```

Expected: non-zero exit with `RED: contains assertion failed`.
