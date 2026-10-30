"""D85 registered boundary for the Jake revenue pipeline (REVENUE-SPEC R1-R7).

Inventory inspects this boundary statically; registration never invokes it.
stage_argv builds the exact launch argv for one pipeline stage; run_stage
transfers it to the OS as a separate process. The stage sources (revenue.py,
landing.py, proposal.py, funnel.py, hygiene.py) are hash-bound in their
Jev-gated receipts under RECEIPTS.md "C:" blocks and run only under their own
verifiers, never from here.
"""
import subprocess


def stage_argv(python_bin, script, argument):
    return [python_bin, script, argument]


def run_stage(python_bin, script, argument):
    argv = stage_argv(python_bin, script, argument)
    return subprocess.call(argv)
