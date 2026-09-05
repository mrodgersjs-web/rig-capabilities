# Snyk Code — 26 MEDIUM findings triaged (2026-09-05)

Source artifact: `.context/snyk-code-review.json` (`snyk code test --org=rodgemd1`,
`exit_code=1`, `scan_completed=true`, summary `total=272 high=0 medium=26 low=246`).
Exit code alone is never the verdict — the 26 MEDIUM rows were opened and read at their
flagged lines.

Two verdicts used: **INVALID** (the scanner's claim is false in this code) and
**ACCEPTED-RISK** (the primitive is real, the taint source is not untrusted in this
threat model, named residual + flip condition below).

Counts are scan ROWS, not distinct lines: `loops.py` contributes 19 rows over 17 lines
(1884 and 1946 are each reported twice, different rule ids). 19+3+1+1+1+1 = 26.
Re-derive: count `severity == "MEDIUM"` rows in the artifact and group by `path`.

| count | rule | file:lines | verdict |
|---|---|---|---|
| 19 | Command Injection | `rig_capabilities/loops.py` 142, 914, 990, 991, 1027, 1167, 1178, 1588, 1590, 1867, 1876, 1884, 1900, 1916, 1946, 1952, 1955 | ACCEPTED-RISK |
| 3 | Command Injection | `scripts/scrape_channel_corpus.py` 119, 144, 189 | INVALID |
| 1 | Command Injection | `rig_capabilities/lease.py` 226 | INVALID |
| 1 | Command Injection | `capabilities/skills/codeql/scripts/verify_query_suite.py` 22 | INVALID |
| 1 | SQL Injection | `rig_capabilities/rounds.py` 486 | INVALID |
| 1 | SSRF | `capabilities/skills/rig-lattice-system/rig_lattice/deviator/dv.py` 203 | INVALID |

## INVALID — with the evidence

**`scrape_channel_corpus.py` 119 / 144 / 189.** All three are `sh([...])` call sites.
`sh` is:

```python
def sh(args, timeout=300):
    """Run an argv list (never a shell string: video ids can start with '-')."""
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
```

`args` is a list, `shell` is not set → no shell, no metacharacter interpretation. The
channel/video URL is a positional argv element after fixed flags. No injection surface.

**`rig_capabilities/lease.py:226`.** `subprocess.run([str(GUARD_BIN), "check", key], …)` —
argv list, `GUARD_BIN` is a module constant path, `key` is an absolute path string passed
as one argv element. No shell.

**`capabilities/skills/codeql/scripts/verify_query_suite.py:22`.** `command =
[codeql_executable, "resolve", "queries", "--format=json", "--", str(suite_path)]` then
`subprocess.run(command, …)` — argv list, `--` terminator present, no shell.

**`rig_capabilities/rounds.py:486`.** No SQL of any kind in this file:
`grep -nE 'execute|sqlite|sql|SELECT|INSERT' rig_capabilities/rounds.py` → no matches.
Line 486 is `r = run_asset(repo, c["id"], source="canonical")`. Nothing to fix.

**`dv.py:203` (SSRF).** `ur.urlopen(req)` where the URL comes from
`p.add_argument("--url", default=DEFAULT_LLM_URL, …)` — an operator CLI flag pointing at a
local OpenAI-compatible endpoint. No request handler, no URL read from stored artifacts,
nothing network-derived reaching `urlopen`. SSRF presumes an attacker-controlled URL; the
only party who can set it can already run the process.

## ACCEPTED-RISK — the 19 in `rig_capabilities/loops.py`

All 19 occurrences collapse to **two** exec primitives, and running declared shell
commands *is* this module's product:

| primitive | line | where the command string comes from |
|---|---|---|
| `_run_cmd()` → `subprocess.run(cmd, shell=True, …)` | 142 | `g["command"]` (gate, 605), `c["cmd"]` (check, 980), `red_cmd`/`green_cmd` (plant-failure, 990/991), `step["sh"]` (spec step, 1955) — every one is text in a committed `loop.yaml`, or an explicit CLI argument |
| `verify()` override → `subprocess.run(cmd, shell=True, …)` | 1178 | `--cmd` / `RIG_LOOP_VERIFIER_CMD`, substituted with `{prompt_file}` and `{cwd}` |

The built-in verifier families take the other branch, `subprocess.run(argv, …)` (1184) —
argv, no shell.

Why not "fix" by removing `shell=True`: a gate harness that cannot run
`pytest -q && ./bin/x | tail -1` is not the product. Argv-only would forbid the
multi-command gates that specs in `capabilities/harnesses/` use, or force a hand-rolled
splitter — more code, same trust boundary, every spec rewritten.

**Named residual.** At 1178 the run-record `cwd` is interpolated into the override string
before the shell sees it, so a `cwd` containing `$(…)` executes. Same trust domain (whoever
sets `cwd` can execute anyway), and the override is opt-in per machine rather than default.
Flip condition: if `rig-loop` ever accepts specs or run records from an untrusted producer
(cross-machine dispatch of foreign `loop.yaml`), this stops being accepted risk — the fix
then is `shlex.split` + argv plus a spec-signature check, not an input filter.

**Not done here:** no `.snyk` ignore rules added. Suppressing these 19 would bury the two
lines that actually matter (142, 1178) under 17 duplicate rows.

## The "org UI toggle" — closed as refused, 2026-09-05

Checked what that setting actually is before touching anything:

| probe | result |
|---|---|
| `snyk --version` | 1.1307.0; scans work (OAuth in configstore, `api_token_length=0` — no REST token) |
| `snyk code test --org=rodgemd1 scripts/blob_license_ledger.py` | exit 0, valid SARIF (auth is live for scans) |
| `snyk projects` / `snyk orgs` | `Unknown command` — the CLI cannot enumerate org/project config in 1.1307 |
| REST `/rest/orgs` | unavailable without an API token, which is unset |
| browser relay | CDP `Network.enable` refused; org settings page not inspectable this session |
| artifact `.context/snyk-code-review.json` | `displayed_count: 149` of 272 is a CLI display grouping, not a setting |

Nothing on disk names an org toggle that would change these 26 findings, and the only bulk
org setting that would — issue ignores — is exactly what line 82 of this file refuses to do:

> **Not done here:** no `.snyk` ignore rules added. Suppressing these 19 would bury the two
> exec primitives.

So: no suppression, no Gate-D request for suppression. If a display/filter toggle is genuinely
wanted, name it (org → project → settings) and it gets a request with the setting and the value.
