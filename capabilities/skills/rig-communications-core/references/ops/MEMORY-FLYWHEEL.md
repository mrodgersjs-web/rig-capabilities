# Memory Flywheel (v16)

## Lanes
- **ships → exemplars**: a shipped artifact is promoted to `data/comms/exemplars/`
  only when its outcome is measured (scoreboard OK / prediction resolved). Copy, plus
  the ship packet's sha256 + outcome row. Taste never promotes anything.
- **red gates → rejected-patterns**: `data/comms/rejected-patterns/` mirrors the
  deterministic blockers (voice.py, gates.py, baselines.json). Files follow code, never
  the reverse.
- **artifacts → GBrain**: writing-craft corpus mirrors at `~/.rig/sources/writing-craft`
  (git + `gbrain sync`, commits `--no-verify`, global git_guard blocks unregistered repos).
  Comms artifacts join the same source, scoped `comms`. Ollama embeds: BLOCKED until
  `ollama serve` is back (currently not listening) — stale embeds age, they don't hide.
- **artifacts → Obsidian**: JakeStudio index note per surface family; human-readable
  entry points, generated mirror, non-authoritative.

## Pruning policy
- exemplar: demote when a later measurement contradicts the outcome that promoted it (append a
  DEMOTED line; never delete — history is the asset).
- rejected-pattern entry: candidate for removal when its gate has not fired for 90 days AND the
  gate itself is retired in code. File follows code.
- corpus transcript: remove on `errors.jsonl` provenance failure (video private/deleted) —
  manifest row keeps a TOMBSTONE with the reason.
- Nothing in the private lane (love-notes, PRIVATE-james) ever enters any flywheel lane.
