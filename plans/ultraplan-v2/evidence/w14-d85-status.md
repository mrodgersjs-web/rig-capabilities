# W14 D85 checklist+cert verify — honest status (2026-09-20)
- Process card authored with the required structure: ~/.rig/d85/processes/ultraplan-v2.process.json
  (7 operations: 5 CODE, 1 declared MODEL (JEV route — never certified as deterministic), 1 HUMAN (Gate-D, excluded)).
- `inventory ultraplan-v2` -> UNKNOWN_PROCESS BLOCK: registration requires authority/registry.json, which does not exist in rig-capabilities. Creating the registry + the first entry is a governance (authority-owned) act, not an agent act — it is the captain's admit-approve path.
- `admit-request` correctly refuses before a bound CHECKLIST_PASS; checklist requires inventory_sha256 from the registry-backed inventory. The chain is intact and refuses at exactly the designed points.
- Additional finding: D85's admitted grammar BLOCKS `open` as a dynamic builtin; the ultraplan runtime uses open() pervasively (ledger, cell runner, console). A real admission needs either registry-level grammar guidance or a stdlib-io refactor pass. This is a genuine build-quality signal, not a paperwork item.
- What is DONE here: card drafted with truthful ops + done-tests; every attempt's BLOCK reason recorded. What is GATED on the captain: authority/registry.json creation + ultraplan-v2 entry + APPROVE of the admission id.
