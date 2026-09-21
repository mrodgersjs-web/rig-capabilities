# `role:"default"` model_change overrides CLI/scope model selection ~1.3s after start

**Version:** omp v18.1.17 (also saw update banner 18.2.2) · macOS (Darwin 25.5.0, arm64)

## Summary

For every fresh session in the affected cwd, the first model_change (from `--model`, `--config` overlay, or first-scoped model) is correct, then ~1.3 seconds later a second `model_change` with `"role":"default"` silently replaces it with a stale provider/model. The override ignores `modelRoles.default` in `config.yml`, `--model`, `--config` overlays (both `modelRoles` and `enabledModels`), and `disabledProviders`. When the stale default is an exhausted OAuth provider, every first turn dies with `usage_limit_reached` and no selector combination in the CLI recovers it.

## Repro (deterministic across 9 launches)

```sh
env -u ORCA_PANE_KEY omp --config /tmp/overlay.yml --print "What is 2+2?"
# /tmp/overlay.yml:
#   enabledModels:
#     - blackwell-qwen38-flash/blackwell-qwen38-flash
```

Session jsonl shows:

```json
{"type":"model_change","timestamp":"...370Z","model":"blackwell-qwen38-flash/blackwell-qwen38-flash","resolvedModelIsFallback":false}
{"type":"model_change","timestamp":"...925Z","model":"openai-codex/gpt-5.6-sol","role":"default","resolvedModelIsFallback":false}
```

…then the turn executes on the role-default model (`provider: openai-codex`, `stopReason: error`, `usage: 0`, `usage_limit_reached`).

## Observed vs expected

- `modelRoles.default` (config.yml, restored flat) is not what gets applied — the applied value matches `model_usage.last_used_at` recency (the failing provider refreshes recency even on `usage_limit_reached` attempts, so it is self-locking).
- `disabledProviders: [openai-codex]` via `--config` overlay does not block the re-application.
- A failed attempt refreshing `model_usage` turns a temporary provider quota outage into a persistent per-directory default lock until manual DB surgery.
- Resume (`--resume <id>`) restores the session and re-applies the same role default; a session whose last model was the exhausted provider is bricked for first turns.

## Asks

1. Failed `usage_limit_reached` attempts must not refresh `model_usage` recency (or role-default resolution must ignore models whose provider is erroring).
2. Document the precedence actually implemented for `role:"default"` re-application vs `--model` / `--config` overlays / `enabledModels` scope — docs (`models.md` "Initial model selection priority") do not match observed behavior.
3. Consider honoring `disabledProviders` at role-resolution time, not only at listing time.

## Workaround used

Resume a session that already contains a persisted non-empty assistant message; the downstream logic still sees real transcript text despite the first turn erroring.
