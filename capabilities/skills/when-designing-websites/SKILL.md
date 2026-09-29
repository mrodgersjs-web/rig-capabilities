---
name: when-designing-websites
description: Meta-skill router for web design studio work. Use when designing, redesigning, critiquing or shipping a website, landing page, marketing site, or web product surface. Routes to 10 domain skills and 20 sub-skills. Enter here before picking a specialist skill.
outcome: A web surface designed against a stated buyer and brief, with every load-bearing design decision traceable to a named source or marked as a deliberate unverified choice.
done_when:
  - the routed skill set is named in one line
  - each loaded skill reports its own done_when as satisfied
  - web-design-critique returns an explicit verdict with zero remaining blockers
great_example: examples/great/design-ux/when-designing-websites.md
quality_floor: No page ships with an unexplained font pair, a palette chosen by vibe, a CTA with no hierarchy decision, or a critique verdict that contains no named finding.
activation: Load at the start of any task that produces or judges a web page: new site, redesign, landing page, hero, pricing page, portfolio, marketing site, or a "make this look better" request on web UI.
instruction: >
  Route the job to the smallest set of domain skills that covers it, in dependency order:
  discovery -> craft (typography, color, layout) -> motion and imagery -> conversion copy ->
  build and ship -> critique. Never start at build. Never skip critique. Every design claim that
  becomes a rule must cite corpus evidence (channel / title / videoId / timestamp) or be marked
  UNVERIFIED.
applies_when:
  env: any context about to produce or judge a web surface
  runtime: web page, site, or web product surface rendered in a browser
  deps: a brief or a named buyer; the corpus at ~/Developer/rig-design-studio/corpus/youtube
  params: job class is one of new, redesign, critique, fix
  budget: load only the skills the surface actually exercises
  scale: single page up to a full marketing site
permissions:
  - fs.read
  - fs.write
  - browser.read
  - gate-d-required:deploy
  - gate-d-required:publish
  - gate-d-required:purchase
  - gate-d-required:send
flow:
  - Classify the job as new, redesign, critique or fix.
  - Load web-design-discovery; if a brief or a buyer is missing, stop and get it.
  - Load the craft skills the surface actually exercises (web-typography, web-color, web-layout).
  - Load web-motion and web-imagery only when the brief calls for motion or imagery.
  - Load web-conversion-copy for any page with an ask (CTA, signup, purchase, booking).
  - Load web-build-ship before anything leaves the machine.
  - Run web-design-critique last; it can fail the job, in which case fix and re-run.
out_of_scope:
  - native mobile app design
  - print and brand-only identity work
  - video production
  - backend architecture
  - any action that spends money or publishes publicly without Gate-D approval
---

## Front door moved (2026-09-28)

Design work now enters through **`design-studio-os`** (`/design-studio`), the RIG Design Studio OS meta
skill in `~/Developer/rig-design-studio-os`. It carries 15 stage mains with 103 sub-skills, 16 agents,
10 harnesses, 8 loops and 7 dormant hooks, all backed by 826 laws cited CLAIM(videoId@mm:ss) to the
design YouTube corpus. This router still resolves its own table below; where a row names a `web-*`
skill, the matching `ds-*` stage is now the canonical owner (see
`~/Developer/rig-design-studio-os/docs/DISPOSITIONS.md`): web-design-discovery -> ds-discovery,
web-typography -> ds-typography, web-color -> ds-color, web-layout -> ds-layout, web-motion ->
ds-motion-3d, web-imagery -> ds-imagery, web-conversion-copy -> ds-conversion-copy, web-build-ship ->
ds-build-ship, web-design-critique -> ds-critique, web-design-business -> ds-business. Read this
router for the estate map; load `design-studio-os` to run the work.
# When Designing Websites

The router for web design studio work. Read the job, then load only the skills it needs.

## The skill tree

| # | skill | sub-skills | load when |
|---|---|---|---|
| 1 | `web-design-discovery` | `web-design-discovery-brief`, `web-design-discovery-sitemap` | always, first |
| 2 | `web-typography` | `web-typography-scale`, `web-typography-pairing` | any page with text |
| 3 | `web-color` | `web-color-tokens`, `web-color-contrast` | any page with color |
| 4 | `web-layout` | `web-layout-grid`, `web-layout-editorial` | any page with more than one section |
| 5 | `web-motion` | `web-motion-narrative`, `web-motion-budget` | brief calls for motion |
| 6 | `web-imagery` | `web-imagery-provenance`, `web-imagery-3d` | brief calls for imagery or 3D |
| 7 | `web-conversion-copy` | `web-conversion-copy-hero`, `web-conversion-copy-proof` | any page with an ask |
| 8 | `web-design-business` | `web-design-business-pricing`, `web-design-business-client` | quoting, positioning or client process |
| 9 | `web-build-ship` | `web-build-ship-responsive`, `web-build-ship-performance` | before anything leaves the machine |
| 10 | `web-design-critique` | `web-design-critique-taste`, `web-design-critique-antislop` | always, last |

## Dependency order (do not reorder)

```
discovery -> typography -> color -> layout -> motion -> imagery -> conversion-copy -> build-ship -> critique
                              \-> design-business (parallel, whenever money or a client is involved)
```

Discovery can invalidate everything downstream. Critique can send you back to any earlier step.

## The evidence rule (hard)

This tree is distilled from the web-design corpus at
`~/Developer/rig-design-studio/corpus/youtube/` (see its `PROVENANCE.md`). Therefore:

- A claim promoted to a **rule or gate** cites `channel / title / videoId / [MM:SS]`.
- A claim with no corpus support is written as `UNVERIFIED` and stays advisory. It never gates.
- A transcript is what someone said, not what is true. Auto-captions mishear numbers: any number
  taken from an `auto` caption is `UNVERIFIED` until checked.
- Never invent a videoId or a timestamp. A missing citation is better than a fabricated one.

## Routing table by job type

| job | route |
|---|---|
| "build me a site / landing page" | 1 -> 2,3,4 -> 5,6 (as needed) -> 7 -> 9 -> 10 |
| "this looks like AI slop" | 10 (`web-design-critique-antislop`) -> whichever craft skill the finding names |
| "make it convert" | 7 -> 4 -> 10 |
| "fix the type / it feels off" | 2 -> 10 |
| "dark mode / brand colors" | 3 (`web-color-tokens`, `web-color-contrast`) |
| "it janks when I scroll" | 5 (`web-motion-budget`) -> 9 (`web-build-ship-performance`) |
| "what should I charge" | 8 -> 10 |
| "audit this page" | 1 (light) -> 10 (full) |
| "ship it" | 9 -> 10 |

## Boundaries

- **Fail closed on the classifier.** When Jev / `rig-s1gate` is unavailable, errors, or has no kind for
  the job at hand, DEFER. Never guess a verdict locally, and never invent a JEV model. An advisory
  PASS is not permission to send, push, deploy or spend.
- Outward and irreversible acts (deploy, DNS, publish, buying assets, sending mail) are Gate-D.
  Prepare everything, then stop and ask.
- The studio's locked regions (`NORTH-STAR.md`, `LOCK:*`) only move on explicit re-lock.
- Critique verdicts name the finding, the location, and the check that failed. Adjectives are not
  findings.
