"""Register a deterministic process authority record from REAL source bytes.

Part of rig-determinism-85. This is the sanctioned authoring tool for
``authority/processes/*.process.json`` records (schema
``rig.d85.process-authority.v1``): the validator in d85.py treats records as
trusted inputs by design, so the trust is established HERE, by hashing real
file bytes and refusing anything the loader would later refuse.

Guarantees:

- ``file_hashes`` are sha256 of the bytes copied into
  ``<out-dir>/sources/<process-id>/<relative>`` — never invented, never
  recomputed from memory.
- Entrypoints must be defined at module top level in the staged files, the
  exact grammar the loader's ``_entrypoint`` accepts.
- Already-registered records are IMMUTABLE: an identical re-registration is
  idempotent (byte-identical re-emission); different bytes are refused and
  the operator must mint a new versioned process-id (S26).
- ``--registry`` publishes ``process_id -> processes/<id>.process.json`` into
  ``<out-dir>/registry.json`` through this tool — never a hand-edit; a
  conflicting existing mapping is refused.
- Fail closed: a missing/invalid authority directory, unreadable file,
  malformed flag, or duplicate-key registry is a refusal with a named
  reason and exit code 2 — never a favorable default.

Stdlib only, deterministic, no network, no credential access. The loader is
never modified to accept a record; records must satisfy the loader as-is.

Usage:
    python3 register_process.py --process-id <id> --source-root <dir>
        --entrypoints "sym,sym@file.py:op" --files a.py,b.py
        [--external-module "name=path.py:sym.sym,sym.attr" ...]
        --out-dir <authority-dir> [--registry]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path

RECORD_SCHEMA = "rig.d85.process-authority.v1"
REGISTRY_SCHEMA = "rig.d85.authority-registry.v1"


class Refusal(Exception):
    """A named fail-closed refusal; detail is the operator-facing reason."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _serialize(record: dict) -> bytes:
    return (json.dumps(record, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _closed_json(path: Path, what: str) -> dict:
    """Parse a closed-object JSON file, rejecting duplicate keys."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Refusal(f"{what}: {exc}") from exc

    def hook(pairs: list[tuple[str, object]]) -> dict:
        seen: dict[str, object] = {}
        for key, value in pairs:
            if key in seen:
                raise Refusal(f"{what}: duplicate key {key!r}")
            seen[key] = value
        return seen

    try:
        value = json.loads(text, object_pairs_hook=hook)
    except RecursionError as exc:
        raise Refusal(f"{what}: nesting too deep") from exc
    except json.JSONDecodeError as exc:
        raise Refusal(f"{what}: {exc}") from exc
    if not isinstance(value, dict):
        raise Refusal(f"{what}: must be a closed JSON object")
    return value


def _publish_mapping(registry_path: Path, process_id: str) -> None:
    """Idempotently publish this process's record path into registry.json."""
    mapping = f"processes/{process_id}.process.json"
    if registry_path.exists():
        registry = _closed_json(registry_path, "registry")
        if set(registry) != {"processes", "schema"} or registry.get("schema") != REGISTRY_SCHEMA:
            raise Refusal(f"registry: unexpected schema or keys: {sorted(registry)}")
        processes = registry["processes"]
        if not isinstance(processes, dict):
            raise Refusal("registry: processes must be a JSON object")
        existing = processes.get(process_id)
        if existing is not None and existing != mapping:
            raise Refusal(
                f"registry: {process_id} already maps to {existing!r}, not {mapping!r}; "
                "removals and remappings are ownership decisions, not registrar work"
            )
        if existing == mapping:
            return
        processes[process_id] = mapping
    else:
        registry = {"processes": {process_id: mapping}, "schema": REGISTRY_SCHEMA}
    registry_path.write_bytes(
        (json.dumps(registry, sort_keys=True, indent=2) + "\n").encode("utf-8")
    )


def _canonical_relative(root: Path, rel: str, what: str) -> Path:
    candidate = Path(rel)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise Refusal(f"{what} must be a canonical relative path: {rel!r}")
    origin = (root / candidate).resolve(strict=True)
    if root not in origin.parents:
        raise Refusal(f"{what} resolves outside the source root: {rel!r}")
    if not origin.is_file():
        raise Refusal(f"{what} is not a file: {rel!r}")
    return origin


def _top_level_functions(path: Path) -> dict[str, ast.FunctionDef]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, ValueError) as exc:
        raise Refusal(f"entrypoint source {path.name}: {exc}") from exc
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


def _entrypoint(spec: str, source_root: Path, rels: list[str]) -> dict:
    """Build one entrypoint in the loader's exact accepted grammar.

    ``SYM`` binds to the file where SYM is defined at top level (self-binding
    form); ``SYM@FILE:OP`` is the rich form.
    """
    symbol, _, rest = spec.partition("@")
    symbol = symbol.strip()
    if not symbol:
        raise Refusal(f"empty entrypoint symbol in {spec!r}")
    if rest:
        file_rel, sep, op = rest.partition(":")
        if not sep or not op.strip():
            raise Refusal(f"entrypoint {spec!r}: rich form must be SYM@FILE:OP")
        file_rel = file_rel.strip()
    else:
        homes = [rel for rel in rels if symbol in _top_level_functions(source_root / rel)]
        if len(homes) != 1:
            raise Refusal(
                f"entrypoint {symbol!r} must be defined at top level in exactly one "
                f"staged file (found {len(homes)}); use SYM@FILE:OP to disambiguate"
            )
        file_rel, op = homes[0], symbol
    target = _canonical_relative(source_root, file_rel, f"entrypoint file for {spec!r}")
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    names = {node.name for node in tree.body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update((alias.asname or alias.name.split(".")[0]) for alias in node.names)
    if symbol not in names:
        raise Refusal(
            f"entrypoint {symbol!r} is neither defined nor imported at module top "
            f"level in {file_rel}; the D85 loader resolves callables only against the "
            "snapshot's top-level defs and imports"
        )
    # Live ENTRYPOINT_KEYS grammar (d85.py): exactly source_path, symbol,
    # adapter_path, adapter_operation. For the self-bound form source==adapter
    # and operation==symbol; the rich form names the adapter explicitly.
    source_home = [rel for rel in rels if symbol in
                   _top_level_functions(source_root / rel)]
    source_path = source_home[0] if source_home else file_rel
    return {
        "source_path": source_path,
        "symbol": symbol,
        "adapter_path": file_rel,
        "adapter_operation": op.strip(),
    }


def _package_binding(name: str, artifact: Path) -> list[str]:
    """Mirror d85._package_reachable for an ``__init__.py`` artifact."""
    import d85  # the one authority this generator obeys; never loosen it

    root = artifact.parent.name
    if not d85._package_reachable(name, root):
        raise Refusal(
            f"external module {name}: package binding rejects root {root!r}; "
            "declare the module the call sites actually import"
        )
    return [root]


def _external_entry(spec: str) -> dict:
    """Parse ``name=path.py:allowed,call,dotted`` into a lock the loader accepts.

    The artifact path must exist; ``__init__.py`` artifacts get the
    ``_package_reachable``-verified package binding. Call names must be dotted
    (``pkg.attr`` or a bare name); the loader re-verifies each against the
    artifact's real surface — this generator does not pre-approve anything.
    """
    name, sep, rest = spec.partition("=")
    name, path_text, calls_text = name.strip(), "", ""
    if not sep:
        raise Refusal(f"external module {spec!r}: form is name=path.py:calls")
    path_part, colon, calls_part = rest.partition(":")
    if not colon:
        raise Refusal(f"external module {spec!r}: form is name=path.py:calls")
    path_text, calls_text = path_part.strip(), calls_part
    if not name or not path_text:
        raise Refusal(f"external module {spec!r}: empty module name or artifact path")
    artifact = Path(path_text).resolve(strict=True)
    if not artifact.is_file():
        raise Refusal(f"external module {name}: artifact is not a file: {artifact}")
    calls = sorted({call.strip() for call in calls_text.split(",") if call.strip()})
    if not calls:
        raise Refusal(f"external module {name}: no allowed calls declared")
    for call in calls:
        if not call.replace(".", "_").replace("[", "").replace("]", "").isidentifier() \
                and "." not in call:
            raise Refusal(f"external module {name}: call {call!r} is not a dotted name")
        if any(part in {"", "."} for part in call.split(".")):
            raise Refusal(f"external module {name}: call {call!r} is not a dotted name")
    entry: dict = {
        "module": name,
        "artifact_path": str(artifact),
        "artifact_sha256": _sha256_bytes(artifact.read_bytes()),
        "allowed_calls": calls,
    }
    if artifact.name == "__init__.py":
        entry["package_modules"] = _package_binding(name, artifact)
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="register_process")
    parser.add_argument("--process-id", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--entrypoints", required=True)
    parser.add_argument("--files", required=True)
    parser.add_argument("--external-module", action="append", default=[])
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--registry", action="store_true",
                        help="also publish the record path into <out-dir>/registry.json")
    args = parser.parse_args(argv)

    process_id = args.process_id.strip()
    if not process_id or any(part in {"", ".", ".."} for part in Path(process_id).parts):
        print(f"register_process: invalid process-id: {process_id!r}", file=sys.stderr)
        return 2
    try:
        source_root = Path(args.source_root).resolve(strict=True)
    except OSError as exc:
        print(f"register_process: source root missing: {args.source_root}: {exc}", file=sys.stderr)
        return 2
    if not source_root.is_dir():
        print(f"register_process: source root is not a directory: {source_root}", file=sys.stderr)
        return 2
    authority_root = Path(args.out_dir).resolve(strict=False)
    processes_dir = authority_root / "processes"
    sources_dir = authority_root / "sources" / process_id
    record_path = processes_dir / f"{process_id}.process.json"
    if not processes_dir.is_dir():
        print(f"register_process: authority processes dir missing: {processes_dir}", file=sys.stderr)
        return 2

    rels = [item.strip() for item in args.files.split(",") if item.strip()]
    if not rels:
        print("register_process: --files must name at least one file", file=sys.stderr)
        return 2
    try:
        file_hashes: dict[str, str] = {}
        staged: list[tuple[Path, Path, bytes]] = []
        for rel in rels:
            origin = _canonical_relative(source_root, rel, f"files[{rel!r}]")
            try:
                data = origin.read_bytes()
            except OSError as exc:
                print(f"register_process: {rel}: {exc}", file=sys.stderr)
                return 2
            target = sources_dir / rel
            if target.exists() and target.read_bytes() != data:
                print(
                    f"register_process: {target} holds different bytes than {origin}; "
                    "never overwrite a registered source snapshot — use a new process-id",
                    file=sys.stderr,
                )
                return 2
            staged.append((origin, target, data))
            file_hashes[rel] = _sha256_bytes(data)

        entrypoints = [_entrypoint(item.strip(), source_root, rels)
                       for item in args.entrypoints.split(",") if item.strip()]
        if not entrypoints:
            print("register_process: --entrypoints must name at least one symbol", file=sys.stderr)
            return 2
        external_modules = [_external_entry(item) for item in args.external_module]
    except Refusal as refusal:
        print(f"register_process: {refusal.detail}", file=sys.stderr)
        return 2
    except ValueError as exc:  # e.g. _package_reachable path hygiene
        print(f"register_process: {exc}", file=sys.stderr)
        return 2

    record = {
        "schema": RECORD_SCHEMA,
        "process_id": process_id,
        "source_root": str(sources_dir),
        "file_hashes": file_hashes,
        "external_modules": external_modules,
        "entrypoints": entrypoints,
        "classification_path": f"processes/{process_id}.classification.json",
    }
    payload = _serialize(record)

    if record_path.exists():
        # S26 immutability: unchanged bytes re-emit byte-identical output;
        # any difference is a refusal that names a new versioned id.
        existing = record_path.read_bytes()
        if existing == payload:
            if args.registry:
                try:
                    _publish_mapping(authority_root / "registry.json", process_id)
                except Refusal as refusal:
                    print(f"register_process: {refusal.detail}", file=sys.stderr)
                    return 2
            sys.stdout.write(existing.decode("utf-8"))
            return 0
        print(
            f"register_process: {record_path} already registers {process_id} with "
            "different bytes; records are immutable — changed source bytes require "
            "a new versioned process-id (e.g. append _v2)",
            file=sys.stderr,
        )
        return 2

    for origin, target, _data in staged:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(origin, target)
    record_path.write_bytes(payload)
    if args.registry:
        try:
            _publish_mapping(authority_root / "registry.json", process_id)
        except Refusal as refusal:
            print(f"register_process: {refusal.detail}", file=sys.stderr)
            return 2
    sys.stdout.write(payload.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
