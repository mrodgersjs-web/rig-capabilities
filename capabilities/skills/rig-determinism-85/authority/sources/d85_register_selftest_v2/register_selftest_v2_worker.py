"""Deterministic selftest worker v2 (synthetic loader-compat asset).

v2 exists because the D85 inventory hash of any process that locks an
external module embeds the loader fingerprint (sys.path of the analyzing
interpreter, d85.py _external_module_locks): v1's hash therefore only
reproduces inside the certifier context that validate_lattice builds, and a
Gate-D mint run from a plain shell saw CLASSIFICATION_STALE. v2 has ZERO
external imports or calls, so no fingerprint enters its inventory and its
hash is context-independent: score_realized returns the same dict from any
interpreter. Same doctrine as v1: synthetic only, earns no work credit; the
loader never executes these bytes.
"""

from __future__ import annotations

RUN_ID = "register-selftest-v2"


def stage(name: str) -> str:
    return "selftest:" + name + ":" + RUN_ID


def run_stage(name: str) -> str:
    return stage(name)


def finish(label: str) -> int:
    if len(label) == 0:
        return 1
    return 0
