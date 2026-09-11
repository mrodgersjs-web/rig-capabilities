"""Parameterized activation worker for the jarvis_blackwell process (v13).

v1 BLOCK: method calls on local objects are unrepresentable (open/write/close).
v2/v3 superseded: multi-op linear activate() cannot fail-fast between effects
(this grammar has no conditionals). v4 superseded: first gate-d attempt bound
an action with a mutable sidecar checksum (TOCTOU). v5 superseded: gate-d was
probed before an approval record existed (exit-2 = terminal for the attempt).
v6 superseded: transaction scope bundled Handy retirement; scope reduced per
advisory so the approved effect is config install + service restart ONLY.
v7: config/restart-only transaction, Gate-D protocol as corrected in v6 —
action hash computed locally, approval minted AFTER typed human approval,
first gate-d invocation is the approved one. The script (staged + hash-bound
in the Gate-D action file, NOT here) enforces ordering executably with set -e:
literal-hash verification of staged bytes, temp-file + atomic rename install,
launchctl restart, PID turnover gate (process must actually restart), health
gate, model-advertised gate. Handy retirement is OUT OF SCOPE for v7 — it
requires a separate later Gate-D action after the voice replacement is proven.
The action file additionally binds sha256 hashes of the OpenJarvis source
files whose changed behavior the restart loads (source-tree binding).
v8 superseded v7: v8 was forked so a freshly scored process would exist after
routes.py changed again (fail-closed host hardening). v8 BLOCKed: classify was
invoked before its classification file was authored (AUTHORITY_FILE_MISSING,
exit 2) — terminal under the D85 exit-2 rule; preserved as failed evidence.
v9 superseded v8: identical worker behavior, classification authored BEFORE
the first classify call; REALIZED_PASS.
v10 supersedes v9: corrects this docstring's provenance wording only. D85
scoring hashes ONLY this worker and its adapter — it does NOT bind OpenJarvis
source bytes. The FINAL routes.py/serve.py/_discovery.py/_openai_compat.py
sha256s and the staged config are bound by the Gate-D ACTION file (and its
embedded transaction-script literals), which is the sole authority for
source-tree binding. No behavior change.
v11 supersedes v10: v10 was terminally BLOCKed because its hand-authored
classification file used a wrong schema shape (AUTHORITY_MALFORMED, exit 2);
preserved as failed evidence. v11 fixes the classification to the
rig.d85.classification.v1 inventory-bound schema and it exists BEFORE the
first classify call. Executable behavior is unchanged from v10; no behavior
change.
v12 supersedes v11: corrects v11's false docstring claim that worker/adapter
BYTES were identical to v10 (they are not — docstrings differ). v12 bytes
differ from v11 only in these docstring lines; executable behavior is
unchanged. No code change.
v13 supersedes v12: v12's first gate-d invocation returned exit 2
(BLOCK_GATE_D_UNAPPROVED) because the typed approval was recorded only in the
session ledger instead of the HMAC-signed authority/gate_d approvals store the
CLI validates — an operational sequencing error, terminal under the exit-2
rule; preserved as failed evidence. Executable behavior is unchanged; only the
worker and adapter docstrings differ. No code change.
"""

import subprocess


def run_activation_transaction(arguments):
    return subprocess.call(arguments)


def activate(transaction_arguments):
    status = run_activation_transaction(transaction_arguments)
    return (status,)
