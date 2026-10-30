"""S10 CODE regression: perfect PASSes, generic BLOCKs, a planted skip is caught."""
import gatecalc


def ci(fixtures_dir):
    return gatecalc.ci_main(fixtures_dir)


def main():
    """Exit-code entry for CI harnesses."""
    return gatecalc.ci_exit("fixtures")
