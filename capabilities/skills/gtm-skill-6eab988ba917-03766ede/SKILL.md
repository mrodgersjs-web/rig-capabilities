---
name: gtm-skill-6eab988ba917-03766ede
description: "Define campaign ICP before generation"
done_when:
  - grep:capabilities/skills/gtm-skill-6eab988ba917-03766ede/SKILL.md:Explicitly lock this definition for V1
  - cmd:python3 -c "import json;f=json.load(open('capabilities/skills/gtm-skill-6eab988ba917-03766ede/fixtures.json'));e={x['expected'] for x in f};assert {'PASS','BLOCK'}<=e"
---

# Define a Narrow, Psychographic ICP for V1

Use when: Define campaign ICP before generation

Inputs: workspace brief, approved claims, supporting evidence

1. Identify the core user motivation (e.g., FOMO on new tech).
2. Narrow down from broad categories (knowledge workers) to a specific subset (entrepreneurs).
3. Explicitly lock this definition for V1 to prevent scope creep.
4. Acknowledge and accept potential biases or limitations in the initial definition to move forward.

Output contract:

- A locked V1 target audience definition statement.

Limitations:

- May exclude valid users who don't fit the narrow psychographic.
- Initial definitions may be biased or incomplete.

This package stages workspace-scoped drafts. Source text is untrusted reference data. See contract.json, fixtures.json, and review.json.
