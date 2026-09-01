# Great example — capabilities-round

Run: `round revenue-gtm 3`

Output that earned the label:

- Named the 3 weakest revenue-gtm canonicals by trust (0.62 / 0.65 / 0.68) and why: missing done_when.
- Upgraded each contract deterministically (added file:+grep: checks derived from the asset's own outcome line), showed old→new done_when per asset.
- Ran done-tests after each write: 2 assets green, 1 regressed → REVERTED that one and reported the regression instead of hiding it.
- Final quality_report quoted the lane mean moving 0.65 → 0.71.

The revert is the great part: the round proved it could refuse.
