"""Which canonical assets are invisible to the catalog because their frontmatter
is cut at HEAD_BYTES?

`catalog._pick_main_text` reads only HEAD_BYTES (4096). An asset whose YAML
frontmatter runs past that boundary is parsed from a truncated buffer, so
`_quality_block` returns {} and the asset reports outcome/done_when/great_example
as absent — while the file on disk has all of them. `./bin/rig-capabilities test
<id>` then answers pass=false with zero results: the gate is not red, it is
unloaded, which is worse than red.

Read-only. Run: python3 scripts/frontmatter_visibility.py   (exit 1 = any victim)
"""
from __future__ import annotations

import sys
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


def main() -> int:
    hidden, other, clean = scan()
    print(f"\nHEAD_BYTES={catalog.HEAD_BYTES}  clean={clean}  "
          f"other_unloaded={other}  truncation_hidden={len(hidden)}")
    for rel, end, size, lost in sorted(hidden, key=lambda x: -x[1]):
        print(f"  {rel}  fm_end={end} bytes={size} lost={','.join(lost)}")
    if hidden:
        print("VERDICT: these assets' gates cannot be loaded by the catalog; "
              "move long programs out of frontmatter into a checker the cmd: invokes.")
    return 1 if (hidden or other) else 0


if __name__ == "__main__":
    sys.exit(main())
