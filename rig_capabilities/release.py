"""V28: public-catalog zip — generated DORMANT.

Builds a zip of `.public-catalog.json` + MANIFEST.json only. No source
tree, no `.signing.key`, no serve/federation tokens. The zip is a local
file under `.context/releases/`. Publishing (git tag, GitHub Release,
upload) is a separate Gate-D action: run_id gd_1788227314643. This
module never tags or uploads.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from . import __version__

GATE_D_RUN = "gd_1788227314643"
BANNED = (".signing.key", ".serve.token", ".token", ".env")


def build_public_zip(repo, apply: bool = True) -> dict:
    from .surface import write_public_catalog
    cat = write_public_catalog(repo)
    cat_path = Path(cat["path"])
    catalog = json.loads(cat_path.read_text(encoding="utf-8"))
    outdir = Path(repo.root) / ".context" / "releases"
    name = f"rig-capabilities-public-{__version__}.zip"
    zpath = outdir / name
    manifest = {
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": catalog["count"],
        "armed": False,
        "gate_d_run_id": GATE_D_RUN,
        "contents": [".public-catalog.json", "MANIFEST.json"],
        "note": "DORMANT. Type APPROVE %s to tag/upload. Zip is public ACL catalog only."
                % GATE_D_RUN,
    }
    if not apply:
        return {"ok": True, "apply": False, "armed": False,
                "path": str(zpath), "count": catalog["count"],
                "manifest": manifest}
    outdir.mkdir(parents=True, exist_ok=True)
    man_bytes = json.dumps(manifest, indent=1).encode()
    cat_bytes = cat_path.read_bytes()
    tmp = zpath.with_suffix(".zip.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(".public-catalog.json", cat_bytes)
        zf.writestr("MANIFEST.json", man_bytes)
        names = zf.namelist()
        assert all(not any(b in n for b in BANNED) for n in names)
    tmp.replace(zpath)
    digest = hashlib.sha256(zpath.read_bytes()).hexdigest()
    return {"ok": True, "apply": True, "armed": False, "path": str(zpath),
            "bytes": zpath.stat().st_size, "sha256": digest,
            "count": catalog["count"], "names": names,
            "gate_d_run_id": GATE_D_RUN}
