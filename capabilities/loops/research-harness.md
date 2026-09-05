---
outcome: research-intel:
done_when:
  - file:capabilities/loops/research-harness.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/research-harness.md
great_example: examples/great/research-intel/research-harness.md.md
quality_floor: 0.6
---

# Research Goal Harness — H_research(GL-RI)

Governs GL-RI (research/investigate) loops.
This is a runtime gate loop. Each gate must produce evidence before the session
may advance to conclusions or recommendations. No gate evidence, no progress.

## 0. Identity Lock

The session starts as Jake RIG Agent executing a research task. Before any
claims are made, identity and scope must be locked.

Gate 0.1 ❏ Session declared as GL-RI in first 3 lines.
Gate 0.2 ❏ RIG procedures loaded — `~/.hermes/jake/rig-operating-procedures.md`
   read or cited by line range.
Gate 0.3 ❏ Coordinate stated: `L{level}-D{diamond}-A{mode}-{step}`.
Gate 0.4 ❏ Research question stated in one sentence. Not a topic — a question.
   Proof: "I am investigating: <question>" appears before any searching begins.
   Bad: "Research AI agents." Good: "What revenue model do AI agent companies
   in the $1-10M ARR range use, and which has the highest LTV/CAC ratio?"

## 1. Source Verification

### 1.1 Source-Per-Claim
Gate S.1 ❏ Every factual claim has a source. No exceptions.
   Proof: each claim in the output is followed by `[source: URL]` or
   `[source: document name, page/section]`. Claims without sources are
   flagged as HYPOTHESIS, not FACT.
Gate S.2 ❏ Sources are primary where possible.
   Proof: for statistics, the original study/report is cited, not a blog
   that cites the study. For company data, SEC filings or official
   announcements, not third-party summaries.
   Hierarchy: primary source > peer-reviewed > trade publication > news >
   blog > social post > AI-generated.
Gate S.3 ❏ Source recency verified.
   Proof: each source has a date. Sources > 2 years old are flagged as
   "historical context" unless the claim is inherently historical.
   For fast-moving domains (AI, crypto, regulation): sources > 6 months
   old require explicit justification.

### 1.2 No Hallucinated Data
Gate NH.1 ❏ Zero fabricated statistics, quotes, or data points.
   Proof: every number in the output can be traced to a source.
   If no source exists for a needed data point, state "No verified data
   found for X" rather than inventing one.
Gate NH.2 ❏ URLs resolve and contain the claimed content.
   Proof: verify at least 3 random URLs from the output by fetching them.
   Show that the content matches what was cited.
Gate NH.3 ❏ Quotes are exact, not paraphrased as quotes.
   Proof: if quoting someone, the quote appears in the source verbatim
   (or is marked as paraphrase with `[paraphrased]`).

## 2. Anti-Generic Check

### 2.1 Specificity Gate
Gate AG.1 ❏ Every recommendation is specific to the research context.
   Proof: strip the company/topic name — if the recommendation still reads
   as generic advice, it fails. Example of generic: "Improve your SEO."
   Example of specific: "RIG's blog gets 12K organic visits/mo but ranks
   #8 for 'AI agent pricing' — rewrite the pricing page with schema markup
   targeting that exact query."
Gate AG.2 ❏ Anti-generic score >= 85.
   Proof: run the output through the AntiGenericForce scorer (or manual
   equivalent). Score must be >= 85/100.
   Scoring: +15 per unique data point, +10 per contrarian insight,
   +10 per specific number, +10 per named source, +10 per actionable
   recommendation, +10 per "I didn't know that" factor, +10 per
   competitive-specific insight, +15 per proprietary data used.
   -20 per generic advice, -15 per unsourced claim, -10 per obvious fact.

### 2.2 Contrarian Angle
Gate CA.1 ❏ At least one contrarian or counter-narrative angle explored.
   Proof: the output contains a section or callout that challenges the
   conventional wisdom on the topic. Not contrarian for contrarian's sake —
   backed by evidence.
Gate CA.2 ❏ Devil's advocate position stated for primary recommendation.
   Proof: "The strongest argument against X is Y" appears with a source.

## 3. Falsification Attempt

### 3.1 Pre-Mortem
Gate FM.1 ❏ Before presenting conclusions, attempted to falsify them.
   Proof: for each major conclusion, show one piece of evidence that would
   disprove it, and explain why it doesn't (or update the conclusion).
Gate FM.2 ❏ Considered alternative explanations.
   Proof: for each observed pattern, at least 2 explanations are listed
   before the preferred one is selected. Show the selection rationale.

### 3.2 Confidence Calibration
Gate CC.1 ❏ Each conclusion has an explicit confidence level.
   Proof: HIGH (90%+) = multiple primary sources agree, data is recent,
   methodology is sound. MEDIUM (60-89%) = sources agree but limited,
   or data is older. LOW (30-59%) = conflicting sources, thin data,
   or extrapolation. SPECULATIVE (<30%) = pattern recognition without
   direct evidence.
Gate CC.2 ❏ Confidence is earned, not assigned.
   Proof: the confidence level references the source quality and quantity.
   "HIGH confidence because 3 independent studies from 2026 show X" —
   not "HIGH confidence" with no justification.

## 4. Depth Discipline

### 4.1 No Surface Skimming
Gate DP.1 ❏ At least 5 distinct sources consulted.
   Proof: list of sources with brief note on what each contributed.
   Different pages on the same site count as 1 source.
Gate DP.2 ❏ Followed at least one unexpected thread.
   Proof: the research discovered something that changed the direction
   or added a dimension not in the original question. Document what
   was found and how it altered the analysis.

### 4.2 Structured Output
Gate SO.1 ❏ Output follows a consistent structure.
   Proof: contains at minimum — Executive Summary, Key Findings (numbered),
   Sources (full list), Confidence Matrix, Recommendations.
Gate SO.2 ❏ Executable next steps are present.
   Proof: at least 2 specific next actions with owner, deadline (or
   "when ready"), and expected outcome. Not "investigate further" —
   actual steps.

## 5. Gate-D Boundary

Gate D.1 ❏ No research findings published externally without approval.
   Proof: findings are internal artifacts. Publishing (blog, social,
   report to client) requires Gate-D approval.
Gate D.2 ❏ No named individuals criticized without legal review awareness.
   Proof: if research surfaces negative findings about named people,
   flag for review before any external use.

## 6. Proof Requirements

Every research session produces a ProofPacket:

```json
{
  "schema_version": "rig.research.v1",
  "run_id": "<uuid>",
  "loop": "GL-RI",
  "research_question": "...",
  "sources_consulted": 7,
  "sources_primary": 4,
  "claims_made": 12,
  "claims_sourced": 12,
  "claims_unsourced": 0,
  "anti_generic_score": 87,
  "gates": {
    "identity_lock": {"pass": true, "evidence": "..."},
    "source_per_claim": {"pass": true, "sourced": 12, "total": 12},
    "no_hallucination": {"pass": true, "urls_verified": 3},
    "anti_generic": {"pass": true, "score": 87},
    "contrarian_angle": {"pass": true, "evidence": "..."},
    "falsification": {"pass": true, "conclusions_tested": 3},
    "confidence_calibration": {"pass": true, "high": 2, "medium": 1, "low": 0},
    "depth": {"pass": true, "sources": 7},
    "gate_d": {"pass": true, "evidence": "internal only"}
  },
  "verdict": "PASS | FAIL",
  "proof_hash": "sha256:..."
}
```

## 7. Definition of Done

A research session is done when:
1. All applicable gates in §0–§5 passed.
2. Every claim has a source. Zero unsourced facts.
3. Anti-generic score >= 85.
4. At least one contrarian angle explored.
5. Confidence levels assigned and justified.
6. ProofPacket written.
7. One improvement entry to `~/.hermes/jake/improvements.log`.
8. Identity closure: coordinate, verdict, top 3 findings, next safe action.

## 8. What Happens When a Gate Fails

| Gate | On Failure |
|------|-----------|
| 0.1–0.4 (Identity) | HALT. No research begins without locked scope. |
| S.1–S.3 (Source) | Block. Add source or downgrade claim to HYPOTHESIS. |
| NH.1–NH.3 (No Hallucination) | HALT. Fabricated data = emergency. Purge and restart section. |
| AG.1–AG.2 (Anti-Generic) | Block. Rewrite until score >= 85. Generic research is worthless. |
| CA.1–CA.2 (Contrarian) | Block. Add contrarian angle before presenting conclusions. |
| FM.1–FM.2 (Falsification) | Warn. If skipped, flag conclusions as "untested." |
| CC.1–CC.2 (Confidence) | Block. Unjustified confidence is dangerous. |
| DP.1–DP.2 (Depth) | Warn. Flag if < 5 sources but allow if domain is niche. |
| SO.1–SO.2 (Structure) | Warn. Restructure output before delivery. |
| D.1–D.2 (Gate-D) | HALT. No external publication without approval. |

## 9. Self-Improvement Loop

After each research session, append to `~/.hermes/jake/improvements.log`:

```text
[YYYY-MM-DD HH:MM] research session: GL-RI
  gates passed: <count>/<total>
  gates failed/skipped: <which>
  sources consulted: <count>
  anti-generic score: <score>
  claims sourced: <count>/<total>
  capability gap: <what was missing>
  improvement: <what to add or change>
```

Every 5 entries: if the same gate fails 3+ times, update this harness.
If hallucination detected: immediate harness update with tighter controls.

## 10. Final Rule

```text
No source, no claim.
No falsification attempt, no conclusion.
No contrarian angle, no confidence.
Every research session leaves the knowledge base stronger than it found it.
```

---

*Companion to: hermes-conductor.md, doer-checker-validator.md*
*Governs: GL-RI (research/investigate)*

## What Great Looks Like (WGLL)

Amazing research output from this harness:

- **Every claim has a source URI** that returns HTTP 200 when tested
- **Sources are primary, not secondary** — original papers, official docs, direct data
- **Findings are structured** — executive summary, methodology, results, implications
- **Contradictions are surfaced, not hidden** — conflicting evidence gets its own section
- **Gaps are named explicitly** — "we don't know X because Y is inaccessible"
- **Numbers are sourced and dated** — no "studies show" without citation + year
- **Anti-generic score ≥ 80** — insights are specific to this context, not boilerplate

