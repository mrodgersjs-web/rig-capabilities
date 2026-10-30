"""S1..S9 step graph, deterministic and event-logged (registered boundary).

Step-kind discipline: MODEL steps are the S2 call (here: a pluggable
deterministic rater, so CI needs no network); HUMAN is S8 (exact-text approval
token, never auto-approve); CODE steps are pure functions of their inputs.
Edges: S1->S2->S3->S4->S5->S6->S7->S8->S9->END (main path == every step).
"""
import gate_config
import gatecalc
import rigmath
import scoring


def graph():
    return {"S1": ["S2"], "S2": ["S3"], "S3": ["S4"], "S4": ["S5"], "S5": ["S6"],
            "S6": ["S7"], "S7": ["S8"], "S8": ["S9"], "S9": ["END"]}


def main_path():
    return ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"]


def config():
    return {"bdf30_min": gate_config.bdf30_min(),
            "antigeneric_min": gate_config.antigeneric_min(),
            "identity_min": gate_config.identity_min(),
            "ethical_min": gate_config.ethical_min(),
            "abstain_band": gate_config.abstain_band()}


def s1_load(draft, audience, channel):
    """S1 CODE load."""
    return gatecalc.artifact(draft, audience, channel)


def s2_rate(rated):
    """S2 CODE validator over rated forces (schema, [0,1] range, size cap)."""
    return gatecalc.rate_validated(rated, gate_config.force_keys(),
                                   gate_config.max_model_output_tokens())


def s2_model(artifact):
    """S2 MODEL rating (deterministic heuristic rater) then the CODE validator."""
    return s2_rate(gatecalc.rate_forces(gatecalc.draft_of(artifact)))


def s3_composites(forces):
    """S3 CODE F-WSUM composites."""
    return {"bdf30": scoring.bdf30(forces)}


def s4_bdf_gate_forces(forces):
    """S4 CODE BDF30 vs ONE constant 0.85 (shared via gate_config)."""
    passed = scoring.verdict(forces)
    return {"passed": passed,
            "bdf30": scoring.bdf30(forces),
            "action": gatecalc.action_name(passed)}


def s4_bdf_gate(artifact):
    return s4_bdf_gate_forces(s2_model(artifact))


def s5_floors_forces(forces):
    """S5 CODE floors: anti-generic >= 0.80, identity >= 0.75, ethical >= 0.70."""
    blocks = scoring.floor_blocks(forces)
    return {"blocks": blocks, "passed": gatecalc.no_blocks(blocks)}


def s5_floors(artifact):
    return s5_floors_forces(s2_model(artifact))


def s6_forecast(forces):
    """S6 CODE forecast p_send = 0.6*bdf30 + 0.4*anti_generic, clamped [.05,.95]."""
    w = rigmath.weighted_sum([scoring.bdf30(forces), gatecalc.pick(forces, "anti_generic_force")],
                             [0.6, 0.4])
    return {"forecast": rigmath.clamp(w, 0.05, 0.95)}


def s6(artifact):
    return s6_forecast(s2_model(artifact))


def s7_send_decision_forces(forces):
    """S7 CODE send/abstain/block with explicit abstain band."""
    return gatecalc.send_decision(forces, s4_bdf_gate_forces(forces),
                                  s5_floors_forces(forces), config())


def s7_send_decision(artifact):
    return s7_send_decision_forces(s2_model(artifact))


def s8_approval(artifact, approval_token):
    """S8 HUMAN: approval only via an exact-text token supplied from outside."""
    return gatecalc.approval(gatecalc.draft_of(artifact), approval_token)


def s9_brier(forces, outcome):
    """S9 CODE outcome + F-BRIER over the S6 forecast derived from rated forces."""
    return {"brier": rigmath.brier(rigmath.dict_picks(s6_forecast(forces), ["forecast"]),
                                    [outcome])}


def conformance(log_steps):
    """Fitness of an event log against the model: < 1.0 when a step was skipped."""
    return rigmath.replay_sequence(gatecalc.append_end(list(log_steps)), graph(),
                                   "S1", "END")
