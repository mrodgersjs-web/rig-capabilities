#!/usr/bin/env bash
# outcome: agent-engineering:
# done_when: cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; L="${TMPDIR:-/tmp}/rrfg-d-$$"; RAIL_REGISTRY=$F/registry.json RAIL_DECISION_LOG="$L" /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-allowed.json"; rc=$?; grep -q '"verdict": "allow"' "$L" && grep -q '"ms":' "$L"; g=$?; rm -f "$L"; test $rc -eq 0 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; o="$(RAIL_REGISTRY=$F/registry.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-denied-exposed.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -q RAIL_DENIED_EXPOSED; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; o="$(RAIL_REGISTRY=$F/registry.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-denied-permitted.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -q RAIL_DENIED_PERMITTED; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; o="$(RAIL_REGISTRY=$F/registry.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-denied-executed.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -q RAIL_DENIED_EXECUTED; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; o="$(RAIL_REGISTRY=$F/registry.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-denied-returned.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -q RAIL_DENIED_RETURNED; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; o="$(RAIL_REGISTRY=$F/registry.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-unknown-action.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -q RAIL_DENIED_UNREGISTERED; g=$?; test $rc -eq 2 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; o="$(RAIL_REGISTRY=$F/registry-bad-event.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-validate.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -q REGISTRY_INVALID_EVENT; g=$?; test $rc -eq 1 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; o="$(RAIL_REGISTRY=$F/registry-order-collision.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-validate.json" 2>&1)"; rc=$?; printf '%s' "$o" | grep -q REGISTRY_INVALID_ORDER; g=$?; test $rc -eq 1 && test $g -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; L="${TMPDIR:-/tmp}/rrfg-v1-$$"; RAIL_REGISTRY=$F/registry.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-visible-main.json" >"$L" 2>/dev/null; rc=$?; diff "$L" "$F/expected-visible-main.txt"; d=$?; rm -f "$L"; test $rc -eq 0 && test $d -eq 0 || cmd:F=capabilities/hooks/fixtures/rail-registry-four-way-gate; L="${TMPDIR:-/tmp}/rrfg-v2-$$"; RAIL_REGISTRY=$F/registry.json /bin/bash capabilities/hooks/rail-registry-four-way-gate.sh <"$F/payload-visible-delegated.json" >"$L" 2>/dev/null; rc=$?; diff "$L" "$F/expected-visible-delegated.txt"; d=$?; rm -f "$L"; test $rc -eq 0 && test $d -eq 0
# great_example: examples/great/agent-engineering/rail-registry-four-way-gate.md
# quality_floor: 0.6
# rail-registry-four-way-gate — PreToolUse-style guard: a candidate action clears a
# registry-declared, ordered set of rails at a named lifecycle boundary, one decision
# per leg (exposed / permitted / executed / returned), failing CLOSED with a named
# refusal per rail. Canonical source: rig-capabilities repo.
#
# Mechanism (openJiuwen, arXiv:2608.27969, video lNlMXsUQggc, repo openJiuwen-ai/jiuwenswarm;
# HELIX four-way decision, arXiv:2608.13951, video USEk7F9GIZk):
# "A rail is a capability attached to a specific life cycle event" — a rail registers
# as the tuple (lifecycle event, order, capability id, agent visibility set) against a
# DECLARED event taxonomy and runs in declaration order at that boundary; composition
# ordering plus visibility gating decides which capabilities a delegated agent can see
# at all. HELIX adds the decision shape: the harness "determines which action of the
# LLM were now exposed, permitted, executed, remembered, and returned", and anything
# with side effects executes OUTSIDE the model on a deterministic surface whose result
# is fed back as the next observation.
#
# RIG gap this closes: capabilities/hooks/ held six unregistered one-off guards with no
# event taxonomy, no ordering guarantee, and a binary allow/block decision model — the
# 'remembered' and 'returned' legs were untracked and nothing quarantined side effects
# to a deterministic executor. Here the taxonomy, the order, and the visibility sets are
# ENFORCED STATE: the validator refuses a rail on an undeclared event or a colliding
# (event, order) pair, and an event that carries action-gate rails must carry exactly
# one rail per leg — a partial four-way set is RED, not a convention.
#
# Contract: JSON payload on stdin; registry at $RAIL_REGISTRY (default
# ~/.rig/rails/registry.json). Modes:
#   {"mode":"gate", ...}            default — gate one candidate action at one boundary
#   {"mode":"validate_registry"}    validator only: taxonomy, ordering, legset, fields
#   {"mode":"visible_rails","agent":{"role":R}}  enumerate R's rails: visibility set
#                                    MINUS gated entries, registry order; a superset of
#                                    the permitted set exits 1 (RAIL_DENIED_VISIBILITY_LEAK)
# Gate payload: {"mode":"gate","event":E,"agent":{"id":A,"role":R},
#                "action":{"id":X,"tool":T,"side_effects":bool,"executor":S,
#                          "returns_observation":bool,"observation_channel":C}}
# Exit codes: 0 allow (all rails green); 1 validator denial (validate_registry mode,
# visibility-leak invariant); 2 gate denial — the harness block code. A registry that
# fails validation during a GATE exits 2 (block), not 1: invalid rails are never a
# licence to run unchecked. Empty stdin exits 0 (nothing was proposed). Malformed JSON,
# unknown mode, unknown event, and an event with no registered rails all exit 2 with
# RAIL_DENIED_UNREGISTERED — denial, never silence.
# Leg predicates (deterministic, payload-only):
#   exposed   agent role is in the rail's visibility set and not in its gated list
#   permitted action.tool is in the rail's allow_tools
#   executed  if action.side_effects, action.executor must be one of the rail's
#             declared deterministic surfaces (sandbox / API) — non-determinism stays
#             quarantined inside the model; no declared surface = denial
#   returned  action declares returns_observation:true + a non-empty observation_channel,
#             so the execution result comes back as the next observation
# Decision record: with $RAIL_DECISION_LOG set, every gate decision appends one JSONL
# row carrying the per-rail verdict AND per-rail duration in ms (ordered rails make one
# slow rail a global stall — the record makes that visible) plus the final verdict; the
# record is the 'remembered' leg. A decision record that cannot be written fails the
# gate closed (RAIL_DENIED_UNREGISTERED).
#
# Ceiling: this hook validates what the payload DECLARES — it cannot observe the real
# world, so 'executed' checks that the payload names a declared deterministic surface,
# not that the surface truly ran; and registry writer identity is a harness-kernel
# concern outside any hook. Wiring this into a harness settings file is a separate
# Gate-D action. Python via /usr/bin/python3 (precedent: guard-secret-write.sh), stdlib
# json/sys/time/os only, per house rule.
set -uo pipefail

payload="$(cat 2>/dev/null || true)"
[ -n "$payload" ] || exit 0

registry="${RAIL_REGISTRY:-$HOME/.rig/rails/registry.json}"

RAIL_GATE_PY="$(cat <<'PYEOF'
import json, os, sys, time

LEGS = ("exposed", "permitted", "executed", "returned")
OK, VALIDATOR, DENY = 0, 1, 2

def refuse(name, detail, code):
    sys.stderr.write("rail-gate: %s — %s\n" % (name, detail))
    sys.exit(code)

def load_registry(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            reg = json.load(fh)
    except FileNotFoundError:
        return None, ["REGISTRY_INVALID_REGISTRY:missing — no registry at %s" % path]
    except Exception as e:
        return None, ["REGISTRY_INVALID_REGISTRY:parse — %s: %s" % (type(e).__name__, e)]
    if not isinstance(reg, dict):
        return None, ["REGISTRY_INVALID_REGISTRY:shape — root is not an object"]
    return reg, []

def validate(reg):
    errs = []
    events = reg.get("events")
    if (not isinstance(events, list) or not events
            or not all(isinstance(e, str) and e for e in events)):
        errs.append("REGISTRY_INVALID_TAXONOMY — 'events' must be a non-empty list of event names")
        events = [e for e in (events or []) if isinstance(e, str)]
    if len(set(events)) != len(events):
        errs.append("REGISTRY_INVALID_TAXONOMY:duplicate — event declared twice")
    rails = reg.get("rails")
    if not isinstance(rails, list) or not rails:
        errs.append("REGISTRY_INVALID_RAILS — 'rails' must be a non-empty list")
        return errs
    seen_ids, seen_orders, legset = set(), {}, {}
    for r in rails:
        if not isinstance(r, dict):
            errs.append("REGISTRY_INVALID_RAILS:shape — rail entry is not an object")
            continue
        rid = r.get("id")
        if not isinstance(rid, str) or not rid:
            errs.append("REGISTRY_INVALID_FIELDS:id — rail entry without id")
            continue
        if rid in seen_ids:
            errs.append("REGISTRY_INVALID_DUPLICATE_ID:%s" % rid)
        seen_ids.add(rid)
        ev, order = r.get("event"), r.get("order")
        if not isinstance(order, int) or isinstance(order, bool):
            errs.append("REGISTRY_INVALID_FIELDS:%s:order — order must be an integer" % rid)
            continue
        if ev not in events:
            errs.append("REGISTRY_INVALID_EVENT:%s — rail '%s' names an event outside the declared taxonomy" % (ev, rid))
        key = (ev, order)
        if key in seen_orders:
            errs.append("REGISTRY_INVALID_ORDER:%s:%s — rails '%s' and '%s' collide on the same boundary slot" % (ev, order, seen_orders[key], rid))
        else:
            seen_orders[key] = rid
        cap = r.get("capability")
        if not isinstance(cap, str) or not cap:
            errs.append("REGISTRY_INVALID_FIELDS:%s:capability" % rid)
        vis = r.get("visibility")
        if not isinstance(vis, list) or not vis or not all(isinstance(v, str) and v for v in vis):
            errs.append("REGISTRY_INVALID_FIELDS:%s:visibility — visibility set must be a non-empty list" % rid)
        gated = r.get("gated", [])
        if not isinstance(gated, list) or not all(isinstance(v, str) for v in gated):
            errs.append("REGISTRY_INVALID_FIELDS:%s:gated" % rid)
        leg = r.get("leg")
        if leg is None:
            continue  # capability rail: ordered and visibility-gated, not an action-gate leg
        if leg not in LEGS:
            errs.append("REGISTRY_INVALID_LEG:%s:%s — leg must be one of %s" % (rid, leg, "/".join(LEGS)))
            continue
        legset.setdefault(ev, []).append(leg)
        if leg == "permitted":
            at = r.get("allow_tools")
            if not isinstance(at, list) or not at or not all(isinstance(t, str) and t for t in at):
                errs.append("REGISTRY_INVALID_FIELDS:%s:allow_tools" % rid)
        elif leg == "executed":
            ex = r.get("executors")
            if not isinstance(ex, list) or not ex or not all(isinstance(t, str) and t for t in ex):
                errs.append("REGISTRY_INVALID_FIELDS:%s:executors" % rid)
    for ev, legs in sorted(legset.items()):
        missing = [l for l in LEGS if legs.count(l) == 0]
        dupes = sorted({l for l in LEGS if legs.count(l) > 1})
        if missing:
            errs.append("REGISTRY_INVALID_LEGSET:%s:missing=%s — an action-gate boundary must carry exactly one rail per leg" % (ev, ",".join(missing)))
        if dupes:
            errs.append("REGISTRY_INVALID_LEGSET:%s:duplicate=%s" % (ev, ",".join(dupes)))
    return errs

def leg_check(leg, rail, role, action):
    if leg == "exposed":
        if role in rail.get("gated", []):
            return False, "role '%s' is gated on rail '%s'" % (role, rail["id"])
        if role not in rail.get("visibility", []):
            return False, "role '%s' is not visible to rail '%s'" % (role, rail["id"])
        return True, ""
    if leg == "permitted":
        tool = action.get("tool")
        if tool in rail.get("allow_tools", []):
            return True, ""
        return False, "tool '%s' is not on rail '%s' allowlist" % (tool, rail["id"])
    if leg == "executed":
        if not action.get("side_effects"):
            return True, ""
        ex = action.get("executor")
        if ex in rail.get("executors", []):
            return True, ""
        return False, ("side-effecting action names executor '%s'; rail '%s' only allows deterministic surfaces [%s]"
                       % (ex, rail["id"], ", ".join(rail.get("executors", []))))
    if leg == "returned":
        ch = action.get("observation_channel")
        if action.get("returns_observation") is True and isinstance(ch, str) and ch:
            return True, ""
        return False, ("action declares no observation channel; rail '%s' requires returns_observation:true + observation_channel so the result returns as the next observation" % rail["id"])
    return False, "unknown leg '%s'" % leg

def log_decision(entry):
    path = os.environ.get("RAIL_DECISION_LOG")
    if not path:
        return True
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
        return True
    except Exception:
        return False

def main():
    reg_path = sys.argv[1]
    try:
        payload = json.load(sys.stdin)
    except Exception:
        refuse("RAIL_DENIED_UNREGISTERED", "payload is not valid JSON — the gate fails closed on an action it cannot parse", DENY)
    if not isinstance(payload, dict):
        refuse("RAIL_DENIED_UNREGISTERED", "payload is not an object — nothing registered matches it", DENY)
    mode = payload.get("mode", "gate")
    reg, errs = load_registry(reg_path)
    if reg is not None:
        errs = validate(reg)
    if mode == "validate_registry":
        if errs:
            for e in errs:
                sys.stderr.write("rail-gate: %s\n" % e)
            sys.exit(VALIDATOR)
        sys.exit(OK)
    if reg is None or errs:
        # Invalid rails are never a licence to run unchecked: gate refuses, block code.
        detail = errs[0] if errs else "registry unreadable"
        refuse("RAIL_DENIED_UNREGISTERED",
               "registry at %s failed validation (%s) — refusing to gate against unverified rails" % (reg_path, detail), DENY)
    agent = payload.get("agent")
    role = agent.get("role") if isinstance(agent, dict) else None
    if mode == "visible_rails":
        if not isinstance(role, str) or not role:
            refuse("RAIL_DENIED_UNREGISTERED", "visible_rails requires agent.role", DENY)
        permitted, out = set(), []
        for r in reg["rails"]:
            vis, gated = r.get("visibility", []), r.get("gated", [])
            if role in vis and role not in gated:
                permitted.add(r["id"])
                out.append(r["id"])
        # Invariant: enumeration is EXACTLY visibility minus gated; any superset leaks.
        if len(out) != len(set(out)) or not set(out).issubset(permitted):
            refuse("RAIL_DENIED_VISIBILITY_LEAK",
                   "visible-rails enumeration escaped the visibility-minus-gated set", VALIDATOR)
        sys.stdout.write("".join(rid + "\n" for rid in out))
        sys.exit(OK)
    if mode != "gate":
        refuse("RAIL_DENIED_UNREGISTERED", "mode '%s' is not registered (gate / validate_registry / visible_rails)" % mode, DENY)
    event = payload.get("event")
    action = payload.get("action")
    if (not isinstance(event, str) or event not in [e for e in reg["events"]]
            or not isinstance(role, str) or not role
            or not isinstance(action, dict) or not isinstance(action.get("id"), str)):
        refuse("RAIL_DENIED_UNREGISTERED",
               "gate payload names an event, agent role, or action this registry does not register", DENY)
    rails = sorted((r for r in reg["rails"] if r.get("event") == event and r.get("leg") in LEGS),
                   key=lambda r: r["order"])
    if len(rails) != 4:
        refuse("RAIL_DENIED_UNREGISTERED",
               "boundary '%s' does not register the full ordered four-way rail set" % event, DENY)
    entry = {
        "gate": "rail-registry-four-way-gate",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "event": event, "agent": agent.get("id") if isinstance(agent, dict) else None,
        "role": role, "action": action.get("id"),
        "verdict": "allow", "refusal": None, "rails": [],
    }
    for rail in rails:
        t0 = time.perf_counter()
        ok, why = leg_check(rail["leg"], rail, role, action)
        ms = round((time.perf_counter() - t0) * 1000.0, 3)
        entry["rails"].append({"id": rail["id"], "leg": rail["leg"], "order": rail["order"],
                               "verdict": "pass" if ok else "deny", "ms": ms})
        if not ok:
            entry["verdict"], entry["refusal"] = "denied", "RAIL_DENIED_" + rail["leg"].upper()
            if not log_decision(entry):
                refuse("RAIL_DENIED_UNREGISTERED", "decision record at $RAIL_DECISION_LOG is not writable — failing closed", DENY)
            refuse("RAIL_DENIED_" + rail["leg"].upper(),
                   "rail '%s' (order %s) refused action '%s': %s" % (rail["id"], rail["order"], action.get("id"), why), DENY)
    if not log_decision(entry):
        refuse("RAIL_DENIED_UNREGISTERED", "decision record at $RAIL_DECISION_LOG is not writable — failing closed", DENY)
    sys.exit(OK)

main()
PYEOF
)"

printf '%s' "$payload" | /usr/bin/python3 -c "$RAIL_GATE_PY" "$registry"
exit $?
