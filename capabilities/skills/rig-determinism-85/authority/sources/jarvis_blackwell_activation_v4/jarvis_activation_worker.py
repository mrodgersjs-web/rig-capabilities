"""Parameterized activation worker for the jarvis_blackwell process (v4).

v1 BLOCK: method calls on local objects are unrepresentable (open/write/close).
v2 superseded: linear activate() could not fail-fast between cp and kickstart.
v3 superseded: still linear; ordering across separate subprocess.call ops is
unenforceable in this grammar (no conditionals).
v4: ONE fail-fast external transaction script invoked once via
subprocess.call. The script (staged + hash-bound in the Gate-D action file,
NOT here) enforces ordering executably with set -e: staged-byte verification,
temp-file + atomic rename install, launchctl restart, live health gate, and
Handy retirement LAST — any failed step aborts before pkill runs.
"""

import subprocess


def run_activation_transaction(arguments):
    return subprocess.call(arguments)


def activate(transaction_arguments):
    status = run_activation_transaction(transaction_arguments)
    return (status,)
