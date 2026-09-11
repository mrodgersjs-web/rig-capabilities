"""Parameterized activation worker for the jarvis_blackwell process (v9).

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
v8 supersedes v7: v7's scored bytes were finalized before its wrapped-topology
regression tests were upgraded (real OllamaEngine leaf, fail-closed 502 on
missing host, posthog analytics disabled in the model-management test app to
kill the interpreter-exit hang). Code under this process_id is unchanged in
behavior — v8 exists so the scored process binds the FINAL OpenJarvis source
bytes (routes.py sha changed again after fail-closed hardening).
v9 supersedes v8: v8's first classify invocation ran before its classification
file was authored (AUTHORITY_FILE_MISSING, exit 2) — terminal for v8 under the
D85 exit-2 rule; v8 is preserved as failed evidence. v9 is byte-identical in
behavior with the classification authored BEFORE the first classify call.
"""

import subprocess


def run_activation_transaction(arguments):
    return subprocess.call(arguments)


def activate(transaction_arguments):
    status = run_activation_transaction(transaction_arguments)
    return (status,)
