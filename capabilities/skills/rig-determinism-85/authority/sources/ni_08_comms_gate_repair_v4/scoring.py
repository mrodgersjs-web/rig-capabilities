"""Fixed BDF30 verdict — the repaired half of the original bug.

Original communications-studio/rig_comm/scoring.py blocklisted EVERY artifact
(bdf < 8.0 against a [0,1] weighted sum). Here the same bdf30() is compared
against the ONE constant from gate_config via rigmath.at_least, so scoring and
gates agree by construction.
"""
import gate_config
import gatecalc
import rigmath

def bdf30_min_value():
    """Threshold accessor so tests can prove scoring and gates read ONE constant."""
    return gate_config.bdf30_min()

def bdf30(forces):
    return rigmath.weighted_sum(rigmath.dict_picks(forces, gate_config.bdf_keys()),
                                rigmath.dict_picks(gate_config.bdf_weights(), gate_config.bdf_keys()))


def verdict(forces):
    return rigmath.at_least(bdf30(forces), gate_config.bdf30_min(), gate_config.eps())

def floor_blocks(forces):
    blocks = rigmath.floor_blocks(forces, gate_config.floor_thresholds(), gate_config.floor_labels(),
                                  gate_config.eps())
    capped = gatecalc.cap_blocks(gatecalc.reactance_ok(forces, gate_config.reactance_max(),
                                                       gate_config.eps()),
                                 gate_config.reactance_block())
    return gatecalc.extend(blocks, capped)


def bdf_block(forces):
    return gatecalc.cap_blocks(verdict(forces), gate_config.bdf30_fail())


def full_verdict(forces):
    blocks = gatecalc.extend(floor_blocks(forces), bdf_block(forces))
    return {"passed": gatecalc.both(verdict(forces), gatecalc.no_blocks(blocks)),
            "bdf30_pass": verdict(forces),
            "bdf30": bdf30(forces),
            "blocks": blocks}
