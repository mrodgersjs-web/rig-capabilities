---
name: web-color-tokens
description: Turn a palette into a token system with roles, themes and dark mode. Use when a design system needs colour tokens or when the same colour is re-decided page by page.
outcome: A semantic colour token system resolved for light and dark with zero raw hex in components.
done_when:
  - 'grep:capabilities/skills/web-color-tokens/SKILL.md:[S]weep for raw hex'
  - 'grep:capabilities/skills/web-color-tokens/SKILL.md:[A]dd roles, not literals'
  - every component colour references a role token and zero raw hex remains
  - light and dark resolve from the same token names
  - both themes pass web-color-contrast with ratios recorded
  - adding a new colour requires adding a role, not a hex literal
great_example: examples/great/design-ux/web-color-tokens.md
quality_floor: Any raw hex in a component after the sweep fails this skill. A dark theme defined by overriding components rather than tokens fails this skill.
activation: Load when building or repairing colour tokens, when dark mode is being added, or when the same colour has three different hex values across the site.
instruction: Encode colours as semantic tokens with role names and resolve them per theme. One source of truth, no raw hex in components, and dark mode is a token resolution rather than a second stylesheet.
applies_when:
  env: a codebase with a design token file
  runtime: web app or site consuming tokens in CSS or JS
  deps: web-color, the project token file
  params: role-named tokens, light and dark resolved from the same names
  budget: one token file, zero raw hex in component code
  scale: one page to a full design system
permissions:
  - fs.read
  - fs.write
flow:
  - Declare role tokens (ink, paper, surface, accent, muted, warn, ok).
  - Assign light values, then dark values for the same role names.
  - Emit them as CSS custom properties or token JSON consumed by the build.
  - Sweep components for raw hex and replace with role tokens.
  - Re-run web-color-contrast against the resolved values for both themes.
out_of_scope:
  - choosing the hues (web-color)
  - photographic and asset colour
  - runtime theme generation
---
# Colour: Tokens

One source of truth. Dark is a resolution.

## Method

**Semantic, not literal.** `--accent` is a token. `--oxblood-600` is a palette swatch. Components
consume roles so a rebrand is a token edit.

**Dark as resolution.** Declare both values for the same role names under a theme selector. Any dark
mode that overrides component styles is a second design system wearing a disguise.

**Sweep for raw hex.** The done-test is a grep that returns zero. If a component hard-codes a colour,
the token set has a hole.

**Add roles, not literals.** A new colour needs a job. "It looked better" is how palettes rot.

## Corpus evidence

- Flux Academy / We Redesigned Hacksmith! (StudioXperience Ep.) / 5rTKCrqxkrQ / [10:18] / "brand toolkit with a color palette"
- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [14:29] / "have like a light mode and a dark mode"

The corpus puts the palette in the brand toolkit and treats light and dark as paired modes. The
semantic-token method and the zero-raw-hex rule are UNVERIFIED against this corpus.

## Anti-patterns

- Palette swatch names used as token names.
- Dark mode as a component-override stylesheet.
- Raw hex in component code.
- A new colour added with no role.
- Two tokens with different names and the same value.

## Links

parent: when-designing-websites
children: none (sub-skill of web-color)
