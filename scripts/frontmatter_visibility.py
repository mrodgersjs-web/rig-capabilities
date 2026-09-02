"""Which canonical assets are invisible to the catalog because their frontmatter
is cut at HEAD_BYTES?

`catalog._pick_main_text` reads only HEAD_BYTES (4096). An asset whose YAML
frontmatter runs past that boundary is parsed from a truncated buffer, so
`_quality_block` returns {} and the asset reports outcome/done_when/great_example
as absent — while the file on disk has all of them. `./bin/rig-capabilities test
<id>` then answers pass=false with zero results: the gate is not red, it is
unloaded, which is worse than red.

Read-only. Covers canonical `capabilities/**` and every non-canonical file asset
the index serves (external harness roots), because those are handed to agents by
the same `get`/`search`/`test` surface.

Run: python3 scripts/frontmatter_visibility.py   (exit 1 = any victim)
"""
from __future__ import annotations

import json
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rig_capabilities import catalog  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ("outcome", "done_when", "great_example", "quality_floor")


def fm_end(text: str) -> int:
    """Byte offset of the frontmatter's closing `---`, or -1 if there is none."""
    if not text.startswith("---"):
        return -1
    nl = text.find("\n---", 3)
    return nl if nl >= 0 else -1


def scan() -> tuple[list, list, int]:
    """(truncation-victims, other-declared-but-unloaded, clean count)."""
    hidden, other, clean = [], 0, 0
    for kind, d in sorted(catalog.KIND_DIR.items()):
        base = ROOT / "capabilities" / d          # KIND_DIR values are bare names
        if not base.exists():
            continue
        for entry in sorted(base.rglob("*")):
            if not entry.is_file() or entry.name.startswith("."):
                continue
            if entry.suffix not in catalog.KIND_EXTS.get(kind, set()):
                continue
            raw = entry.read_text(encoding="utf-8", errors="replace")
            end = fm_end(raw)
            if end < 0:
                continue                          # no frontmatter, nothing to hide
            loaded = catalog._quality_block(catalog._pick_main_text(entry))
            lost = [f for f in FIELDS
                    if f in raw[:end] and not loaded.get(f)]
            rel = str(entry.relative_to(ROOT))
            if not lost:
                clean += 1
            elif end >= catalog.HEAD_BYTES:
                hidden.append((rel, end, len(raw), lost))
            else:
                other += 1
                print(f"  UNLOADED, NOT TRUNCATION {rel}: {lost}")
    return hidden, other, clean

def scan_external() -> tuple[list, list, int]:
    """The same test over non-canonical file assets served from external roots."""
    idx_p = ROOT / ".index.json"          # gitignored; the gate degrades to canonical-only
    if not idx_p.exists():
        return [], [], 0
    idx = json.loads(idx_p.read_text(encoding="utf-8"))
    hidden, other, clean = [], 0, 0
    for a in idx.get("assets", []):
        if a.get("source") == "canonical":
            continue
        p = Path(a.get("abs_path") or (ROOT / a.get("path", "")))
        if not p.is_file():
            continue                      # skill packages are directories
        raw = p.read_text(encoding="utf-8", errors="replace")
        end = fm_end(raw)
        if end < 0:
            continue
        loaded = catalog._quality_block(catalog._pick_main_text(p))
        lost = [f for f in FIELDS if re.search(rf"^{f}\s*:", raw[:end], re.M) and not loaded.get(f)]
        label = f"{a.get('source')}:{a.get('id')}"
        if not lost:
            clean += 1
        elif end >= catalog.HEAD_BYTES:
            hidden.append((label, end, len(raw), lost))
        else:
            other += 1
            print(f"  UNLOADED, NOT TRUNCATION (external) {label}: {lost}")
    return hidden, other, clean


def main() -> int:
    hidden, other, clean = scan()
    xhidden, xother, xclean = scan_external()
    print(f"\nHEAD_BYTES={catalog.HEAD_BYTES}  clean={clean + xclean}  "
          f"other_unloaded={other + xother}  truncation_hidden={len(hidden) + len(xhidden)}")
    for rel, end, size, lost in sorted(hidden + xhidden, key=lambda x: -x[1]):
        print(f"  {rel}  fm_end={end} bytes={size} lost={','.join(lost)}")
    if hidden or xhidden:
        print("VERDICT: these assets' gates cannot be loaded by the catalog; "
              "move long programs out of frontmatter into a checker the cmd: invokes.")
    return 1 if (hidden or other or xhidden or xother) else 0


if __name__ == "__main__":
    sys.exit(main())
