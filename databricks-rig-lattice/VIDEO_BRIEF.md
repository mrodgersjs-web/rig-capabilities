# Video Brief — Databricks × RIG Lattice (drafted 2026-09-10, gated on build)

Two products, two acceptance sets. Do not merge them into one cut.

## Sequencing law
1. Build first. 2. REAL product capture second (screen-recorded workflow).
3. Higgsfield generation third — **B-roll, transitions, title cards, and
   atmospheric shots only**. No Higgsfield frame may depict product UI,
   output, or latency. Anything synthetic must read as atmosphere, never as
   product evidence.
4. Render spend is a paid effect: exact-action Gate-D before Higgsfield
   credits are burned.

## Demo cut — acceptance set
- **Source of truth:** recorded from the actual runner/Marketplace/MCP surface
  in a live session. No fabricated or mock UI anywhere in frame.
- **Deterministic script:** narration and on-screen steps generated from real
  command output + ProofPacket artifacts (commit SHAs, exit codes, seal IDs
  may be shown verbatim).
- **Visible inputs and outputs:** viewer sees what was typed/registered and
  what came back, in the same shot.
- **Error path shown once:** a planted failure → gate goes RED → restore →
  GREEN (the adversarial-verification loop is part of the demo, not hidden).
- **Latency honesty:** real timing on screen (no speed-ramp hiding waits).
- **Captions:** burned or sidecar, WCAG-legible, verbatim.
- Duration ≤ 90 s hero; 16:9 primary + 9:16 vertical variant.
- Endcard: D85 seal artifact (real, from the sealed run).
- Gate: reviewer verdict "no synthetic UI presented as product" or it does not
  ship.

## Marketing cut — acceptance set
- Duration ≤ 30 s hero, ≤ 60 s full; variants 16:9 / 9:16 / 1:1.
- Hook: partner-gravity claim, worded only from Tier-A rows of
  PARTNER_ANALYSIS.md (public award facts). No co-brand implication: naming
  Accenture/SAP/Salesforce/Deloitte requires "public record" phrasing; logo
  usage requires written clearance, otherwise text-only treatment.
- Determinism as trust beat; one CTA, single destination.
- Brand gates before ship: brand-quantify pass, virality-predictor score at
  picture-lock, captions/a11y, multi-platform export set.
- Higgsfield scope here: cinematic B-roll (lattice visuals, dataflow
  atmosphere), transitions, title typography — per the treatment.

## Pipeline routing (when unblocked)
rig-film-studio treatment → real capture (screen) → Higgsfield B-roll via
higgsfield-generate (CLI) → edit → brand gates → Gate-D'd export. If Mike
appears: rig-soul-mike for likeness-faithful frames.
