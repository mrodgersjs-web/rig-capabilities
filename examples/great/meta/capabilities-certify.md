# Great example — capabilities-certify

Run: `certify plant`

Matrix produced (V22, real):

| gate | green | red_when_planted | restored |
|---|---|---|---|
| suite | Y | Y | Y |
| index_fresh | Y | Y | Y |
| done_tests | Y | Y | Y |
| idp_integrity | Y | Y | Y |
| acl_jake | Y | Y | Y |

It also caught a live bug: `semgrep`'s done_when grepped `SKILL.md:Semgrep` — the frontmatter itself carried the pattern, so the check could never fail. The plant proved the gate was theater; the contract was rewired to an external file. A certification run that finds its own weakness is worth more than five clean green runs.
