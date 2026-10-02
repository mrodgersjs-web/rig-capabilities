"""B1: Capability Atlas — resolve a requested transformation into what already
exists, what is missing, and who owns the states the request touches.

Thin resolution layer over the committed stores, never a new one:
- existing/missing primitives come from `capability_register.csv` via
  `register.load_register` (no second index, no migration);
- state owners come from `data/control_plane_owners.csv`, one row per
  (state_decision x control plane).

DOC 3 §6 invariant, enforced as code: exactly one authoritative owner per
state_decision. Rival planes are recorded with authoritative_owner =
`claimant` — visible, never a second owner. A touched state with zero or
two-or-more authoritative owners raises `AtlasConflict`; the CLI turns that
into a conflict packet on stdout and exit 3 (DOC 3 §10: stop and emit a
conflict packet, never silently reconcile).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from . import register as reg

OWNERS_STORE = "data/control_plane_owners.csv"
OWNERS_FIELDS = ("state_decision", "plane", "authority_class",
                 "authoritative_owner", "evidence_path")
CLAIMANT = "claimant"

# Words that carry no matching signal on their own.
_STOP = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "becomes", "by", "for",
    "from", "in", "inside", "into", "is", "it", "of", "on", "one", "or",
    "per", "the", "to", "under", "with", "within",
})


class AtlasConflict(Exception):
    """Owner invariant violated for a state the request touched."""

    def __init__(self, packets: list[dict]):
        self.packets = packets
        kinds = ", ".join(sorted({p["kind"] for p in packets}))
        super().__init__(f"atlas ownership conflict: {kinds}")


# --------------------------------------------------------------------- input

def _repo_root(repo) -> Path:
    return Path(getattr(repo, "root", repo))


def owners_path(repo, path=None) -> Path:
    return Path(path) if path is not None else _repo_root(repo) / OWNERS_STORE


def load_owners(repo, path=None) -> list[dict]:
    """Rows of the control-plane owners table. A missing file is an empty
    table (which can only ever produce zero-owner conflicts, never owners)."""
    p = owners_path(repo, path)
    if not p.is_file():
        return []
    with p.open(newline="", encoding="utf-8") as fh:
        return [{(f or "").strip(): (v or "").strip()
                 for f, v in row.items() if f is not None}
                for row in csv.DictReader(fh)]


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOP]


def _row_haystack(row: dict) -> str:
    """One lowercase string per register row: id, name, product classes, deps."""
    parts = [row.get("id", ""), row.get("name", "")]
    parts += list(row.get("enables_product_classes") or [])
    parts += list(row.get("blocking_deps") or [])
    return " ".join(str(p) for p in parts).lower().replace("_", " ")


def _phrase(state_decision: str) -> str:
    return state_decision.replace("_", " ").strip().lower()


# ------------------------------------------------------------------- resolve

def _existing_primitives(rows: list[dict], request_tokens: list[str]) -> list[dict]:
    """Register rows whose id/name/enables/deps share a token with the request."""
    out = []
    for row in rows:
        hay = _row_haystack(row)
        hit = sorted({t for t in request_tokens
                      if re.search(rf"\b{re.escape(t)}", hay)})
        if hit:
            out.append({"id": row.get("id"), "name": row.get("name"),
                        "maturity_M0_5": row.get("maturity_M0_5"),
                        "matched_tokens": hit})
    return out


def _missing_primitives(rows: list[dict], request_tokens: list[str]) -> list[dict]:
    """Adjacent content-word pairs in the request with no enabling primitive:
    either no register row covers both tokens, or every covering row is M0."""
    out = []
    for a, b in zip(request_tokens, request_tokens[1:]):
        if a == b:
            continue
        covering = [r for r in rows
                    if re.search(rf"\b{re.escape(a)}", _row_haystack(r))
                    and re.search(rf"\b{re.escape(b)}", _row_haystack(r))]
        if not covering:
            out.append({"product_class": f"{a} {b}",
                        "reason": "no_enabling_primitive"})
        elif all((r.get("maturity_M0_5") or 0) == 0 for r in covering):
            out.append({"product_class": f"{a} {b}",
                        "reason": "only_m0_rows",
                        "m0_rows": sorted(r.get("id") for r in covering)})
    return out


def _state_owners(owner_rows: list[dict], request: str) -> tuple[list[dict], list[dict]]:
    """(named_state_owners, conflict_packets) for the states the request
    touches. Touched = the state_decision phrase appears verbatim in the
    request. Exactly one non-claimant authoritative_owner per touched state."""
    hay = request.lower()
    by_state: dict[str, list[dict]] = {}
    for row in owner_rows:
        state = row.get("state_decision", "")
        if state and _phrase(state) in hay:
            by_state.setdefault(state, []).append(row)

    owners, conflicts = [], []
    for state in sorted(by_state):
        rows = by_state[state]
        authoritative = [r for r in rows
                         if r.get("authoritative_owner")
                         and r["authoritative_owner"] != CLAIMANT]
        if len(authoritative) == 1:
            r = authoritative[0]
            owners.append({"state_decision": state,
                           "plane": r.get("plane"),
                           "authority_class": r.get("authority_class"),
                           "authoritative_owner": r["authoritative_owner"],
                           "evidence_path": r.get("evidence_path"),
                           "claimants": sorted(
                               x.get("plane") for x in rows
                               if x.get("authoritative_owner") == CLAIMANT)})
        else:
            conflicts.append({
                "conflict": True,
                "kind": "zero_owner" if not authoritative else "dual_owner",
                "state_decision": state,
                "claimants": sorted(
                    f'{r.get("plane")} ({r.get("authoritative_owner") or "unowned"})'
                    for r in rows),
                "rule": "DOC 3 §6: exactly one authoritative owner per "
                        "state_decision; §10: emit a conflict packet, never "
                        "silently reconcile",
            })
    return owners, conflicts


def resolve(repo, request: str, owners_csv=None) -> dict:
    """Resolve one requested transformation. Raises AtlasConflict when any
    touched state violates the single-owner invariant."""
    rows = reg.load_register(repo)
    owner_rows = load_owners(repo, owners_csv)
    tokens = _tokens(request)

    owners, conflicts = _state_owners(owner_rows, request)
    if conflicts:
        raise AtlasConflict(conflicts)

    return {
        "request": request,
        "existing_primitives": _existing_primitives(rows, tokens),
        "missing_primitives": _missing_primitives(rows, tokens),
        "named_state_owners": owners,
    }


# ----------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        prog="rig-capabilities atlas",
        description="Resolve a requested transformation into existing "
                    "primitives, missing primitives and named state owners.")
    parser.add_argument("atlas_cmd", choices=["resolve"])
    parser.add_argument("request")
    parser.add_argument("--owners", help="owners CSV (default "
                        "data/control_plane_owners.csv)")
    parser.add_argument("--repo", help="repo root (default: parent of package)")
    args = parser.parse_args(argv)

    root = Path(args.repo) if args.repo else Path(__file__).resolve().parent.parent
    try:
        out = resolve(root, args.request, owners_csv=args.owners)
    except AtlasConflict as exc:
        print(json.dumps({"conflict": True, "packets": exc.packets}, indent=1))
        return 3
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
