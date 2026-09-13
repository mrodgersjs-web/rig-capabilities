# rig_capabilities_engine_v1 D85 chain receipts

Repo: /Users/rig128gb/Developer/rig-capabilities (branch master, HEAD d7d5743)
Run: 2026-09-12, by subagent D85Register.

Loader-environment pin (mandatory, identical for every command):
  export D8PIN=/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-lattice-system
  export PYTHONPATH="$D8PIN"

Why: the WIP loader fingerprint (d85.py `_external_module_locks`) hashes sys.path into every
external-module call op. `validate_lattice` (tool_selection.py) inserts the rig-lattice-system
path inside certify_build's inventory recomputation, so without the pin the classify/score
shape and the certify shape disagree and source_derived_d85 can never bind. With the pin set
identically on all commands, validate_lattice's insert is a dedup no-op and all five commands
share one inventory hash: 82d4cb9f34ed01cc6c44edb9a36541ab6679bb1a878a456bf4fcf6409e2135ad.
Defect reported to OwnerConsolidate (2026-09-12). If the fingerprint is later excluded from
the op hash, recompute all receipts without the pin.

Commands (each raw stdout+stderr captured to <verb>.json in this directory):

  PYTHONPATH="$D8PIN" ./capabilities/skills/rig-determinism-85/bin/rig-determinism-85 inventory rig_capabilities_engine_v1   # rc=0  -> inventory.json
  PYTHONPATH="$D8PIN" ./capabilities/skills/rig-determinism-85/bin/rig-determinism-85 classify  rig_capabilities_engine_v1   # rc=0  -> classify.json
  PYTHONPATH="$D8PIN" ./capabilities/skills/rig-determinism-85/bin/rig-determinism-85 score    rig_capabilities_engine_v1   # rc=0  -> score.json   REALIZED_PASS
  PYTHONPATH="$D8PIN" ./capabilities/skills/rig-determinism-85/bin/rig-determinism-85 checklist runs/agentic-stack-buildout/d85/build.json --process-id rig_capabilities_engine_v1 --root /Users/rig128gb/Developer/rig-capabilities   # rc=0 -> checklist.json  CHECKLIST_PASS, inventory_binding=bound
  PYTHONPATH="$D8PIN" ./capabilities/skills/rig-determinism-85/bin/rig-determinism-85 verify-cert runs/agentic-stack-buildout/d85/build.json runs/agentic-stack-buildout/d85/certificate.json --root /Users/rig128gb/Developer/rig-capabilities   # rc=0 -> verify-cert.json  CERTIFICATION_VERIFIED

certificate.json is the byte copy of the bound CHECKLIST_PASS stdout above;
build.json is the build record. verify-cert was re-run against later d85.py bytes
(caeecc3e1cdf3042…) after the chain and still returned CERTIFICATION_VERIFIED.

Authority-record bindings:
  process record:  authority/processes/rig_capabilities_engine_v1.process.json
  classification:  authority/processes/rig_capabilities_engine_v1.classification.json (bound to 82d4cb9f…)
  sources:         authority/sources/rig_capabilities_engine_v1/rig_engine_worker.py (e543907e…), rig_engine_adapter.py (088f7405…)
  registry:        authority/registry.json entry rig_capabilities_engine_v1 (grammar intact; existing entries undisturbed)

Estate note: estate-validate exits 2 on this tree with 450 problems, all from the concurrent
launchd-launcher-admission WIP (launcher_epoch / launcher-missing rows) and julie launchd-label
carrier facts — zero problems reference rig_capabilities_engine_v1, the process registry, or the
classification grammar. Receipt kept as estate-validate.json.
