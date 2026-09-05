---
outcome: agent-engineering:
done_when:
  - file:capabilities/loops/ops-harness.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/ops-harness.md
great_example: examples/great/agent-engineering/ops-harness.md
quality_floor: 0.6
---

# Ops Harness — GL-OF Gate Loop

**Owner:** Jake PAI
**Scope:** GL-OF (Operations / Infrastructure loops)
**Status:** RUNTIME GATE LOOP
**Signed:** 2026-07-10

This harness governs every GL-OF cycle. No operation advances past a gate without producing evidence. The loop is: CHECK → ACT → VERIFY → LOG.

---

## Gate 0 — Identity Lock

Every GL-OF session must confirm identity before any operation executes.

- G0.1 ❏ Load `jake-active-goal.json` and confirm `status == "ACTIVE"`
- G0.2 ❏ State the current GL-OF cycle number and operation type (deploy, backup, rollback, health-check)
- G0.3 ❏ Confirm operator: `Jake PAI` or `Mike Rodgers` — no other identity may authorize destructive ops
- G0.4 ❏ Confirm node identity: state hostname, verify against `~/.rig/fleet/node-registry.json`

**Evidence:** `hostname` output + goal JSON contents + operator confirmation string
**On-fail:** HALT. Write `G0-FAIL-{timestamp}` to `~/.rig/state/ops-failures.log`. No operation proceeds.

---

## Gate 1 — Node Health

Before any operation touches infrastructure, every target node must be healthy.

- G1.1 ❏ Ping each target node — `ping -c 3 -W 2 {node_ip}` — 0% packet loss
- G1.2 ❏ Verify disk usage < 90% on all target nodes: `ssh {node} 'df -h /'`
- G1.3 ❏ Verify memory pressure < 80%: `ssh {node} 'free -m'` or `vm_stat` on macOS
- G1.4 ❏ Verify no zombie processes > 10: `ssh {node} 'ps aux | grep -c Z'`
- G1.5 ❏ Verify required services running (Ollama, GBrain, Hermes daemon): `curl -s http://{node}:{port}/health`

**Evidence:** Raw terminal output for each check, captured verbatim
**On-fail:** Write node name + failure to `~/.rig/state/ops-node-health-failures.log`. If >50% nodes fail → HALT. If ≤50% → quarantine failed nodes, continue with healthy subset.

---

## Gate 2 — LAN-First Verification

RIG operates LAN-first. No operation may route through the internet when a LAN path exists.

- G2.1 ❏ Verify target node is on local network (192.168.x.x, 10.x.x.x, or .local mDNS): `ip route get {node_ip}`
- G2.2 ❏ If node has both LAN and WAN addresses, confirm LAN path is selected: `traceroute -n -m 3 {node_ip}` shows no public hops
- G2.3 ❏ Verify no cloud fallback configured for the operation: check `~/.rig/fleet/routing.json` — `prefer: lan`
- G2.4 ❏ If LAN node unreachable, HALT — do NOT silently fall back to WAN/cloud

**Evidence:** IP route output + traceroute hops + routing config contents
**On-fail:** HALT operation. Write `G2-FAIL: WAN fallback detected for {node}` to `~/.rig/state/ops-failures.log`. Alert Jake-direct. No silent cloud routing.

---

## Gate 3 — Backup Confirmation

**ENFORCED RULE: No deploy without backup. No destructive action without backup.**

- G3.1 ❏ Identify all artifacts that will be modified by this operation
- G3.2 ❏ Create backup: `tar czf ~/.rig/backups/{op-name}-{timestamp}.tar.gz {artifacts}`
- G3.3 ❏ Verify backup integrity: `tar tzf {backup}.tar.gz | wc -l` matches expected file count
- G3.4 ❏ Verify backup is non-empty: `stat -f%z {backup}.tar.gz` > 0 bytes
- G3.5 ❏ Record backup path + hash: `shasum -a 256 {backup}.tar.gz` → write to `~/.rig/state/backup-registry.json`

**Evidence:** tar output + file count + byte size + SHA256 hash
**On-fail:** If backup creation fails → HALT. If backup verification fails → HALT. Write `G3-FAIL` to failures log. **No exceptions. This gate cannot be overridden by automation.**

---

## Gate 4 — Deployment Safety

Every deployment passes through this gate. No deployment may execute without Gates 0-3 all PASS.

- G4.1 ❏ Confirm Gates 0-3 all recorded PASS in current cycle proof file
- G4.2 ❏ Run dry-run if available: `{command} --dry-run` or equivalent simulation
- G4.3 ❏ Confirm rollback command is valid and tested: `echo $?` after `which {rollback-cmd}` or equivalent
- G4.4 ❏ Set deployment timeout: if operation exceeds 300s without progress, auto-abort
- G4.5 ❏ If deploying to >1 node, confirm rolling strategy (not all-at-once): deploy node 1 → verify → deploy node 2 → verify
- G4.6 ❏ Write deployment receipt: `{op-name} started at {timestamp} on {nodes} by {operator}`

**Evidence:** Dry-run output + rollback path confirmed + deployment receipt written
**On-fail:** If dry-run fails → HALT. If rollback path invalid → HALT. If timeout triggers → auto-rollback via Gate 5. Write `G4-FAIL-{reason}` to failures log.

---

## Gate 5 — Rollback Readiness

Every operation must have a tested rollback path before it starts. This gate also fires on auto-rollback triggers.

- G5.1 ❏ Rollback command documented: `rollback: {exact command}`
- G5.2 ❏ Rollback tested in dry-run: `{rollback-cmd} --dry-run` returns exit 0
- G5.3 ❏ Rollback artifacts exist: backup from Gate 3 is present and readable
- G5.4 ❏ Rollback timeout set: if rollback exceeds 120s, escalate to Jake-direct
- G5.5 ❏ Post-rollback verification plan: `{verify-cmd}` will confirm system returned to pre-deployment state

**Evidence:** Rollback command + dry-run exit code + backup path + verify command
**On-fail:** If rollback cannot be verified → CRITICAL. Halt all GL-OF cycles. Alert Mike via Telegram. Write `G5-CRITICAL-{timestamp}` to failures log.

---

## ENFORCED INVARIANTS

These rules apply across all gates, all cycles. Violations are CRITICAL.

| ID | Invariant | Enforcement |
|---|---|---|
| INV-OF-1 | No deploy without backup | Gate 3 must PASS before Gate 4 executes |
| INV-OF-2 | No destructive action without explicit confirmation | Destructive ops require `operator: "Mike Rodgers"` OR `operator: "Jake PAI"` + `confirm: true` |
| INV-OF-3 | No silent WAN fallback | Gate 2 must PASS; any WAN route = HALT |
| INV-OF-4 | Rollback always tested before deploy | Gate 5.2 must PASS before Gate 4 executes |
| INV-OF-5 | Every cycle produces a proof packet | `~/.rig/state/ops-proof-{cycle}.json` must exist after each cycle |

---

## PROOF PACKET

Each GL-OF cycle produces:

```json
{
  "schema": "rig.ops.proof.v1",
  "cycle": 0,
  "timestamp": "ISO-8601",
  "operator": "Jake PAI | Mike Rodgers",
  "operation": "deploy | backup | rollback | health-check",
  "gates": {
    "G0_identity": { "pass": true, "evidence": "..." },
    "G1_node_health": { "pass": true, "nodes_checked": 3, "nodes_healthy": 3 },
    "G2_lan_first": { "pass": true, "route": "192.168.x.x" },
    "G3_backup": { "pass": true, "path": "...", "sha256": "...", "bytes": 0 },
    "G4_deploy_safety": { "pass": true, "dry_run": true, "timeout_s": 300 },
    "G5_rollback": { "pass": true, "rollback_cmd": "...", "tested": true }
  },
  "verdict": "PASS | FAIL | CRITICAL",
  "failure_log": []
}
```

---

## FAILURE SEVERITY

| Severity | Trigger | Action |
|---|---|---|
| LOW | Slow node, disk warning | Log only |
| MEDIUM | Single node unhealthy, backup slow | Log + continue with healthy subset |
| HIGH | WAN fallback detected, deploy timeout | Log + HALT + alert Jake |
| CRITICAL | Backup failure, rollback failure, destructive without confirmation | Log + HALT all GL-OF + alert Mike Telegram |

---

*Signed: Jake PAI, 2026-07-10*
*Governs: GL-OF loops (operations, infrastructure, deploy, rollback)*

## What Great Looks Like (WGLL)

Amazing ops output from this harness:

- **Infrastructure is reproducible** — IaC (Terraform/Docker) with documented setup steps
- **Health checks are automated** — every service has a /health endpoint monitored
- **Rollback is tested** — deploy → break → rollback → verify within 5 minutes
- **Alerts are actionable** — "service X is down, check Y" not "something happened"
- **Logs are structured** — JSON with request_id, timestamp, level, message
- **Cost is tracked** — monthly spend per service with anomaly alerts
- **Walk-away test passed** — 24h autonomous operation with zero human intervention

