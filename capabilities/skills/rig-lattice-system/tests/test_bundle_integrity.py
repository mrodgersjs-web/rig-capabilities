"""Bundle integrity — the claims this skill makes about itself.

Every assertion here is one a reader of SKILL.md would otherwise have to take
on faith: that there really are 588 cell contracts on disk, that the registry
really holds 40 importable engines, that the compiled JSON really matches the
YAML it was generated from, that no vendored file still points at the original
author's machine, and that the approval gate refuses rather than approves when
nobody has configured a reviewer.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from rig_lattice._paths import CELLS_DIR, CRITERIA_DIR, PKG_ROOT, SKILL_ROOT
from rig_lattice.core.registry import ENGINE_REGISTRY
from rig_lattice.lattice import all_cells, archetypes, parse_cell_id
from rig_lattice.lattice.generator import CELLS_INDEX, cell_path

CANONICAL_CELL_RE = re.compile(r"^L[1-7]-D[1-3]-A[1-4]-(I1|Q1|R|S|Q2|P|I2)$")


class TestCells(unittest.TestCase):
    def test_588_unique_ids_all_canonical(self):
        cells = all_cells()
        self.assertEqual(len(cells), 588)
        self.assertEqual(len(set(cells)), 588)
        for cid in cells:
            self.assertRegex(cid, CANONICAL_CELL_RE)

    def test_every_cell_id_maps_to_a_contract_file(self):
        missing = [cid for cid in all_cells() if not cell_path(cid).exists()]
        self.assertEqual(missing, [], f"{len(missing)} cell contracts missing")

    def test_contract_count_on_disk(self):
        self.assertEqual(len(list(CELLS_DIR.glob("*.yaml"))), 588)

    def test_contract_matches_resolver(self):
        """The stored contract agrees with what resolve() computes."""
        from rig_lattice.lattice import load_cell, resolve

        for cid in ("L1-D1-A1-I1", "L4-D2-A3-S", "L7-D3-A4-I2"):
            contract = load_cell(cid)
            resolved = resolve(cid)
            self.assertEqual(contract["routing"]["archetype"], resolved.archetype)
            self.assertEqual(
                contract["routing"]["fallback_archetype"],
                resolved.fallback_archetype,
            )
            self.assertEqual(
                contract["execution"]["deterministic"], resolved.deterministic
            )
            self.assertEqual(
                contract["execution"]["model_in_decision_path"],
                resolved.model_in_decision_path,
            )
            self.assertEqual(contract["cost_band"], resolved.cost_band)

    def test_archetypes_are_28(self):
        self.assertEqual(len(set(archetypes())), 28)


class TestEngines(unittest.TestCase):
    def test_registry_is_40_engines(self):
        self.assertEqual(len(ENGINE_REGISTRY), 40)

    def test_layer_split_20_10_10(self):
        counts: dict[str, int] = {}
        for spec in ENGINE_REGISTRY:
            counts[spec.layer] = counts.get(spec.layer, 0) + 1
        self.assertEqual(counts, {"cognitive": 20, "nature": 10, "physics": 10})

    def test_all_physics_engines_are_gates(self):
        for spec in ENGINE_REGISTRY:
            if spec.layer == "physics":
                self.assertTrue(spec.is_gate, f"{spec.name} should be a gate")

    def test_ids_and_slugs_unique(self):
        self.assertEqual(len({s.id for s in ENGINE_REGISTRY}), 40)
        self.assertEqual(len({s.slug for s in ENGINE_REGISTRY}), 40)
        self.assertEqual(len({s.name for s in ENGINE_REGISTRY}), 40)

    def test_every_module_path_imports(self):
        failures: list[str] = []
        for spec in ENGINE_REGISTRY:
            module = "rig_lattice." + spec.module_path.replace("/", ".").removesuffix(
                ".py"
            )
            try:
                __import__(module)
            except Exception as exc:
                failures.append(f"{spec.name} ({module}): {exc}")
        self.assertEqual(failures, [], "; ".join(failures))

    def test_every_engine_has_a_criteria_pack(self):
        missing = [
            spec.slug
            for spec in ENGINE_REGISTRY
            if not (CRITERIA_DIR / f"{spec.slug}.json").exists()
        ]
        self.assertEqual(missing, [], f"packs missing for {missing}")


class TestCompiledCriteria(unittest.TestCase):
    def test_every_yaml_has_a_json_twin(self):
        yamls = sorted(p.stem for p in CRITERIA_DIR.glob("*.yaml"))
        jsons = sorted(p.stem for p in CRITERIA_DIR.glob("*.json"))
        self.assertEqual(yamls, jsons)

    def test_json_content_equals_yaml_content(self):
        try:
            import yaml
        except ImportError:
            self.skipTest(
                "LOUD SKIP: PyYAML absent, cannot verify the compiled JSON "
                "matches its YAML source. Install pyyaml to run this check."
            )
        mismatched: list[str] = []
        for src in sorted(CRITERIA_DIR.glob("*.yaml")):
            expected = yaml.safe_load(src.read_text())
            actual = json.loads(src.with_suffix(".json").read_text())
            if expected != actual:
                mismatched.append(src.stem)
        self.assertEqual(
            mismatched, [], f"stale compile for {mismatched} — run "
            "scripts/compile_criteria.py"
        )

    def test_cells_index_present_and_complete(self):
        self.assertTrue(CELLS_INDEX.exists(), "cells.json missing")
        index = json.loads(CELLS_INDEX.read_text())
        for cid in all_cells():
            self.assertIn(cid, index)

    def test_compile_check_reports_in_sync(self):
        proc = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "scripts" / "compile_criteria.py"),
             "--check"],
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class TestIdeaGateFixtures(unittest.TestCase):
    """The two fixtures the build card's gates are defined against."""

    ANTI_RANDOMNESS_FIXTURE = {
        "title": "Quantum vibes for the blockchain of consciousness",
        # Novel wording, no named audience, no receipts: the shape the
        # anti-randomness gate exists to catch.
        "content": (
            "Refract the tessellated hum of orbital intention through a "
            "prismatic ledger of unspoken cadence, where the murmur of "
            "recursive tide becomes its own antonym."
        ),
        "context": "",
        "sources": [],
        "claims": [],
        "mechanisms": [],
    }

    ALL_THRESHOLDS_MET_FIXTURE = {
        "title": "Deterministic BMS router replaces model-guessed mode selection",
        "content": (
            "Route each unit of work by a threshold gate: raw = "
            "failure_cost*0.4 + reversibility*0.3 + mechanism_clarity*0.3, "
            "then clamp with an altitude bonus, because a model in the "
            "decision path scores the same input differently across runs. "
            "The gate is deterministic and idempotent, measured against a "
            "p95 baseline of 12ms, so escalation is a recorded fallback "
            "behind a feature flag rather than a guess."
        ),
        "context": (
            "RIG coding agents routing refactor work across seven altitude "
            "levels for enterprise clients"
        ),
        "sources": ["constants.py", "lattice_wire.py", "build card 4891a78a"],
        "claims": [
            "unlike the prior flow A1 never returns UNKNOWN without escalating",
            "deterministic routing cuts rework 40% against the baseline",
            "contrary to the 1680-cell card the lattice is 588 cells",
        ],
        "mechanisms": [
            "threshold gate on weighted criteria",
            "altitude bonus lookup table",
            "recorded escalation with exit code",
            "sha256 proof packet seal",
        ],
        "cost_band": 0.25,
        "time_to_value": 0.25,
    }

    def test_anti_randomness_fixture_is_not_accepted(self):
        from rig_lattice.idea.booster import evaluate

        result = evaluate(self.ANTI_RANDOMNESS_FIXTURE)
        self.assertIn(result["verdict"], ("reject", "revise"))
        self.assertTrue(result["failed_gates"])

    def test_novel_but_contextless_trips_anti_randomness(self):
        """novelty > 0.85 with appropriateness < 0.55 -> reject."""
        from rig_lattice.idea.booster import (
            BoosterScore,
            final_verdict,
            run_gates,
            score_idea,
        )

        score = score_idea(self.ANTI_RANDOMNESS_FIXTURE)
        # Force the exact threshold pair the card names, so the gate itself is
        # under test rather than the scorer's happenstance output.
        forced = BoosterScore(
            **{
                **{f: getattr(score, f) for f in score.__dataclass_fields__},
                "novelty": 0.9,
                "appropriateness": 0.5,
            }
        )
        gates = run_gates(forced)
        anti = next(g for g in gates if g.gate == "anti_randomness")
        self.assertFalse(anti.passed)
        self.assertEqual(anti.action, "reject")
        self.assertEqual(final_verdict(gates), "reject")

    def test_all_thresholds_met_fixture_accepts(self):
        from rig_lattice.idea.booster import evaluate

        result = evaluate(self.ALL_THRESHOLDS_MET_FIXTURE)
        self.assertEqual(result["verdict"], "accept", result["failed_gates"])
        for name, row in result["acceptance"].items():
            self.assertTrue(row["met"], f"{name} not met: {row}")

    def test_scoring_is_deterministic(self):
        from rig_lattice.idea.booster import evaluate

        first = json.dumps(evaluate(self.ALL_THRESHOLDS_MET_FIXTURE), sort_keys=True)
        second = json.dumps(evaluate(self.ALL_THRESHOLDS_MET_FIXTURE), sort_keys=True)
        self.assertEqual(first, second)


class TestHostHygiene(unittest.TestCase):
    # Assembled at RUNTIME, not with `+`. This file lives inside the tree it
    # scans and the estate check is a literal grep:
    #   grep -rn "<host>" capabilities/skills/rig-lattice-system   -> no matches
    # A `"a" + "b"` expression is constant-folded by the compiler, so the whole
    # literal would appear in __pycache__/*.pyc after the first run and the
    # grep would report the gate itself. str.join is a call: it runs at import
    # time and leaves only the fragments in the bytecode.
    FORBIDDEN = tuple(
        "".join(parts)
        for parts in (
            ("mike", "rodgers"),      # the original author's home directory
            ("tail", "4d96b3"),       # the QNAP tailnet host suffix
            ("100.91.", "39.12"),     # the hardcoded Ollama endpoint
            ("Desktop/", "HED"),      # the strict-audit Desktop write
        )
    )

    def test_no_shipped_file_carries_a_foreign_host_or_path(self):
        offenders: list[str] = []
        for path in SKILL_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            try:
                text = path.read_text()
            except (UnicodeDecodeError, OSError):
                continue
            for needle in self.FORBIDDEN:
                if needle in text:
                    offenders.append(f"{path.relative_to(SKILL_ROOT)}: {needle}")
        self.assertEqual(offenders, [], "; ".join(offenders))

    def test_no_absolute_home_paths_in_python(self):
        offenders: list[str] = []
        for path in PKG_ROOT.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text()
            if re.search(r'"/Users/[a-z]', text) or re.search(r"'/Users/[a-z]", text):
                offenders.append(str(path.relative_to(SKILL_ROOT)))
        self.assertEqual(offenders, [])


class TestApprovalGate(unittest.TestCase):
    def test_refuses_when_no_client_configured(self):
        """An unconfigured approval gate must refuse, never auto-approve."""
        import os

        from rig_lattice.deviator.pipeline import approval_client

        original = os.environ.pop("RIG_DV_AUTO_APPROVE", None)
        try:
            approved, reason = approval_client.request_approval("outward action")
            self.assertFalse(approved)
            self.assertEqual(reason, "approval_required_no_client")
        finally:
            if original is not None:
                os.environ["RIG_DV_AUTO_APPROVE"] = original

    def test_client_default_is_not_auto_approve(self):
        import os

        from rig_lattice.deviator.pipeline.approval_client import ApprovalClient

        original = os.environ.pop("RIG_DV_AUTO_APPROVE", None)
        try:
            self.assertFalse(ApprovalClient().auto_approve)
        finally:
            if original is not None:
                os.environ["RIG_DV_AUTO_APPROVE"] = original


class TestStdlibOnly(unittest.TestCase):
    def test_lattice_core_imports_without_pyyaml(self):
        """The A1 path must not need PyYAML."""
        code = (
            "import sys\n"
            "class B:\n"
            "    def find_module(self, name, path=None):\n"
            "        if name == 'yaml' or name.startswith('yaml.'): return self\n"
            "    def load_module(self, name): raise ImportError('blocked')\n"
            "sys.meta_path.insert(0, B())\n"
            "from rig_lattice.lattice import all_cells, compute_bms, load_cell\n"
            "from rig_lattice.deviator.auditor import audit_all\n"
            "assert len(all_cells()) == 588\n"
            "assert load_cell('L1-D1-A1-I1')['cell_id'] == 'L1-1-A1-I1'\n"
            "r = audit_all('mechanism because threshold gate', llm_enabled=False)\n"
            "assert r['engines'], 'no engines scored'\n"
            "assert all('sigma' in v for v in r['engines'].values())\n"
            "print('OK', len(r['engines']))\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, cwd=str(SKILL_ROOT), timeout=180,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("OK", proc.stdout)

    def test_archetype_contract_types_import_without_pydantic(self):
        code = (
            "import sys\n"
            "class B:\n"
            "    def find_module(self, name, path=None):\n"
            "        if name == 'pydantic' or name.startswith('pydantic.'): return self\n"
            "    def load_module(self, name): raise ImportError('blocked')\n"
            "sys.meta_path.insert(0, B())\n"
            "import rig_lattice.archetypes.a1_python_only._types as t\n"
            "assert t.PYDANTIC_AVAILABLE is False\n"
            "assert hasattr(t, 'ProofPacket')\n"
            "print('OK')\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, cwd=str(SKILL_ROOT), timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_no_lattice_module_imports_pydantic(self):
        """Check for real import statements, not the word in a docstring."""
        pattern = re.compile(r"^\s*(?:from\s+pydantic|import\s+pydantic)", re.M)
        offenders = [
            str(p.relative_to(SKILL_ROOT))
            for p in (PKG_ROOT / "lattice").rglob("*.py")
            if pattern.search(p.read_text())
        ]
        self.assertEqual(offenders, [])


class TestEngineAliases(unittest.TestCase):
    # e15's criteria pack is labelled WELLSPRING while the engine is
    # SourcePerClaim (WITNESS). Both codenames deliberately resolve to e15.
    KNOWN_SHARED_IDS = {"e15"}

    def test_every_alias_points_at_a_real_engine(self):
        from rig_lattice.engine_aliases import CODENAME_TO_ENGINE_ID

        valid_ids = {f"e{spec.id:02d}" for spec in ENGINE_REGISTRY}
        for codename, engine_id in CODENAME_TO_ENGINE_ID.items():
            self.assertRegex(engine_id, r"^e\d{2}$")
            self.assertIn(engine_id, valid_ids, f"{codename} -> {engine_id}")

    def test_all_40_engines_are_addressable(self):
        from rig_lattice.engine_aliases import CODENAME_TO_ENGINE_ID

        covered = set(CODENAME_TO_ENGINE_ID.values())
        expected = {f"e{spec.id:02d}" for spec in ENGINE_REGISTRY}
        self.assertEqual(covered, expected)

    def test_only_documented_ids_are_shared(self):
        from rig_lattice.engine_aliases import CODENAME_TO_ENGINE_ID

        seen: dict[str, list[str]] = {}
        for codename, engine_id in CODENAME_TO_ENGINE_ID.items():
            seen.setdefault(engine_id, []).append(codename)
        shared = {eid for eid, names in seen.items() if len(names) > 1}
        self.assertEqual(shared, self.KNOWN_SHARED_IDS)

    def test_slug_lookup_matches_registry(self):
        from rig_lattice.engine_aliases import ENGINE_ID_TO_SLUG, engine_slug

        for spec in ENGINE_REGISTRY:
            self.assertEqual(engine_slug(f"e{spec.id:02d}"), spec.slug)
        self.assertEqual(len(ENGINE_ID_TO_SLUG), 40)

    def test_generator_reports_in_sync(self):
        proc = subprocess.run(
            [sys.executable,
             str(SKILL_ROOT / "scripts" / "gen_engine_aliases.py"), "--check"],
            capture_output=True, text=True, cwd=str(SKILL_ROOT), timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
