# A3 — AGENT_BOUNDED (stub)

RIG Lattice Mode 3. BMS band ≈ 0.25–0.50. LangGraph bounded-agent mode.

## Doctrine
- Handles ambiguous / previously-`UNKNOWN` intent escalated from **A1.1**.
- **Approval is mandatory** (A3 and above).
- **Mechanism maps required** (A3 and above).
- Stronger audit trail: `ProofPacket → ApprovalPacket → Action → Result`.
- Imports the frozen contract from `a1_python_only`.

## Required components (every A3 step)
LangGraph state object · explicit nodes/edges · tool allowlist · cost budget ·
runtime budget · mechanism map · guardrail result · approval packet · audit row ·
failure/escalation path. (See `REQUIRED_COMPONENTS` in `__init__.py`.)

## Interface
Each `a3_N_*.py` exposes `run(state) -> <PacketType>` — SAME packet types as A1.
See `STEP_INTERFACE` in `__init__.py`.

## Status
Interface stub only. Implementation: Phase 5 of the lattice build order.

## Files to add
`a3_1_intent.py` … `a3_7_integrate.py`.
