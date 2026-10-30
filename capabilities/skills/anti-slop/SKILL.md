---
name: anti-slop
description: Deterministic anti-slop audit and fix router for web and app interfaces. Flags the generic AI-generated look — centered-hero-plus-cards, default Tailwind indigo/violet gradients, glassmorphism auroras, single-font single-radius monotony, emoji icons, marketing filler without numbers, missing states, wrong-easing motion, missing tabular-nums, sub-44px hit areas, platform-ignoring mobile UI — and routes every finding to the canonical skill that owns the fix. Use when building or reviewing web/app UI, when asked to "anti-slop" or "/anti-slop" a target, or before shipping any interface that must not look AI-generated.
done_when:
  - grep:capabilities/skills/anti-slop/SKILL.md:FLAG. requires file:line
  - grep:capabilities/skills/anti-slop/SKILL.md:N flagged of \(11 web \+ 5 app\) checks
---

# Anti-Slop

Slop is the look any stranger could have generated. An audit reports one line per check: `PASS` or `FLAG file:line / evidence -> fix route`. Nothing is called "polished" without a named check behind it.

Run on `/anti-slop <file|page|component|app>`. No target: audit the module/page under work.

## Web interface checks

| # | Slop tell | Flag when | Route |
|---|-----------|-----------|-------|
| W1 | Centered hero + subtitle + two CTAs above N feature cards | Template hero leads the page with no proof/data/product | better-interface |
| W2 | Default palette | Tailwind `indigo-500`/`gray-900` as brand, or violet/purple gradient unearned | better-colors |
| W3 | Glassmorphism aurora | Backdrop-blur panels + 2 or more blurred gradient blobs as site-wide texture (one intentional panel allowed) | better-ui (surfaces) |
| W4 | Type and radius monotony | One font, one weight, one corner radius on every element | better-typography, better-ui |
| W5 | Emoji or mixed iconography | Emoji or inconsistent icon sets where an icon system belongs | better-ui (icons) |
| W6 | Marketing filler | "Lightning-fast", "Next-generation", "We help you" with no number | better-writing |
| W7 | Missing states | Any interactive element without hover / focus-visible / active / disabled / loading / empty defined | better-ui (enter-exit), review-animations |
| W8 | Wrong motion | Enter animations on `ease-in`; one duration for everything; motion that cannot be interrupted | animate, animation-vocabulary |
| W9 | No `tabular-nums` for data, no `text-balance` on headings | Numbers drift, headings break badly | better-typography |
| W10 | Hit areas under 44x44 px | Touch targets too small | better-accessibility |
| W11 | Shadow soup or border+shadow stacking | Giant drop shadows everywhere, or both a hard border and a big shadow on one element | better-ui (surfaces) |

## App and mobile checks

| # | Slop tell | Flag when | Route |
|---|-----------|-----------|-------|
| A1 | Platform-ignoring chrome | Web CSS pasted into native (or vice versa): missing platform sheet/bottom-bar/tab conventions | apple-design, animate-expo |
| A2 | JS-thread motion | Spring/transition work on the JS thread in React Native/Expo (drops frames under scroll) | animate-expo |
| A3 | Information-dump screen | 8+ dense independent items on one mobile screen | better-layout |
| A4 | Non-interruptible interactions | Swipe/sheet/transition that fights the user's velocity | apple-design |
| A5 | No haptics/gesture affordance at state changes | Sheet snaps, toasts, and destructive gestures with no sensory confirmation | animate-expo |

## Verdict

End with:

```
anti-slop: N flagged of (11 web + 5 app) checks
Wx FLAG <file:line> <evidence> -> <route skill>
```

Every FLAG names its fix skill and says one line what that skill will change. While any FLAG is open, the interface is not ship-ready. After routed fixes, re-run the audit; clean = `0 flagged`.

## Guardrails

- The audit is evidence-based: `FLAG` requires file:line (or the missing-state name) — no "feels generic" without a check number.
- Routes, not dupes: this skill detects; the 30 canonical design skills (better-ui, better-typography, better-colors, better-accessibility, better-layout, better-writing, better-interface, apple-design, animate, animate-expo, review-animations, improve-animations, find-animation-opportunities, animation-vocabulary, prototype, pick-ui-library, baseline-ui, improve-ui, etc.) own the fixes. On a full pass, finish with better-interface as the integrated review.