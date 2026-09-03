"""Result-packet emitter per DOCTRINE.md §6.1.

Every audit completion writes the canonical JSON schema:

    {
      "mission_id": "...",
      "artifact": "...",
      "tier": "client",
      "engines": { "GravityEscape": 88, ... },
      "madz":    { "GravityEscape": 4.2, ... },
      "physics_state_gates": { "QuantumTunneling": "PASS", ... },
      "rig_l": 5.8,
      "bdf":  6.4,
      "status": "needs_rework",
      "weakest_gate": "FineTuning",
      "escalation_cost": 1024,
      "next_action": "narrow viable-parameter band; add hysteresis evidence"
    }

Plus DES² amplifier results when amplification ran.
"""
from __future__ import annotations
import hashlib
import json
import time
import uuid
from pathlib import Path
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent
PACKETS_DIR = AUDITS_DIR / "packets"


def escalation_cost(sigma: float) -> int:
    """DOCTRINE.md §2.3 — cost ladder."""
    n = abs(sigma)
    if n <= 10:
        return int(2 ** n)
    if n <= 20:
        return int(1024 * (3 ** (n - 10)))
    return int(1024 * (3 ** 10) * (5 ** (n - 20)))


def bdf(intent: float, madz: float, craft: float, restraint: float) -> float:
    """DOCTRINE.md §2.4 — BDF composite."""
    return intent * abs(madz) * craft * restraint


def physics_gates(audit: dict) -> dict:
    """Extract physics layer gate verdicts from an audit dict."""
    physics_slugs = {
        "absolute_zero", "pauli_exclusion", "speed_of_lumen", "critical_phase",
        "quantum_tunnel", "hawking_horizon", "fine_structure", "casimir_force",
        "bell_entanglement", "vacuum_zeropoint",
    }
    return {
        slug: r.get("status", "?")
        for slug, r in audit.get("engines", {}).items()
        if slug in physics_slugs
    }


def weakest_engine(audit: dict) -> str | None:
    engines = audit.get("engines", {})
    if not engines:
        return None
    return min(engines.items(), key=lambda kv: kv[1].get("sigma", 0))[0]


def next_action(audit: dict) -> str:
    """Derive a one-line next-action prompt from failed required questions."""
    blockers = [r for r in audit.get("engines", {}).values() if r.get("failed_required")]
    if not blockers:
        return "Ship — no required failures."
    worst = min(blockers, key=lambda r: r.get("sigma", 0))
    fail_id = worst.get("failed_required", ["?"])[0]
    q = next((qq for qq in worst.get("questions", []) if qq["id"] == fail_id), {})
    return f"Fix {worst.get('codename','?')} / {fail_id}: {q.get('question','')[:100]}"


def status_label(audit: dict, tier: str = "client") -> str:
    """Per DOCTRINE.md §2.5 RIG-L ladder + tier minimum."""
    rl = audit.get("rig_l", 0)
    if audit.get("hard_blocks", 0) > 0:
        return "BLOCK"
    if rl < 3.0:
        return "block"
    if rl < 4.0:
        return "pass_needs_strengthening"
    if rl < 5.0:
        return "category_rupture"
    if rl < 8.0:
        return "rig_signature"
    if rl < 10.0:
        return "frontier_artifact"
    return "doctrine_artifact"


def emit(audit: dict,
          artifact_path: str | Path,
          tier: str = "client",
          mission_id: str | None = None,
          des2: dict | None = None,
          intent: float = 1.0,
          craft: float = 1.0,
          restraint: float = 1.0) -> dict:
    """Build the canonical result-packet and persist it (append-only)."""
    artifact_path = str(artifact_path)
    content = Path(artifact_path).read_bytes() if Path(artifact_path).exists() else b""
    content_hash = hashlib.sha256(content).hexdigest()[:24]
    mid = mission_id or f"m-{int(time.time())}-{uuid.uuid4().hex[:8]}"

    engines_score = {r["codename"]: round(r["sigma"], 2)
                      for r in audit.get("engines", {}).values()}
    madz = {r["codename"]: round(r["sigma"], 2)
            for r in audit.get("engines", {}).values()}
    weakest_slug = weakest_engine(audit)
    weakest_codename = (audit.get("engines", {})
                              .get(weakest_slug, {}).get("codename", weakest_slug))
    rig_l = audit.get("rig_l", 0)

    packet = {
        "mission_id": mid,
        "artifact": artifact_path,
        "content_hash": content_hash,
        "tier": tier,
        "engines": engines_score,
        "madz": madz,
        "physics_state_gates": physics_gates(audit),
        "rig_l": rig_l,
        "bdf": round(bdf(intent, rig_l, craft, restraint), 2),
        "status": status_label(audit, tier),
        "weakest_gate": weakest_codename,
        "escalation_cost": escalation_cost(rig_l),
        "next_action": next_action(audit),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if des2:
        packet["des2"] = des2

    # Append-only write to packets dir
    PACKETS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PACKETS_DIR / f"{mid}.json"
    out_path.write_text(json.dumps(packet, indent=2, default=str))
    return packet


if __name__ == "__main__":
    import sys
    from rig_lattice.deviator.auditor import audit_all
    from rig_lattice.deviator.des_squared import amplify

    text = Path(sys.argv[1]).read_text()
    base = audit_all(text, llm_enabled=False)
    enriched = amplify(base, text)
    packet = emit(enriched, sys.argv[1],
                   tier=sys.argv[2] if len(sys.argv) > 2 else "client",
                   des2=enriched.get("des2"))
    print(json.dumps(packet, indent=2, default=str))
