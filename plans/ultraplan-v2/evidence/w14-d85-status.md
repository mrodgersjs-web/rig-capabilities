# D85 status — ultraplan-v2 (updated 2026-09-21, captain gate-approval session)

DONE (captain-approved, executed):
- register_process.py published `ultraplan-v2` into authority/registry.json
  with hash-bound source snapshots (ledger/commands/cell_runner/cli/subs),
  3 entrypoints, external binding rig_capabilities.ultra_cell:validate_tree.
- cell_runner module-level sys.path side-effect moved to lazy function
  (ultraplan c801a0e..latest) — one genuine grammar offense removed.
- registration grammar learned: SYM@FILE:OP entrypoints; external module =
  single identifier + dotted allowed_calls + PYTHONPATH resolution (3 refusal
  messages led to it).

BLOCKED — certification, quantified, NOT code debt:
- Fresh registration (current snapshot, post-fix source): inventory first
  refusal now runtime/cell_runner.py:12 `Attribute` — the chained
  Path(__file__).resolve().parent expression inside the lazy helper; function
  grammar is as closed as module grammar.
- D85 closed module grammar refuses, with line numbers, on all five staged
  files: even a plain module-level constant Assign (ledger.py:20,
  commands.py:18) and module-level Expr (cli.py:12) are
  SOURCE_UNSUPPORTED_GRAMMAR; calls with keyword arguments are banned outright
  (d85.py:251-253 "keyword arguments"). Ultraplan's command-authority table
  is a module-level dict; the ledger's policy kwargs (mission_id=,
  capture_output=, indent=) are pervasive (300+ sites).
- Conforming means rewriting a 680-times-audited product into a dialect that
  would degrade it (no keyword args, no constants, positional-only calls)
  and invalidating freshly accepted evidence. Not done.
- Prior finding still stands: open()/I/O families also blocked; that was
  strictly downstream of the module-grammar wall and is subsumed by it.

CAPTAIN DECISION (unchanged question, now fully evidenced):
 (a) amend d85.py module grammar to admit module constants + keyword calls
     (owner call: it is the governance tool, not the audited party), or
 (b) accept ultraplan-v2 as JEV-audited (0.85 bar, 680 rows) but D85-uncertified.
The process stays REGISTERED (registry + snapshot on disk prove it);
checklist/admit correctly refuse upstream of certification.
