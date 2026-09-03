#!/usr/bin/env python3
"""Regenerate rig_lattice/engine_aliases.py from the registry + criteria packs.

The alias table maps the short RIG codenames (GRAVITON, COLLIDER, ...) that the
~40 ``rig-<codename>`` skills and the Alfred pipeline use onto engine ids. It
is generated, never typed, so it cannot drift from ``core/registry.py``.

    PYTHONPATH=. python3 scripts/gen_engine_aliases.py
    PYTHONPATH=. python3 scripts/gen_engine_aliases.py --check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))

from rig_lattice.core.registry import ENGINE_REGISTRY  # noqa: E402

TARGET = SKILL_ROOT / "rig_lattice" / "engine_aliases.py"
CRITERIA = SKILL_ROOT / "rig_lattice" / "criteria"

# e15 is hermeneutic_density / SourcePerClaim — per-claim source weighting,
# i.e. the WITNESS engine. Its criteria pack is labelled WELLSPRING, which is a
# different concept (hedonic adaptation). Both names resolve to e15 rather than
# silently dropping one. Recorded in PROVENANCE.md.
EXTRA_ALIASES: dict[str, str] = {"WITNESS": "e15"}


def rows() -> list[tuple[str, str, str, str, str]]:
    out = []
    for spec in sorted(ENGINE_REGISTRY, key=lambda e: e.id):
        pack = CRITERIA / f"{spec.slug}.json"
        codename = spec.name
        if pack.exists():
            codename = json.loads(pack.read_text()).get("codename") or spec.name
        out.append((f"e{spec.id:02d}", codename.upper(), spec.slug, spec.name,
                    spec.layer))
    return out


def render() -> str:
    data = rows()
    entries = "\n".join(
        f'    "{codename}": "{eid}",'.ljust(42) + f"# {slug} ({layer})"
        for eid, codename, slug, _name, layer in data
    )
    extras = "\n".join(
        f'    "{name}": "{eid}",' for name, eid in EXTRA_ALIASES.items()
    )
    slugs = "\n".join(f'    "{eid}": "{slug}",' for eid, _c, slug, _n, _l in data)
    return f'''"""Codename -> engine id aliases. GENERATED — do not hand-edit.

The ~40 ``rig-<codename>`` skills and the Alfred LinkedIn pipeline address the
deviation engines by short codename (COLLIDER, SURPRISE, BREAKER, ...). This
table is the machine-readable twin of the table in
``capabilities/commands/rig-lattice.md``; a done-test asserts the two agree.

Regenerate with::

    PYTHONPATH=. python3 scripts/gen_engine_aliases.py

Source of truth: ``rig_lattice/core/registry.py`` for the id ordering and
``rig_lattice/criteria/<slug>.json`` for the codename. Nothing here is typed
by hand, so the table cannot drift from the registry silently.

One known upstream conflict, preserved rather than papered over: engine 15 is
``hermeneutic_density`` / ``SourcePerClaim`` — per-claim source weighting,
which is the WITNESS engine. Its criteria pack is labelled ``WELLSPRING``
(the hedonic-adaptation concept, a different engine entirely). Both codenames
resolve to e15 so either caller works; the mislabel is recorded in
PROVENANCE.md.
"""

from __future__ import annotations

CODENAME_TO_ENGINE_ID: dict[str, str] = {{
{entries}
    # Upstream mislabel: e15's pack says WELLSPRING, the engine is WITNESS.
{extras}
}}

ENGINE_ID_TO_CODENAME: dict[str, str] = {{
    engine_id: codename
    for codename, engine_id in CODENAME_TO_ENGINE_ID.items()
    if codename not in {set(EXTRA_ALIASES)!r}
}}

ENGINE_ID_TO_SLUG: dict[str, str] = {{
{slugs}
}}


def resolve_codename(codename: str) -> str:
    """Codename (any case) -> engine id. Raises KeyError on an unknown name."""
    return CODENAME_TO_ENGINE_ID[codename.strip().upper()]


def engine_slug(engine_id: str) -> str:
    """Engine id (e01..e40) -> criteria slug."""
    return ENGINE_ID_TO_SLUG[engine_id.strip().lower()]


__all__ = [
    "CODENAME_TO_ENGINE_ID",
    "ENGINE_ID_TO_CODENAME",
    "ENGINE_ID_TO_SLUG",
    "engine_slug",
    "resolve_codename",
]
'''


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                     help="fail if the committed file is stale")
    args = ap.parse_args()

    rendered = render()
    if args.check:
        current = TARGET.read_text() if TARGET.exists() else ""
        if current != rendered:
            print("STALE: engine_aliases.py differs from the registry — run "
                  "scripts/gen_engine_aliases.py", file=sys.stderr)
            return 1
        print(f"OK: engine_aliases.py in sync ({len(rows())} engines)")
        return 0

    TARGET.write_text(rendered)
    print(f"wrote {TARGET.relative_to(SKILL_ROOT)} ({len(rows())} engines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
