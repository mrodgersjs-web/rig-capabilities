"""Exemplar names preserve asset-id extensions and cannot silently collide."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import rounds
from rig_capabilities.quality import migrate_canonical
from scripts import seed_great_examples as seeder


class _Repo:
    def __init__(self, assets: list[dict]):
        self.assets = assets
        self.builds = 0

    def load_index(self) -> dict:
        return {"assets": self.assets}

    def build_index(self) -> None:
        self.builds += 1


def _great_example(path: Path) -> str:
    match = re.search(r"^(?:#\s*)?great_example:\s*(\S+)",
                      path.read_text(), re.MULTILINE)
    if not match:
        raise AssertionError(f"no great_example in {path}")
    return match.group(1)


def _assets(tmp: Path, ids: tuple[str, ...]) -> tuple[_Repo, dict[str, Path]]:
    paths = {}
    assets = []
    for index, asset_id in enumerate(ids):
        path = tmp / f"asset-{index}"
        path.write_text(f"# {asset_id}\nA substantive fixture body.\n")
        paths[asset_id] = path
        assets.append({
            "id": asset_id,
            "kind": "harness",
            "source": "canonical",
            "path": f"capabilities/harnesses/{asset_id}",
            "abs_path": str(path),
            "description": "collision fixture",
        })
    return _Repo(assets), paths


class ExemplarSlugCollisions(unittest.TestCase):
    def test_seed_round_and_quality_share_extension_preserving_paths(self):
        ids = ("a.yaml", "a.md", "a")
        expected = {
            "a.yaml": "examples/great/misc/a-yaml.md",
            "a.md": "examples/great/misc/a-md.md",
            "a": "examples/great/misc/a.md",
        }
        self.assertEqual(len({seeder._slug(asset_id) for asset_id in ids}), 3)

        round_paths = {
            asset_id: rounds._upgrade_plan({
                "id": asset_id,
                "path": f"capabilities/harnesses/{asset_id}",
                "description": "collision fixture",
                "quality": {"outcome": "misc: collision fixture"},
            })["great_example"]
            for asset_id in ids
        }
        self.assertEqual(round_paths, expected)

        with tempfile.TemporaryDirectory() as td:
            repo, paths = _assets(Path(td), ids)
            with patch("rig_capabilities.taxonomy.route",
                       return_value={"lanes": [{"outcome": "misc"}]}):
                migrate_canonical(repo)
            migrated = {asset_id: _great_example(path)
                        for asset_id, path in paths.items()}
        self.assertEqual(migrated, expected)

    def test_each_batch_generator_refuses_a_slug_collision_before_writing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, paths = _assets(root, ("a.yaml", "a-yaml"))
            before = {asset_id: path.read_text()
                      for asset_id, path in paths.items()}

            with self.assertRaisesRegex(ValueError, "exemplar slug collision"):
                rounds.run_round(repo, "misc")
            with self.assertRaisesRegex(ValueError, "exemplar slug collision"):
                migrate_canonical(repo)
            self.assertEqual(before, {asset_id: path.read_text()
                                      for asset_id, path in paths.items()})

            (root / ".index.json").write_text(json.dumps({"assets": [
                {"id": asset_id, "source": "canonical", "okf": {"trust": 1.0}}
                for asset_id in ("a.yaml", "a-yaml")
            ]}))
            out = root / "examples" / "great"
            with patch.object(seeder, "REPO", root), \
                    patch.object(seeder, "OUT", out), \
                    patch.object(seeder, "VAULT_EXEMPLARS", {}), \
                    self.assertRaisesRegex(ValueError, "exemplar slug collision"):
                seeder.seed()
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
