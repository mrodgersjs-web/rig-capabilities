"""Source-derived, fail-closed D85 realized-operation inventory.

Production entry points read one repository-owned authority registry. Process
records name source entrypoints, exact files, adapter bindings, and locked
single-file external modules. A closed Python grammar produces the structural
symbols and sequential call-site IR. Classification and D85 scoring remain
separate gates.
"""
from __future__ import annotations

import ast
import builtins
import hashlib
import importlib.machinery
import os
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CAPABILITY_ROOT = Path(__file__).resolve().parent
AUTHORITY_REGISTRY = CAPABILITY_ROOT / "authority" / "registry.json"

REGISTRY_SCHEMA = "rig.d85.authority-registry.v1"
PROCESS_SCHEMA = "rig.d85.process-authority.v1"
INVENTORY_SCHEMA = "rig.d85.realized-inventory.v1"
REGISTRY_KEYS = {"schema", "processes"}
PROCESS_KEYS = {
    "schema",
    "process_id",
    "source_root",
    "file_hashes",
    "external_modules",
    "entrypoints",
}
ENTRYPOINT_KEYS = {"source_path", "symbol", "adapter_path", "adapter_operation"}
EXTERNAL_MODULE_KEYS = {
    "module",
    "artifact_path",
    "artifact_sha256",
    "allowed_calls",
}
BUILTIN_CALLS = frozenset(dir(builtins))
DYNAMIC_BUILTIN_CALLS = frozenset(
    {
        "__import__",
        "breakpoint",
        "compile",
        "delattr",
        "eval",
        "exec",
        "getattr",
        "globals",
        "locals",
        "setattr",
        "vars",
    }
)
HIGHER_ORDER_BUILTINS = frozenset({"filter", "map"})
SAFE_EXTERNAL_IMPORTS = frozenset({"__future__"})


class AdmissionBlock(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail

    def as_dict(self) -> dict[str, str]:
        return {"verdict": "BLOCK", "reason": self.code, "detail": self.detail}


@dataclass(frozen=True)
class SymbolRef:
    path: str
    symbol: str


@dataclass
class ModuleIndex:
    relative_path: str
    symbols: dict[str, ast.FunctionDef | ast.AsyncFunctionDef]
    imports: dict[str, tuple[str, str, str | None]]


class _DirectCallVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls: list[ast.Call] = []

    def visit_Call(self, node: ast.Call) -> None:
        self.generic_visit(node)
        self.calls.append(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return



def _block(code: str, detail: str) -> None:
    raise AdmissionBlock(code, detail)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _closed_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            _block("AUTHORITY_MALFORMED", f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _load_json(path: Path, code: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw, object_pairs_hook=_closed_json_object)
    except (OSError, json.JSONDecodeError) as exc:
        _block(code, f"{path}: {exc}")
    if not isinstance(value, dict):
        _block(code, f"{path}: top level must be an object")
    return value, raw


def _exact_keys(
    value: dict[str, Any],
    expected: set[str],
    where: str,
    optional: set[str] = frozenset(),
) -> None:
    actual = set(value)
    allowed = set(expected) | set(optional)
    missing = set(expected) - actual
    extra = actual - allowed
    if missing or extra:
        _block(
            "AUTHORITY_MALFORMED",
            f"{where}: keys must be exactly {sorted(expected)}"
            f" (optional {sorted(optional)}); got {sorted(actual)}",
        )


def _nonempty(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _block("AUTHORITY_MALFORMED", f"{where}: expected non-empty string")
    return value


def _resolve_relative(root: Path, relative: Any, escape_code: str) -> Path:
    rel = Path(_nonempty(relative, "relative path"))
    if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        _block(escape_code, f"path must be canonical and relative: {relative!r}")
    try:
        candidate = (root / rel).resolve(strict=True)
    except OSError as exc:
        _block("AUTHORITY_FILE_MISSING", f"{relative}: {exc}")
    try:
        candidate.relative_to(root)
    except ValueError:
        _block(escape_code, f"{relative!r} resolves outside {root}")
    if not candidate.is_file():
        _block("AUTHORITY_FILE_MISSING", f"{candidate} is not a regular file")
    return candidate


def _module_name(relative_path: str) -> str:
    parts = list(Path(relative_path).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _relative_import(module_name: str, imported: str | None, level: int) -> str:
    if level == 0:
        return imported or ""
    package = module_name.split(".")[:-1]
    keep = len(package) - (level - 1)
    if keep < 0:
        return imported or ""
    prefix = package[:keep]
    if imported:
        prefix.extend(imported.split("."))
    return ".".join(prefix)

def _grammar_block(relative_path: str, node: ast.AST, detail: str) -> None:
    line = getattr(node, "lineno", 0)
    _block("SOURCE_UNSUPPORTED_GRAMMAR", f"{relative_path}:{line}: {detail}")


def _validate_value_expression(
    expression: ast.expr,
    relative_path: str,
    *,
    allow_call: bool,
    call_target: bool = False,
) -> None:
    if isinstance(expression, (ast.Name, ast.Constant)):
        return
    if isinstance(expression, (ast.List, ast.Tuple, ast.Set)):
        for item in expression.elts:
            _validate_value_expression(
                item, relative_path, allow_call=allow_call
            )
        return
    if isinstance(expression, ast.Dict):
        for item in (*expression.keys, *expression.values):
            if item is not None:
                _validate_value_expression(
                    item, relative_path, allow_call=allow_call
                )
        return
    if isinstance(expression, ast.Attribute) and call_target:
        _validate_value_expression(
            expression.value,
            relative_path,
            allow_call=allow_call,
            call_target=True,
        )
        return
    if isinstance(expression, ast.Call) and allow_call:
        if not isinstance(expression.func, (ast.Name, ast.Attribute, ast.Call)):
            _grammar_block(relative_path, expression.func, "unsupported call target")
        _validate_value_expression(
            expression.func,
            relative_path,
            allow_call=True,
            call_target=True,
        )
        for argument in expression.args:
            if isinstance(argument, ast.Starred):
                _grammar_block(relative_path, argument, "starred call argument")
            _validate_value_expression(
                argument, relative_path, allow_call=True
            )
        if expression.keywords:
            _grammar_block(relative_path, expression, "keyword arguments")
        return
    _grammar_block(
        relative_path,
        expression,
        f"{type(expression).__name__} is outside the closed expression grammar",
    )


def _function_annotations(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ast.expr]:
    annotations = [
        argument.annotation
        for argument in (
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        )
        if argument.annotation is not None
    ]
    for argument in (node.args.vararg, node.args.kwarg):
        if argument is not None and argument.annotation is not None:
            annotations.append(argument.annotation)
    if node.returns is not None:
        annotations.append(node.returns)
    return annotations


def _validate_function_grammar(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    relative_path: str,
    future_annotations: bool,
) -> None:
    if node.decorator_list:
        _grammar_block(relative_path, node, "decorator")
    if _function_annotations(node) and not future_annotations:
        _grammar_block(relative_path, node, "runtime annotation")
    for default in (
        *node.args.defaults,
        *(value for value in node.args.kw_defaults if value is not None),
    ):
        _validate_value_expression(default, relative_path, allow_call=False)
    terminated = False
    assigned_names: set[str] = set()

    for index, statement in enumerate(node.body):
        if terminated:
            _grammar_block(relative_path, statement, "statement after return")
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            _grammar_block(relative_path, statement, "function-local import")
        if isinstance(statement, ast.Pass):
            continue
        if isinstance(statement, ast.FunctionDef):
            _validate_function_grammar(
                statement, relative_path, future_annotations
            )
            continue
        if isinstance(statement, ast.Return):
            if statement.value is not None:
                _validate_value_expression(
                    statement.value, relative_path, allow_call=True
                )
            terminated = True
            continue
        if isinstance(statement, ast.Expr):
            if (
                isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, str)
            ):
                continue
            if (
                isinstance(statement.value, ast.Call)
                and _call_name(statement.value.func) in DYNAMIC_BUILTIN_CALLS
            ):
                _validate_value_expression(
                    statement.value, relative_path, allow_call=True
                )
                continue
            _grammar_block(relative_path, statement, "discarded expression")
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
        ):
            target = statement.targets[0].id
            if target in assigned_names:
                _grammar_block(relative_path, statement, f"reassigned local {target}")
            assigned_names.add(target)
            _validate_value_expression(
                statement.value, relative_path, allow_call=True
            )
            if any(isinstance(child, ast.Call) for child in ast.walk(statement.value)):
                used_later = any(
                    isinstance(child, ast.Name)
                    and isinstance(child.ctx, ast.Load)
                    and child.id == target
                    for later in node.body[index + 1 :]
                    for child in ast.walk(later)
                )
                if not used_later:
                    _grammar_block(relative_path, statement, f"dead call result {target}")
            continue
        _grammar_block(
            relative_path,
            statement,
            f"{type(statement).__name__} is outside the closed statement grammar",
        )


def _validate_module_grammar(tree: ast.Module, relative_path: str) -> None:
    future_annotations = any(
        isinstance(statement, ast.ImportFrom)
        and statement.module == "__future__"
        and any(alias.name == "annotations" for alias in statement.names)
        for statement in tree.body
    )
    bindings: set[str] = set()
    for statement in tree.body:
        if isinstance(statement, ast.Import):
            names = [
                alias.asname or alias.name.split(".")[0]
                for alias in statement.names
            ]
        elif (
            isinstance(statement, ast.ImportFrom)
            and statement.module != "__future__"
        ):
            names = [alias.asname or alias.name for alias in statement.names]
        elif isinstance(statement, ast.FunctionDef):
            names = [statement.name]
        else:
            names = []
        duplicate = bindings.intersection(names)
        if duplicate:
            _grammar_block(
                relative_path,
                statement,
                f"duplicate module binding {sorted(duplicate)}",
            )
        bindings.update(names)
    for statement in tree.body:
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(statement, ast.FunctionDef):
            _validate_function_grammar(
                statement, relative_path, future_annotations
            )
            continue
        if (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        ):
            continue
        _grammar_block(
            relative_path,
            statement,
            f"{type(statement).__name__} is outside the closed module grammar",
        )


def _index_symbols(
    body: list[ast.stmt], prefix: str = ""
) -> dict[str, ast.FunctionDef]:
    symbols: dict[str, ast.FunctionDef] = {}
    for item in body:
        if isinstance(item, ast.FunctionDef):
            name = f"{prefix}.{item.name}" if prefix else item.name
            symbols[name] = item
            symbols.update(_index_symbols(item.body, name))
    return symbols


def _index_imports(tree: ast.Module, module_name: str) -> dict[str, tuple[str, str, str | None]]:
    imports: dict[str, tuple[str, str, str | None]] = {}
    for item in tree.body:
        if isinstance(item, ast.Import):
            for alias in item.names:
                local = alias.asname or alias.name.split(".")[0]
                imports[local] = ("module", alias.name, None)
        elif isinstance(item, ast.ImportFrom):
            imported_module = _relative_import(module_name, item.module, item.level)
            for alias in item.names:
                if alias.name == "*":
                    _block("SOURCE_DYNAMIC_IMPORT", f"{module_name}: star import")
                local = alias.asname or alias.name
                imports[local] = ("symbol", imported_module, alias.name)
    return imports


def _parse_module(
    path: Path, relative_path: str, snapshot: bytes
) -> ModuleIndex:
    if path.suffix != ".py":
        _block("SOURCE_LANGUAGE_UNSUPPORTED", f"{relative_path}: only Python is admitted")
    try:
        tree = ast.parse(snapshot.decode("utf-8"), filename=str(path))
    except (UnicodeDecodeError, SyntaxError) as exc:
        _block("SOURCE_PARSE_FAILED", f"{path}: {exc}")
    _validate_module_grammar(tree, relative_path)
    module_name = _module_name(relative_path)
    return ModuleIndex(
        relative_path=relative_path,
        symbols=_index_symbols(tree.body),
        imports=_index_imports(tree, module_name),
    )


def _symbol_span(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[int, int]:
    start = int(node.lineno)
    if node.decorator_list:
        start = min(start, *(int(item.lineno) for item in node.decorator_list))
    end = node.end_lineno
    if not isinstance(end, int) or end < start:
        _block("SOURCE_PARSE_FAILED", f"no complete span for {node.name}")
    return start, end


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return f"{_call_name(node.func)}(...)"
    if isinstance(node, ast.Subscript):
        return f"{_call_name(node.value)}[...]"
    return f"<{type(node).__name__}>"


def _calls(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.Call]:
    visitor = _DirectCallVisitor()
    for statement in node.body:
        visitor.visit(statement)
    return visitor.calls






def _shadowed_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[str]:
    names = {
        argument.arg
        for argument in (
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        )
    }
    for argument in (node.args.vararg, node.args.kwarg):
        if argument is not None:
            names.add(argument.arg)
    for statement in node.body:
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
        ):
            names.add(statement.targets[0].id)
    return names
def _external_callee(
    func: ast.expr,
    imports: dict[str, tuple[str, str, str | None]],
    external_modules: dict[str, dict[str, Any]],
    used_external_modules: set[str],
) -> tuple[str, str | None] | None:
    if isinstance(func, ast.Name):
        if func.id in BUILTIN_CALLS:
            return func.id, None
        imported = imports.get(func.id)
        if imported and imported[0] == "symbol":
            module_name = imported[1]
            callee = f"{module_name}.{imported[2]}"
            lock = external_modules.get(module_name)
            if lock is None or callee not in lock["allowed_calls"]:
                _block("EXTERNAL_CALL_UNDECLARED", callee)
            used_external_modules.add(module_name)
            return callee, module_name
        return None
    if isinstance(func, ast.Attribute):
        root: ast.AST = func
        while isinstance(root, ast.Attribute):
            root = root.value
        if isinstance(root, ast.Name) and root.id in imports:
            imported = imports[root.id]
            if imported[0] == "module":
                module_name = imported[1]
                callee = f"{module_name}.{_call_name(func).partition('.')[2]}"
            else:
                module_name = imported[1]
                base = ".".join(
                    part for part in (module_name, imported[2]) if part
                )
                callee = f"{base}.{_call_name(func).partition('.')[2]}"
            lock = external_modules.get(module_name)
            if lock is None or callee not in lock["allowed_calls"]:
                _block("EXTERNAL_CALL_UNDECLARED", callee)
            used_external_modules.add(module_name)
            return callee, module_name
        if isinstance(root, (ast.Constant, ast.List, ast.Tuple, ast.Dict, ast.Set)):
            return _call_name(func), None
    return None

def _module_paths(module_name: str) -> tuple[str, str] | None:
    if not module_name:
        return None
    plain = Path(*module_name.split(".")).with_suffix(".py").as_posix()
    package = (Path(*module_name.split(".")) / "__init__.py").as_posix()
    return plain, package


def _local_module_path(
    module_name: str, source_root: Path, available_files: set[str]
) -> str | None:
    candidates = [
        relative
        for relative in _module_paths(module_name) or ()
        if (source_root / relative).is_file()
    ]
    if len(candidates) > 1:
        _block("SOURCE_IMPORT_AMBIGUOUS", f"{module_name}: {candidates}")
    if not candidates:
        return None
    relative = candidates[0]
    if relative not in available_files:
        _block("UNHASHED_REACHABLE_FILE", relative)
    return relative


def _resolve_call(
    module: ModuleIndex,
    current_symbol: str,
    call: ast.Call,
    source_root: Path,
    available_files: set[str],
    imports: dict[str, tuple[str, str, str | None]],
    shadowed_names: set[str],
) -> SymbolRef | None:
    func = call.func
    if isinstance(func, ast.Name):
        if func.id in shadowed_names:
            return None
        scope = current_symbol
        while scope:
            candidate = f"{scope}.{func.id}"
            if candidate in module.symbols:
                return SymbolRef(module.relative_path, candidate)
            scope = scope.rpartition(".")[0]
        imported = imports.get(func.id)
        if imported and imported[0] == "symbol":
            relative = _local_module_path(
                imported[1], source_root, available_files
            )
            if relative:
                return SymbolRef(relative, imported[2] or func.id)
        if func.id in module.symbols:
            return SymbolRef(module.relative_path, func.id)
        return None

    if isinstance(func, ast.Attribute):
        dotted = _call_name(func)
        root, _, rest = dotted.partition(".")
        if root in shadowed_names:
            return None
        imported = imports.get(root)
        if imported and imported[0] == "module" and rest:
            relative = _local_module_path(
                imported[1], source_root, available_files
            )
            if relative:
                return SymbolRef(relative, rest)
        if imported and imported[0] == "symbol" and rest:
            module_name = ".".join(
                part for part in (imported[1], imported[2]) if part
            )
            relative = _local_module_path(
                module_name, source_root, available_files
            )
            if relative:
                return SymbolRef(relative, rest)
    return None

def _validate_callable_references(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    module: ModuleIndex,
    current_symbol: str,
    source_root: Path,
    available_files: set[str],
    imports: dict[str, tuple[str, str, str | None]],
    shadowed_names: set[str],
    external_modules: dict[str, dict[str, Any]],
) -> None:
    def walk(current: ast.AST, parent: ast.AST) -> None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if isinstance(current, (ast.Name, ast.Attribute)) and not isinstance(
            parent, ast.Attribute
        ):
            direct_target = isinstance(parent, ast.Call) and parent.func is current
            if not direct_target:
                probe = ast.copy_location(
                    ast.Call(func=current, args=[], keywords=[]), current
                )
                if _resolve_call(
                    module,
                    current_symbol,
                    probe,
                    source_root,
                    available_files,
                    imports,
                    shadowed_names,
                ) is not None:
                    _block(
                        "SOURCE_DYNAMIC_CALL",
                        f"{module.relative_path}:{getattr(current, 'lineno', 0)}: callable escapes execution graph",
                    )
                shadowed_value = (
                    isinstance(current, ast.Name)
                    and current.id in shadowed_names
                )
                if not shadowed_value and _external_callee(
                    current, imports, external_modules, set()
                ) is not None:
                    _block(
                        "SOURCE_DYNAMIC_CALL",
                        f"{module.relative_path}:{getattr(current, 'lineno', 0)}: external callable escapes execution graph",
                    )
        for child in ast.iter_child_nodes(current):
            walk(child, current)

    for statement in node.body:
        walk(statement, node)

def _validate_local_imports(
    imports: dict[str, tuple[str, str, str | None]],
    source_root: Path,
    available_files: set[str],
    external_modules: dict[str, dict[str, Any]],
) -> None:
    for kind, module_name, symbol in imports.values():
        local_module = _local_module_path(
            module_name, source_root, available_files
        )
        local_submodule = None
        if kind == "symbol" and symbol:
            local_submodule = _local_module_path(
                ".".join(part for part in (module_name, symbol) if part),
                source_root,
                available_files,
            )
        if local_module is not None or local_submodule is not None:
            continue
        if module_name in SAFE_EXTERNAL_IMPORTS:
            continue
        if module_name not in external_modules:
            _block("SOURCE_EXTERNAL_IMPORT", module_name)


def _read_verified_file(
    path: Path, expected: Any, kind: str
) -> tuple[bytes, str, tuple[int, int]]:
    expected_hash = _nonempty(expected, f"{kind}_sha256")
    if len(expected_hash) != 64 or any(c not in "0123456789abcdef" for c in expected_hash):
        _block("AUTHORITY_MALFORMED", f"{kind}_sha256 must be lowercase SHA-256")
    try:
        with path.open("rb") as handle:
            identity = os.fstat(handle.fileno())
            snapshot = handle.read()
    except OSError as exc:
        _block(f"{kind.upper()}_READ_FAILED", f"{path}: {exc}")
    actual = _sha256_bytes(snapshot)
    if actual != expected_hash:
        _block(f"{kind.upper()}_HASH_MISMATCH", f"{path}: {expected_hash} != {actual}")
    return snapshot, actual, (identity.st_dev, identity.st_ino)



def _deterministic_module_origin(module_name: str) -> Path:
    suffixes = [
        *importlib.machinery.EXTENSION_SUFFIXES,
        ".py",
        ".pyc",
    ]
    for raw_root in sys.path:
        root = Path(raw_root or ".").resolve()
        if not root.is_dir():
            continue
        candidates = [
            *(root / module_name / f"__init__{suffix}" for suffix in suffixes),
            *(root / f"{module_name}{suffix}" for suffix in suffixes),
        ]
        matches = [candidate.resolve() for candidate in candidates if candidate.is_file()]
        if not matches:
            continue
        if (
            len(matches) != 1
            or matches[0].suffix != ".py"
            or matches[0].name == "__init__.py"
        ):
            _block(
                "EXTERNAL_MODULE_LOADER_MISMATCH",
                f"{module_name}: ambiguous or unsupported candidates {matches}",
            )
        return matches[0]
    _block("EXTERNAL_MODULE_LOADER_MISMATCH", f"{module_name}: no source module")


def _external_module_locks(
    process: dict[str, Any], source_root: Path
) -> tuple[dict[str, dict[str, Any]], dict[tuple[int, int], str]]:
    raw_modules = process.get("external_modules")
    if not isinstance(raw_modules, list):
        _block("AUTHORITY_MALFORMED", "external_modules must be a list")
    locks: dict[str, dict[str, Any]] = {}
    loader_fingerprint = _canonical_hash(
        {
            "executable": str(Path(sys.executable).resolve()),
            "python": sys.version,
            "sys_path": [str(Path(item or ".").resolve()) for item in sys.path],
        }
    )
    artifact_identities: dict[tuple[int, int], str] = {}
    for index, raw_module in enumerate(raw_modules):
        where = f"external_modules[{index}]"
        if not isinstance(raw_module, dict):
            _block("AUTHORITY_MALFORMED", f"{where}: expected object")
        _exact_keys(raw_module, EXTERNAL_MODULE_KEYS, where)
        module_name = _nonempty(raw_module.get("module"), f"{where}.module")
        if not module_name.isidentifier():
            _block(
                "AUTHORITY_MALFORMED",
                f"{where}.module must be one top-level Python identifier",
            )
        if module_name in locks:
            _block("AUTHORITY_DUPLICATE_BINDING", module_name)
        if module_name in sys.modules:
            _block(
                "EXTERNAL_MODULE_LOADER_STATE",
                f"{module_name}: already present in sys.modules",
            )
        artifact_value = _nonempty(
            raw_module.get("artifact_path"), f"{where}.artifact_path"
        )
        artifact_path = Path(artifact_value)
        if not artifact_path.is_absolute():
            _block("AUTHORITY_MALFORMED", f"{where}.artifact_path must be absolute")
        try:
            artifact_path = artifact_path.resolve(strict=True)
        except OSError as exc:
            _block("EXTERNAL_MODULE_MISSING", f"{artifact_value}: {exc}")
        if not artifact_path.is_file():
            _block("EXTERNAL_MODULE_MISSING", str(artifact_path))
        try:
            artifact_path.relative_to(source_root)
        except ValueError:
            pass
        else:
            _block(
                "AUTHORITY_MALFORMED",
                f"{module_name}: source-root modules use file_hashes",
            )
        artifact_snapshot, artifact_hash, artifact_identity = _read_verified_file(
            artifact_path,
            raw_module.get("artifact_sha256"),
            "external_module",
        )
        if artifact_identity in artifact_identities:
            _block(
                "AUTHORITY_DUPLICATE_BINDING",
                f"{module_name}: artifact aliases "
                f"{artifact_identities[artifact_identity]!r}",
            )
        artifact_identities[artifact_identity] = module_name
        allowed_calls = raw_module.get("allowed_calls")
        if (
            not isinstance(allowed_calls, list)
            or not allowed_calls
            or any(
                not isinstance(call, str)
                or not call.startswith(module_name + ".")
                for call in allowed_calls
            )
            or len(allowed_calls) != len(set(allowed_calls))
        ):
            _block(
                "AUTHORITY_MALFORMED",
                f"{where}.allowed_calls must be unique {module_name}.* names",
            )
        try:
            external_tree = ast.parse(
                artifact_snapshot.decode("utf-8"),
                filename=str(artifact_path),
            )
        except (UnicodeDecodeError, SyntaxError) as exc:
            _block("EXTERNAL_MODULE_PARSE_FAILED", f"{module_name}: {exc}")
        defined_calls = {
            f"{module_name}.{node.name}"
            for node in external_tree.body
            if isinstance(node, ast.FunctionDef)
        }
        missing_calls = set(allowed_calls) - defined_calls
        if missing_calls:
            _block(
                "EXTERNAL_CALL_UNRESOLVED",
                f"{module_name}: {sorted(missing_calls)}",
            )
        resolved_origin = _deterministic_module_origin(module_name)
        if resolved_origin != artifact_path:
            _block(
                "EXTERNAL_MODULE_LOADER_MISMATCH",
                f"{module_name}: {resolved_origin} != {artifact_path}",
            )
        locks[module_name] = {
            "module": module_name,
            "origin": str(resolved_origin),
            "sha256": artifact_hash,
            "resolver": "rig.d85.sys-path-source.v1",
            "loader_fingerprint": loader_fingerprint,
            "runtime_loader_proof_required": True,
            "runtime_loader_proven": False,
            "allowed_calls": sorted(allowed_calls),
        }
    return locks, artifact_identities

def _build_inventory_from_registry(
    registry_path: Path, process_id: str
) -> dict[str, Any]:
    registry_path = registry_path.resolve(strict=False)
    registry, _ = _load_json(registry_path, "AUTHORITY_REGISTRY_MISSING")
    if set(registry) != REGISTRY_KEYS or registry.get("schema") != REGISTRY_SCHEMA:
        _block("AUTHORITY_MALFORMED", f"{registry_path}: invalid registry grammar")
    processes = registry.get("processes")
    if not isinstance(processes, dict):
        _block("AUTHORITY_MALFORMED", f"{registry_path}: processes must be an object")
    if process_id not in processes:
        _block("UNKNOWN_PROCESS", process_id)

    authority_root = registry_path.parent.resolve()
    process_path = _resolve_relative(
        authority_root, processes[process_id], "AUTHORITY_ROOT_ESCAPE"
    )
    process, process_raw = _load_json(process_path, "AUTHORITY_PROCESS_MISSING")
    _exact_keys(
        process,
        PROCESS_KEYS,
        str(process_path),
        optional={"classification_path"},
    )
    if process.get("schema") != PROCESS_SCHEMA or process.get("process_id") != process_id:
        _block("AUTHORITY_MALFORMED", f"{process_path}: schema or process_id mismatch")

    source_root_value = _nonempty(process.get("source_root"), "source_root")
    source_root_path = Path(source_root_value)
    if not source_root_path.is_absolute():
        _block("AUTHORITY_MALFORMED", "source_root must be absolute")
    try:
        source_root = source_root_path.resolve(strict=True)
    except OSError as exc:
        _block("SOURCE_ROOT_MISSING", f"{source_root_path}: {exc}")
    if not source_root.is_dir():
        _block("SOURCE_ROOT_MISSING", f"{source_root} is not a directory")
    external_modules, artifact_identities = _external_module_locks(
        process, source_root
    )
    used_external_modules: set[str] = set()

    raw_hashes = process.get("file_hashes")
    if not isinstance(raw_hashes, dict) or not raw_hashes:
        _block("AUTHORITY_MALFORMED", "file_hashes must be a non-empty object")
    files: dict[str, Path] = {}
    snapshots: dict[str, bytes] = {}
    hashes: dict[str, str] = {}
    identities: dict[tuple[int, int], str] = {}
    for relative, expected_hash in raw_hashes.items():
        path = _resolve_relative(source_root, relative, "SOURCE_ROOT_ESCAPE")
        snapshot, digest, identity = _read_verified_file(
            path, expected_hash, "source"
        )
        if identity in identities:
            _block(
                "AUTHORITY_DUPLICATE_BINDING",
                f"{relative!r} aliases {identities[identity]!r}",
            )
        identities[identity] = relative
        files[relative] = path
        snapshots[relative] = snapshot
        hashes[relative] = digest
    for artifact_identity, module_name in artifact_identities.items():
        if artifact_identity in identities:
            _block(
                "AUTHORITY_DUPLICATE_BINDING",
                f"external module {module_name} aliases "
                f"{identities[artifact_identity]!r}",
            )

    raw_entrypoints = process.get("entrypoints")
    if not isinstance(raw_entrypoints, list) or not raw_entrypoints:
        _block("AUTHORITY_MALFORMED", "entrypoints must be a non-empty list")
    entrypoints: list[tuple[SymbolRef, dict[str, Any]]] = []
    bindings: set[tuple[str, str, str, str]] = set()
    for index, entrypoint in enumerate(raw_entrypoints):
        where = f"entrypoints[{index}]"
        if not isinstance(entrypoint, dict):
            _block("AUTHORITY_MALFORMED", f"{where}: expected object")
        _exact_keys(entrypoint, ENTRYPOINT_KEYS, where)
        source_path = _nonempty(entrypoint.get("source_path"), f"{where}.source_path")
        symbol = _nonempty(entrypoint.get("symbol"), f"{where}.symbol")
        adapter_path = _nonempty(entrypoint.get("adapter_path"), f"{where}.adapter_path")
        adapter_operation = _nonempty(
            entrypoint.get("adapter_operation"), f"{where}.adapter_operation"
        )
        if source_path not in files or adapter_path not in files:
            _block("UNHASHED_REACHABLE_FILE", f"{where}: source and adapter need file hashes")
        binding = (source_path, symbol, adapter_path, adapter_operation)
        if binding in bindings:
            _block("AUTHORITY_DUPLICATE_BINDING", f"{where}: {binding}")
        bindings.add(binding)
        entrypoints.append((SymbolRef(source_path, symbol), entrypoint))

    modules: dict[str, ModuleIndex] = {}

    def module(relative: str) -> ModuleIndex:
        if relative not in files:
            _block("UNHASHED_REACHABLE_FILE", relative)
        if relative not in modules:
            modules[relative] = _parse_module(
                files[relative], relative, snapshots[relative]
            )
        return modules[relative]

    adapter_details: dict[tuple[str, str], dict[str, Any]] = {}
    for _, entrypoint in entrypoints:
        adapter_path = entrypoint["adapter_path"]
        adapter_operation = entrypoint["adapter_operation"]
        adapter_module = module(adapter_path)
        adapter_node = adapter_module.symbols.get(adapter_operation)
        if adapter_node is None:
            _block("ADAPTER_OPERATION_MISSING", f"{adapter_path}: {adapter_operation}")
        start, end = _symbol_span(adapter_node)
        adapter_details[(adapter_path, adapter_operation)] = {
            "path": adapter_path,
            "operation": adapter_operation,
            "start_line": start,
            "end_line": end,
            "sha256": hashes[adapter_path],
        }

    reachable: dict[SymbolRef, dict[str, Any]] = {}
    queue = [
        (
            SymbolRef(entrypoint["adapter_path"], entrypoint["adapter_operation"]),
            entrypoint,
        )
        for _, entrypoint in entrypoints
    ]
    while queue:
        ref, entrypoint = queue.pop(0)
        existing = reachable.get(ref)
        adapter_key = (entrypoint["adapter_path"], entrypoint["adapter_operation"])
        if existing:
            if existing["adapter_key"] != adapter_key:
                _block("AMBIGUOUS_ADAPTER_BINDING", f"{ref.path}:{ref.symbol}")
            continue
        source_module = module(ref.path)
        node = source_module.symbols.get(ref.symbol)
        if node is None:
            _block("SOURCE_SYMBOL_MISSING", f"{ref.path}: {ref.symbol}")
        start, end = _symbol_span(node)
        local_successors: list[SymbolRef] = []
        steps: list[dict[str, Any]] = []
        imports = dict(source_module.imports)
        _validate_local_imports(
            imports,
            source_root,
            set(files),
            external_modules,
        )
        available_files = set(files)
        shadowed_names = _shadowed_names(node)
        _validate_callable_references(
            node,
            source_module,
            ref.symbol,
            source_root,
            available_files,
            imports,
            shadowed_names,
            external_modules,
        )
        calls = _calls(node)
        for call in calls:
            callee = _call_name(call.func)
            target_root: ast.AST = call.func
            while isinstance(target_root, ast.Attribute):
                target_root = target_root.value
            if (
                isinstance(target_root, ast.Name)
                and target_root.id in shadowed_names
            ):
                _block(
                    "SOURCE_DYNAMIC_CALL",
                    f"{ref.path}:{call.lineno}: shadowed {target_root.id}",
                )
            if callee in HIGHER_ORDER_BUILTINS or (
                callee == "iter" and len(call.args) >= 2
            ):
                _block(
                    "SOURCE_DYNAMIC_CALL",
                    f"{ref.path}:{call.lineno}: higher-order builtin {callee}",
                )
            if callee in DYNAMIC_BUILTIN_CALLS or (
                callee.startswith("builtins.")
                and callee.rsplit(".", 1)[-1] in DYNAMIC_BUILTIN_CALLS
            ):
                _block("SOURCE_DYNAMIC_CALL", f"{ref.path}:{call.lineno}: {callee}")

            resolved = _resolve_call(
                source_module,
                ref.symbol,
                call,
                source_root,
                available_files,
                imports,
                shadowed_names,
            )
            if resolved is None:
                external_target = _external_callee(
                    call.func,
                    imports,
                    external_modules,
                    used_external_modules,
                )
                if external_target is None:
                    _block(
                        "SOURCE_DYNAMIC_CALL",
                        f"{ref.path}:{call.lineno}: {callee}",
                    )
                external_callee, external_module = external_target
                steps.append(
                    {
                        "kind": "external",
                        "callee": external_callee,
                        "external_module": external_module,
                        "start_line": int(call.lineno),
                        "end_line": int(call.end_lineno or call.lineno),
                        "start_col": int(call.col_offset),
                        "end_col": int(call.end_col_offset or call.col_offset),
                    }
                )
            else:
                local_successors.append(resolved)
                queue.append((resolved, entrypoint))
                steps.append(
                    {
                        "kind": "local",
                        "target": resolved,
                        "start_line": int(call.lineno),
                        "start_col": int(call.col_offset),
                    }
                )

        reachable[ref] = {
            "start": start,
            "end": end,
            "adapter_key": adapter_key,
            "successor_refs": sorted(set(local_successors), key=lambda item: (item.path, item.symbol)),
            "steps": steps,
        }

    for source_ref, entrypoint in entrypoints:
        adapter_key = (
            entrypoint["adapter_path"],
            entrypoint["adapter_operation"],
        )
        detail = reachable.get(source_ref)
        if detail is None or detail["adapter_key"] != adapter_key:
            _block(
                "ADAPTER_ENTRYPOINT_DISCONNECTED",
                f"{adapter_key[0]}:{adapter_key[1]} -> {source_ref.path}:{source_ref.symbol}",
            )

    used_files = {ref.path for ref in reachable}
    used_files.update(path for path, _ in adapter_details)
    extra_hashes = set(files) - used_files
    if extra_hashes:
        _block("AUTHORITY_PADDING", f"unreachable hashed files: {sorted(extra_hashes)}")

    extra_external_modules = set(external_modules) - used_external_modules
    if extra_external_modules:
        _block(
            "AUTHORITY_PADDING",
            f"unused external modules: {sorted(extra_external_modules)}",
        )
    symbols: dict[SymbolRef, dict[str, Any]] = {}
    for ref, detail in reachable.items():
        adapter = adapter_details[detail["adapter_key"]]
        symbol = {
            "symbol_id": "",
            "credit_eligible": False,
            "source": {
                "path": ref.path,
                "symbol": ref.symbol,
                "start_line": detail["start"],
                "end_line": detail["end"],
                "sha256": hashes[ref.path],
            },
            "adapter": adapter,
            "predecessors": [],
            "successors": [],
        }
        symbol["symbol_id"] = "sha256:" + _canonical_hash(
            {
                "process_id": process_id,
                "source_root": str(source_root),
                "source": symbol["source"],
                "adapter": symbol["adapter"],
            }
        )
        symbols[ref] = symbol

    for ref, detail in reachable.items():
        symbol = symbols[ref]
        symbol["successors"] = sorted(
            symbols[successor]["symbol_id"]
            for successor in detail["successor_refs"]
        )
        for successor in detail["successor_refs"]:
            symbols[successor]["predecessors"].append(symbol["symbol_id"])
    for symbol in symbols.values():
        symbol["predecessors"].sort()

    def expand(
        ref: SymbolRef,
        execution_path: tuple[str, ...],
        stack: tuple[SymbolRef, ...],
    ) -> list[dict[str, Any]]:
        if ref in stack:
            cycle = " -> ".join(
                f"{item.path}:{item.symbol}" for item in (*stack, ref)
            )
            _block("SOURCE_RECURSIVE_CALL_GRAPH", cycle)
        detail = reachable[ref]
        adapter = adapter_details[detail["adapter_key"]]
        sequence: list[dict[str, Any]] = []
        for step in detail["steps"]:
            callsite = (
                f"{ref.path}:{ref.symbol}@"
                f"{step['start_line']}:{step['start_col']}"
            )
            if step["kind"] == "local":
                target = step["target"]
                edge = f"{callsite}->{target.path}:{target.symbol}"
                sequence.extend(
                    expand(
                        target,
                        (*execution_path, edge),
                        (*stack, ref),
                    )
                )
                continue
            source = {
                "path": ref.path,
                "symbol": ref.symbol,
                "start_line": step["start_line"],
                "end_line": step["end_line"],
                "start_col": step["start_col"],
                "end_col": step["end_col"],
                "sha256": hashes[ref.path],
            }
            external_call = {"callee": step["callee"]}
            external_module = step["external_module"]
            if external_module is not None:
                external_call["module_initialization"] = external_modules[
                    external_module
                ]
            path = (*execution_path, f"{callsite}:{step['callee']}")
            operation = {
                "inventory_id": "",
                "operation_kind": (
                    "EXTERNAL_MODULE_CALL"
                    if external_module is not None
                    else "EXTERNAL_CALL"
                ),
                "credit_eligible": False,
                "source": source,
                "adapter": adapter,
                "external_call": external_call,
                "execution_path": list(path),
                "predecessors": [],
                "successors": [],
            }
            operation["inventory_id"] = "sha256:" + _canonical_hash(
                {
                    "process_id": process_id,
                    "source_root": str(source_root),
                    "operation_kind": operation["operation_kind"],
                    "source": source,
                    "adapter": adapter,
                    "external_call": external_call,
                    "execution_path": operation["execution_path"],
                }
            )
            sequence.append(operation)
        return sequence

    inventory_by_id: dict[str, dict[str, Any]] = {}
    roots: list[str] = []
    terminals: list[str] = []
    for _, entrypoint in entrypoints:
        adapter_ref = SymbolRef(
            entrypoint["adapter_path"], entrypoint["adapter_operation"]
        )
        root_label = f"{adapter_ref.path}:{adapter_ref.symbol}"
        sequence = expand(adapter_ref, (root_label,), ())
        if not sequence:
            _block(
                "ZERO_WORK_PROCESS",
                f"{root_label}: no provisional call-site stage",
            )
        for index, operation in enumerate(sequence):
            inventory_id = operation["inventory_id"]
            if inventory_id in inventory_by_id:
                _block("AUTHORITY_DUPLICATE_BINDING", inventory_id)
            if index:
                predecessor = sequence[index - 1]
                operation["predecessors"] = [predecessor["inventory_id"]]
                predecessor["successors"] = [inventory_id]
            inventory_by_id[inventory_id] = operation
        roots.append(sequence[0]["inventory_id"])
        terminals.append(sequence[-1]["inventory_id"])

    ordered_operations = sorted(
        inventory_by_id.values(), key=lambda item: item["inventory_id"]
    )
    ordered_symbols = sorted(
        symbols.values(), key=lambda item: item["symbol_id"]
    )
    inventory_core = {
        "schema": INVENTORY_SCHEMA,
        "process_id": process_id,
        "source_root": str(source_root),
        "authority_sha256": _sha256_bytes(process_raw),
        "credit_operation_count": 0,
        "structural_node_count": len(ordered_symbols),
        "d85_admission": False,
        "roots": sorted(roots),
        "terminals": sorted(terminals),
        "symbols": ordered_symbols,
        "operations": ordered_operations,
    }
    return {**inventory_core, "inventory_sha256": _canonical_hash(inventory_core)}


def _compare_inventory_from_registry(
    registry_path: Path, process_id: str, submitted: Any
) -> dict[str, Any]:
    expected = _build_inventory_from_registry(registry_path, process_id)
    if submitted != expected:
        _block("INVENTORY_MISMATCH", "submitted inventory differs from source extraction")
    return {
        "schema": "rig.d85.inventory-verdict.v1",
        "verdict": "INVENTORY_PASS",
        "gate": "operation_inventory",
        "process_id": process_id,
        "inventory_sha256": expected["inventory_sha256"],
        "operation_count": len(expected["operations"]),
        "credit_operation_count": expected["credit_operation_count"],
        "structural_node_count": expected["structural_node_count"],
        "d85_admission": False,
    }


def build_inventory(process_id: str) -> dict[str, Any]:
    return _build_inventory_from_registry(AUTHORITY_REGISTRY, process_id)


def compare_inventory(process_id: str, submitted: Any) -> dict[str, Any]:
    return _compare_inventory_from_registry(AUTHORITY_REGISTRY, process_id, submitted)
