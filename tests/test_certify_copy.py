"""Regression for certify's copy-tree plant harness."""

from __future__ import annotations

import os
from pathlib import Path

from rig_capabilities.certify import _copytree


def test_certify_copy_preserves_dangling_catalog_symlinks(tmp_path: Path) -> None:
    """A missing optional asset is a gate input, not a reason to crash before gates run."""
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    target = "../../capabilities/skills/not-installed-here"
    (src / "catalog-entry").symlink_to(target)

    _copytree(src, dst)

    copied = dst / "catalog-entry"
    assert copied.is_symlink()
    assert os.readlink(copied) == target
    assert not copied.exists()  # still dangling, honestly preserved
