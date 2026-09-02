"""V10: the IQRSQPI seven-stage pass as a stdlib runtime.

One canonical order — Intent, Question, Research, Solution, Quality, Proof,
Integrate. Harnesses write that order in whatever vocabulary they grew up
with (`I, Q, R, S, Q2, P, I2` or `intake … iterate`); `normalize_stage`
collapses the vocabulary, never the order.

Two things this module refuses to do: execute a model or a subprocess, and
read anything outside `repo.root`. The stage-order gate is hermetic (L1) —
it reads one committed fixture. The pass runner validates a walk directory
that already exists; it never writes, because a runner that invents its own
artifacts is how a walk launders itself into "done".

Tokens are matched as whole words, case-insensitive and trimmed, and a
canonical name is always a valid token for itself. `I2` is never read as `I`
and `Q2` is never read as `Q` — the suffix is the stage, not noise.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

STAGES = ("Intent", "Question", "Research", "Solution", "Quality", "Proof",
          "Integrate")

# Whole-token vocabulary, keys lowercase. Every element of STAGES also
# resolves to itself (see `_BY_TOKEN` below); this table records only the
# non-canonical spellings the harness vocabularies actually write.
STAGE_ALIASES: dict[str, str] = {
    "intake": "Intent",
    "i1": "Intent",
    "i": "Intent",
    "question": "Question",
    "q1": "Question",
    "q": "Question",
    "research": "Research",
    "r": "Research",
    "synthesize": "Solution",
    "solution": "Solution",
    "s": "Solution",
    "quantify": "Quality",
    "q2": "Quality",
    "produce": "Proof",
    "proof": "Proof",
    "p": "Proof",
    "iterate": "Integrate",
    "i5": "Integrate",
    "i2": "Integrate",
}

# The resolution table: canonical names first (each maps to itself), then the
# aliases on top. Whole tokens are looked up by exact equality, so no token
# can be swallowed by a prefix of itself — `I2` and `I` are separate keys.
_BY_TOKEN: dict[str, str] = {stage.lower(): stage for stage in STAGES}
_BY_TOKEN.update(STAGE_ALIASES)

# The four artifacts a v10 walk can carry, in the order they get written.
ARTIFACTS = ("00-intake", "01-reality", "02-decision", "proof")

# Which artifacts a stage may not be called "reached" without.
#   Intent opens the intake; Question may not raise assumptions without the
#   reality document being opened alongside it; Research owns 01-reality;
#   Solution owns 02-decision; Quality scores that decision and opens proof;
#   Proof seals it; Integrate may not ship a walk with no proof behind it.
STAGE_ARTIFACTS: dict[str, tuple[str, ...]] = {
    "Intent": ("00-intake",),
    "Question": ("00-intake", "01-reality"),
    "Research": ("01-reality",),
    "Solution": ("02-decision",),
    "Quality": ("02-decision", "proof"),
    "Proof": ("proof",),
    "Integrate": ("proof",),
}

WALK_ROOT = ".context/iqrsqpi"
GATE_FIXTURE = "tests/fixtures/fable2031/iqrsqpi-run.json"

# Whose word each artifact is. A stage may demand a document it does not own
# (Question must open the reality document Research wrote), but a number
# inside it is audited exactly once, against the stage that owns it.
ARTIFACT_OWNER: dict[str, str] = {
    "00-intake": "Intent",
    "01-reality": "Research",
    "02-decision": "Solution",
    "proof": "Proof",
}

# A number without a source is a fabrication, however it arrives: typed value,
# numeric string, or a digit embedded in the claim text.
_NUMBER_RE = re.compile(r"(?<![\w.])[+-]?\d[\d,]*(?:\.\d+)?%?")


class StageError(Exception):
    """The pass violated the stage contract. Message is the reason code."""


def normalize_stage(token: str) -> str:
    """Collapse one stage token to its canonical stage name.

    Case-insensitive and whitespace-trimmed. Every canonical name maps to
    itself; every documented alias maps to its stage. Unknown tokens raise
    rather than landing on a guess.
    """
    key = str(token if token is not None else "").strip().lower()
    if not key:
        raise StageError("stage_token_empty")
    stage = _BY_TOKEN.get(key)
    if stage is None:
        raise StageError(f"unknown_stage_token:{token!r}")
    return stage


def stage_order_ok(sequence) -> tuple[bool, str]:
    """True iff the tokens normalize to an in-order subsequence of STAGES.

    No backward steps, no repeats. Never raises — a bad token is a False
    with the reason, because the gate that calls this must report, not blow
    up, when a fixture is malformed.
    """
    tokens = list(sequence or [])
    if not tokens:
        return False, "empty_stage_sequence"
    stages = []
    for tok in tokens:
        try:
            stages.append(normalize_stage(tok))
        except StageError as exc:
            return False, str(exc)
    ranks = [STAGES.index(s) for s in stages]
    for i, stage in enumerate(stages):
        if i and ranks[i] <= ranks[i - 1]:
            step = "stage_backtrack" if ranks[i] < ranks[i - 1] else "stage_repeated"
            return (False,
                    f"{step}:{stages[i - 1]}->{stage}@{i}"
                    f" of {len(stages)}")
    return True, f"in_order:{len(stages)}/{len(STAGES)}>{'>'.join(stages)}"


def run_pass(repo, walk_id, stages, *, verifier, generator) -> dict:
    """Validate one recorded IQRSQPI v10 pass. Read-only; raises StageError.

    Checks, in order: the builder is not the checker; the walk's stages are an
    in-order subsequence of STAGES; every reached stage's required artifact is
    on disk under `.context/iqrsqpi/<walk_id>/`; and no recorded claim states
    a number without naming a source.

    `repo` may be a `catalog.Repo`, a `str`, or a `Path` — anything that says
    where the tree is. Each artifact's claims are audited once, attributed to
    the stage that owns that artifact, so a document two stages both demand is
    never counted twice.

    A walk directory that does not exist at all is reported as the first
    artifact its first reached stage demands — no separate code, no silence.
    """
    if str(verifier) == str(generator):
        raise StageError("verifier_is_generator")
    if not str(verifier).strip() or not str(generator).strip():
        raise StageError("verifier_and_generator_must_be_named")

    ok, detail = stage_order_ok(stages)
    if not ok:
        raise StageError(f"stage_out_of_order:{detail}")
    reached = [normalize_stage(t) for t in stages]

    walk_dir = _root_of(repo) / WALK_ROOT / str(walk_id)
    manifest = _read_json(walk_dir / "run.json")
    artifacts: dict[str, list[str]] = {}
    claims_checked = 0
    audited: set[str] = set()
    for stage in reached:
        found = []
        for name in STAGE_ARTIFACTS[stage]:
            hit = _artifact_path(walk_dir, name)
            if hit is None:
                raise StageError(f"artifact_missing:{name}")
            found.append(str(hit.relative_to(walk_dir)))
            if name not in audited:
                audited.add(name)
                owner = ARTIFACT_OWNER.get(name)
                claims_checked += _audit_claims(
                    _claims_in(_read_json(hit)),
                    owner if owner in reached else stage)
        claims_checked += _audit_claims(
            _claims_for(manifest, stage), stage)
        artifacts[stage] = found

    return {"walk_id": str(walk_id), "ok": True,
            "stages": reached, "reached": len(reached),
            "verifier": str(verifier), "generator": str(generator),
            "artifacts": artifacts, "claims_checked": claims_checked,
            "walk_dir": str(walk_dir)}


def gate_stage_order(repo) -> tuple[bool, str]:
    """Hermetic certify gate: the recorded pass is in canonical stage order.

    Reads one committed fixture and nothing else. Never raises — a missing or
    unparseable fixture is a RED with the reason, never a silent green.
    """
    path = _root_of(repo) / GATE_FIXTURE
    try:
        if not path.is_file():
            return False, f"fixture_missing:{GATE_FIXTURE}"
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            return False, f"fixture_not_an_object:{GATE_FIXTURE}"
        stages = doc.get("stages")
        if not isinstance(stages, list):
            return False, "fixture_stages_missing"
        tokens = [s.get("stage") if isinstance(s, dict) else s for s in stages]
        return stage_order_ok(tokens)
    except json.JSONDecodeError as exc:
        return False, f"fixture_unparseable:{exc.msg}@line{exc.lineno}"
    except OSError as exc:
        return False, f"fixture_unreadable:{exc.strerror or exc}"
    except Exception as exc:                                    # noqa: BLE001
        return False, f"fixture_error:{type(exc).__name__}:{exc}"


# ------------------------------------------------------------- internals

def _root_of(repo) -> Path:
    """The root of a `catalog.Repo`, a path string, or a `Path`.

    A path-like argument is checked FIRST on purpose: `Path("/abs").root` is
    `"/"`, so consulting `.root` on a Path silently walks up to the filesystem
    root and reads fixtures nobody handed us.
    """
    if isinstance(repo, (str, os.PathLike)):
        return Path(repo)
    return Path(repo.root)


def _artifact_path(walk_dir: Path, name: str) -> Path | None:
    """An artifact is a `.json`, a `.md`, or a directory holding a file."""
    for cand in (walk_dir / f"{name}.json", walk_dir / f"{name}.md"):
        if cand.is_file():
            return cand
    d = walk_dir / name
    if d.is_dir() and any(p.is_file() for p in sorted(d.iterdir())):
        return d
    return None


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    except (json.JSONDecodeError, OSError):
        return None


def _claims_in(payload) -> list:
    """Claims a payload records, tolerating both claim shapes."""
    if isinstance(payload, dict):
        raw = payload.get("claims")
    elif isinstance(payload, list):
        raw = payload
    else:
        raw = None
    return list(raw) if isinstance(raw, list) else []


def _claims_for(manifest, stage: str) -> list:
    """Claims the walk manifest attributes to one canonical stage."""
    if not isinstance(manifest, dict):
        return []
    out = []
    rows = manifest.get("stages")
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            token = row.get("stage") if "stage" in row else row.get("step")
            try:
                if normalize_stage(token) == stage:
                    out.extend(_claims_in(row))
            except StageError:
                continue
    if isinstance(rows, dict) and isinstance(rows.get(stage), dict):
        out.extend(_claims_in(rows[stage]))
    return out


def _is_numeric(claim) -> bool:
    value = claim.get("value")
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str) and _NUMBER_RE.fullmatch(value.strip()):
        return True
    return bool(_NUMBER_RE.search(str(claim.get("claim", ""))))


def _has_source(claim) -> bool:
    src = claim.get("source")
    if isinstance(src, str):
        return bool(src.strip())
    if isinstance(src, (list, tuple)):
        return bool(src) and all(
            isinstance(s, str) and s.strip() for s in src)
    if isinstance(src, dict):
        return bool(str(src.get("path") or src.get("ref") or "").strip())
    return False


def _audit_claims(claims: list, stage: str) -> int:
    """Every number in this stage names a source, or the stage is refused."""
    for claim in claims:
        if isinstance(claim, dict) and _is_numeric(claim) and not _has_source(claim):
            raise StageError(f"no_source_no_number:{stage}")
    return len(claims)
