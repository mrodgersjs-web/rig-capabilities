# Optional: behavioral advisory pass (`bx-advice.json`)

An optional step after the working draft exists and before Mike's evidence review. It runs three Behavioral
Science Studio tools over the packet and writes one file, `bx-advice.json`, beside it:

| Tool | Looks at | Gives |
|---|---|---|
| `bx_committee_simulate` | the hiring committee implied by the posting (hiring manager, risk reviewer, technical panel, business sponsor, recruiter screen) and how well the packet evidences the requirements each one owns | consensus probability, veto set, the member most likely to stall, and the red lines to confirm first |
| `bx_bias_audit` | the draft resume text (contact details redacted) | bias findings with the exact quote and a suggested correction |
| `bx_falsify` | the top claim: the resume line the packet cites for the most requirements | the strongest disconfirming evidence, a kill criterion and a verdict |

## Rules

- Advisory only. It never edits the resume, the spec, the claim ledger or any gate receipt, and it never passes or
  fails a gate. The file records `"advisory": true, "blocks_gate": false, "edits_resume": false` and the SHA-256 of
  every input before and after the run (`inputs_unchanged`).
- A finding is a question for Mike's review, not a reason to change a claim. A `REFUTED` top claim means "bring the
  artifact, name and number that would survive an interview", not "delete the line". Only Mike's confirm, replace or
  omit changes a claim.
- Committee roles, blame priors and keyword ownership are heuristics stated in the file (`derivation`), not
  measurements of any person at the employer.
- If a model call fails, the error is written to the file and the command still exits 0. Exit 2 only means the packet
  could not be read.

## Run it

Runs on rig256gb (studio at `~/Developer/behavioral-science-studio`, MCP server `com.rig.bx-studio-mcp` on
`127.0.0.1:4236/mcp`). Set `BX_MCP_URL` to use that server; without it the command starts its own over stdio.

Red-line packet (after `parity_gate.py` has written the render dir):

```bash
cd ~/Developer/behavioral-science-studio
BX_MCP_URL=http://127.0.0.1:4236/mcp .venv/bin/bx-jobs-advice redline \
  ~/rig-builds/resume-review-20261028/redline/specs/01-citi.json \
  "$HOME/rig-builds/resume-review-20261028/redline/01-Citi - DRAFT (red = review).docx" \
  --out-dir ~/rig-builds/resume-review-20261028/redline/render/01-citi
```

Job Applier packet (`posting.txt`, `resume.txt`, `jd-requirements.json`, `jd-coverage.json`):

```bash
BX_MCP_URL=http://127.0.0.1:4236/mcp .venv/bin/bx-jobs-advice v5 ~/.applypilot/packets/<date>/<packet>/v5
```

It prints the `summary` lines. Show them to Mike next to the claim decisions; the full tool outputs are under `steps`.
