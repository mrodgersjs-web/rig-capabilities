# D85 scope design

## Recorded routing before edits

The intent router initially returned L3-D2-A2-I1 with its default confidence of 0.62. Explicit engineering criteria were then supplied: failure_cost=0.5, reversibility=0.95, mechanism_clarity=0.95, level=L3. The canonical BMS scorer returned confidence=0.89, mode=A1, deterministic=true, model_in_decision_path=false. The resolved implementation coordinate is L3-D2-A1-I1. These criteria are engineering judgments, not measured production statistics.

## Decision

Separate ordinary operation from build certification at the existing function boundaries. `dispatch_hook` continues to enforce active-loop policy but does not consult the D85 production-root classifier. `certify_build` is the authoritative D85 build gate; `verify_certification` replays it against live source.

Alternative considered: introduce a runtime scope switch with build and legacy modes. Rejected because a switch adds another mutable default that can silently restore blanket blocking. Existing explicit admission and launcher APIs remain available without running them for every tool.

Alternative rejected: accumulate command-name exceptions. The earlier greeting-only exception exposed this design problem and does not solve ordinary work across the estate.

## Data model

A submitted build retains its source-inventory binding and adds a closed Lattice context. The canonical Lattice parser and BMS scorer validate the context. Certification records the live source-derived D85 score in its checks; a claimed pass is insufficient. Old build records without routing evidence require migration and recertification, not automatic approval.

## Principles applied

`principle-fix-root-causes` changes the policy boundary instead of adding more command exceptions. `principle-model-the-domain` represents a build's routing evidence explicitly instead of inferring whether arbitrary shell commands are applications.

## Limit

Passing the pre-tool hook never means an app is certified. Certification is enforced at the explicit D85 build boundary. Build workflows must invoke checklist/verify-cert and preserve their evidence; this change does not claim to detect every app build from arbitrary shell text.

## Placement

The required rig-repo-guard command was attempted and rejected by the existing D85 hook. Read-only recovery confirmed the registry's exact canonical rig-capabilities root with write_enabled=true and write_mode=code. No blocked executable was invoked through another path. Ordinary edits remain subject to the active tool gate.
