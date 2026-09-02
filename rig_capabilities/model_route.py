"""Dormant-by-default Claude Fable 5.1 route: dry-run plan, gated apply, ladder audits.

Three registries, one transaction, one Gate-D approval. Nothing here promotes a
model — the route lands DORMANT and only a strictly lower `E_stage` on a Studio's
own golden run may lift it (card: "Promotion gate — nothing ships at 0σ").

Every path resolves AT CALL TIME and `RIG_ROUTE_TARGETS_ROOT` redirects the three
targets into repo fixtures, so a certify gate can read this module's data hermetically
(L1) without ever touching `~/.hermes` or `~/.rig/grokbot-router`.

The YAML handling is a deliberate line-level reader/rewriter, not a parser: it only
understands the three structures it must touch (registry `providers:`, Hermes
`providers:` block, LiteLLM `model_list:` / `router_settings:` chains) and copies
every other line byte-for-byte. Unrelated lines are never restyled or reordered.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

# --- frozen identity -------------------------------------------------------
FABLE_MODEL_ID = "claude-fable-5-1"
FABLE_DEPLOYMENT = "rig-fable51"

# The card's verified specs — nothing here is invented.
FABLE_FAMILY = "claude-fable"      # prefix: catches claude-fable-5 and claude-fable-5-1
FABLE_EFFORT = "high"
FABLE_CONTEXT = 1000000
FABLE_MAX_OUTPUT = 128000
FABLE_COST_IN = 10.0
FABLE_COST_OUT = 50.0
FABLE_PROMOTION_GATE = "DORMANT_PER_STUDIO_UNTIL_E_STAGE_LOWER_THAN_OPUS5"
FABLE_PROMOTION_NOTE = ("golden-run replay per Studio must record E_stage strictly lower than "
                        "Opus 5 on that Studio's own missions before the model enters a "
                        "tool-allowlist; a Studio that does not drop stays Opus 5")

GATE_D_ACTION = "route-projection"

# --- default (live) targets; overridable per call --------------------------
HOME = Path.home()
REGISTRY_PATH = HOME / ".rig" / "agent-doctrine" / "registries" / "model_registry.yaml"
HERMES_CONFIG = HOME / ".hermes" / "config.yaml"
LITELLM_CONFIG = HOME / ".rig" / "grokbot-router" / "litellm.yaml"
OMP_CONFIG = HOME / ".omp" / "agent" / "config.yml"
PROOF_DIR = HOME / ".rig" / "proof"

# Explicitly out of scope for this route projection — listed so plan() can say so.
UNTOUCHED = ("~/.claude/settings.json",
             "~/.rig/lobe-gateway/rig_lobe_gateway.py",
             "~/.rig/config/omp-flash-default.yml",
             "~/.rig/route-table.json")

ROUTES_ENV = "RIG_ROUTE_TARGETS_ROOT"
PROOF_ENV = "RIG_PROOF_ROOT"
FIXTURE_DIR = Path("tests") / "fixtures" / "fable2031" / "routes"
LITELLM_FIXTURE = FIXTURE_DIR / "litellm.yaml"
_FIXTURE_NAMES = {"registry": "model_registry.yaml",
                  "hermes": "config.yaml",
                  "litellm": "litellm.yaml"}

# Hermes starvation bug being closed: one value everywhere.
HERMES_BUG_MAX_TOKENS = 512

HARNESS_SUFFIXES = (".yaml", ".yml", ".json", ".md", ".toml")
SCAN_SKIP = frozenset((".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"))
MAX_SCAN_FILES = 5000
MAX_SCAN_BYTES = 1_000_000
TOOL_CHOICE_RE = re.compile(r"""(?<![A-Za-z0-9_])['\"]?tool_choice['\"]?\s*[:=]\s*(?P<val>.+?)\s*$""")
UNFORCED_VALUES = ("", "auto", "none", '""', "''")


class RouteGateError(Exception):
    """Route projection refused. Nothing was written when this is raised."""


# --------------------------------------------------------------------------
# call-time path resolution (L1)
# --------------------------------------------------------------------------
def targets_root() -> Path | None:
    """$RIG_ROUTE_TARGETS_ROOT when set; None means the live targets."""
    raw = (os.environ.get(ROUTES_ENV) or "").strip()
    return Path(raw).expanduser() if raw else None


def proof_root() -> Path:
    """$RIG_PROOF_ROOT when set, else ~/.rig/proof."""
    raw = (os.environ.get(PROOF_ENV) or "").strip()
    return Path(raw).expanduser() if raw else PROOF_DIR


def _target(name: str, live: Path) -> Path:
    root = targets_root()
    return (root / _FIXTURE_NAMES[name]) if root else live


def registry_path() -> Path:
    """model_registry.yaml at call time."""
    return _target("registry", REGISTRY_PATH)


def hermes_config() -> Path:
    """Hermes config.yaml at call time."""
    return _target("hermes", HERMES_CONFIG)


def litellm_config() -> Path:
    """LiteLLM router config at call time."""
    return _target("litellm", LITELLM_CONFIG)


def omp_config() -> Path:
    """OMP agent config — read by plan() for disclosure, never edited."""
    raw = (os.environ.get("RIG_OMP_CONFIG") or "").strip()
    return Path(raw).expanduser() if raw else OMP_CONFIG


def gate_d_path(run_id: str) -> Path:
    return proof_root() / f"gate-d-{run_id}.json"


def targets() -> list[tuple[str, Path]]:
    return [("registry", registry_path()),
            ("hermes", hermes_config()),
            ("litellm", litellm_config())]


# --------------------------------------------------------------------------
# minimal line-level YAML reader (no third-party parser, no full parse)
# --------------------------------------------------------------------------
def _indent(raw: str) -> int:
    return len(raw) - len(raw.lstrip(" "))


def _blank(raw: str) -> bool:
    return not raw.strip()


def _skip_blanks(lines: list[str], i: int, end: int, backwards: bool = False) -> int:
    step = -1 if backwards else 1
    while 0 <= i < end and _blank(lines[i]):
        i += step
    return i


def find_key(lines: list[str], key: str, indent: int, start: int = 0,
             end: int | None = None) -> int:
    """Index of `key:` at exactly `indent`, else -1."""
    pat = re.compile(r"^(" + re.escape(key) + r")(\s*:|:)(\s|$)")
    hi = len(lines) if end is None else end
    for j in range(start, hi):
        raw = lines[j]
        if _blank(raw) or raw.lstrip().startswith("#"):
            continue
        if _indent(raw) != indent:
            continue
        if pat.match(raw.strip()):
            return j
    return -1


def block_end(lines: list[str], idx: int, indent: int, end: int | None = None) -> int:
    """First line after `idx` that leaves `idx`'s block (dedented to <= indent)."""
    hi = len(lines) if end is None else end
    for j in range(idx + 1, hi):
        if _blank(lines[j]):
            continue
        if _indent(lines[j]) <= indent:
            return j
    return hi


def find_key_path(lines: list[str], key_path) -> tuple[int, int] | None:
    """Walk a key path by NAME (never by line number). -> (index, indent) | None.

    Children are found at the shallowest indent deeper than the parent's, which is
    how both target files nest (2-space steps) without hardcoding depth per level.
    """
    start, end, parent_indent = 0, len(lines), -1
    idx = -1
    for depth, key in enumerate(key_path):
        pat = re.compile(r"^(?:-\s+)?" + re.escape(key) + r"(\s*:|:)(\s|$)")
        best: tuple[int, int] | None = None
        for j in range(start, end):
            raw = lines[j]
            if _blank(raw) or raw.lstrip().startswith("#"):
                continue
            ind = _indent(raw)
            if ind <= parent_indent:
                break
            if pat.match(raw.strip()) and (best is None or ind < best[0]):
                best = (ind, j)
        if best is None:
            return None
        parent_indent, idx = best
        if depth == len(key_path) - 1:
            return idx, parent_indent
        start = idx + 1
        end = block_end(lines, idx, parent_indent)
    return None


def inline_value(raw: str) -> str:
    """Value after the first `:` on a mapping line, '' when the value is a block."""
    stripped = raw.strip()
    if stripped.startswith("- "):
        stripped = stripped[2:].strip()
    head, sep, tail = stripped.partition(":")
    return tail.strip() if sep else ""


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp-rig-route")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


# --------------------------------------------------------------------------
# the three projections (pure text -> text; never write here)
# --------------------------------------------------------------------------
def _registry_entry_lines() -> list[str]:
    return [
        f"  {FABLE_MODEL_ID}:",
        "    lane: Anthropic",
        "    route: cloud",
        "    api: anthropic_messages",
        f"    default_model: {FABLE_MODEL_ID}",
        f"    context_window: {FABLE_CONTEXT}",
        f"    max_output_tokens: {FABLE_MAX_OUTPUT}",
        f"    effort: {FABLE_EFFORT}",
        "    default: false",
        f"    cost_per_mtok: {{ input: {FABLE_COST_IN}, output: {FABLE_COST_OUT} }}",
        "    models:",
        f"      - {FABLE_MODEL_ID}",
        f"    promotion_gate: {FABLE_PROMOTION_GATE}",
        f"    promotion_note: {FABLE_PROMOTION_NOTE}",
    ]


def _insert_block(lines: list[str], start: int, end: int,
                  entry: list[str]) -> tuple[list[str], int]:
    """Insert `entry` at the end of [start, end), preserving blank separation."""
    j = end
    while j - 1 > start and _blank(lines[j - 1]):
        j -= 1
    block = [""] + list(entry)
    out = lines[:j] + block + lines[j:]
    return out, j


def project_registry(text: str) -> tuple[str, list[dict]]:
    """Add `claude-fable-5-1` under `providers:`; never restate another entry."""
    changes: list[dict] = []
    lines = text.split("\n")
    pi = find_key(lines, "providers", 0)
    if pi < 0:
        changes.append({"action": "blocked", "reason": "providers_block_missing"})
        return text, changes
    pend = block_end(lines, pi, 0)
    if find_key(lines, FABLE_MODEL_ID, 2, pi + 1, pend) >= 0:
        changes.append({"action": "noop", "reason": "registry_entry_present",
                        "key": FABLE_MODEL_ID})
        return text, changes
    out, at = _insert_block(lines, pi + 1, pend, _registry_entry_lines())
    changes.append({"action": "add", "where": "providers", "key": FABLE_MODEL_ID,
                    "lines": len(_registry_entry_lines()),
                    "fields": ["promotion_gate", "default", "context_window",
                               "max_output_tokens", "effort", "cost_per_mtok"]})
    return "\n".join(out), changes


def _hermes_provider_block(lines: list[str]) -> tuple[int, int, int]:
    """-> (providers_idx, rig-fable5_idx, block_end). -1s when absent."""
    pi = find_key(lines, "providers", 0)
    if pi < 0:
        return -1, -1, -1
    pend = block_end(lines, pi, 0)
    fi = find_key(lines, "rig-fable5", 2, pi + 1, pend)
    if fi < 0:
        return pi, -1, -1
    return pi, fi, block_end(lines, fi, 2)


def _fable_block_new_lines(block: list[str]) -> list[str]:
    """Clone a provider block body for rig-fable51: model id, name, cap corrected."""
    out: list[str] = []
    for raw in block:
        s = re.sub(r"(^|[^A-Za-z0-9._-])claude-fable-5(?!-1)",
                   lambda m: m.group(1) + FABLE_MODEL_ID, raw)
        s = re.sub(r"^(\s*max_tokens:\s*)\d+\s*$",
                   lambda m: m.group(1) + str(FABLE_MAX_OUTPUT), s)
        s = re.sub(r"^(\s*name:\s*).*$",
                   lambda m: m.group(1) + "Claude Fable 5.1 \u00b7 Anthropic "
                                          "subscription gateway", s)
        out.append(s)
    return out


def project_hermes(text: str) -> tuple[str, list[dict]]:
    """Provider `rig-fable51` modelled on `rig-fable5`; 512 -> 128000 output fix."""
    changes: list[dict] = []
    lines = text.split("\n")
    pi, fi, fend = _hermes_provider_block(lines)
    if pi < 0:
        changes.append({"action": "blocked", "reason": "providers_block_missing"})
        return text, changes
    if fi < 0:
        changes.append({"action": "blocked", "reason": "rig_fable5_block_missing"})
        return text, changes
    pend = block_end(lines, pi, 0)
    if find_key(lines, FABLE_DEPLOYMENT, 2, pi + 1, pend) >= 0:
        changes.append({"action": "noop", "reason": "provider_present",
                        "key": FABLE_DEPLOYMENT})
        return text, changes

    # (a) correct the starvation bug inside the existing rig-fable5 block.
    fixed: list[str] = []
    for j in range(fi + 1, fend):
        raw = lines[j]
        m = re.match(r"^(\s*max_tokens:\s*)(\d+)(\s*)$", raw)
        if m and int(m.group(2)) == HERMES_BUG_MAX_TOKENS:
            fixed.append("%s%d%s" % (m.group(1), FABLE_MAX_OUTPUT, m.group(3)))
            lines[j] = fixed[-1]
            changes.append({"action": "edit", "key": "rig-fable5.max_tokens",
                            "from": HERMES_BUG_MAX_TOKENS, "to": FABLE_MAX_OUTPUT})
    if not fixed:
        has_any = any(re.match(r"^\s*max_tokens:\s*\d+", lines[j])
                      for j in range(fi + 1, fend))
        if has_any:
            changes.append({"action": "noop", "key": "rig-fable5.max_tokens",
                            "note": "already_above_512"})
        else:
            # no output cap at all: add one at the block's deepest mapping indent
            best_ind, best_idx = _indent(lines[fi]) + 1, -1
            for j in range(fi + 1, fend):
                if _blank(lines[j]):
                    continue
                if _indent(lines[j]) >= best_ind:
                    best_ind, best_idx = _indent(lines[j]), j
            if best_idx < 0:
                changes.append({"action": "blocked", "reason": "no_model_mapping"})
                return text, changes
            lines.insert(best_idx + 1, " " * best_ind
                         + f"max_tokens: {FABLE_MAX_OUTPUT}")
            fend += 1
            changes.append({"action": "edit", "key": "rig-fable5.max_tokens",
                            "from": None, "to": FABLE_MAX_OUTPUT, "note": "inserted"})

    # (b) append the new provider, modelled on the (now corrected) block.
    _, fi2, fend2 = _hermes_provider_block(lines)
    block = lines[fi2 + 1:fend2]
    clone = [f"  {FABLE_DEPLOYMENT}:"] + _fable_block_new_lines(block)
    out, _at = _insert_block(lines, pi + 1, pend, clone)
    changes.append({"action": "add", "where": "providers", "key": FABLE_DEPLOYMENT,
                    "modelled_on": "rig-fable5",
                    "max_tokens": FABLE_MAX_OUTPUT, "lines": len(clone)})
    return "\n".join(out), changes


def _litellm_deployment_lines() -> list[str]:
    return [
        f"  - model_name: {FABLE_DEPLOYMENT}",
        "    litellm_params:",
        f"      model: anthropic/{FABLE_MODEL_ID}",
        "      api_key: os.environ/ANTHROPIC_API_KEY",
        "      timeout: 180",
    ]


def _router_slice(text: str) -> str:
    """The `router_settings:` section, for the mechanical fallback guarantee."""
    lines = text.split("\n")
    ri = find_key(lines, "router_settings", 0)
    if ri < 0:
        return ""
    return "\n".join(lines[ri:block_end(lines, ri, 0)])


def project_litellm(text: str) -> tuple[str, list[dict]]:
    """Deployment `rig-fable51` under `model_list:` — in NEITHER fallback ladder."""
    changes: list[dict] = []
    lines = text.split("\n")
    mi = find_key(lines, "model_list", 0)
    if mi < 0:
        changes.append({"action": "blocked", "reason": "model_list_block_missing"})
        return text, changes
    mend = block_end(lines, mi, 0)
    if any(re.match(r"^\s*-\s*model_name:\s*" + re.escape(FABLE_DEPLOYMENT) + r"\s*$", raw)
           for raw in lines[mi + 1:mend]):
        changes.append({"action": "noop", "reason": "deployment_present",
                        "key": FABLE_DEPLOYMENT})
        return text, changes
    out, _at = _insert_block(lines, mi + 1, mend, _litellm_deployment_lines())
    new = "\n".join(out)
    if _router_slice(new) != _router_slice(text):
        changes.append({"action": "blocked",
                        "reason": "fallback_ladders_were_touched"})
        return text, changes
    changes.append({"action": "add", "where": "model_list", "key": FABLE_DEPLOYMENT,
                    "model": f"anthropic/{FABLE_MODEL_ID}",
                    "fallback_lists": "none", "lines": len(_litellm_deployment_lines())})
    return new, changes


_PROJECTORS = {"registry": project_registry,
               "hermes": project_hermes,
               "litellm": project_litellm}


def project(name: str, text: str) -> tuple[str, list[dict]]:
    """Pure projection for one named target — exported for plan()/tests."""
    return _PROJECTORS[name](text)


# --------------------------------------------------------------------------
# audits
# --------------------------------------------------------------------------
def _chain_aliases(lines: list[str], start: int, end: int) -> list[str]:
    """Every alias string named inside a fallback list block."""
    out: list[str] = []
    for j in range(start, end):
        raw = lines[j]
        if _blank(raw) or raw.lstrip().startswith("#"):
            continue
        body = raw.strip()
        if body.startswith("- "):
            body = body[2:].strip()
        elif body.startswith("-"):
            body = body[1:].strip()
        else:
            continue
        if body.startswith("[") and body.endswith("]"):
            out.extend(t.strip().strip("'\"")
                       for t in body[1:-1].split(",") if t.strip())
            continue
        head = body.split(":", 1)[0].strip().strip("'\"")
        if head:
            out.append(head)
    return out


def alias_models(lines: list[str]) -> dict[str, str]:
    """model_list deployment alias -> litellm_params.model."""
    out: dict[str, str] = {}
    mi = find_key(lines, "model_list", 0)
    if mi < 0:
        return out
    mend = block_end(lines, mi, 0)
    cur: str | None = None
    for j in range(mi + 1, mend):
        raw = lines[j]
        if _blank(raw):
            continue
        m = re.match(r"^\s*-\s*model_name:\s*(\S+)\s*$", raw)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"^\s+model:\s*(\S+)\s*$", raw)
        if m and cur is not None and cur not in out:
            out[cur] = m.group(1)
    return out


_CHAIN_NAMES = ("fallbacks", "context_window_fallbacks")


def audit_fallback_ladders(root=None) -> dict:
    """Deployment-alias audit: Fable must be unreachable by any fallback ladder.

    Checks the DEPLOYMENT ALIAS (`rig-fable51`), not the raw model id, then resolves
    every alias named in a chain through `model_list[].litellm_params.model` so an
    alias that points at `claude-fable-5-1` cannot smuggle it in.
    """
    path = Path(root).expanduser() if root else litellm_config()
    if path.is_dir():
        path = path / "litellm.yaml"
    report = {"ok": True, "path": str(path), "exists": path.is_file(),
              "chains": [], "alias_models": {}, "reasons": [],
              "governance_incident": False}
    if not path.is_file():
        report.update(ok=False, reasons=[f"litellm_config_missing:{path}"],
                      governance_incident=True)
        return report
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
    except OSError as exc:
        report.update(ok=False, reasons=[f"litellm_config_unreadable:{exc.__class__.__name__}"],
                      governance_incident=True)
        return report

    models = alias_models(lines)
    report["alias_models"] = models
    ri = find_key(lines, "router_settings", 0)
    if ri >= 0:
        rend = block_end(lines, ri, 0)
        for name in _CHAIN_NAMES:
            ci = find_key(lines, name, 2, ri + 1, rend)
            if ci < 0:
                continue
            cend = block_end(lines, ci, 2)
            aliases = _chain_aliases(lines, ci + 1, cend)
            deployment_hits = sorted({a for a in aliases if a == FABLE_DEPLOYMENT})
            model_hits = sorted({a for a in aliases
                                 if FABLE_MODEL_ID in models.get(a, "")})
            id_hits = sorted({a for a in aliases if FABLE_MODEL_ID in a})
            entry = {"chain": f"router_settings.{name}", "line": ci + 1,
                     "aliases": aliases, "deployment_hits": deployment_hits,
                     "model_id_hits": id_hits, "resolved_model_hits": model_hits}
            report["chains"].append(entry)
            if deployment_hits:
                report["reasons"].append(f"{name}:deployment_alias_reachable:{FABLE_DEPLOYMENT}")
            if id_hits:
                report["reasons"].append(f"{name}:model_id_named_in_chain:{FABLE_MODEL_ID}")
            if model_hits:
                report["reasons"].append(
                    f"{name}:alias_resolves_to_fable:{','.join(model_hits)}")
    # No `default:` sweep here: the dormancy contract is the promotion_gate field in
    # the registry and the absence of the alias from every ladder, both checked above.
    report["ok"] = not report["reasons"]
    report["governance_incident"] = not report["ok"]
    return report


def _repo_root(repo) -> Path:
    """Repo-shaped, Path, or str -> repo root. Path.root is '/', so never trust it."""
    if isinstance(repo, (str, os.PathLike)):
        return Path(repo)
    root = getattr(repo, "root", None)
    if root is None:
        raise TypeError("repo must be Repo-shaped, str, or PathLike")
    return Path(root)


def gate_fable_dormant(repo) -> tuple[bool, str]:
    """Hermetic certify gate: the FIXTURE ladder keeps Fable out of every chain.

    Reads only <repo.root>/tests/fixtures/fable2031/routes/litellm.yaml — never live
    config (L1) — and never raises: a missing fixture is a red, not an exception.
    Accepts a catalog.Repo, a Repo-shaped stub, a Path, or a str.
    """
    try:
        path = _repo_root(repo) / FIXTURE_DIR / "litellm.yaml"
        if not path.is_file():
            return False, f"fixture_missing:{path}"
        report = audit_fallback_ladders(path)
        if report["ok"]:
            named = sorted({a for chain in report["chains"] for a in chain["aliases"]})
            return True, (f"dormant: {FABLE_DEPLOYMENT} absent from "
                          f"{len(report['chains'])} ladder(s) over {len(named)} alias(es)")
        return False, ";".join(report["reasons"])
    except Exception as exc:  # a gate must never raise
        return False, f"gate_error:{exc.__class__.__name__}:{exc}"


def audit_forced_tool_choice(roots) -> dict:
    """Breaking change #1: forced `tool_choice` returns an error on Fable 5.1.

    Any reachable harness that names the Fable family and pins `tool_choice` to
    something other than `auto`/`none` fails closed → promotion must be blocked.
    """
    if isinstance(roots, (str, Path)):
        roots = [roots]
    files: list[Path] = []
    for raw in roots or []:
        p = Path(raw).expanduser()
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for path in sorted(p.rglob("*")):
                if path.is_file() and path.suffix in HARNESS_SUFFIXES:
                    if SCAN_SKIP.intersection(part for part in path.parts):
                        continue
                    files.append(path)
    files = files[:MAX_SCAN_FILES]
    findings: list[dict] = []
    fable_files = 0
    scanned = 0
    for path in files:
        try:
            if path.stat().st_size > MAX_SCAN_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        if FABLE_FAMILY not in text.lower():
            continue
        fable_files += 1
        for n, raw in enumerate(text.split("\n"), 1):
            m = TOOL_CHOICE_RE.search(raw)
            if not m:
                continue
            val = m.group("val").strip().strip("'\"").strip()
            if val.lower() in UNFORCED_VALUES:
                continue
            findings.append({"path": str(path), "line": n,
                             "declaration": raw.strip(), "tool_choice": val})
    report = {"ok": not findings, "roots": [str(Path(r).expanduser()) for r in roots or []],
              "files_scanned": scanned, "fable_files": fable_files,
              "forced_tool_choice": findings}
    report["reasons"] = ([f"forced_tool_choice_in_fable_harness:{len(findings)}"]
                         if findings else [])
    report["promotion_blocked"] = bool(findings)
    return report


def audit_omp_designer_binding(path=None) -> dict:
    """The ungoverned route: OMP pins a designer role to the Fable family.

    Located BY KEY PATH (`modelRoles.designer`, `task.agentModelOverrides.designer`);
    the recorded line numbers are the ones actually observed on disk this run.
    """
    p = Path(path).expanduser() if path else omp_config()
    out = {"detected": False, "file": str(p), "exists": p.is_file(),
           "bindings": [], "other_fable_references": [],
           "file_edited": False,
           "gate_d_followup": ("bringing the OMP designer binding under the dormancy "
                               "policy is a named Gate-D follow-up; this projection "
                               "does not edit this file"),
           "scope": ("the dormant-by-default claim is scoped to the three route "
                     "registries (model_registry / hermes config / litellm)")}
    if not p.is_file():
        out["reason"] = f"omp_config_missing:{p}"
        return out
    try:
        lines = p.read_text(encoding="utf-8").split("\n")
    except OSError as exc:
        out["reason"] = f"omp_config_unreadable:{exc.__class__.__name__}"
        return out
    hit_lines = set()
    for key_path in (["modelRoles", "designer"],
                     ["task", "agentModelOverrides", "designer"]):
        found = find_key_path(lines, key_path)
        if found is None:
            continue
        idx, _ind = found
        value = inline_value(lines[idx])
        binding = {"key_path": ".".join(key_path), "line": idx + 1, "value": value}
        if FABLE_FAMILY in value.lower():
            out["detected"] = True
            binding["fable_family"] = True
        out["bindings"].append(binding)
        hit_lines.add(idx)
    for idx, raw in enumerate(lines):
        if idx in hit_lines or FABLE_FAMILY not in raw.lower():
            continue
        out["other_fable_references"].append({"line": idx + 1, "text": raw.strip()})
    return out


# --------------------------------------------------------------------------
# Gate-D
# --------------------------------------------------------------------------
def _gate_d(run_id: str, max_budget_usd) -> dict:
    """Read and adjudicate the Gate-D artifact. Raises before anything is written."""
    if run_id is None or not str(run_id).strip():
        raise RouteGateError("gate_d_required")
    path = gate_d_path(run_id)
    if not path.is_file():
        raise RouteGateError("gate_d_required")
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RouteGateError(f"gate_d_unreadable:{exc.__class__.__name__}") from exc
    if not isinstance(rec, dict):
        raise RouteGateError("gate_d_required")
    if str(rec.get("status") or "").upper() != "APPROVED":
        raise RouteGateError("gate_d_required")
    if str(rec.get("action") or "") != GATE_D_ACTION:
        raise RouteGateError(f"gate_d_action_mismatch:{rec.get('action')}")
    cap = rec.get("max_budget_usd")
    if cap is None:
        raise RouteGateError("gate_d_required")
    try:
        cap_f, want_f = float(cap), float(max_budget_usd)
    except (TypeError, ValueError):
        raise RouteGateError("gate_d_budget_unparseable") from None
    if want_f <= 0:
        raise RouteGateError("budget_required")
    if want_f > cap_f:
        raise RouteGateError(f"budget_exceeds_gate_d_cap:{want_f}>{cap_f}")
    return {"run_id": str(run_id), "path": str(path), "action": GATE_D_ACTION,
            "approved_budget_usd": cap_f, "requested_budget_usd": want_f,
            "model_id": str(rec.get("model_id") or FABLE_MODEL_ID)}


# --------------------------------------------------------------------------
# plan / apply / verify
# --------------------------------------------------------------------------
def _read_target(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def plan(repo) -> dict:
    """Dry run: exactly what would change, and what is ungoverned. NEVER writes."""
    out: dict = {"dry_run": True, "writes": False, "model_id": FABLE_MODEL_ID,
                 "deployment": FABLE_DEPLOYMENT,
                 "promotion_gate": FABLE_PROMOTION_GATE,
                 "targets": [], "blocked": [], "untouched": list(UNTOUCHED),
                 "route_targets_root": (str(targets_root()) if targets_root() else None)}
    for name, path in targets():
        entry = {"name": name, "path": str(path), "exists": path.is_file(),
                 "actions": []}
        entry["writable"] = bool(path.is_file() and os.access(path, os.W_OK))
        if not entry["exists"]:
            entry["actions"] = [{"action": "blocked", "reason": "target_missing"}]
            out["blocked"].append(f"{name}:target_missing")
            out["targets"].append(entry)
            continue
        try:
            text = _read_target(path)
        except OSError as exc:
            entry["actions"] = [{"action": "blocked",
                                 "reason": f"unreadable:{exc.__class__.__name__}"}]
            out["blocked"].append(f"{name}:unreadable")
            out["targets"].append(entry)
            continue
        new, changes = _PROJECTORS[name](text)
        entry["sha256_before"] = _sha(text)
        entry["sha256_after"] = _sha(new)
        entry["actions"] = changes
        entry["changed"] = new != text
        for ch in changes:
            if ch.get("action") == "blocked":
                out["blocked"].append(f"{name}:{ch['reason']}")
        entry["bytes_before"] = len(text.encode("utf-8"))
        entry["bytes_after"] = len(new.encode("utf-8"))
        out["targets"].append(entry)
    out["fable_spec"] = {"context": FABLE_CONTEXT, "max_output": FABLE_MAX_OUTPUT,
                         "effort": FABLE_EFFORT, "default": False,
                         "cost_per_mtok": {"input": FABLE_COST_IN,
                                           "output": FABLE_COST_OUT}}
    out["hermes_starvation_fix"] = {"rig-fable5.max_tokens":
                                    [HERMES_BUG_MAX_TOKENS, FABLE_MAX_OUTPUT],
                                    "adapter_advertises": FABLE_MAX_OUTPUT}
    out["ungoverned_route_detected"] = audit_omp_designer_binding()
    out["fallback_audit"] = audit_fallback_ladders()
    out["tool_choice_audit"] = None
    out["gate_d"] = {"path_template": str(proof_root() / "gate-d-<run_id>.json"),
                     "required": {"status": "APPROVED", "action": GATE_D_ACTION,
                                  "max_budget_usd": "<approved cap>"},
                     "grants": "projection only — never a promotion"}
    out["promotion"] = {"mechanism": "E_stage strictly lower than Opus 5 per Studio",
                        "state": "DORMANT", "auto_fallback_to_earlier_family": False,
                        "note": FABLE_PROMOTION_NOTE}
    out["ok"] = bool(out["fallback_audit"]["ok"] and not out["blocked"])
    return out


def apply(repo, *, gate_d_run_id, max_budget_usd,
          expected_hashes: dict | None = None) -> dict:
    """ONE transaction over the three targets. Backup before every write.

    Refuses with nothing written when Gate-D is absent, a target is unwritable or
    missing, or a precondition hash is stale. A mid-transaction failure restores
    every backup it made.
    """
    gate = _gate_d(gate_d_run_id, max_budget_usd)

    # 1. pre-flight: every target readable, writable, and hash-stable.
    before: dict[str, str] = {}
    resolved: list[tuple[str, Path]] = []
    for name, path in targets():
        if not path.is_file():
            raise RouteGateError(f"target_missing:{name}")
        if not os.access(path, os.W_OK):
            raise RouteGateError(f"target_unwritable:{name}")
        text = _read_target(path)
        digest = _sha(text)
        if expected_hashes is not None:
            want = expected_hashes.get(name) or expected_hashes.get(str(path))
            if want and want != digest:
                raise RouteGateError(f"stale_precondition:{name}")
        before[name] = digest
        resolved.append((name, path))

    # 2. compute every projection before touching disk; a blocked plan aborts here.
    proposed: dict[str, str] = {}
    actions: dict[str, list[dict]] = {}
    for name, path in resolved:
        new, changes = _PROJECTORS[name](_read_target(path))
        for ch in changes:
            if ch.get("action") == "blocked":
                raise RouteGateError(f"projection_blocked:{name}:{ch['reason']}")
        proposed[name], actions[name] = new, changes

    # 3. re-check at the write boundary — the precondition must still hold.
    for name, path in resolved:
        if _sha(_read_target(path)) != before[name]:
            raise RouteGateError(f"stale_precondition:{name}")

    # 4. write: backup immediately before each atomic replace; restore all on failure.
    stamp = _now_stamp()
    written: list[tuple[str, Path, Path, str]] = []
    backups: list[str] = []
    unchanged: list[str] = []
    current = resolved[0][0] if resolved else "none"
    try:
        for name, path in resolved:
            current = name
            if proposed[name] == _read_target(path):
                unchanged.append(name)
                continue
            bak = path.with_name(f"{path.name}.bak-{stamp}")
            shutil.copy2(path, bak)
            backups.append(str(bak))
            _atomic_write(path, proposed[name])
            written.append((name, path, bak, _sha_file(path)))
    except Exception as exc:
        failed = current
        restored: list[str] = []
        for _name, path, bak, _sha_after in written:
            try:
                shutil.copy2(bak, path)
                restored.append(str(path))
            except OSError:
                pass
        raise RouteGateError(
            f"transaction_failed_restored:{failed}:{exc.__class__.__name__};"
            f"restored={len(restored)}") from exc

    return {"ok": True, "dry_run": False, "gate_d": gate,
            "applied": [n for n, _p, _b, _h in written],
            "unchanged": unchanged, "backups": backups,
            "sha_before": before,
            "sha_after": {**{n: h for n, _p, _b, h in written},
                          **{n: before[n] for n in unchanged}},
            "actions": actions,
            "fallback_audit": audit_fallback_ladders(),
            "promotion": {"state": "DORMANT", "gate": FABLE_PROMOTION_GATE},
            "untouched": list(UNTOUCHED)}


def verify_projection(repo) -> dict:
    """Does the projected route actually exist in each target, and stay dormant?"""
    checks: dict[str, bool] = {}
    paths: dict[str, str] = {}
    for name, path in targets():
        paths[name] = str(path)
        if not path.is_file():
            checks[f"{name}_present"] = False
            continue
        text = _read_target(path)
        if name == "registry":
            checks["registry_model_present"] = bool(
                re.search(r"^  " + re.escape(FABLE_MODEL_ID) + r":\s*$", text, re.M))
            checks["registry_promotion_gate_dormant"] = (
                FABLE_PROMOTION_GATE in text)
        elif name == "hermes":
            checks["hermes_provider_present"] = bool(
                re.search(r"^  " + re.escape(FABLE_DEPLOYMENT) + r":\s*$", text, re.M))
            _pi, fi, fend = _hermes_provider_block(text.split("\n"))
            checks["hermes_starvation_fixed"] = not (
                fi >= 0 and re.search(r"^\s*max_tokens:\s*%d\s*$" % HERMES_BUG_MAX_TOKENS,
                                      "\n".join(text.split("\n")[fi + 1:fend]), re.M))
        else:
            checks["litellm_deployment_present"] = bool(
                re.search(r"^  - model_name: " + re.escape(FABLE_DEPLOYMENT) + r"\s*$",
                          text, re.M))
    audit = audit_fallback_ladders()
    checks["fallback_ladders_clean"] = audit["ok"]
    return {"ok": all(checks.values()), "checks": checks, "paths": paths,
            "fallback_audit": audit, "promotion_state": "DORMANT"}


def verify(repo) -> dict:
    """Alias for verify_projection — what `model-route verify` calls."""
    return verify_projection(repo)
