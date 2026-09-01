---
name: capabilities-done-test
description: Run one asset's executable done_when contract (cmd/file/grep forms) and report pass/fail with the exact failing check — no adjective without the command.
argument-hint: "<asset-id>"
allowed-tools: Read, Bash
category: meta
outcome: "meta: done means every runnable check exited 0, quoted — unrunnable is stated, never counted as green"
done_when:
  - file:capabilities/commands/capabilities-done-test.md
  - file:examples/great/meta/capabilities-done-test.md
  - grep:capabilities/commands/capabilities-done-test.md:The grep target must live OUTSIDE
great_example: examples/great/meta/capabilities-done-test.md
acl: public
quality_floor: 0.7
---

# capabilities-done-test

1. Resolve `<asset-id>` via the index (canonical wins; note the source actually run).
2. Run `./bin/rig-capabilities test <asset-id>` — every cmd/file/grep check executes; mcp: entries are reported as contract lines, marked unrunnable unless an executor is wired.
3. Report per-check: form, ok, detail. A pass claim without the per-check table did not happen.
4. If done_when is missing entirely, the asset is `uncontracted` — that is a gap to round-fix, not a pass.

The grep target must live OUTSIDE the asset's own frontmatter — a done_when that greps for its own text is tautology (found by plant-failure, V22).
