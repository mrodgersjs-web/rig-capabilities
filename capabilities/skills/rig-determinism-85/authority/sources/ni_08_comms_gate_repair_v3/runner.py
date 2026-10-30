"""CLI entry: runs S1..S9, writes runs/<id>.jsonl, exits 2 when fitness < 1.0."""
import gatecalc


def run(draft, audience, channel, approve=False, outcome=None):
    """Run S1..S9, append S9 when sent+approved, and write the event log."""
    return gatecalc.run_pipeline(draft, audience, channel, approve, outcome)


def cli_main(argv):
    """argparse entry; returns the process exit code."""
    return gatecalc.cli_main(argv)
