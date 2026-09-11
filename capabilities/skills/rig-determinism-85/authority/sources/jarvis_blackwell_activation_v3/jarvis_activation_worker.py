"""Parameterized activation worker for the jarvis_blackwell process (v3).

v1 BLOCK: method calls on local objects are unrepresentable (open/write/close).
v2 superseded: linear activate() could not fail-fast between cp and kickstart.
v3: config install + restart + health gate is ONE fail-fast external
transaction (hash-bound script, set -e, temp-file + atomic rename, health
check) invoked once; Handy retirement is a separate operation with the
transaction's verified success as an explicit execution precondition.
All payloads arrive as positional inputs at Gate-D execution time.
"""

import subprocess


def run_activation_transaction(arguments):
    return subprocess.call(arguments)


def retire_handy(arguments):
    return subprocess.call(arguments)


def activate(transaction_arguments, quit_arguments):
    status = run_activation_transaction(transaction_arguments)
    quit_status = retire_handy(quit_arguments)
    return (status, quit_status)
