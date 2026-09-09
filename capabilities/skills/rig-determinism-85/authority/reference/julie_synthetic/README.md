# Worked example: tool selection → certification → verification

Synthetic-only reference for the D85 tool-selection standard (v1.4.0). Every
*output* here was produced by the real CLI against this directory; the inputs
(`evidence.json`, `build.json`, `root/diagram.json`) are hand-authored
closed-schema records. Copy this shape; do not hand-edit the outputs.

## The flow (all through `bin/rig-determinism-85`)

```sh
# 1. Select: closed-schema evidence → one framework verdict.
select evidence.json                       # → select.json (framework: temporal)

# 2. Checklist + certification: build declares process_id and the
#    inventory_sha256 snapshot it was generated against; certification
#    recomputes the live inventory and binds only on exact equality.
checklist build.json --root root --process-id julie_synthetic
#                                           # → certificate.json (CHECKLIST_PASS, bound)

# 3. Verify: the consumer boundary. Recomputes the build digest, rejects
#    non-exact certificate schemas, rejects unbound/non-PASS certificates,
#    blocks post-cert mutation replays and tampered payloads, and
#    re-certifies against the live inventory.
verify-cert build.json certificate.json --root root
#                                           # → verify.json (CERTIFICATION_VERIFIED)
```

Certificates are root-portable: check details carry the declared
`archify_diagram_path`, so a certificate made under one root verifies under
any root containing an identical diagram (see
`test_certificate_portable_across_identical_roots`).

## Files

| file | produced by | meaning |
|---|---|---|
| `evidence.json` | hand-authored | closed-schema evidence record (clock-critical batch) |
| `select.json` | `select` | framework verdict + D85 obligations |
| `build.json` | hand-authored | 10-key closed-schema build; `inventory_sha256` from `inventory julie_synthetic` |
| `root/diagram.json` | hand-authored | archify lifecycle diagram the checklist resolves under `root` |
| `certificate.json` | `checklist --process-id` | bound CHECKLIST_PASS with `checklist_sha256` |
| `verify.json` | `verify-cert` | CERTIFICATION_VERIFIED at archive time |
| `score.json` | `score julie_synthetic` | process-level admission snapshot |

`certificate.json` is only valid while the live inventory hash equals the one
it names — rerun `verify-cert` before trusting an archived certificate.

## What blocks (see tests/test_tool_selection*.py)

- unbound checklist (no `--process-id`) — BLOCK
- declared hash ≠ live inventory — BLOCK (`binding: stale`)
- mutated build replayed against a saved PASS — BLOCK (digest mismatch)
- tampered certificate (`inventory_sha256`, `expected_framework`, `checks`) — BLOCK
- unknown/missing certificate fields — CERTIFICATION_MALFORMED
