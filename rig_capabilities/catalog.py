"""Capability catalog: scan, index, search, install. Stdlib only.

Canonical assets live in this repo under capabilities/<kind-dir>/.
External roots (installed harness dirs) are indexed read-only so search sees
everything; canonical entries shadow same-id externals (one owner per name).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from .okf import meta as _okf_meta

KINDS = ("skill", "agent", "hook", "harness", "loop", "command", "data")
KIND_DIR = {
    "skill": "skills",
    "agent": "agents",
    "hook": "hooks",
    "harness": "harnesses",
    "loop": "loops",
    "command": "commands",
    "data": "data",
}
DIR_KIND = {v: k for k, v in KIND_DIR.items()}

# A directory under a kind is an asset only when it carries this descriptor —
# the phantom-asset guard. `skill` uses SKILL.md; `data` uses DATA.md (a data
# asset is a directory of fixtures + a validator + a descriptor, exactly like a
# skill, so it packages the same way). A kind absent here is a single-file kind.
DIR_DESCRIPTOR = {
    "skill": "SKILL.md",
    "data": "DATA.md",
}

# kind -> file extension used when the canonical asset is a single file
KIND_EXTS = {
    "hook": {".sh", ".py", ".ts", ".js", ".mjs"},
    "harness": {".yaml", ".yml"},
    "loop": {".md", ".yaml", ".yml"},
    "command": {".md"},
    "agent": {".md", ".toml", ".json"},
    "skill": {".md"},
    # `data` is intentionally absent: it is a directory-descriptor kind (DATA.md),
    # so a loose file under capabilities/data/ must NEVER index as a single-file
    # asset. `KIND_EXTS.get("data", set())` is empty, so the single-file branch of
    # _asset_from_canonical rejects every stray .json/.md there.
}

DEFAULT_EXTERNAL_ROOTS = [
    {"label": "claude-skills", "kind": "skill", "path": "~/.claude/skills", "pattern": "*/SKILL.md"},
    {"label": "codex-skills", "kind": "skill", "path": "~/.codex/skills", "pattern": "*/SKILL.md"},
    {"label": "hermes-skills", "kind": "skill", "path": "~/.hermes/skills", "pattern": "*/SKILL.md"},
    {"label": "agents-skills", "kind": "skill", "path": "~/.agents/skills", "pattern": "*/SKILL.md"},
    {"label": "claude-agents", "kind": "agent", "path": "~/.claude/agents", "pattern": "*.md"},
    {"label": "codex-agents", "kind": "agent", "path": "~/.codex/agents", "pattern": "*.toml"},
    {"label": "hermes-agents", "kind": "agent", "path": "~/.hermes/agents", "pattern": "*.json"},
    {"label": "claude-harnesses", "kind": "harness", "path": "~/.claude/harnesses", "pattern": "*.yaml"},
    {"label": "jake-goal-harnesses", "kind": "harness", "path": "~/.hermes/jake/goal-harnesses", "pattern": "*.yaml"},
    {"label": "claude-hooks", "kind": "hook", "path": "~/.claude/hooks", "pattern": "*.sh;*.py"},
    {"label": "claude-commands", "kind": "command", "path": "~/.claude/commands", "pattern": "*.md"},
    {"label": "codex-commands", "kind": "command", "path": "~/.codex/commands", "pattern": "*.md"},
]

DEFAULT_INSTALL_ROOTS = {
    "skill": {"claude": "~/.claude/skills", "codex": "~/.codex/skills",
              "hermes": "~/.hermes/skills", "agents": "~/.agents/skills",
              "omp": "~/.omp/skills"},
    "agent": {"claude": "~/.claude/agents", "codex": "~/.codex/agents",
              "hermes": "~/.hermes/agents"},
    "hook": {"claude": "~/.claude/hooks", "codex": "~/.codex/hooks",
             "hermes": "~/.hermes/hooks", "omp": "~/.omp/hooks",
             "prime-agent": "~/.prime/agent/hooks"},
    "harness": {"claude": "~/.claude/harnesses", "codex": "~/.codex/harnesses",
                "hermes": "~/.hermes/jake/goal-harnesses"},
    "loop": {"claude": "~/.claude/harnesses", "codex": "~/.codex/harnesses",
             "hermes": "~/.hermes/jake/goal-harnesses"},
    "command": {"claude": "~/.claude/commands", "codex": "~/.codex/commands",
                "hermes": "~/.hermes/commands", "omp": "~/.omp/agent/commands",
                "agents": "~/.agents/commands",
                "prime-agent": "~/.prime/agent/commands"},
}

HEAD_BYTES = 4096
CONTENT_CAP = 40000
INDEX_TTL = 6 * 3600

_FM_KEY = re.compile(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pick_main_text(path: Path) -> str:
    """Best-effort human text for a file (skill dirs may have SKILL.md;
    toml/json get raw — parsers normalize later)."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            return fh.read(HEAD_BYTES)
    except OSError:
        return ""


def _unquote(val: str) -> str:
    """Strip a *paired* surrounding quote only.

    `.strip("\"'")` looks equivalent and is not: `cmd:python3 -c 'print(1)'`
    has no leading quote and a load-bearing trailing one, and stripping it
    hands `/bin/sh` an unterminated string. So a `done_when` cmd that ran in
    the shell by hand fails the gate for a reason that has nothing to do with
    the asset. Only remove quotes that wrap the whole value.
    """
    v = val.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return val


def parse_frontmatter(text: str) -> dict:
    """Minimal YAML-ish frontmatter: key: value pairs in a leading --- fence.
    Also captures top-level `name/description` lines for toml/json assets."""
    out: dict = {}
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for ln in lines[1:40]:
            if ln.strip() in ("---", "..."):
                break
            m = _FM_KEY.match(ln)
            if m:
                key, val = m.group(1).lower(), _unquote(m.group(2))
                out.setdefault(key, val)   # fenced keys are structural (OKF reads them)
        return out
    # fallback: first plain key: value lines anywhere in the head (toml/json-ish)
    for ln in lines[:80]:
        m = _FM_KEY.match(ln.strip())
        if m:
            key, val = m.group(1).lower(), _unquote(m.group(2).rstrip(","))
            if key in ("name", "title", "description", "summary", "prompt") and key not in out:
                if val:
                    out["description" if key == "prompt" else key] = val
    return out


def _first_heading(text: str) -> str:
    for ln in text.splitlines():
        if ln.startswith("#"):
            return ln.lstrip("# ").strip()
    return ""


class Repo:
    def __init__(self, root: Path | str):
        self.root = Path(root)
        self.cap_root = self.root / "capabilities"
        self.index_path = self.root / ".index.json"
        self.ledger_path = self.root / ".install.json"
        self.config_path = self.root / "config.json"

    # -- config ------------------------------------------------------------

    def config(self) -> dict:
        user: dict = {}
        if self.config_path.exists():
            try:
                user = json.loads(self.config_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                user = {}
        use_defaults = user.get("defaults", True) is not False
        cfg = {"external_roots": (list(DEFAULT_EXTERNAL_ROOTS) if use_defaults else []),
               "install_roots": ({k: dict(v) for k, v in DEFAULT_INSTALL_ROOTS.items()}
                                 if use_defaults else {}),
               "federates": [], "connectors": [], "observe": {}}
        if isinstance(user.get("external_roots"), list):
            seen = {r["label"] for r in cfg["external_roots"]}
            for r in user["external_roots"]:
                if not isinstance(r, dict) or not r.get("label"):
                    continue
                if r.get("path") is None:
                    cfg["external_roots"] = [x for x in cfg["external_roots"]
                                             if x["label"] != r["label"]]
                elif r["label"] in seen:
                    cfg["external_roots"] = [x if x["label"] != r["label"] else r
                                             for x in cfg["external_roots"]]
                else:
                    cfg["external_roots"].append(r)
        if isinstance(user.get("install_roots"), dict):
            for kind, roots in user["install_roots"].items():
                if roots is None:
                    cfg["install_roots"].pop(kind, None)
                else:
                    cfg["install_roots"][kind] = dict(roots)
        if isinstance(user.get("federates"), list):
            cfg["federates"] = [f for f in user["federates"]
                                if isinstance(f, dict) and f.get("label")
                                and (f.get("path") or f.get("url"))]
        if isinstance(user.get("connectors"), list):
            cfg["connectors"] = [c for c in user["connectors"]
                                 if isinstance(c, dict) and c.get("label") and c.get("type")]
        if isinstance(user.get("observe"), dict):
            cfg["observe"] = dict(user["observe"])
        return cfg

    # -- hashing -----------------------------------------------------------

    @staticmethod
    def _sha_file(p: Path) -> str:
        h = hashlib.sha256()
        try:
            h.update(p.read_bytes())
        except OSError:
            return "unreadable"
        return h.hexdigest()[:12]

    @classmethod
    def _sha_dir(cls, p: Path) -> str:
        h = hashlib.sha256()
        for f in sorted(p.rglob("*")):
            if f.is_file():
                h.update(str(f.relative_to(p)).encode())
                h.update(cls._sha_file(f).encode())
        return h.hexdigest()[:12]

    # -- scanning ----------------------------------------------------------

    def _asset_from_canonical(self, kind: str, entry: Path) -> dict | None:
        if entry.is_dir():
            if entry.name.startswith(".") or entry.name == "__pycache__":
                return None
            descriptor = DIR_DESCRIPTOR.get(kind)
            if descriptor is None:
                # This kind packages as single files, not directories — a folder
                # under it is support, never an asset.
                return None
            main = entry / descriptor
            if not main.exists():
                # A directory is an asset only when it carries its kind's
                # descriptor (skill -> SKILL.md, data -> DATA.md). Otherwise every
                # support folder under a kind becomes a phantom asset whose "main
                # text" is whatever `rglob` found first: `capabilities/hooks/
                # fixtures` indexed as a hook, `capabilities/loops/__pycache__` as
                # a LOOP — a .pyc read with errors="replace" clears the
                # 10-character floor, so bytecode was served as a capability.
                # Anything that wants to be an asset states it has a descriptor;
                # support directories do not.
                return None
            text = _pick_main_text(main)
            sha = self._sha_dir(entry)
            path_disp = str(entry.relative_to(self.root))
        elif entry.is_file():
            if entry.name.startswith(".") or entry.suffix not in KIND_EXTS.get(kind, set()):
                return None
            if entry.name.lower() == "readme.md":
                return None
            text = _pick_main_text(entry)
            sha = self._sha_file(entry)
            path_disp = str(entry.relative_to(self.root))
        else:
            return None
        if len(text.strip()) < 10:
            return None
        fm = parse_frontmatter(text)
        name = fm.get("name") or fm.get("title") or fm.get("harness_name") \
            or _first_heading(text) or entry.name
        return {
            "id": entry.name,
            "kind": kind,
            "source": "canonical",
            "path": path_disp,
            "abs_path": str(entry),
            "name": name,
            "description": (fm.get("description") or fm.get("summary") or "")[:400],
            "tags": _tags(fm.get("tags")),
            "sha": sha,
            # Installable only when the kind actually has a harness install root.
            # `data` has none (it is a descriptor+fixtures package, not something
            # you drop into a harness), so it reports installable=False and the
            # install/release paths refuse it cleanly instead of offering a target
            # that does not exist.
            "installable": bool(self.install_roots(kind)),
            "okf": _okf_meta(fm, "canonical", kind=kind),
            "quality": _quality_block(text),
        }

    def _assets_from_external(self, root: dict) -> list:
        label, kind = root["label"], root["kind"]
        base = Path(os.path.expanduser(root["path"]))
        if not base.exists():
            return []
        out = []
        pats = [p.strip() for p in root.get("pattern", "*").split(";") if p.strip()]
        files: list[Path] = []
        for pat in pats:
            try:
                files.extend(base.glob(pat))
            except OSError:
                continue
        for m in sorted(files):
            if not m.is_file():
                continue
            try:
                if m.stat().st_size < 10:
                    continue
            except OSError:
                continue
            text = _pick_main_text(m)
            fm = parse_frontmatter(text)
            name = fm.get("name") or fm.get("title") or _first_heading(text) or m.stem
            if kind == "skill" and m.name == "SKILL.md":
                name = fm.get("name") or m.parent.name
            out.append({
                "id": m.parent.name if (kind == "skill" and m.name == "SKILL.md") else m.name,
                "kind": kind,
                "source": label,
                "path": str(m),
                "abs_path": str(m),
                "name": name,
                "description": (fm.get("description") or fm.get("summary") or "")[:400],
                "tags": _tags(fm.get("tags")),
                "sha": self._sha_file(m),
                "installable": False,
                "okf": _okf_meta(fm, label if label in ("great",) else "installed"),
                "quality": _quality_block(text),
            })
            if root.get("mtime_verified"):
                # external corpus files are never edited: freshness = file mtime
                q = out[-1]["quality"]
                if q is None:
                    q = out[-1]["quality"] = _quality_block("")
                if isinstance(q, dict) and not q.get("verified_on"):
                    import time as _t
                    q["verified_on"] = _t.strftime(
                        "%Y-%m-%d", _t.localtime(m.stat().st_mtime))
        return out

    def scan(self) -> list:
        assets: list[dict] = []
        seen: set = set()
        for kind in KINDS:
            d = self.cap_root / KIND_DIR[kind]
            if not d.exists():
                continue
            for entry in sorted(d.iterdir()):
                a = self._asset_from_canonical(kind, entry)
                if a:
                    assets.append(a)
                    seen.add((a["id"], a["kind"]))
        for root in self.config()["external_roots"]:
            for a in self._assets_from_external(root):
                if (a["id"], a["kind"]) in seen:
                    continue  # canonical shadows external
                seen.add((a["id"], a["kind"]))
                assets.append(a)
        from .federation import federated_assets
        for a in federated_assets(self):
            key = (a["id"], a.get("kind"))
            if key in seen:
                continue
            seen.add(key)
            assets.append(a)
        from .connectors import connector_assets
        for a in connector_assets(self):
            key = (a["id"], a.get("kind"))
            if key in seen:
                continue
            seen.add(key)
            assets.append(a)
        return assets

    # -- index -------------------------------------------------------------

    def build_index(self) -> dict:
        assets = self.scan()
        overlay = {}
        lanes_p = self.root / ".lanes.json"
        if lanes_p.exists():
            try:
                overlay = json.loads(lanes_p.read_text())
            except json.JSONDecodeError:
                overlay = {}
        if overlay:
            for a in assets:
                lane = overlay.get(a["id"])
                if lane:
                    a["lane"] = lane
        doc = {"generated_at": _now(), "count": len(assets), "assets": assets}
        tmp = self.index_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.index_path)
        return doc

    def load_index(self, force: bool = False) -> dict:
        if not force and self.index_path.exists():
            try:
                doc = json.loads(self.index_path.read_text(encoding="utf-8"))
                gen = doc.get("generated_epoch", 0)
                if time.time() - gen < INDEX_TTL:
                    return doc
            except json.JSONDecodeError:
                pass
        doc = self.build_index()
        doc["generated_epoch"] = int(time.time())
        tmp = self.index_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.index_path)
        return doc

    # -- search ------------------------------------------------------------

    def search(self, query: str, kind: str | None = None, limit: int = 20) -> list:
        doc = self.load_index()
        toks = [t for t in re.split(r"[^a-z0-9]+", query.lower()) if t]
        if not toks:
            return []
        scored = []
        for a in doc["assets"]:
            if kind and a["kind"] != kind:
                continue
            hay_id = re.sub(r"[^a-z0-9]+", " ", a["id"].lower())
            hay_name = re.sub(r"[^a-z0-9]+", " ", a["name"].lower())
            hay_desc = a["description"].lower()
            hay_tags = " ".join(t.lower() for t in a["tags"])
            score = 0
            q = query.lower().strip()
            if q == a["id"].lower():
                score += 100
            if q in a["id"].lower():
                score += 30
            for t in toks:
                if re.search(rf"\b{re.escape(t)}", hay_id) or re.search(rf"\b{re.escape(t)}", hay_name):
                    score += 10
                if re.search(rf"\b{re.escape(t)}", hay_tags):
                    score += 6
                if t in hay_desc:
                    score += 1
            if score <= 0:
                continue
            if a["source"] == "canonical":
                score += 20
            scored.append((score, a))
        scored.sort(key=lambda sa: (-sa[0], sa[1]["kind"], sa[1]["id"]))
        return [{"score": s, **a} for s, a in scored[:limit]]

    def resolve(self, asset_id: str) -> list:
        doc = self.load_index()
        return [a for a in doc["assets"] if a["id"].lower() == asset_id.lower()]

    # -- install ledger ------------------------------------------------------

    def ledger(self) -> dict:
        if self.ledger_path.exists():
            try:
                return json.loads(self.ledger_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def _ledger_add(self, asset_id: str, harness: str, target: str, sha: str) -> None:
        led = self.ledger()
        led.setdefault(asset_id, []).append(
            {"harness": harness, "target": target, "sha": sha, "ts": _now()})
        tmp = self.ledger_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(led, indent=1, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.ledger_path)

    def install_roots(self, kind: str) -> dict:
        return self.config()["install_roots"].get(kind, {})

    def install(self, asset_id: str, harness: str, force: bool = False,
                kind: str | None = None) -> dict:
        matches = [a for a in self.resolve(asset_id)
                   if a["source"] == "canonical" and (kind is None or a["kind"] == kind)]
        if not matches:
            ext = self.resolve(asset_id)
            if ext:
                raise ValueError(
                    f"'{asset_id}' lives only in {ext[0]['source']} — canonicalize first: "
                    f"capability_add id={asset_id} kind={ext[0]['kind']} "
                    f"source_path={ext[0]['abs_path']}")
            raise ValueError(f"unknown capability: {asset_id}")
        asset = matches[0]
        kind = asset["kind"]
        roots = self.install_roots(kind)
        if harness not in roots:
            raise ValueError(f"harness '{harness}' not supported for kind '{kind}'. "
                             f"Options: {sorted(roots)}")
        target_dir = Path(os.path.expanduser(roots[harness]))
        src = Path(asset["abs_path"])
        dst = target_dir / src.name
        target_dir.mkdir(parents=True, exist_ok=True)
        action = "installed"
        if dst.exists():
            cur_sha = self._sha_dir(dst) if dst.is_dir() else self._sha_file(dst)
            if cur_sha == asset["sha"] and not force:
                return {"status": "already-installed", "id": asset_id, "harness": harness,
                        "target": str(dst), "sha": cur_sha}
            if not force:
                raise ValueError(f"target exists and differs ({dst}); re-run with force=true "
                                 "(existing copy is backed up)")
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            bak = dst.with_name(f"{dst.name}.bak-{ts}")
            dst.rename(bak)
            action = "replaced"
        if src.is_dir():
            shutil.copytree(src, dst)
            sha = self._sha_dir(dst)
        else:
            shutil.copy2(src, dst)
            sha = self._sha_file(dst)
        self._ledger_add(asset_id, harness, str(dst), sha)
        return {"status": action, "id": asset_id, "kind": kind, "harness": harness,
                "target": str(dst), "sha": sha}

    # -- canonicalize --------------------------------------------------------

    def add(self, asset_id: str, kind: str, source_path: str, overwrite: bool = False) -> dict:
        if kind not in KINDS:
            raise ValueError(f"unknown kind '{kind}'. Options: {list(KINDS)}")
        src = Path(os.path.expanduser(source_path))
        if not src.exists():
            raise ValueError(f"source not found: {src}")
        dest_dir = self.cap_root / KIND_DIR[kind]
        dest_dir.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            dst = dest_dir / asset_id
        else:
            suffix = src.suffix or ".md"
            base = (asset_id[:-len(suffix)] if asset_id.endswith(suffix) else asset_id)
            dst = dest_dir / f"{base}{suffix}"
        # Already-canonical source (src and dst resolve to the same path): a
        # self-referential register. Copying/rmtree would delete the source, so
        # short-circuit to a re-index instead.
        try:
            same = src.resolve() == dst.resolve()
        except OSError:
            same = False
        if same:
            sha = self._sha_dir(dst) if dst.is_dir() else self._sha_file(dst)
            self.build_index()
            return {"status": "registered", "id": asset_id, "kind": kind,
                    "path": str(dst.relative_to(self.root)), "sha": sha}
        if dst.exists() and not overwrite:
            raise ValueError(f"canonical asset exists: {dst} — re-run with overwrite=true")
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            sha = self._sha_dir(dst)
        else:
            shutil.copy2(src, dst)
            sha = self._sha_file(dst)
        self.build_index()
        return {"status": "replaced" if overwrite else "added", "id": asset_id,
                "kind": kind, "path": str(dst.relative_to(self.root)), "sha": sha}

    # -- content -------------------------------------------------------------

    def content(self, abs_path: str) -> str:
        if not abs_path:
            return ""
        p = Path(abs_path)
        files = [f for f in sorted(p.rglob("*")) if f.is_file()][:20] if p.is_dir() else [p]
        out = []
        total = 0
        for f in files:
            chunk = _pick_main_text(f)
            out.append(f"--- {f.name} ---\n{chunk}")
            total += len(chunk)
            if total > CONTENT_CAP:
                out.append("[truncated]")
                break
        return "\n".join(out)

    # -- stats ---------------------------------------------------------------

    def stats(self) -> dict:
        doc = self.load_index()
        by_kind: dict = {}
        by_source: dict = {}
        for a in doc["assets"]:
            by_kind[a["kind"]] = by_kind.get(a["kind"], 0) + 1
            by_source[a["source"]] = by_source.get(a["source"], 0) + 1
        return {"generated_at": doc.get("generated_at"), "total": doc.get("count", 0),
                "by_kind": by_kind, "by_source": by_source,
                "install_ledger": {k: len(v) for k, v in self.ledger().items()}}


def _tags(raw: str | None) -> list:
    if not raw:
        return []
    return [t for t in re.split(r"[,\[\]]+", raw.strip()) if t.strip()][:8]


_QUAL_KEYS = ("outcome", "great_example", "quality_floor")


def _quality_block(text: str) -> dict:
    """Quality fields from a leading --- fence, or `# key: value` comments in a
    shebang script (hooks). Block lists supported in both forms."""
    lines = text.splitlines()
    if lines and lines[0].startswith("#!"):
        return _quality_from_comments(lines)
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        return {}
    fence = lines[1:end]
    out: dict = {}
    i = 0
    while i < len(fence):
        ln = fence[i]
        m = _FM_KEY.match(ln)
        if m:
            key, val = m.group(1).lower(), _unquote(m.group(2))
            if key == "done_when":
                items = []
                if val:
                    items = [_unquote(t.strip().strip("[]")) for t in val.split(",") if t.strip()]
                j = i + 1
                while j < len(fence) and re.match(r"^\s*-\s+", fence[j]):
                    items.append(_unquote(re.sub(r"^\s*-\s+", "", fence[j])))
                    j += 1
                out["done_when"] = items
                i = j
                continue
            if key in _QUAL_KEYS:
                out[key] = val
        i += 1
    return out


def _quality_from_comments(lines: list) -> dict:
    """Parse `# key: value` (+ `#   - item` block lists) from a script's head."""
    out: dict = {}
    i = 1  # skip shebang
    limit = min(len(lines), 40)
    while i < limit:
        raw = lines[i]
        m = re.match(r"^#\s*([A-Za-z0-9_\-]+)\s*:\s*(.*)$", raw)
        if m:
            key, val = m.group(1).lower(), _unquote(m.group(2))
            if key == "done_when":
                items = [t.strip() for t in val.split("||") if t.strip()] if val else []
                j = i + 1
                while j < limit and re.match(r"^#\s*-\s+", lines[j]):
                    items.append(re.sub(r"^#\s*-\s+", "", lines[j]).strip())
                    j += 1
                out["done_when"] = items
                i = j
                continue
            if key in _QUAL_KEYS:
                out[key] = val
        i += 1
    return out
