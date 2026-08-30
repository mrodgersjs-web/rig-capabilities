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

KINDS = ("skill", "agent", "hook", "harness", "loop", "command")
KIND_DIR = {
    "skill": "skills",
    "agent": "agents",
    "hook": "hooks",
    "harness": "harnesses",
    "loop": "loops",
    "command": "commands",
}
DIR_KIND = {v: k for k, v in KIND_DIR.items()}

# kind -> file extension used when the canonical asset is a single file
KIND_EXTS = {
    "hook": {".sh", ".py", ".ts", ".js", ".mjs"},
    "harness": {".yaml", ".yml"},
    "loop": {".md", ".yaml", ".yml"},
    "command": {".md"},
    "agent": {".md", ".toml", ".json"},
    "skill": {".md"},
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
             "hermes": "~/.hermes/hooks"},
    "harness": {"claude": "~/.claude/harnesses", "codex": "~/.codex/harnesses",
                "hermes": "~/.hermes/jake/goal-harnesses"},
    "loop": {"claude": "~/.claude/harnesses", "codex": "~/.codex/harnesses",
             "hermes": "~/.hermes/jake/goal-harnesses"},
    "command": {"claude": "~/.claude/commands", "codex": "~/.codex/commands",
                "hermes": "~/.hermes/commands"},
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
                key, val = m.group(1).lower(), m.group(2).strip().strip("\"'")
                if key in ("name", "title", "description", "summary", "harness_name",
                           "harness_id", "command", "tags"):
                    out[key] = val
        return out
    # fallback: first plain key: value lines anywhere in the head (toml/json-ish)
    for ln in lines[:80]:
        m = _FM_KEY.match(ln.strip())
        if m:
            key, val = m.group(1).lower().strip("\"'"), m.group(2).strip().strip("\"',")
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
                                 if use_defaults else {})}
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
            if entry.name.startswith("."):
                return None
            main = entry / "SKILL.md"
            if not main.exists():
                cands = [f for f in sorted(entry.rglob("*")) if f.is_file()]
                main = cands[0] if cands else None
            text = _pick_main_text(main) if main else ""
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
            "installable": True,
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
            })
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
        return assets

    # -- index -------------------------------------------------------------

    def build_index(self) -> dict:
        assets = self.scan()
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

    def install(self, asset_id: str, harness: str, force: bool = False) -> dict:
        matches = [a for a in self.resolve(asset_id) if a["source"] == "canonical"]
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
