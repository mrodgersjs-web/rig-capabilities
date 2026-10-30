"""CLI entry: runs S1..S9, writes runs/<id>.jsonl, exits 2 when fitness < 1.0."""
import gate_config
import gates
import gatecalc
import scoring
import steps


def run(draft, audience, channel, approve=False, outcome=None):
    """Run S1..S9, append S9 when sent+approved, and write the event log."""
    # D85 reachability: pin the model path, thresholds, and both gate paths
    # into the execution graph through one sink before the run.
    path = steps.main_path()
    thresholds = steps.config()
    probe = scoring.bdf30(gatecalc.rate_forces("reachability probe"))
    floor_min = gates.bdf30_min_value()
    pinned = gatecalc.boundary_check(path, thresholds, probe, floor_min)
    result = gatecalc.run_pipeline(draft, audience, channel, approve, outcome)
    return gatecalc.passthrough(result, pinned)


def cli_main(argv):
    """argparse entry; returns the process exit code."""
    return gatecalc.cli_main(argv)
