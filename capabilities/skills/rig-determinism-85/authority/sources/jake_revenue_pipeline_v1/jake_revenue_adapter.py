"""Execution root: the durable loop calls one adapter per pipeline stage."""
from jake_revenue_worker import run_stage


def execute(python_bin, script, argument):
    return run_stage(python_bin, script, argument)
