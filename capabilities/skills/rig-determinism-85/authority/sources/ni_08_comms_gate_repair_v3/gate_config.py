"""Named config for the comms gate. ONE constant source, reached by scoring.py AND gates.py.

Registered source (D85 boundary). Constants are functions so the module stays inside the
closed grammar; every consumer calls these functions, so an edit here changes both gates at
once (the bug fixed: scoring compared bdf30() < 8.0 while gates.py used the 0.85 constant).
Assumption (named, testable): BDF30_MIN=0.85 because bdf30() is a weighted sum of [0,1]
forces (range 0-1). Mike/council may re-rule by editing this file only.
"""


def bdf30_min():
    """Single BDF30 threshold imported by both scoring and gates."""
    return 0.85


def antigeneric_min():
    return 0.80


def identity_min():
    return 0.75


def ethical_min():
    return 0.70


def reactance_max():
    return 0.20


def abstain_band():
    """S7: within this margin of a threshold, abstention is offered."""
    return 0.05


def eps():
    """F-STOP: never claim zero remaining work."""
    return 1e-9


def max_model_output_tokens():
    """Bounded S2 call: rater output past this cap is rejected by the validator."""
    return 512


def force_keys():
    """Full typed output schema of the S2 call (all values floats in [0,1])."""
    return ["semantic_inversion", "proof_density", "enemy_specificity", "catchphrase_voltage",
            "structural_novelty", "negative_space_weight", "identity_force",
            "anti_generic_force", "ethical_restraint", "reactance_risk"]


def bdf_keys():
    """The seven forces carrying BDF30 weight (subset of force_keys, stable order)."""
    return ("semantic_inversion", "proof_density", "enemy_specificity",
            "catchphrase_voltage", "structural_novelty", "negative_space_weight",
            "identity_force")


def bdf_weights():
    """F-WSUM weights for BDF30, sum = 1.0 (same decomposition as communications-studio scoring.py:125-135)."""
    return {"semantic_inversion": 0.25, "proof_density": 0.20, "enemy_specificity": 0.15,
            "catchphrase_voltage": 0.15, "structural_novelty": 0.10,
            "negative_space_weight": 0.10, "identity_force": 0.05}


def floor_thresholds():
    """Lower-bound floors (anti-generic / identity / ethical)."""
    return {"anti_generic_force": antigeneric_min(), "identity_force": identity_min(),
            "ethical_restraint": ethical_min()}


def floor_labels():
    return {"anti_generic_force": "FLOOR_ANTIGENERIC: anti_generic_force below floor",
            "identity_force": "FLOOR_IDENTITY: identity_force below floor",
            "ethical_restraint": "FLOOR_ETHICAL: ethical_restraint below floor"}


def reactance_block():
    """Upper-bound floor: reactance_risk must not exceed the cap."""
    return "FLOOR_REACTANCE: reactance_risk above cap"


def bdf30_fail():
    """Block message mirroring communications-studio's BDF30_FAIL, now with the right scale."""
    return "BDF30_FAIL: bdf30 below threshold - Not deviant enough"
