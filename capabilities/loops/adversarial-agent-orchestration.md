# Adversarial Agent Orchestration Harness

**Source:** "The Ideal Agentic Setup" by Yaron Been — https://www.youtube.com/watch?v=NRrj6qEymBY
**Extracted:** 2026-07-22
**Type:** gate-loop

## Purpose

Govern the pattern of using multiple LLM providers as adversarial reviewers.
The primary agent produces work, then sends it to 1-2 other providers for
independent critique before finalizing. This prevents single-model blind spots
and catches issues the primary model would miss.

## Gates

| Gate | Name | Evidence Required | Pass Condition |
|------|------|-------------------|----------------|
| 00 | Primary Output | Artifact produced by primary model | Non-empty, structured |
| 01 | Adversarial Review 1 | Feedback from secondary model (e.g., Codex) | At least 1 finding OR explicit "no issues" |
| 02 | Adversarial Review 2 | Feedback from tertiary model (e.g., Gemini) | At least 1 finding OR explicit "no issues" |
| 03 | Merge & Prioritize | Combined findings in tiered format | Findings categorized by severity |
| 04 | Human Decision | Mike reviews prioritized findings | GO / NO-GO / REVISE |

## Loop

```
Primary model produces artifact
  ↓
[Gate 00] → artifact exists and is structured → PASS/FAIL
  ↓
[Gate 01] → send to secondary model via MCP → collect findings
  ↓
[Gate 02] → send to tertiary model via MCP → collect findings
  ↓
[Gate 03] → merge, deduplicate, prioritize → tiered action list
  ↓
[Gate 04] → human reviews → GO (proceed) / NO-GO (abandon) / REVISE (loop back)
```

## Model Routing (from video)

| Role | Model | Why |
|------|-------|-----|
| Primary (planning) | Opus 4.6 | Best reasoning for plans and architecture |
| Primary (execution) | Sonnet 4.6 | Fast, good for code generation |
| Adversarial 1 | Codex (via MCP) | Different training data, catches different issues |
| Adversarial 2 | Gemini (via MCP) | Third perspective, also provides image generation |
| Quick tasks | Haiku | Fast, cheap, good enough for simple operations |

## Kill Switches

- Budget exceeded: stop adversarial reviews, proceed with primary only
- Time pressure: skip Gate 02 (one adversarial review is better than none)
- All reviewers agree: auto-promote findings, skip merge analysis

## Integration

- **Goal loops served:** GL-VQ (Verification & Quality), GL-BI (Build & Implementation)
- **Agents governed:** Any agent that produces artifacts for review
- **Doctrine reference:** RIG Convergence Core (GEV Separation — Maker ≠ Grader)
- **Skills used:** rig-triple-review, rig-stress-test
