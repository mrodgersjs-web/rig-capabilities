## 4. ARTIFACT AND ADVERSARIAL VERIFICATION

Your answer is captured to **`/tmp/fable-2031-result.json`** — that file is the authoritative
artifact of this session (its `modelUsage` must name `claude-fable-5-1`; `total_cost_usd` is
recorded against the approved cap; it is sha256'd and sealed as a ProofPacket).

Afterwards a **different-family, adversarial verifier (never Fable)** will:

- **re-open every S7 `path:line` and match the quoted text — one miss rejects that row**;
- schema-validate every S2 row through `register.validate_row`;
- treat **any row traceable to a truncated region, or citing content absent from disk, as
  `FABRICATED`**;
- confirm no file in the repo worktree, in `/Users/rig128gb/Downloads`, or in
  `~/.hermes/skills/tac-pan` changed during the session window.

Write so that survives: read before you cite, quote what you read, and where the record stops, say
out loud that the record stops. End your own answer with the terminal marker on a line of its own:

`FABLE2031-END`
