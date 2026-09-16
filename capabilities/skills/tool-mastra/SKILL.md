---
name: tool-mastra
description: Verify installed Mastra CLI APIs and advise on TypeScript agents and workflows without treating Mastra as the Design Harness carrier.
outcome: "code-engineering: Mastra questions are answered against the installed CLI and embedded docs, while Temporal remains the selected runtime carrier"
done_when:
  - cmd:/Users/rig128gb/.hermes/node/bin/mastra --version
great_example: "Before suggesting a Mastra agent or workflow, inspect the installed package docs and validate requested components and model provider names with the installed CLI."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: registry:mastra-ai/skills
---

# tool-mastra

## Role in our stack

Mastra CLI 1.12.2 is a TypeScript specialist surface, not the Design Harness runtime carrier. The tool specialist verifies current installed APIs and can advise on Agent versus Workflow choices. The compiled RIG lanes remain on Temporal to avoid a second production runtime.

## Verified snippets

The globally installed artifact is the Mastra CLI bundle; its parser exports are the version-matched offline surface available without creating a project.

### 1. Construct the installed CLI logger

```javascript
const cli = await import("file:///Users/rig128gb/.hermes/node/lib/node_modules/mastra/dist/chunk-EH2DTFDR.js");
const logger = cli.createLogger(false);
if (!logger) throw new Error("logger construction failed");
```

Verified: `/Users/rig128gb/.hermes/node/bin/node /tmp/agentforge-snippets/mastra/verify.mjs 1` → exit 0.

### 2. Validate selected components

```javascript
const helpers = await import("file:///Users/rig128gb/.hermes/node/lib/node_modules/mastra/dist/chunk-W6CPGIEC.js");
const components = helpers.parseComponents("agents,workflows");
```

Verified: `/Users/rig128gb/.hermes/node/bin/node /tmp/agentforge-snippets/mastra/verify.mjs 2` → exit 0.

### 3. Validate a provider key

```javascript
const provider = helpers.parseLlmProvider("openai");
if (provider !== "openai") throw new Error("provider parse failed");
```

Verified: `/Users/rig128gb/.hermes/node/bin/node /tmp/agentforge-snippets/mastra/verify.mjs 3` → exit 0.

## Pitfalls

- Mastra changes quickly; inspect embedded docs/types for the installed project version before writing framework code.
- The global install is the CLI, not an application dependency on `@mastra/core`.
- Mastra requires ES2022 modules; CommonJS examples are not valid defaults.
- Do not choose Mastra as a carrier merely because a TypeScript agent could be expressed in it.

## Planted failure

The installed parser rejects an unknown component:

```bash
/Users/rig128gb/.hermes/node/bin/node --input-type=module -e "const m=await import('file:///Users/rig128gb/.hermes/node/lib/node_modules/mastra/dist/chunk-W6CPGIEC.js'); m.parseComponents('unknown')"
```

Expected: non-zero exit naming valid components.
