"""Comms MCP endpoint v20 — governed transformation engine surface.

Stdlib JSON-RPC over stdio, no dependencies, no LLM in-process. Deterministic
tools (schemas, energy, gates, ledger, golden replay, verdict sealing) + LLM-work
prompts (GEV roles). Private lane: machine scoring refused unconditionally
(PRIVACY_LOCK, v19.6); human:true only unlocks drafting/packet.

Run: python3 -m rig_comms.mcp   (stdio; one JSON-RPC message per line)

Server contract carried to every client at initialize:
  recipient-state control is the objective; the drafter never certifies;
  hard floors override beauty; private lane is out of machine reach.
"""
from __future__ import annotations

import json
import sys

from . import (claims, compress, energy, gates, golden, lineage, models, outcomes,
               packets, roles, seal, surfaces, vehicles, voice)

VERSION = "20.0.0"

INSTRUCTIONS = (
    "rig-communications v20: governed transformation engine. Flow: intent_check -> "
    "audience -> vehicle -> (draft via prompts) -> claims/compress/energy -> gates -> "
    "verdict (verifier/human only; GEV_LOCK refuses self-certification) -> outcome. "
    "Hard floors override the weighted score. Private lane scoring returns PRIVACY_LOCK "
    "and there is no override. The harness agent plays the GEV roles via the prompts; "
    "the server never drafts and never approves."
)

_AUDIENCE_ITEM_SCHEMA = {
    "anyOf": [
        {"type": "string"},
        {"type": "object", "properties": {
            "field": {"type": "string"},
            "provenance": {"type": "string"},
            "relevance": {"type": "string"},
        }},
    ],
}
_CLAIM_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "claim": {"type": "string"},
        "kind": {"type": "string", "enum": ["fact", "inference", "proposal"]},
        "provenance": {"type": "string"},
        "externally_checkable": {"type": "boolean"},
    },
}

_TOOLS = [
    {"name": "comms.surfaces", "description": "surface registry: lanes, engines, budgets",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "comms.route", "description": "route a natural-language writing intent to a surface",
     "inputSchema": {"type": "object", "properties": {"intent": {"type": "string"}},
                     "required": ["intent"]}},
    {"name": "comms.packet", "description": "assemble the drafting context packet for a surface",
     "inputSchema": {"type": "object", "properties":
                     {"surface": {"type": "string"}, "brief": {"type": "string"},
                      "persona": {"type": "string"},
                      "human": {"type": "boolean", "description": "required for private lane"}},
                     "required": ["surface", "brief"]}},
    {"name": "comms.score", "description": "v2 gate stack over an artifact (block-level)",
     "inputSchema": {"type": "object", "properties":
                     {"surface": {"type": "string"}, "artifact": {"type": "string"}},
                     "required": ["surface", "artifact"]}},
    {"name": "comms.intent_check",
     "description": "C1: validate CommunicationIntent (schema + state-delta proof obligation) and preview vehicle",
     "inputSchema": {"type": "object", "properties":
                     {"intent": {"type": "object", "description": "CommunicationIntent dict"}},
                     "required": ["intent"]}},
    {"name": "comms.audience",
     "description": "C2: assemble known/inferred/unknown audience model; every element needs provenance (known) or relevance (inferred)",
     "inputSchema": {"type": "object", "properties":
                     {"known": {"type": "array", "items": _AUDIENCE_ITEM_SCHEMA},
                      "inferred": {"type": "array", "items": _AUDIENCE_ITEM_SCHEMA},
                      "unknown": {"type": "array", "items": _AUDIENCE_ITEM_SCHEMA}}, "required": []}},
    {"name": "comms.vehicle",
     "description": "C3+C22: choose cheapest valid vehicle; may advise no-send",
     "inputSchema": {"type": "object", "properties":
                     {"intent": {"type": "object"}}, "required": ["intent"]}},
    {"name": "comms.energy",
     "description": "E_comm: 8-dimension weighted energy + hard floors (floors override score)",
     "inputSchema": {"type": "object", "properties":
                     {"scores": {"type": "object"},
                      "stakes": {"type": "string", "enum": list(models.STAKES)}},
                     "required": ["scores"]}},
    {"name": "comms.claims",
     "description": "C5/C6: claim-ledger lint (facts need provenance) + show-don't-label audit of text",
     "inputSchema": {"type": "object", "properties":
                     {"claims": {"type": "array", "items": _CLAIM_ITEM_SCHEMA}, "text": {"type": "string"}}}},
    {"name": "comms.compress",
     "description": "C7: throat-clearing/hedges/nominalizations + BLUF latency + suggested cut %",
     "inputSchema": {"type": "object", "properties": {"artifact": {"type": "string"}},
                     "required": ["artifact"]}},
    {"name": "comms.gates",
     "description": "v20 stack: claims lint + compression pass + E_comm floors over an artifact and evaluator scores",
     "inputSchema": {"type": "object", "properties":
                     {"surface": {"type": "string"}, "artifact": {"type": "string"},
                      "scores": {"type": "object"},
                      "claims": {"type": "array", "items": _CLAIM_ITEM_SCHEMA},
                      "stakes": {"type": "string"}},
                     "required": ["artifact"]}},
    {"name": "comms.golden",
     "description": "run the 20-case golden replay suite (10 must-pass + 10 must-fail)",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "comms.verdict",
     "description": "sole termination: verifier/human issue pass|revise|escalate|abstain; GEV_LOCK refuses all others; optionally seals the 12-part proof packet",
     "inputSchema": {"type": "object", "properties":
                     {"role": {"type": "string"}, "decision": {"type": "string",
                                                               "enum": list(models.VERDICTS)},
                      "scores": {"type": "object"}, "stakes": {"type": "string"},
                      "packet": {"type": "object", "description": "optional CommunicationPacket dict to seal"},
                      "run_id": {"type": "string"}, "lineage_log": {"type": "string"}},
                     "required": ["role", "decision"]}},
    {"name": "comms.outcome",
     "description": "C11 telemetry: action=record (predicted_p + outcome) | brier | promote (>=3 wins; minting stays human)",
     "inputSchema": {"type": "object", "properties":
                     {"action": {"type": "string", "enum": ["record", "brier", "promote"]},
                      "pattern_id": {"type": "string"}, "archetype": {"type": "string"},
                      "predicted_p": {"type": "number"}, "outcome": {"type": "integer"},
                      "stakes": {"type": "string"}}, "required": ["action"]}},
]

_RESOURCE_URIS = ("comms://archetypes", "comms://doctrine", "comms://golden",
                  "comms://fingerprint", "comms://roles")

DOCTRINE = """# Build Card non-negotiables (v20)
1. Recipient first. 2. Bottom line up front. 3. Warmth x competence (both, never one for the other).
4. Show, do not label. 5. One-in-a-million specificity. 6. Positive-direction control.
7. No throat-clearing. 8. Value before extraction. 9. Truth over urgency theater.
10. Public-page test. 11. Human voice over AI baseline. 12. No self-verification.
Out of scope: invented facts/relationships/urgency; unapproved sends; sensitive-attribute
targeting; impersonation; autonomous crisis/legal/payment comms; click-optimization over truth."""


def _prompts() -> list:
    def p(name, desc, args):
        return {"name": name, "description": desc, "arguments": args}
    mode_desc = {"skeptical": "believes everything until sourced; hunts every unsupported claim",
                 "busy": "reads one screen on a phone; anything after the first sentence is lost",
                 "friendly": "wants to say yes; reports where yes is ambiguous or costly",
                 "hostile": "reads to forward to a lawyer; every hedge and asymmetry is a weapon",
                 "literal": "no implied meaning; flags anything that reads differently than meant"}
    out = []
    for mode, d in mode_desc.items():
        out.append(p(f"sim-{mode}", f"Recipient Simulator ({mode} mode): {d}. Report only; never rewrite.", []))
    out += [
        p("draft", "Message Architect: build the semantic skeleton + first draft from the approved intent and evidence. You cannot score or release your draft.", []),
        p("voice", "Voice Smith: render the verified semantic draft into Mike/RIG voice. You cannot alter facts, commitments, prices, dates, or risk posture.", []),
        p("critic-clarity", "Clarity & Compression Critic: BLUF latency, reading load, jargon, redundancy, mobile scanability, action clarity. Report only.", []),
        p("critic-warmth", "Warmth/Competence Critic: score both axes independently; flag manipulative warmth, unsupported authority, accidental contempt. Report only.", []),
        p("redteam", "Red-Team Communicator: screenshot risk, claim inflation, privacy leakage, coercion, fake urgency, reputational downside. Report only.", []),
        p("verify", "Communications Verifier: check all release gates over the evaluator transcript; issue pass|revise|escalate|abstain via comms.verdict. You never draft or repair.", []),
    ]
    return out


_RULES = {
    "draft": "GEV: you are the generator. Cite every fact to the claim ledger. "
             "Bottom line in the first useful sentence. You may NOT score or release this draft.",
    "voice": "GEV: preserve every claim, number, commitment, date, price. Apply fingerprint-v2 "
             "(hard-banned words, signature vocab, sentence bands). If meaning shifts, stop.",
    "verify": "GEV: you are the sole termination authority. Call comms.verdict with role='verifier'. "
              "Hard floors are non-negotiable. You did not write this and must not repair it.",
}


def _system(role: str) -> str:
    cannot = "; ".join(roles.role_cannot(role)) or "nothing — this role may not act, only approve"
    return (f"You are the {role} role in the rig-communications GEV topology. "
            f"You CANNOT: {cannot}. {_RULES.get(role, 'Report findings as typed defects; never rewrite outside your role.')}")


def handle(req: dict) -> dict | None:
    m = req.get("method")
    if m == "initialize":
        return {"protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                "serverInfo": {"name": "rig-comms", "version": VERSION},
                "instructions": INSTRUCTIONS}
    if m == "notifications/initialized":
        return None
    if m == "tools/list":
        return {"tools": _TOOLS}
    if m == "resources/list":
        return {"resources": [{"uri": u, "name": u.split("//")[1]} for u in _RESOURCE_URIS]}
    if m == "resources/read":
        uri = req["params"].get("uri")
        if uri == "comms://archetypes":
            body = {"vehicles": vehicles.VEHICLES, "weights_low": energy.WEIGHTS_LOW,
                    "weights_high": energy.WEIGHTS_HIGH}
        elif uri == "comms://doctrine":
            return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": DOCTRINE}]}
        elif uri == "comms://golden":
            body = golden.run_suite()
        elif uri == "comms://fingerprint":
            body = voice.FINGERPRINT
        elif uri == "comms://roles":
            body = roles.ROLES
        else:
            return _err(req, -32602, f"unknown resource {uri}")
        return {"contents": [{"uri": uri, "mimeType": "application/json",
                              "text": json.dumps(body, indent=2, default=str)[:512 * 1024]}]}
    if m == "prompts/list":
        return {"prompts": _prompts()}
    if m == "prompts/get":
        name = req["params"].get("name", "")
        base = name.replace("sim-", "")
        if name.startswith("sim-") and base in ("skeptical", "busy", "friendly", "hostile", "literal"):
            content = [{"type": "text", "text":
                        f"Read the message as a {base} recipient. List ambiguities, unintended "
                        f"emotional residue, and the first point of resistance. Report only."}]
        elif name in ("draft", "voice", "critic-clarity", "critic-warmth", "redteam", "verify"):
            content = [{"type": "text", "text": _system(name)}]
        else:
            return _err(req, -32602, f"unknown prompt {name}")
        return {"description": name, "messages": [{"role": "user", "content": content[0]}]}
    if m == "tools/call":
        name = req["params"].get("name")
        args = req["params"].get("arguments", {})
        try:
            if name == "comms.surfaces":
                out = {sid: {"lane": s.lane, "engines": list(s.engines),
                             "budget": s.budget, "sigma_target": s.sigma_target}
                       for sid, s in surfaces.SURFACES.items()}
            elif name == "comms.route":
                out = {"route": surfaces.route(args["intent"])}
            elif name == "comms.packet":
                if args["surface"] in surfaces.PRIVATE_SURFACES and not args.get("human"):
                    return _err(req, -32001,
                                "PRIVACY_LOCK: private lane requires human:true (exit-3 semantics)")
                out = {"packet": packets.build_packet(args["surface"], args["brief"],
                                                      args.get("persona", ""))}
            elif name == "comms.score":
                s = surfaces.resolve(args["surface"])
                if s is None:
                    return _err(req, -32602, f"unknown surface '{args['surface']}'")
                if s.lane == "private":
                    return _err(req, -32001, "PRIVACY_LOCK: machine scoring of the private lane "
                                             "is refused (v19.6). Human writes, human ships.")
                st = gates.evaluate_stack(s, args["artifact"])
                out = {**st, "exit": 0 if st["can_ship"] else 2}
            elif name == "comms.intent_check":
                ci = models.CommunicationIntent.from_dict(args["intent"])
                errs = ci.validate()
                out = {"valid": not errs, "errors": errs,
                       "vehicle_preview": vehicles.choose(ci) if not errs else None}
            elif name == "comms.audience":
                am = models.AudienceModel(known=args.get("known", []),
                                          inferred=args.get("inferred", []),
                                          unknown=args.get("unknown", []))
                out = {"audience_model": models.asdict_model(am) if hasattr(models, "asdict_model")
                       else {"known": am.known, "inferred": am.inferred, "unknown": am.unknown},
                       "c2_errors": models.audience_model_errors(am)}
            elif name == "comms.vehicle":
                out = vehicles.choose(models.CommunicationIntent.from_dict(args["intent"]))
            elif name == "comms.energy":
                out = energy.evaluate(args["scores"], args.get("stakes", "medium"))
            elif name == "comms.claims":
                out = {**claims.lint_ledger(args.get("claims", [])),
                       **({"text_audit": claims.audit_text(args["text"])} if args.get("text") else {})}
            elif name == "comms.compress":
                out = compress.analyze(args["artifact"])
            elif name == "comms.gates":
                surf = surfaces.resolve(args["surface"]) if args.get("surface") else None
                if surf is not None and surf.lane == "private":
                    return _err(req, -32001, "PRIVACY_LOCK: machine scoring of the private lane "
                                             "is refused (v19.6). Human writes, human ships.")
                lint = claims.lint_ledger(args.get("claims", []))
                comp = compress.analyze(args["artifact"])
                scores = dict(args.get("scores", {}))
                scores.setdefault("claim_support", lint["claim_support"])
                scores.setdefault("first_sentence_value",
                                  comp["bluf_latency_secs"] <= energy.ASK_LATENCY_MAX_SECS
                                  and comp["clean"])
                ev = energy.evaluate(scores, args.get("stakes", "medium"))
                out = {"claim_lint": lint, "compression": comp, "energy": ev,
                       "can_ship": ev["ship_eligible"],
                       "exit": 0 if ev["ship_eligible"] else 2}
            elif name == "comms.golden":
                out = golden.run_suite()
            elif name == "comms.verdict":
                ev = None
                if args.get("scores") is not None:
                    ev = energy.evaluate(args["scores"], args.get("stakes", "medium"))
                floors_ok = bool(ev and ev["floors_ok"] and ev["ship_eligible"])
                if args.get("decision") != "pass":
                    floors_ok = True  # floors only bind `pass`
                v = roles.issue_verdict(args["role"], args["decision"], floors_ok)
                out = {"verdict": v}
                if v["admitted"] and args.get("packet"):
                    pk = models.CommunicationPacket.from_dict(args["packet"])
                    pk.verifier_decision = args["decision"]
                    out["sealed_packet"] = pk.finalize().to_dict()
                if v["admitted"] and args.get("run_id") and args.get("lineage_log"):
                    out["lineage_event"] = lineage.append_event(
                        args["lineage_log"], args["run_id"], "VERIFY", args["role"],
                        {"decision": args["decision"], "packet_hash":
                         out.get("sealed_packet", {}).get("packet_hash")})
            elif name == "comms.outcome":
                action = args["action"]
                if action == "record":
                    out = outcomes.record(args["pattern_id"], args["archetype"],
                                          args["predicted_p"], args["outcome"],
                                          args.get("stakes", "medium"))
                elif action == "brier":
                    out = outcomes.brier(args.get("archetype"))
                else:
                    out = {"candidates": outcomes.promotion_candidates()}
            else:
                return _err(req, -32601, f"unknown tool {name}")
            return {"content": [{"type": "text",
                                 "text": json.dumps(out, indent=2, default=str)}]}
        except (KeyError, ValueError, AttributeError, TypeError) as e:
            return _err(req, -32602, str(e))
    return _err(req, -32601, f"unknown method {m}")


def _err(req, code, msg):
    return {"error": {"code": code, "message": msg}}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "id": None,
                              "error": {"code": -32700, "message": "parse error"}}), flush=True)
            continue
        resp = handle(req)
        if resp is None or "id" not in req:
            continue
        out = {"jsonrpc": "2.0", "id": req["id"]}
        out.update({"error": resp["error"]} if "error" in resp else {"result": resp})
        print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
