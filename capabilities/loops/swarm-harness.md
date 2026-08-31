---
outcome: agent-engineering:
done_when:
  - file:capabilities/loops/swarm-harness.md
  - the loop file parses and declares a termination test
great_example: examples/great/agent-engineering/swarm-harness.md.md
quality_floor: 0.6
---

# Swarm Harness — GL-SW / GL-AD Gate Loop

**Owner:** Jake PAI
**Scope:** GL-SW (Swarm research loops) + GL-AD (Adversarial/deviation loops)
**Status:** RUNTIME GATE LOOP
**Signed:** 2026-07-10

This harness governs every GL-SW and GL-AD cycle. No swarm result is accepted until all agents produce unique insights and the synthesis identifies conflicts. The loop is: SPAWN → DIVERGE → CONVERGE → SYNTHESIZE → VERIFY.

---

## Gate 0 — Identity Lock

Every swarm session must confirm identity before agents are spawned.

- G0.1 ❏ Load `jake-active-goal.json` and confirm `status == "ACTIVE"`
- G0.2 ❏ State the swarm type: `GL-SW` (research swarm) or `GL-AD` (adversarial/deviation swarm)
- G0.3 ❏ State the swarm objective: one-sentence problem statement for all agents
- G0.4 ❏ State the agent count target: `N` agents (minimum 3, maximum 10 for GL-SW; minimum 2, maximum 5 for GL-AD)

**Evidence:** Goal JSON + swarm type + objective string + agent count
**On-fail:** HALT. Write `G0-FAIL-{timestamp}` to `~/.rig/state/swarm-failures.log`. No agents spawned.

---

## Gate 1 — Agent Count Verification

All agents must be confirmed spawned and responsive before divergence begins.

- G1.1 ❏ Count spawned agents: `ps aux | grep {agent_process}` or process registry count
- G1.2 ❏ Each agent has a unique identifier: `{agent_id}` is non-colliding across the swarm
- G1.3 ❏ Each agent's context is isolated: no agent shares a context window or state file with another
- G1.4 ❏ Each agent has received its assignment: agent state is `RUNNING` not `PENDING`
- G1.5 ❏ Agent count matches target: spawned == target ± 0 (no extra, no fewer)

**Evidence:** Process list + agent IDs + state registry dump + count comparison
**On-fail:** If agent count < target → attempt respawn (max 2 retries). If still < target → proceed with available agents, log WARNING. If agent count > target → kill extras, log WARNING. If any agent shares context → HALT (contamination risk).

---

## Gate 2 — Angle Uniqueness

Each agent must investigate a genuinely different angle. No two agents may produce the same analysis.

- G2.1 ❏ Each agent's assignment includes a unique angle descriptor:
  - GL-SW: different search terms, different sources, different analytical lens
  - GL-AD: different attack vectors, different assumptions to challenge, different failure modes
- G2.2 ❏ After divergence, compare agent outputs pairwise: `diff {agent_i_output} {agent_j_output}`
- G2.3 ❏ Similarity score between any two agents < 70% (using keyword overlap: `comm -12 {sorted_i} {sorted_j} | wc -l` / total unique keywords)
- G2.4 ❏ No agent's output is a subset of another's: each must contain ≥ 1 claim not found in any other agent
- G2.5 ❏ If GL-AD: each adversarial agent must challenge a *different* assumption — no two agents attack the same target

**Evidence:** Agent assignment descriptors + pairwise diff outputs + similarity scores + unique-claim count per agent
**On-fail:** If similarity > 70% between any pair → re-spawn one agent with a forced-different angle. If one agent is a subset → re-spawn with wider scope. If GL-AD agents converge on same target → reassign targets. After 2 re-spawn attempts → proceed with best-available divergence, log WARNING.

---

## Gate 3 — Convergence Quality

After divergence, the swarm must converge on findings. Quality is measured by evidence density, not agreement.

- G3.1 ❏ Each agent produces a structured output: `{claim, evidence, confidence, source}`
- G3.2 ❏ Evidence density: each agent has ≥ 3 evidence-backed claims (not just opinions)
- G3.3 ❏ Claims cite sources: each claim has `{source_url, source_type, retrieved_at}` — no unsourced claims
- G3.4 ❏ Cross-agent corroboration: ≥ 1 claim is independently confirmed by ≥ 2 agents
- G3.5 ❏ Cross-agent contradiction: if agents disagree, the contradiction is *explicitly flagged*, not smoothed over
- G3.6 ❏ For GL-AD: adversarial agents must produce ≥ 1 finding that contradicts the baseline assumption

**Evidence:** Structured output per agent + evidence count + source citations + corroboration matrix + contradiction list
**On-fail:** If evidence density < 3 per agent → reject that agent's output, flag as WEAK. If no corroboration → log WARNING (may indicate isolated analysis). If contradictions not flagged → HALT (synthesis integrity compromised).

---

## Gate 4 — Confidence Score Honesty

Agents must report honest confidence. No inflated certainty.

- G4.1 ❏ Each claim has a confidence score: `0.0` to `1.0` where:
  - `0.0-0.3`: speculation, low evidence
  - `0.3-0.6`: partial evidence, reasonable hypothesis
  - `0.6-0.8`: strong evidence, high confidence
  - `0.8-1.0`: verified fact, multiple independent sources
- G4.2 ❏ No claim has confidence > 0.8 without ≥ 2 independent sources
- G4.3 ❏ No claim has confidence > 0.9 without terminal/log proof
- G4.4 ❏ Confidence calibration check: pick the top 3 highest-confidence claims, verify sources independently
- G4.5 ❏ If an agent reports all claims at > 0.7 → flag as UNCALIBRATED (likely overconfident)

**Evidence:** Confidence distribution per agent + source count per high-confidence claim + calibration verification output
**On-fail:** If confidence > 0.8 without 2 sources → downgrade to 0.6, log WARNING. If all claims > 0.7 → flag agent as UNCALIBRATED, weight its output at 0.5x in synthesis. If calibration check reveals fabrication → HALT + CRITICAL.

---

## Gate 5 — Synthesis with Conflict Identification

The final synthesis must preserve disagreements, not paper over them.

- G5.1 ❏ Synthesis document produced: `~/.rig/state/swarm-synthesis-{cycle}.md`
- G5.2 ❏ Synthesis includes:
  - **Consensus findings** (agreed by ≥ 60% of agents)
  - **Contested findings** (disagreement between agents — each position listed with its agent and evidence)
  - **Unique findings** (only 1 agent found this — flagged as single-source)
  - **Confidence-weighted summary** (findings ranked by calibrated confidence)
- G5.3 ❏ Every contested finding lists both positions with equal detail (no favoritism)
- G5.4 ❏ Synthesis explicitly states what is NOT known: `open_questions: [...]`
- G5.5 ❏ For GL-AD: synthesis includes `baseline_assumption_challenges: [...]` — each challenge with its adversarial agent's evidence
- G5.6 ❏ Synthesis is signed by the conductor: `Synthesized by: Jake PAI, {timestamp}, from {N} agents`

**Evidence:** Synthesis file exists + structure verified (has consensus/contested/unique/open sections) + conflict count + open question count
**On-fail:** If synthesis missing conflict section → HALT, rewrite. If contested findings are absent despite agent disagreement detected in Gate 3 → HALT (suppressing disagreement). If synthesis is a simple merge without analysis → HALT + alert Jake.

---

## ENFORCED INVARIANTS

| ID | Invariant | Enforcement |
|---|---|---|
| INV-SW-1 | Each agent produces unique insight | Gate 2.4 — ≥ 1 unique claim per agent |
| INV-SW-2 | Synthesis identifies conflicts | Gate 5.2 — contested findings section required |
| INV-SW-3 | No inflated confidence | Gate 4.2-4.3 — confidence ceiling tied to evidence count |
| INV-SW-4 | Agent context isolation | Gate 1.3 — no shared state between agents |
| INV-SW-5 | Unsourced claims rejected | Gate 3.3 — every claim needs a source |
| INV-SW-6 | Adversarial agents must challenge, not agree | Gate 3.6 + Gate 2.5 — GL-AD agents attack different assumptions |

---

## PROOF PACKET

Each GL-SW / GL-AD cycle produces:

```json
{
  "schema": "rig.swarm.proof.v1",
  "cycle": 0,
  "timestamp": "ISO-8601",
  "swarm_type": "GL-SW | GL-AD",
  "objective": "...",
  "agents": {
    "target_count": 5,
    "spawned_count": 5,
    "agent_ids": ["...", "..."],
    "angle_descriptors": ["...", "..."]
  },
  "gates": {
    "G0_identity": { "pass": true },
    "G1_agent_count": { "pass": true, "spawned": 5, "target": 5 },
    "G2_angle_uniqueness": {
      "pass": true,
      "max_pairwise_similarity": 0.45,
      "unique_claims_per_agent": [3, 4, 2, 5, 3]
    },
    "G3_convergence": {
      "pass": true,
      "evidence_density": [3, 4, 3, 5, 3],
      "corroborated_claims": 2,
      "contradictions_found": 1,
      "contradictions_flagged": true
    },
    "G4_confidence_honesty": {
      "pass": true,
      "calibrated": true,
      "uncalibrated_agents": [],
      "high_conf_with_evidence": true
    },
    "G5_synthesis": {
      "pass": true,
      "consensus_count": 0,
      "contested_count": 0,
      "unique_count": 0,
      "open_questions": 0
    }
  },
  "synthesis_path": "~/.rig/state/swarm-synthesis-{cycle}.md",
  "verdict": "PASS | FAIL | CRITICAL"
}
```

---

## FAILURE SEVERITY

| Severity | Trigger | Action |
|---|---|---|
| LOW | Single agent slow to respond, minor similarity | Log only |
| MEDIUM | Agent count below target, uncalibrated confidence, low evidence density | Log + re-spawn or flag WEAK |
| HIGH | Agent context contamination, contradictions suppressed, synthesis without conflicts | Log + HALT cycle + alert Jake |
| CRITICAL | Confidence fabrication, synthesis favoritism, adversarial agents agreeing with baseline | Log + HALT all GL-SW/GL-AD + alert Mike Telegram |

---

*Signed: Jake PAI, 2026-07-10*
*Governs: GL-SW loops (swarm research) + GL-AD loops (adversarial/deviation analysis)*

## What Great Looks Like (WGLL)

Amazing swarm output from this harness:

- **Agents are independent** — no shared mutable state, no implicit ordering
- **Work is decomposed** — each agent gets a well-scoped task with clear done criteria
- **Results are mergeable** — outputs combine without conflicts or duplication
- **Failures are isolated** — one agent failing doesn't block others
- **Progress is visible** — real-time status for each agent and overall completion
- **Proof packets emitted** — each agent produces a sealed ProofPacket with evidence
- **Anti-swarm-collapse** — not just one agent doing everything while others idle

