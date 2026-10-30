# Skill and agent quality program

Status: active. The estate is not certified.

## Done condition

Every retained, loadable skill and agent in the configured Codex, Claude,
Hermes, OMP, Prime Agent, Aside, and shared-agent roots has a canonical owner,
a valid client-specific load path, and independently verified held-out task
outcomes above 0.90. Each asset has at least 30 source-bound cases with
representative, non-trigger, and adversarial coverage. No hard-block case may
fail. All configured install roots have zero broken links and zero unexplained
canonical byte drift. Prompt and subskill coverage uses the same outcome rule.
The weekly job detects regression but cannot promote or delete an asset.

An installed file, a declared `quality_floor`, a Jev confidence, and a green
router fixture do not satisfy this condition.

## Baseline and scope

- At the 2026-09-24 16:15 UTC snapshot,
  `python3 scripts/audit_skill_agent_quality.py --summary` scanned 219
  top-level skills, 23 agents, and one nested subskill. None had verified
  outcome evidence. Source inventory can change during this program.
- `python3 scripts/audit_installed_skill_agent_estate.py --summary` scans the
  12 configured top-level install roots. It currently finds 5,734 entries,
  400 broken links, 157 canonical byte drifts, and 4,605 noncanonical entries.
  The 4,804 physical sources and 3,774 distinct file hashes are not quality
  scores. The one nested `SKILL.md` is counted in the source-quality audit but
  its ownership/load intent and actual client loading need separate checks.
- A 4-case offline Promptfoo router run passes its own routing assertions but
  fails the asset-outcome screen. Jev's `ultra.proof` rubric is advisory while
  calibration is stale. Per-signal calibration now refuses whole-decision labels
  for multi-signal rubrics, but local callers can still self-assert a `human`
  label. Authenticate human review before treating such labels as ground truth.

## Sequence

1. Keep the source and installed inventories reproducible. Record canonical
   owners, aliases, format variants, broken targets, and byte drift. Review
   each repair target before changing an install. Use recoverable backups.
2. Decide which noncanonical assets remain loadable. Resolve their source
   owner and permissions. Do not delete an entry because names or hashes match.
   Keep an explicit retained, retired, or unresolved ledger.
3. Make each retained skill and agent specification loadable. Migrate RIG
   quality fields without breaking the catalog and done-test consumers.
   Validate the real client path, not only YAML syntax.
4. Build held-out fixtures for each retained asset. Run actual agent or skill
   behavior through Promptfoo or a source-bound equivalent. Record traces,
   negative cases, model and prompt versions, and runtime cost. Use the
   independent verifier to inspect artifacts and source bindings.
5. Calibrate Jev rubrics on labeled cases. Use Jev for bounded semantic
   triage and evidence mismatch. Code owns thresholds and hard blocks. Label
   each question's ground truth separately on multi-question rubrics. The
   current `ultra.proof` corpus has zero eligible signal-scoped labels after
   removing whole-decision label contamination; keep it advisory until each
   rule has at least 30 reviewed labels, train/holdout checks pass, and an
   independent reviewer checks the corpus.
6. Test Codex, OMP, Prime Agent, Aside, Claude, and Hermes separately. Prove
   skill and agent selection, Memory OS retrieval, tool boundaries, behavior,
   and failure handling from each client. Promote only the asset versions
   that pass every relevant gate.
7. Keep the weekly review active. Compare the new inventory and outcome
   evidence with the previous week. Stage changes for review. Never turn a
   scheduled audit into automatic promotion, deletion, or outward action.

The first three installed-pack repairs this run were bounded. The canonical
meta-skill matched all seven configured skill roots after installation.
`caveman` matched its three existing roots, and `jev-system1-cascade` matched
its five existing roots. These are distribution checks, not outcome tests.
The central `skill-upgrades` pack now also matches all seven configured roots,
but has no held-out outcome score. Its old file-presence completion rule was
replaced with a runnable regression command and explicit source-bound outcome
and independent-verifier requirements. The done-test runner refuses a cached
source hash after an asset changes. Keep source index freshness visible; do not
read a green cached test as a quality verdict.
The canonical `/skill-upgrades` command now delegates to that pack. Five
configured command copies match; OMP shares Claude's command root. The runner
also blocks noncanonical executable checks, nonaffirmative MCP replies, and
skipped criteria. The existing whole-repo done-test gate remains red and must
be repaired asset by asset, not suppressed.

Read-only provenance triage found zero safe canonical targets for the 400
broken symlinks. Forty-two broken names have a live noncanonical same-ID copy
elsewhere, but no canonical ownership or outcome evidence. Queue all 400 for
source-backed intake or explicit lifecycle disposition, not automatic relinking
or deletion.
