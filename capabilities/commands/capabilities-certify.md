---
name: capabilities-certify
description: Run the deterministic certification gates over the capability estate — with --plant proving each gate fires — and refuse promotion of any candidate that has not cleared a held-out non-regression check with a declared cost envelope.
argument-hint: "[plant]"
allowed-tools: Read, Bash
category: meta
outcome: "meta: a green certification is earned, never assumed — every gate must be able to go RED, and no candidate is promoted on the seen set alone"
done_when:
  - file:capabilities/commands/capabilities-certify.md
  - file:examples/great/meta/capabilities-certify.md
  - file:scripts/held_out_nonregression.py
  - grep:capabilities/commands/capabilities-certify.md:No LLM participates in certification
  - cmd:python3 scripts/held_out_nonregression.py check examples/fixtures/held-out/good; test $? -eq 0
  - cmd:python3 scripts/held_out_nonregression.py check examples/fixtures/held-out/heldout_regression; rc=$?; test $rc -eq 1
  - cmd:python3 scripts/held_out_nonregression.py check examples/fixtures/held-out/seen_only; rc=$?; test $rc -eq 1
  - cmd:python3 scripts/held_out_nonregression.py check examples/fixtures/held-out/missing_budget; rc=$?; test $rc -eq 1
  - cmd:python3 scripts/held_out_nonregression.py check examples/fixtures/held-out/hidden_negative; rc=$?; test $rc -eq 1
  - cmd:python3 scripts/held_out_nonregression.py check examples/fixtures/held-out/cost_overrun; rc=$?; test $rc -eq 1
  - cmd:python3 scripts/held_out_nonregression.py selftest; test $? -eq 0
great_example: examples/great/meta/capabilities-certify.md
acl: public
quality_floor: 0.7
---

# capabilities-certify

What `certify` is today (read `rig_capabilities/certify.py`; re-read it before
trusting this paragraph — the gate list grows): the `capabilities_certify`
handler runs its `GATES` table unconditionally — as of this writing twelve:
`suite`, `index_fresh`, `done_tests`, `idp_integrity`, `acl_jake`, `register`,
`corpus_refusal`, `canary_detection`, `lease_exclusivity`, `fable_dormant`,
`stage_order`, `evidence_ledger` — and `plant: true` replants all of them
every run, writing the seal under `.context/certify/`. Every one of those
gates scores the estate on the tasks the estate was written against. That is
the hole this command's second half closes: **a candidate (a round contract
edit, a forged harness, any upgrade being promoted) can only replace the
incumbent if it beats the incumbent on the seen split AND does not degrade a
held-out set it was not written against** — the unseen tasks are chosen, not
consulted, while producing the candidate (mechanism derived from arXiv:2608.13560
AutoDesign's acceptance gate and arXiv:2608.20169 Task-CoEvolve's moving
validation set; Discover-AI videos LEsKxMfRFjA, MvI17TNFW9c).

## Procedure

1. Call `capabilities_certify` with `{}` for the live gate matrix. Quote the
   artifact path written under `.context/certify/` — the seal references it,
   not this conversation.
2. With the word `plant` in args, call it with `{plant: true}`: copies the
   repo, breaks exactly what each gate guards, and demands RED — restore —
   GREEN for every gate. A gate that stays green while planted is a bug in
   the gate: file it before anything built on that gate is trusted.
3. **Held-out non-regression precedes any promotion.** Assemble the
   candidate's promotion-record directory — `baseline.jsonl`,
   `candidate.jsonl`, `held_out.json`, optional `history.jsonl` and
   `record.json`, format in the header of `scripts/held_out_nonregression.py`
   — where `held_out.json` names the task ids the candidate was NOT produced
   against, and run:

   ```bash
   python3 scripts/held_out_nonregression.py check <case-dir>
   ```

   Exit 0 promotes only when all of: the candidate strictly beats the
   incumbent on the train split; **zero previously-passing cases regress**
   (each one is named, whichever split it lives on); the held-out pass-rate
   does not fall by more than the noise band `max(0.02, 2 × robust σ)` over
   the sealed held-out rates in `history.jsonl` (RobustMADZ scale,
   1.4826 × MAD — the estate's existing movement-scoring primitive, applied
   to the right subsystem); the candidate record still carries every task the
   baseline recorded (a retained negative stays visible — deleting it from
   the ledger hides damage, it does not fix it); and the promotion record
   declares a cost envelope (tool calls, wall-clock, spend) next to the
   quality floor, which the candidate's summed cost stays inside.
   Exit 1 refuses and names every violated rule — fix or drop the candidate,
   never edit the baseline to erase the refusal.
4. The fixture estate under `examples/fixtures/held-out/` is the permanent
   plant-failure set: any edit to the checker must keep `good` at 0,
   `heldout_regression` (train +25 pts, held-out −37.5 pts — the overfitting
   mutation) at 1 naming `h1`, `seen_only` (no held-out declared: promotion
   decided on the seen set alone — the RED this gate exists to catch) at 1,
   `missing_budget`, `hidden_negative`, and `cost_overrun` at 1, and
   `selftest` (every case decides exactly as its `expect.json` declares) at 0:

   ```bash
   python3 scripts/held_out_nonregression.py selftest   # exit 0 or the checker is broken
   ```

5. Taste carries Gate-D, not each artifact: a candidate that changes a
   declared taste/brand/tokens rule needs a typed `APPROVE <run_id>` before
   promotion regardless of scores; a candidate that only tightens a failing
   validator may promote on a green checker. Where mechanical checks cannot
   arbitrate quality, run a blind paired comparison against the incumbent and
   quote the win-rate — never a self-scored rubric.

No LLM participates in certification. If a gate needs judgment, it is the
wrong gate.
