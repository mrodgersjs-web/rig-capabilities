#!/usr/bin/env python3
"""Gate for the Doer/Checker/VALIDATOR output contract (`rig.verifier.v1`).

Why this is a script and not frontmatter: `catalog._pick_main_text` reads only
HEAD_BYTES (4096). A `done_when` program longer than that is parsed from a
truncated buffer, `_quality_block` returns {}, and the contract becomes
INVISIBLE — `test` answers pass=false with zero results, which is worse than
red because nothing looks broken. This file is the durable copy of the
programs; the loop's `cmd:` lines are one line each. This checker therefore
checks its own host asset for that failure, using the loader's own code path.

Modes
    check <doc>            validate the contract as written         exit 0 / 2
    plant <doc> <name>     validate a MUTATED copy held in memory    exit 2 / 0
    report <file|->        validate one produced VerifierReport      exit 0 / 2
    self-test [doc]        mutate the doc + judge 2 clean + 9 planted exit 0 / 2

`plant` exit codes are the loop's, not a report card: 2 means the mutation was
CAUGHT (the checker works), 0 means it ESCAPED — and the loop's
`test $rc -eq 2` goes red on an escaped plant.

The fixture names its own copy of the contract (SLOTS/LABELS below). Deliberate:
a checker that read the document's declaration and asked "is the declaration
satisfied by the declaration" could be satisfied by deleting the declaration.

STDLIB ONLY. Exit 0 = clean, 2 = a rule fired.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# The contract this fixture owns. Changing the contract means changing it HERE
# and in the document; the document cannot satisfy the gate by editing itself.
SLOTS = (
    "verdict", "evidence_refs", "bears_on", "findings", "target", "action",
    "patch_delta", "diagnosed_reason", "independence", "validator_model_family",
    "doer_model_family", "evidence_route", "attempts_declared",
    "attempts_executed", "environment", "what_would_change_verdict",
    "confidence", "confidence_basis",
)
LABELS = ("resolved", "target-missed", "regression", "noisy-patch",
          "evaluator-gap", "new-action")
DECL = {"slots": "#contract-slots:", "labels": "#contract-labels:",
        "negative": "#contract-negative:"}
MARKER = "NOT-A-VERDICT"
QUAL_FIELDS = ("outcome", "done_when", "great_example", "quality_floor")
DEFAULT_DOC = "capabilities/loops/doer-checker-validator.md"


# -- host-asset visibility ---------------------------------------------------

def visibility(path: Path) -> list:
    """Reasons this asset's own gates cannot be LOADED (empty = they load).

    Uses the loader's own code path, not a copy of it: `_pick_main_text` is the
    truncation being tested, so re-implementing it here would certify the bug.
    Run as a script, sys.path[0] is this directory and carries no package, so the
    repo root is inserted first — the same bootstrap `scripts/frontmatter_visibility.py`
    uses to reach the loader.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    try:
        from rig_capabilities import catalog
    except ImportError:
        return ["catalog_unimportable"]
    raw = path.read_text(encoding="utf-8", errors="replace")
    if not raw.startswith("---"):
        return []                               # no fence: nothing to truncate
    end = raw.find("\n---", 3)
    if end < 0:
        return ["frontmatter_unterminated"]
    loaded = catalog._quality_block(catalog._pick_main_text(path))
    return [f + "@unloadable" for f in QUAL_FIELDS
            if f in raw[:end] and not loaded.get(f)]


# -- document rules ----------------------------------------------------------

def _pipe_list(rows: list) -> str:
    if not rows or ":" not in rows[0]:
        return ""
    return rows[0].split(":", 1)[1].strip()


def check_contract(doc: str, host: str | None = None) -> list:
    """Reasons the contract as written is unsatisfied. Empty = the gate holds."""
    missing: list = []
    L = doc.splitlines()
    decl = {k: [l for l in L if l.startswith(v)] for k, v in DECL.items()}
    for key, rows in decl.items():
        if not rows:
            missing.append(f"{key}@declaration")
    declared_slots = _pipe_list(decl["slots"]).split("|")
    declared_labels = _pipe_list(decl["labels"]).split("|")
    missing += [f"{s}@declared" for s in SLOTS if s not in declared_slots]
    missing += [f"{lab}@declared" for lab in LABELS if lab not in declared_labels]
    # every slot must ALSO be a key in the packet schema the loop parses, and
    # every label must have a router row carrying a consumer
    schema_keys = {l.strip().strip('"').split('"')[0] for l in L
                   if l.lstrip().startswith('"')}
    missing += [f"{s}@schema" for s in SLOTS if s not in schema_keys]
    # each label's OWN router row (the row that begins with that label) must carry a
    # consumer. Rows that merely mention a label — the legacy map, the precedence
    # note — are not its router and must not satisfy or break this rule.
    for lab in LABELS:
        own = [l for l in L if l.startswith(f"| `{lab}`")]
        if not own or not any("route:" in r for r in own):
            missing.append(f"{lab}@route")
    # the law must be STATED, on a line that starts with the marker
    if not any(l.startswith(MARKER) for l in L):
        missing.append(f"{MARKER}@rule")
    if host:
        missing += visibility(Path(host))
    return missing


# -- report rules ------------------------------------------------------------

def check_report(r: dict) -> list:
    """Reasons one validator response is NOT A VERDICT. Empty = it counts."""
    bad = []
    if r.get("verdict") not in LABELS:
        bad.append("outcome_label_outside_vocabulary")
    refs = r.get("evidence_refs") or []
    if not refs or not all(bool(e.get("ref")) and bool(e.get("bears_on"))
                           for e in refs):
        bad.append("claim_with_no_evidence")
    if not all(f.get("target") and f.get("action") and f.get("patch_delta")
               and f.get("diagnosed_reason") and f.get("route")
               for f in (r.get("findings") or [])):
        bad.append("unroutable_finding_tuple")
    if not (r.get("validator_model_family") and r.get("doer_model_family")):
        bad.append("model_family_absent")
    if r.get("validator_model_family") == r.get("doer_model_family"):
        bad.append("same_family_collusion")
    if not (r.get("attempts_executed", 0) >= r.get("attempts_declared", 0) >= 3):
        bad.append("attempts_below_declared_k")
    if not r.get("environment"):
        bad.append("environment_unrecorded")
    if not (r.get("what_would_change_verdict") and r.get("confidence_basis")
            and r.get("confidence") is not None):
        bad.append("incomplete_not_a_verdict")
    return bad


def _ref(ref: str, claim: str) -> dict:
    return {"ref": ref, "bears_on": claim}


CLEAN = [
    {"verdict": "resolved", "findings": [],
     "evidence_refs": [_ref("gate.log#L41",
                            "Doer claim that parse() refuses empty keys")],
     "validator_model_family": "kimi", "doer_model_family": "glm",
     "attempts_declared": 3, "attempts_executed": 5,
     "environment": {"temperature": 0.0},
     "what_would_change_verdict": "a clean rerun green at parent AND here makes it target-missed",
     "confidence": 0.8, "confidence_basis": "5 of 5 attempts agreed; deterministic exit code"},
    {"verdict": "regression",
     "findings": [{"target": "parser.py", "action": "modify",
                   "patch_delta": "-1 guard removed",
                   "diagnosed_reason": "test green at parent", "route": "doer"}],
     "evidence_refs": [_ref("gate.log#L9", "Doer claim that the suite is green")],
     "validator_model_family": "claude", "doer_model_family": "gpt",
     "attempts_declared": 3, "attempts_executed": 4,
     "environment": {"temperature": 0.2},
     "what_would_change_verdict": "green at the parent too means target-missed",
     "confidence": 0.9, "confidence_basis": "4 of 4 reproduced"},
]

# name -> (patch on CLEAN[0], the ONE reason it must be refused for)
PLANTED = {
    "looks_good": ({"verdict": "looks_good"}, "outcome_label_outside_vocabulary"),
    "evidence_no_claim": ({"evidence_refs": [{"ref": "gate.log#L41"}]},
                          "claim_with_no_evidence"),
    "no_evidence": ({"evidence_refs": []}, "claim_with_no_evidence"),
    "tuple_no_patch_delta": ({"findings": [{"target": "parser.py", "action": "modify"}]},
                             "unroutable_finding_tuple"),
    "family_absent": ({"validator_model_family": ""}, "model_family_absent"),
    "same_family": ({"doer_model_family": "kimi"}, "same_family_collusion"),
    "single_run": ({"attempts_executed": 1}, "attempts_below_declared_k"),
    "no_environment": ({"environment": {}}, "environment_unrecorded"),
    "no_falsifier": ({"what_would_change_verdict": ""}, "incomplete_not_a_verdict"),
    "confidence_no_basis": ({"confidence_basis": ""}, "incomplete_not_a_verdict"),
}

# name -> line deletion/rewrite on the document; each must be CAUGHT
DOC_PLANTS = {
    "schema_key": lambda s: [l for l in s if '"what_would_change_verdict":' not in l],
    "router_row": lambda s: [l for l in s if not l.startswith("| `evaluator-gap`")],
    "law_line": lambda s: [l for l in s if not l.startswith(MARKER)],
    "marker_renamed": lambda s: [l.replace(MARKER, "NOT_A_VERDICT") for l in s],
    "slots_declaration": lambda s: [l for l in s if not l.startswith(DECL["slots"])],
    "labels_declaration": lambda s: [l for l in s if not l.startswith(DECL["labels"])],
    "negative_declaration": lambda s: [l for l in s if not l.startswith(DECL["negative"])],
    "route_consumers": lambda s: [l.replace("route:", "r0ute:") for l in s],
}


def mutate(lines: list, name: str) -> list:
    fn = DOC_PLANTS.get(name)
    if fn is None:
        raise KeyError(name)
    return fn(lines)


# -- self-test ---------------------------------------------------------------

# The plant tables are part of the contract: a self-test that iterates whatever
# happens to be in them would "pass" forever once they were emptied.
EXPECT = {"clean_reports": 2, "doc_plants": 8, "report_plants": 10}


def self_test(doc: str, host: str | None = None) -> int:
    """Counts, the clean case, and every plant — or this returns 2."""
    fails = []
    counts = {"clean_reports": len(CLEAN), "doc_plants": len(DOC_PLANTS),
              "report_plants": len(PLANTED)}
    for k, want in EXPECT.items():
        if counts[k] != want:
            fails.append(f"{k}_expected_{want}_got_{counts[k]}")
    clean = check_contract(doc, host)
    if clean:
        fails.append(f"clean_document_reports:{clean}")
    for name in sorted(DOC_PLANTS):
        if not check_contract("\n".join(mutate(_lines(doc), name)), host):
            fails.append(f"doc_plant_escaped:{name}")
    for i, rep in enumerate(CLEAN):
        if check_report(rep):
            fails.append(f"clean_report_rejected:{i}:{check_report(rep)}")
    for name, (patch, reason) in sorted(PLANTED.items()):
        bad = check_report(dict(CLEAN[0], **patch))
        if bad != [reason]:
            fails.append(f"report_plant:{name}:{bad}")
    print("self_test fails:", fails)
    print(f"doc_plants={counts['doc_plants']} report_plants={counts['report_plants']} "
          f"clean_reports={counts['clean_reports']}")
    return 2 if fails else 0


def _lines(doc: str) -> list:
    return doc.splitlines()


# -- cli ---------------------------------------------------------------------

def main(argv: list) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    mode = argv[1]
    if mode == "self-test":
        host = argv[2] if len(argv) > 2 else DEFAULT_DOC
        return self_test(Path(host).read_text(), host)
    if mode == "report":
        src = sys.stdin.read() if argv[2] == "-" else Path(argv[2]).read_text()
        try:
            rep = json.loads(src)
        except json.JSONDecodeError as exc:
            print(f"report_unparseable: {exc}")
            return 2
        bad = check_report(rep)
        print("not_a_verdict:", bad)
        return 2 if bad else 0
    if mode in ("check", "plant"):
        host = argv[2]
        doc = Path(host).read_text()
        if mode == "check":
            missing = check_contract(doc, host)
            print("verifier-contract missing:", missing)
            return 2 if missing else 0
        try:
            mutated = mutate(_lines(doc), argv[3])
        except (KeyError, IndexError):
            print(f"unknown plant; known: {', '.join(sorted(DOC_PLANTS))}")
            return 2
        # a plant mutates only the contract surface, so any visibility failure
        # it reports is the host asset's real state, not the mutation's doing
        missing = [m for m in check_contract("\n".join(mutated)) if not m.endswith("@unloadable")] \
            + visibility(Path(host))
        print(f"plant {argv[3]} -> verifier-contract missing:", missing)
        return 2 if missing else 0
    print(f"unknown mode: {mode}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
