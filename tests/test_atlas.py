"""B1 Atlas tests: happy path plus the two planted owner-invariant failures.

Fixture-only, stdlib-only, no subprocess: runs inside `certify`'s copied tree.
"""
from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import atlas

REQUEST = ("one approved candidate becomes a verified artifact "
           "inside declared boundaries")

REGISTER_HEADER = ["id", "name", "maturity_M0_5", "enables_product_classes",
                   "blocking_deps"]
REGISTER_ROWS = [
    ["proofchain_roadmap_verification",
     "ROADMAP packet prefixes verified against sealed proof", "2",
     '["impossible_state_contract","independent_verification"]',
     '["certify_plant_failure_gates"]'],
    ["harness_goal_spec_compiler",
     "Harness YAML to compiled goal-spec pipeline", "2",
     '["company_os_factory","session_harness"]', "[]"],
]

OWNERS_HEADER = ["state_decision", "plane", "authority_class",
                 "authoritative_owner", "evidence_path"]
OWNERS_ROWS = [
    ["approved_candidate", "Pantheon", "workflow durability",
     "pantheon-conductor", "PLAN-SOURCE.md"],
    ["verified_artifact", "CellFoundry", "domain operations",
     "cellfoundry-tier1", "PLAN-SOURCE.md"],
    ["declared_boundaries", "Agent CP Retrofit", "constitution/policy",
     "agent-cp-retrofit", "PLAN-SOURCE.md"],
]


def _write_csv(path: Path, header: list, rows: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _repo(owners_rows) -> Path:
    root = Path(tempfile.mkdtemp(prefix="atlas-test-"))
    _write_csv(root / "capability_register.csv", REGISTER_HEADER, REGISTER_ROWS)
    _write_csv(root / "owners.csv", OWNERS_HEADER, owners_rows)
    return root


class TestAtlasResolve(unittest.TestCase):
    def test_happy_path_three_non_empty_keys(self):
        root = _repo(OWNERS_ROWS)
        out = atlas.resolve(root, REQUEST, owners_csv=root / "owners.csv")
        self.assertTrue(out["existing_primitives"])
        self.assertTrue(out["missing_primitives"])
        self.assertTrue(out["named_state_owners"])
        # every existing primitive cites a real register id
        reg_ids = {r[0] for r in REGISTER_ROWS}
        for prim in out["existing_primitives"]:
            self.assertIn(prim["id"], reg_ids)
        # the verified-proof row matches the request's "verified" token
        self.assertIn("proofchain_roadmap_verification",
                      {p["id"] for p in out["existing_primitives"]})
        # every touched state carries exactly one authoritative owner
        states = {o["state_decision"]: o for o in out["named_state_owners"]}
        self.assertEqual({"approved_candidate", "verified_artifact",
                          "declared_boundaries"}, set(states))
        for owner in states.values():
            self.assertTrue(owner["authoritative_owner"])
            self.assertNotEqual(owner["authoritative_owner"], "claimant")

    def test_planted_dual_owner_conflicts(self):
        rows = OWNERS_ROWS + [["approved_candidate", "Fleet CP",
                               "infrastructure lifecycle",
                               "fleet-cp-24x7", "PLAN-SOURCE.md"]]
        root = _repo(rows)
        with self.assertRaises(atlas.AtlasConflict) as ctx:
            atlas.resolve(root, REQUEST, owners_csv=root / "owners.csv")
        packets = ctx.exception.packets
        self.assertEqual(1, len(packets))
        pkt = packets[0]
        self.assertEqual("dual_owner", pkt["kind"])
        self.assertEqual("approved_candidate", pkt["state_decision"])
        # both claimants named, no silent pick
        self.assertIn("Pantheon (pantheon-conductor)", pkt["claimants"])
        self.assertIn("Fleet CP (fleet-cp-24x7)", pkt["claimants"])

    def test_planted_zero_owner_conflicts(self):
        rows = [r for r in OWNERS_ROWS if r[0] != "verified_artifact"]
        rows.append(["verified_artifact", "Paddock", "domain operations",
                     "claimant", "PLAN-SOURCE.md"])
        root = _repo(rows)
        with self.assertRaises(atlas.AtlasConflict) as ctx:
            atlas.resolve(root, REQUEST, owners_csv=root / "owners.csv")
        pkt = ctx.exception.packets[0]
        self.assertEqual("zero_owner", pkt["kind"])
        self.assertEqual("verified_artifact", pkt["state_decision"])

    def test_cli_conflict_exits_3(self):
        rows = OWNERS_ROWS + [["declared_boundaries", "GTM CP",
                               "domain operations", "gtm-cp",
                               "PLAN-SOURCE.md"]]
        root = _repo(rows)
        rc = atlas.main(["resolve", REQUEST, "--owners",
                         str(root / "owners.csv"), "--repo", str(root)])
        self.assertEqual(3, rc)

    def test_cli_success_exits_0(self):
        root = _repo(OWNERS_ROWS)
        rc = atlas.main(["resolve", REQUEST, "--owners",
                         str(root / "owners.csv"), "--repo", str(root)])
        self.assertEqual(0, rc)

    def test_missing_primitives_reasons(self):
        root = _repo(OWNERS_ROWS)
        out = atlas.resolve(root, REQUEST, owners_csv=root / "owners.csv")
        missing = {m["product_class"]: m["reason"]
                   for m in out["missing_primitives"]}
        # "approved candidate" has no enabling primitive in the register
        self.assertEqual("no_enabling_primitive", missing.get("approved candidate"))


if __name__ == "__main__":
    unittest.main()
