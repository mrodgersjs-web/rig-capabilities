#!/usr/bin/env python3
"""extract_routines.py — REVERSE EXTRACTION (A1, read-only): read live Aside routines back
into workflow-design-studio design rows so the REGISTRY is the single source of truth.

Source: ~/.aside/u/0/state.db (routines table, read-only URI).
Output: registry/imported/aside-routines.yaml + stdout summary.
"""
import hashlib, json, os, sqlite3, sys

HOME = os.path.expanduser("~")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "registry", "imported", "aside-routines.yaml")

db = sqlite3.connect(f"file:{HOME}/.aside/u/0/state.db?mode=ro", uri=True)
db.row_factory = sqlite3.Row
rows = db.execute("SELECT * FROM routines WHERE deleted_at IS NULL ORDER BY created_at").fetchall()

def one(s):
    return (s or "").replace("\n", " ").replace('"', "'")[:160]

lines = [
    "# Reverse-extracted design rows — live Aside routines (A1 extract, read-only).",
    "# SSOT merge target: registry/registry.yaml. done-test is unknown for imported rows:",
    "# these workflows were designed by hand before the studio existed.",
    f"# extracted_from: ~/.aside/u/0/state.db routines (deleted_at IS NULL) — {len(rows)} rows",
    "rows:",
]
for r in rows:
    d = dict(r)
    sc = json.loads(d.get("session_config") or "{}")
    model = (sc.get("model") or {}).get("modelId", "unknown")
    rrule = one(d.get("rrule"))
    lines += [
        f"  - id: {d['id']}",
        f"    name: \"{one(d.get('name'))}\"",
        "    surface: [aside-routine]",
        f"    schedule: \"{rrule}\"",
        "    owner: aside-runtime",
        "    done-test: none-recorded (imported; design predates the studio)",
        "    last-drift-check: never — run compiler/drift_doctor.py",
        f"    embed_state: live (status={d.get('status')})",
        f"    model: {model}",
        f"    prompt_sha256: {hashlib.sha256((d.get('prompt') or '').encode()).hexdigest()[:16]}",
    ]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write("\n".join(lines) + "\n")
live = sum(1 for r in rows if r["status"] == "active")
print(f"EXTRACTED {len(rows)} routines -> registry/imported/aside-routines.yaml "
      f"(active={live}, other={len(rows)-live})")
