---
id: rig-hq-sub-j5-1-a-map-has-red-links
version: 1
status: draft
tier: sub
department: Intelligence
agent: nadia-data
parent: rig-hq-prompt-iris-strategy
task: Interrupt sub-prompt (J5): a map has red links — file build cards to turn them green
triggers: red links, map gaps, unresolved links in the map
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J5 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J5 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a map has red links

**Trigger.** A process/system map shows unresolved (red) links.

**Typed inputs.** `map_path`, `red_links` (each: from, to, why unknown).

**Steps.**
1. For each red link, name what is missing: a decision, a data source, an owner, or
   a mechanism.
2. File one build card per link, sized to be checkable ("turn link X green by
   proving <artifact>").
3. Order the cards by what unblocks the most of the map; report the order.

**Output format.**
```
STATUS: <n> CARDS FILED
Red links: <from -> to> — missing: <decision|data|owner|mechanism>
Cards: <paths> (ordered)
First: <card> — unblocks <what>
```

**Expected output.** The map's gaps become a work queue, not a mood.

**Done test.** Every red link has exactly one card; each card names its check.

**Failure handling.** A link that is red because the idea is wrong -> a map revision
card instead of a build card.

**Persistence.** Cards filed where the build pipeline reads them; map keeps its red
until proven green.

**Redaction.** n/a.

**Stop / escape hatch.** Never draw over a red link to make the map look finished.
