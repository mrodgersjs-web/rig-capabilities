# D85 build scope

Mike's 2026-09-11 clarification makes D85 a solution and application build certification gate. Ordinary startup, research, diagnostics, memory capture, file access, and authorized edits do not require D85 admission. Independent approval and active-loop controls still apply.

The former shared pre-tool interception blocked useful work before there was a build to evaluate. It has been removed from `dispatch_hook`. Explicit legacy admission and sandbox launcher commands remain available for their deliberate consumers.

D85 remains active during ordinary work through session and turn advisories. A RED advisory tells the agent what to repair but does not deny tools. The agent continues, fixes reachable findings, and reports applied changes plus any remaining certification gaps. Only explicit build certification can withhold a certified completion claim; Gate-D independently blocks an unapproved outward action.

For a solution or app, use the normal IQRSQPI build loop and append this gate to its final stage:

```yaml
gate:
  - type: d85_certified
    root: .
    build: build.json
    certificate: certificate.json
```

Paths resolve against the loop workspace. Keep the existing stage gates. Certification requires current registered source inventory, all four authoritative deterministic ratios at least 0.85, and validated lattice/BMS context. The legacy `d85_realized_pass` claim is insufficient. Start with A1; higher-mode certification is blocked until a trusted A1 execution-receipt verifier is available. A recorded command, output, and hash are reference data, not execution proof. Ordinary work remains available.

Create the certificate with the canonical `rig-determinism-85 checklist` command and replay it with `verify-cert`. See `authority/reference/julie_synthetic/build.json` for the updated input shape. That synthetic reference is a fixture, not certification of another application. Source changes require fresh certification. Declared D85 gates are rechecked at final completion and sealing; `--force` cannot override failure.

Build scope is explicit. Existing generic loops are unchanged; this does not automatically classify arbitrary shell commands or certify applications whose build loops omit the gate. Unknown or unregistered process scores cannot pass certification. Failed certification leaves repair work available.

## Lattice audit limitation

This repair records coordinate `L3-D2-A1-I1` and recomputed BMS confidence 0.89. The full text audit of the design returned `HARD_BLOCK`, despite CLI exit code zero. Its sales-document rubric demands dollar counts, refund commitments, buyer metrics, and commercial proof statements that this engineering design cannot honestly supply. The raw result remains at `capabilities/skills/rig-lattice-system/runs/d85-build-scope-audit.json`. No full lattice-audit pass or estate-wide D85 certification is claimed. Routing and build-input validation are separately tested.

## Recovery

Restart an already-running harness if it caches the Python hook module or previously loaded policy. New hook processes read the corrected source. If OMP still reports `uv_cwd`, leave and re-enter the working directory from the affected terminal; that filesystem error is separate from D85 admission.
