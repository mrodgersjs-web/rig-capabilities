"""Second opinion over the same draft — independent BDF30 + floor path.

Reimplements the composite (plain accumulator in gatecalc) and the floor scan
without rigmath, so gate_agreement is a numeric cross-check between two code
paths, not a shared-code tautology. The threshold constant itself is shared BY
DESIGN: both modules call gate_config.bdf30_min(). This replaces the original
gates.py:230 which was right while scoring was wrong.
"""
import gate_config
import gatecalc
import rigmath


def bdf30_min_value():
    return gate_config.bdf30_min()


def bdf30(forces):
    return gatecalc.bdf30_accumulate(forces, gate_config.bdf_weights(), gate_config.force_keys())


def verdict(forces):
    return rigmath.at_least(bdf30(forces), bdf30_min_value(), gate_config.eps())


def floor_blocks(forces):
    floors = gatecalc.gates_floor_blocks(forces, gate_config.floor_thresholds(),
                                         gate_config.floor_labels(), gate_config.eps())
    caps = gatecalc.cap_blocks(gatecalc.reactance_ok(forces, gate_config.reactance_max(),
                                                     gate_config.eps()), gate_config.reactance_block())
    return gatecalc.extend(floors, caps)


def verdict_full(forces):
    blocks = floor_blocks(forces)
    return {"passed": gatecalc.both(verdict(forces), gatecalc.no_blocks(blocks)),
            "bdf30": bdf30(forces),
            "blocks": blocks}


def gate_agreement(artifacts):
    """Objective gate_agreement: fraction of artifacts where scoring and gates agree."""
    return gatecalc.agreement(artifacts)
