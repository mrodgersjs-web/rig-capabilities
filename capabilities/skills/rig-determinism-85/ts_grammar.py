"""Closed TypeScript/TSX grammar for the D85 realized-operation inventory.

This module admits .ts and .tsx sources into the same source-derived inventory
pipeline d85.py applies to Python. It is fail-closed and deliberately narrow:
anything outside the closed grammar below returns SOURCE_UNSUPPORTED_GRAMMAR,
never a guess.

The closed TypeScript grammar mirrors the closed Python grammar
(d85._validate_module_grammar / d85._validate_function_grammar):

module level
    import declarations (default, named, namespace, combined; `import type`
    records no bindings), `export` / `export default` around the forms below,
    `export { a, b as c }` same-module re-export bindings, function
    declarations, `const NAME = (params) => ...` / `const NAME = function ...`
    bindings, erased type declarations (`type X = ...`, `interface X { ... }`),
    and string-literal expression statements. Nothing else: no classes, no
    decorators, no async, no module-level values, no control flow, no
    re-exports from other modules.

function level
    `return`, single-assignment `const` / `let` / `var` bindings, bare single
    assignment, nested function declarations, and the same string-literal and
    dynamic-builtin expression statements the Python grammar admits.
    Statements after `return` are rejected. Reassignment of a local binding is
    rejected. A call result that is never used later in the block is rejected.

expressions
    identifiers, literals (string, number, true/false/null/undefined), array
    literals, object literals, calls with positional arguments, member access
    only as a call target, and (in .tsx only) JSX elements with literal or
    expression attributes and expression children. No operators, no spread, no
    template substitution, no `new`, `await`, `yield`, `throw`, regex
    literals, and no function values passed as arguments.

types
    Type annotations are erased by TypeScript and cannot execute, so they are
    balance-scanned and discarded over a restricted type vocabulary.

Symbols are indexed exactly like Python: module-level and nested function
declarations (d85._index_symbols), plus `default` and same-module re-export
aliases. Relative specifiers (`./x`, `../y`) resolve against the importing
file to sources under the source root (`x.ts`, `x.tsx`, `x/index.ts`,
`x/index.tsx`); anything else is an external import that must be locked in the
process record (locked external modules are Python-only, see
d85._external_module_locks: a TypeScript process admits external_modules: []).

The parse produces the same structural nodes d85.py consumes
(ast.FunctionDef, ast.Call, ast.Name, ast.Attribute, ... subclasses), so
call-graph extraction, span capture, shadowing, and callable-escape checks are
shared with the Python path unchanged.

Supported-callable notes: builtin TypeScript globals (Math, JSON, String,
console, ...) are admitted as plain EXTERNAL_CALL steps like Python builtins;
`eval`, `Function`, and `require` are always SOURCE_DYNAMIC_CALL.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

import d85

LANGUAGE = "typescript"

# Statement-level calls pass the grammar only for these dynamic-builtin names
# (mirroring the Python grammar); the inventory then rejects every one of them
# with SOURCE_DYNAMIC_CALL.
DYNAMIC_BUILTIN_CALLS = d85.DYNAMIC_BUILTIN_CALLS | frozenset({"Function", "require"})

_TYPE_PUNCTUATION = frozenset("{}[]()<>|&?:,;=.*+-~!^%/`")
_TYPE_KEYWORDS = frozenset({"keyof", "typeof", "extends", "infer", "readonly", "new"})
_DECLARATION_KEYWORDS = frozenset(
    {
        "if",
        "for",
        "while",
        "do",
        "switch",
        "try",
        "throw",
        "class",
        "async",
        "await",
        "yield",
        "break",
        "continue",
        "debugger",
        "with",
        "import",
        "export",
        "type",
        "interface",
    }
)
_EXPRESSION_KEYWORDS = frozenset(
    {
        "function",
        "new",
        "await",
        "yield",
        "this",
        "super",
        "class",
        "import",
        "delete",
        "typeof",
        "void",
        "in",
        "instanceof",
        "async",
        "throw",
    }
)


def _block(code: str, detail: str) -> None:
    raise d85.AdmissionBlock(code, detail)


def _grammar(relative_path: str, line: int, detail: str) -> None:
    _block("SOURCE_UNSUPPORTED_GRAMMAR", f"{relative_path}:{line}: {detail}")


def _surrogate(base: type) -> type:
    return type(base.__name__, (base,), {"__module__": __name__})


FunctionDef = _surrogate(ast.FunctionDef)
Call = _surrogate(ast.Call)
Name = _surrogate(ast.Name)
Attribute = _surrogate(ast.Attribute)
Constant = _surrogate(ast.Constant)
List = _surrogate(ast.List)
Dict = _surrogate(ast.Dict)
Return = _surrogate(ast.Return)
Assign = _surrogate(ast.Assign)
Expr = _surrogate(ast.Expr)
Arg = _surrogate(ast.arg)
Arguments = _surrogate(ast.arguments)


class JsxElement(ast.AST):
    _fields = ("name", "attributes", "children")


class JsxAttribute(ast.AST):
    _fields = ("name", "value")


def _node(cls: type, **attrs: object) -> ast.AST:
    node = cls.__new__(cls)
    for key, value in attrs.items():
        setattr(node, key, value)
    return node


def _span(node: ast.AST, start: "_Token", end: "_Token") -> ast.AST:
    node.lineno = start.line
    node.col_offset = start.col
    node.end_lineno = end.end_line
    node.end_col_offset = end.end_col
    return node


class _Token:
    __slots__ = ("kind", "text", "line", "col", "end_line", "end_col")

    def __init__(
        self, kind: str, text: str, line: int, col: int, end_line: int, end_col: int
    ) -> None:
        self.kind = kind
        self.text = text
        self.line = line
        self.col = col
        self.end_line = end_line
        self.end_col = end_col


_PUNCT = sorted(
    (
        ">>>=",
        "...",
        "===",
        "!==",
        "**=",
        "<<=",
        ">>=",
        ">>>",
        "=>",
        "==",
        "!=",
        "<=",
        ">=",
        "&&",
        "||",
        "??",
        "?.",
        "++",
        "--",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "&=",
        "|=",
        "^=",
        "<<",
        ">>",
        "**",
    ),
    key=len,
    reverse=True,
)
_PUNCT_CHARS = frozenset("()[]{}.,;:?+-*/%<>=!&|^~@#")


def _tokenize(source: str, relative_path: str) -> list[_Token]:
    tokens: list[_Token] = []
    line = 1
    col = 0
    index = 0
    length = len(source)

    def advance(text: str) -> None:
        nonlocal line, col
        newlines = text.count("\n")
        if newlines:
            line += newlines
            col = len(text) - text.rfind("\n") - 1
        else:
            col += len(text)

    while index < length:
        char = source[index]
        if char in " \t\r\n":
            advance(char)
            index += 1
            continue
        if source.startswith("//", index):
            end = source.find("\n", index)
            end = length if end == -1 else end
            advance(source[index:end])
            index = end
            continue
        if source.startswith("/*", index):
            end = source.find("*/", index + 2)
            if end == -1:
                _grammar(relative_path, line, "unterminated block comment")
            advance(source[index : end + 2])
            index = end + 2
            continue
        start_line, start_col = line, col
        if char in "'\"":
            cursor = index + 1
            while cursor < length:
                if source[cursor] == "\\":
                    cursor += 2
                    continue
                if source[cursor] == char:
                    break
                if source[cursor] == "\n":
                    _grammar(relative_path, start_line, "unterminated string literal")
                cursor += 1
            else:
                _grammar(relative_path, start_line, "unterminated string literal")
            text = source[index : cursor + 1]
            advance(text)
            index = cursor + 1
            tokens.append(_Token("string", text, start_line, start_col, line, col))
            continue
        if char == "`":
            cursor = index + 1
            substituted = False
            while cursor < length:
                if source[cursor] == "\\":
                    cursor += 2
                    continue
                if source[cursor] == "`":
                    break
                if source[cursor : cursor + 2] == "${":
                    substituted = True
                cursor += 1
            else:
                _grammar(relative_path, start_line, "unterminated template literal")
            if substituted:
                _grammar(
                    relative_path,
                    start_line,
                    "template substitution is outside the closed expression grammar",
                )
            text = source[index : cursor + 1]
            advance(text)
            index = cursor + 1
            tokens.append(_Token("template", text, start_line, start_col, line, col))
            continue
        if char.isdigit():
            cursor = index + 1
            while cursor < length:
                current = source[cursor]
                if current.isalnum() or current in "._":
                    cursor += 1
                elif current in "+-" and source[cursor - 1] in "eE":
                    cursor += 1
                else:
                    break
            text = source[index:cursor]
            advance(text)
            index = cursor
            tokens.append(_Token("number", text, start_line, start_col, line, col))
            continue
        if char.isalpha() or char in "_$":
            cursor = index + 1
            while cursor < length and (source[cursor].isalnum() or source[cursor] in "_$"):
                cursor += 1
            text = source[index:cursor]
            advance(text)
            index = cursor
            tokens.append(_Token("ident", text, start_line, start_col, line, col))
            continue
        for punctuation in _PUNCT:
            if source.startswith(punctuation, index):
                advance(punctuation)
                index += len(punctuation)
                tokens.append(
                    _Token("punct", punctuation, start_line, start_col, line, col)
                )
                break
        else:
            if char in _PUNCT_CHARS:
                advance(char)
                index += 1
                tokens.append(_Token("punct", char, start_line, start_col, line, col))
            else:
                _grammar(
                    relative_path,
                    line,
                    f"character {char!r} is outside the closed tokenizer vocabulary",
                )
    tokens.append(_Token("eof", "", line, col, line, col))
    return tokens


class _Parser:
    def __init__(
        self,
        tokens: list[_Token],
        relative_path: str,
        source_root: Path,
        tsx: bool,
    ) -> None:
        self.tokens = tokens
        self.position = 0
        self.relative_path = relative_path
        self.source_root = source_root
        self.tsx = tsx
        self.module_body: list[ast.AST] = []
        self.module_functions: dict[str, ast.AST] = {}
        self.export_aliases: dict[str, str] = {}
        self.imports: dict[str, tuple[str, str, str | None]] = {}
        self.bindings: set[str] = set()

    # -- token plumbing -------------------------------------------------

    @property
    def current(self) -> _Token:
        return self.tokens[self.position]

    def peek(self, offset: int = 1) -> _Token:
        index = min(self.position + offset, len(self.tokens) - 1)
        return self.tokens[index]

    def advance(self) -> _Token:
        token = self.current
        if token.kind != "eof":
            self.position += 1
        return token

    def at(self, text: str) -> bool:
        token = self.current
        return token.kind in ("ident", "punct") and token.text == text

    def accept(self, text: str) -> _Token | None:
        if self.at(text):
            return self.advance()
        return None

    def expect(self, text: str) -> _Token:
        token = self.accept(text)
        if token is None:
            self.reject(f"expected {text!r}, found {self.current.text!r}")
        return token

    def reject(self, detail: str) -> None:
        _grammar(self.relative_path, self.current.line, detail)

    def semi(self) -> None:
        self.accept(";")

    def expect_ident(self) -> str:
        token = self.current
        if token.kind != "ident":
            self.reject(f"expected an identifier, found {token.text!r}")
        self.advance()
        return token.text

    # -- type annotations (erased at runtime; balance-scanned) -----------

    def skip_type(self, terminators: tuple[str, ...]) -> None:
        depth = 0
        while True:
            token = self.current
            if token.kind == "eof":
                self.reject("unterminated type annotation")
            if depth == 0 and token.kind == "punct" and token.text in terminators:
                return
            if token.kind == "ident":
                pass
            elif token.kind in ("number", "string", "template"):
                pass
            elif token.kind == "punct":
                if token.text == "=>":
                    self.advance()
                    continue
                if any(character not in _TYPE_PUNCTUATION for character in token.text):
                    self.reject(f"{token.text!r} is outside the type vocabulary")
                depth += token.text.count("<") - token.text.count(">")
                if depth < 0:
                    self.reject("unbalanced type annotation")
            else:  # pragma: no cover - tokenizer is closed
                self.reject("unexpected token in type annotation")
            self.advance()

    # -- module structure ----------------------------------------------

    def parse_module(self) -> None:
        while self.current.kind != "eof":
            self.parse_module_statement()

    def parse_module_statement(self) -> None:
        token = self.current
        if token.kind == "string":
            self.advance()
            self.semi()
            return
        if self.accept(";"):
            return
        if token.kind != "ident":
            self.reject(f"{token.text!r} is outside the closed module grammar")
        if token.text == "import":
            self.parse_import()
            return
        if token.text == "export":
            self.parse_export()
            return
        if token.text in ("type", "interface"):
            self.parse_type_declaration()
            return
        if token.text == "function":
            self.parse_function_declaration()
            return
        if token.text == "const":
            self.parse_const_function(exported=False, default=False)
            return
        self.reject(f"{token.text!r} is outside the closed module grammar")

    def parse_import(self) -> None:
        self.expect("import")
        type_only = False
        if self.at("type"):
            following = self.peek()
            if not (following.kind == "ident" and following.text == "from"):
                type_only = self.accept("type") is not None
        default_name: str | None = None
        namespace_name: str | None = None
        named: list[tuple[str, str]] = []
        if self.current.kind == "string":
            self.reject("side-effect import has no binding to certify")
        if self.current.kind == "ident":
            default_name = self.advance().text
            self.accept(",")
        if self.at("*"):
            self.advance()
            self.expect("as")
            namespace_name = self.expect_ident()
        elif self.at("{"):
            self.advance()
            while not self.at("}"):
                if self.accept("type"):
                    self.expect_ident()
                    self.accept("as") and self.expect_ident()
                else:
                    local = self.expect_ident()
                    exported = local
                    if self.accept("as"):
                        exported = self.expect_ident()
                    named.append((local, exported))
                if not self.accept(","):
                    break
            self.expect("}")
        self.expect("from")
        specifier = self.current
        if specifier.kind not in ("string", "template"):
            self.reject("import specifier must be a string literal")
        self.advance()
        self.semi()
        resolved = self.resolve_specifier(_string_value(specifier.text), specifier.line)
        if type_only:
            return
        if default_name is not None:
            self.bind(default_name)
            self.imports[default_name] = ("symbol", resolved, "default")
        if namespace_name is not None:
            self.bind(namespace_name)
            self.imports[namespace_name] = ("module", resolved, None)
        for local, exported in named:
            self.bind(local)
            self.imports[local] = ("symbol", resolved, exported)

    def parse_export(self) -> None:
        self.expect("export")
        default = self.accept("default") is not None
        token = self.current
        if token.kind == "ident" and token.text in ("type", "interface"):
            self.parse_type_declaration()
            return
        if token.kind == "ident" and token.text == "function":
            self.parse_function_declaration(exported=True, default=default)
            return
        if token.kind == "ident" and token.text == "const":
            self.parse_const_function(exported=True, default=default)
            return
        if default:
            self.reject("export default is only admissible around a function")
        if self.at("{"):
            self.advance()
            while not self.at("}"):
                source_name = self.expect_ident()
                exported_name = source_name
                if self.accept("as"):
                    exported_name = self.expect_ident()
                if source_name not in self.module_functions:
                    self.reject(f"export {source_name!r} is not a module function binding")
                self.export_aliases[exported_name] = source_name
                self.bindings.add(exported_name)
                if not self.accept(","):
                    break
            self.expect("}")
            if self.at("from"):
                self.reject("re-export from another module is outside the closed grammar")
            self.semi()
            return
        self.reject("export is outside the closed module grammar")

    def parse_type_declaration(self) -> None:
        keyword = self.advance().text
        self.expect_ident()
        if keyword == "type":
            self.expect("=")
            self.skip_type((";",))
            self.semi()
            return
        while not self.at("{"):
            if self.current.kind == "eof":
                self.reject("unterminated interface declaration")
            self.advance()
        depth = 0
        while True:
            token = self.advance()
            if token.kind == "eof":
                self.reject("unterminated interface declaration")
            if token.kind == "punct" and token.text == "{":
                depth += 1
            elif token.kind == "punct" and token.text == "}":
                depth -= 1
                if depth == 0:
                    break
        self.semi()

    def bind(self, name: str) -> None:
        if name in self.bindings:
            self.reject(f"duplicate module binding {name!r}")
        self.bindings.add(name)

    # -- functions ------------------------------------------------------

    def parse_function_declaration(
        self, *, exported: bool = False, default: bool = False
    ) -> None:
        start = self.expect("function")
        name = self.expect_ident()
        node = self.parse_function_tail(name, start)
        self.declare_function(name, node, default=default)

    def parse_const_function(self, *, exported: bool, default: bool) -> None:
        start = self.expect("const")
        name = self.expect_ident()
        if self.accept(":"):
            self.skip_type(("=",))
        self.expect("=")
        node = self.parse_function_value(name, start)
        self.declare_function(name, node, default=default)

    def declare_function(self, name: str, node: ast.AST, *, default: bool) -> None:
        self.bind(name)
        self.module_functions[name] = node
        self.module_body.append(node)
        if default:
            if "default" in self.export_aliases:
                self.reject("duplicate module binding 'default'")
            self.export_aliases["default"] = name

    def parse_function_tail(self, name: str, start: _Token) -> ast.AST:
        self.expect("(")
        params = self.parse_parameters()
        if self.accept(":"):
            self.skip_type(("{",))
        self.expect("{")
        body = self.parse_block()
        return _span(
            _node(
                FunctionDef,
                name=name,
                args=params,
                body=body,
                decorator_list=[],
                returns=None,
                type_comment=None,
            ),
            start,
            self.tokens[self.position - 1],
        )

    def parse_function_value(self, name: str, start: _Token) -> ast.AST:
        if self.at("function"):
            self.advance()
            declared = self.expect_ident()
            if declared != name:
                self.reject("const binding and function name must agree")
            return self.parse_function_tail(name, start)
        params = self.parse_arrow_parameters()
        if self.accept(":"):
            self.skip_type(("=",))
        self.expect("=>")
        if self.at("{"):
            self.expect("{")
            body = self.parse_block()
            end = self.tokens[self.position - 1]
        else:
            expression = self.parse_expression(allow_call=True)
            self.validate_value_expression(expression, allow_call=True)
            end = self.tokens[self.position - 1]
            body = [_span(_node(Return, value=expression), start, end)]
            self.semi()
        return _span(
            _node(
                FunctionDef,
                name=name,
                args=params,
                body=body,
                decorator_list=[],
                returns=None,
                type_comment=None,
            ),
            start,
            end,
        )

    def parse_arrow_parameters(self) -> ast.AST:
        if self.current.kind == "ident" and self.peek().kind == "punct" and self.peek().text == "=>":
            name = self.expect_ident()
            return self.build_arguments([name])
        self.expect("(")
        names = self.parse_parameters(as_names=True)
        return self.build_arguments(names)

    def build_arguments(self, names: list[str]) -> ast.AST:
        args = [
            _node(Arg, arg=name, annotation=None, type_comment=None) for name in names
        ]
        return _node(
            Arguments,
            posonlyargs=[],
            args=args,
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )

    def parse_parameters(self, *, as_names: bool = False) -> object:
        names: list[str] = []
        while not self.at(")"):
            token = self.current
            if token.kind == "punct" and token.text in ("{", "[", "..."):
                self.reject(f"parameter {token.text!r} is outside the closed grammar")
            name = self.expect_ident()
            names.append(name)
            if self.accept(":"):
                self.skip_type(("=", ",", ")"))
            if self.accept("="):
                default = self.parse_expression(allow_call=False)
                self.validate_value_expression(default, allow_call=False)
            if not self.accept(","):
                break
        self.expect(")")
        if as_names:
            return names
        return self.build_arguments(names)

    # -- statements -----------------------------------------------------

    def parse_block(self) -> list[ast.AST]:
        body: list[ast.AST] = []
        terminated = False
        assigned: set[str] = set()
        while not self.at("}"):
            if self.current.kind == "eof":
                self.reject("unterminated function body")
            if terminated:
                self.reject("statement after return")
            statement = self.parse_statement(assigned)
            if statement is not None:
                body.append(statement)
                if isinstance(statement, Return):
                    terminated = True
        self.expect("}")
        return body

    def parse_statement(self, assigned: set[str]) -> ast.AST | None:
        token = self.current
        if self.accept(";"):
            return None
        if token.kind == "string":
            self.advance()
            self.semi()
            return _span(
                _node(
                    Expr,
                    value=_span(
                        _node(Constant, value=_string_value(token.text), kind=None),
                        token,
                        token,
                    ),
                ),
                token,
                token,
            )
        if token.kind != "ident":
            self.reject(f"{token.text!r} is outside the closed statement grammar")
        if token.text == "return":
            self.advance()
            if self.at(";") or self.at("}"):
                self.semi()
                return _span(_node(Return, value=None), token, token)
            value = self.parse_expression(allow_call=True)
            self.validate_value_expression(value, allow_call=True)
            end = self.tokens[self.position - 1]
            self.semi()
            return _span(_node(Return, value=value), token, end)
        if token.text in ("const", "let", "var"):
            return self.parse_local_binding(assigned)
        if token.text == "function":
            self.advance()
            name = self.expect_ident()
            return self.parse_function_tail(name, token)
        if token.text in _DECLARATION_KEYWORDS:
            self.reject(f"{token.text!r} is outside the closed statement grammar")
        if self.peek().kind == "punct" and self.peek().text == "=":
            self.advance()
            self.advance()
            return self.parse_assignment(token, assigned)
        value = self.parse_expression(allow_call=True)
        if isinstance(value, Call) and d85._call_name(value.func) in DYNAMIC_BUILTIN_CALLS:
            self.validate_value_expression(value, allow_call=True)
            end = self.tokens[self.position - 1]
            self.semi()
            return _span(_node(Expr, value=value), token, end)
        self.reject("discarded expression")

    def parse_assignment(self, start: _Token, assigned: set[str]) -> ast.AST:
        name = start.text
        if name in assigned:
            self.reject(f"reassigned local {name}")
        assigned.add(name)
        value = self.parse_expression(allow_call=True)
        self.validate_value_expression(value, allow_call=True)
        end = self.tokens[self.position - 1]
        self.semi()
        statement = _span(
            _node(
                Assign,
                targets=[_span(_node(Name, id=name, ctx=ast.Load()), start, start)],
                value=value,
                type_comment=None,
            ),
            start,
            end,
        )
        if self.contains_call(value) and not self.used_later(name):
            self.reject(f"dead call result {name}")
        return statement

    def parse_local_binding(self, assigned: set[str]) -> ast.AST:
        start = self.advance()
        name = self.expect_ident()
        if self.accept(":"):
            self.skip_type(("=",))
        self.expect("=")
        if self.at("function") or (
            self.at("(")
            or (self.current.kind == "ident" and self.peek().kind == "punct" and self.peek().text == "=>")
        ):
            return self.parse_function_value(name, start)
        if name in assigned:
            self.reject(f"reassigned local {name}")
        assigned.add(name)
        value = self.parse_expression(allow_call=True)
        self.validate_value_expression(value, allow_call=True)
        end = self.tokens[self.position - 1]
        self.semi()
        statement = _span(
            _node(
                Assign,
                targets=[_span(_node(Name, id=name, ctx=ast.Load()), start, start)],
                value=value,
                type_comment=None,
            ),
            start,
            end,
        )
        if self.contains_call(value) and not self.used_later(name):
            self.reject(f"dead call result {name}")
        return statement

    def contains_call(self, node: ast.AST) -> bool:
        if isinstance(node, Call):
            return True
        return any(self.contains_call(child) for child in ast.iter_child_nodes(node))

    def used_later(self, name: str) -> bool:
        depth = 0
        for token in self.tokens[self.position :]:
            if token.kind == "punct":
                if token.text == "}":
                    if depth == 0:
                        return False
                    depth -= 1
                elif token.text == "{":
                    depth += 1
            elif token.kind == "eof":
                return False
            elif token.kind == "ident" and token.text == name:
                return True
        return False

    # -- expressions ----------------------------------------------------

    def parse_expression(self, *, allow_call: bool) -> ast.AST:
        start = self.current
        token = self.current
        if token.kind == "ident":
            if token.text in ("true", "false"):
                self.advance()
                node: ast.AST = _span(
                    _node(Constant, value=token.text == "true", kind=None), token, token
                )
            elif token.text in ("null", "undefined"):
                self.advance()
                node = _span(_node(Constant, value=None, kind=None), token, token)
            elif token.text in _EXPRESSION_KEYWORDS:
                self.reject(f"{token.text!r} is outside the closed expression grammar")
            else:
                self.advance()
                node = _span(_node(Name, id=token.text, ctx=ast.Load()), token, token)
        elif token.kind in ("number", "string", "template"):
            self.advance()
            node = _span(_node(Constant, value=_literal_value(token), kind=None), token, token)
        elif token.kind == "punct" and token.text == "(":
            self.advance()
            node = self.parse_expression(allow_call=allow_call)
            self.expect(")")
        elif token.kind == "punct" and token.text == "[":
            node = self.parse_array(allow_call=allow_call)
        elif token.kind == "punct" and token.text == "{":
            node = self.parse_object(allow_call=allow_call)
        elif token.kind == "punct" and token.text == "<":
            if not self.tsx:
                self.reject("JSX is only admissible in .tsx sources")
            node = self.parse_jsx_element()
        else:
            self.reject(f"{token.text!r} is outside the closed expression grammar")
        return self.parse_postfix(node, allow_call=allow_call, start=start)

    def parse_postfix(
        self, node: ast.AST, *, allow_call: bool, start: _Token
    ) -> ast.AST:
        while True:
            if self.at("."):
                self.advance()
                attribute = self.expect_ident()
                node = _span(
                    _node(Attribute, value=node, attr=attribute, ctx=ast.Load()),
                    start,
                    self.tokens[self.position - 1],
                )
                continue
            if self.at("("):
                if not allow_call:
                    self.reject("call is outside the closed value grammar")
                self.advance()
                args: list[ast.AST] = []
                while not self.at(")"):
                    if self.current.kind == "punct" and self.current.text == "...":
                        self.reject("spread call argument")
                    args.append(self.parse_expression(allow_call=True))
                    if not self.accept(","):
                        break
                self.expect(")")
                node = _span(
                    _node(Call, func=node, args=args, keywords=[]),
                    start,
                    self.tokens[self.position - 1],
                )
                continue
            return node

    def parse_array(self, *, allow_call: bool) -> ast.AST:
        start = self.expect("[")
        elements: list[ast.AST] = []
        while not self.at("]"):
            if self.current.kind == "punct" and self.current.text == "...":
                self.reject("spread array element")
            elements.append(self.parse_expression(allow_call=allow_call))
            if not self.accept(","):
                break
        self.expect("]")
        return _span(
            _node(List, elts=elements, ctx=ast.Load()),
            start,
            self.tokens[self.position - 1],
        )

    def parse_object(self, *, allow_call: bool) -> ast.AST:
        start = self.expect("{")
        keys: list[ast.AST] = []
        values: list[ast.AST] = []
        while not self.at("}"):
            token = self.current
            if token.kind == "punct" and token.text == "...":
                self.reject("spread object property")
            if token.kind in ("ident", "string", "number", "template"):
                self.advance()
                key_name = _literal_value(token)
                if self.accept(":"):
                    value = self.parse_expression(allow_call=allow_call)
                else:
                    if token.kind != "ident":
                        self.reject("shorthand property must be an identifier")
                    value = _span(_node(Name, id=token.text, ctx=ast.Load()), token, token)
            else:
                self.reject(f"{token.text!r} is outside the closed object grammar")
            keys.append(_span(_node(Constant, value=key_name, kind=None), token, token))
            values.append(value)
            if not self.accept(","):
                break
        self.expect("}")
        return _span(
            _node(Dict, keys=keys, values=values),
            start,
            self.tokens[self.position - 1],
        )

    # -- JSX (tsx only) --------------------------------------------------

    def parse_jsx_element(self) -> ast.AST:
        start = self.expect("<")
        name = self.parse_jsx_name()
        attributes = self.parse_jsx_attributes()
        if self.at("/"):
            self.advance()
            self.expect(">")
            return _span(
                _node(JsxElement, name=name, attributes=attributes, children=[]),
                start,
                self.tokens[self.position - 1],
            )
        self.expect(">")
        children = self.parse_jsx_children()
        self.expect("<")
        self.expect("/")
        closing = self.parse_jsx_name()
        if closing != name:
            self.reject(f"JSX closing tag {closing!r} does not match {name!r}")
        self.expect(">")
        return _span(
            _node(JsxElement, name=name, attributes=attributes, children=children),
            start,
            self.tokens[self.position - 1],
        )

    def parse_jsx_name(self) -> str | None:
        if self.at(">") or self.at("/"):
            return None
        parts = [self.expect_ident()]
        while self.at(".") or self.at("-"):
            separator = self.advance().text
            parts.append(separator + self.expect_ident())
        return "".join(parts)

    def parse_jsx_attributes(self) -> list[ast.AST]:
        attributes: list[ast.AST] = []
        while not self.at(">") and not self.at("/"):
            name_token = self.current
            name = self.expect_ident()
            while self.at("-"):
                self.advance()
                name = name + "-" + self.expect_ident()
            value: ast.AST | None = None
            if self.accept("="):
                token = self.current
                if token.kind in ("string", "template"):
                    self.advance()
                    value = _span(
                        _node(Constant, value=_literal_value(token), kind=None),
                        token,
                        token,
                    )
                elif self.at("{"):
                    self.advance()
                    if self.at("}"):
                        self.reject("empty JSX attribute expression")
                    if self.current.kind == "punct" and self.current.text == "...":
                        self.reject("spread JSX attribute")
                    value = self.parse_expression(allow_call=True)
                    self.validate_value_expression(value, allow_call=True)
                    self.expect("}")
                else:
                    self.reject("JSX attribute value must be a literal or expression")
            attributes.append(
                _span(_node(JsxAttribute, name=name, value=value), name_token, name_token)
            )
        return attributes

    def parse_jsx_children(self) -> list[ast.AST]:
        children: list[ast.AST] = []
        while True:
            if self.current.kind == "eof":
                self.reject("unterminated JSX element")
            if self.at("<"):
                if self.peek().kind == "punct" and self.peek().text == "/":
                    return children
                children.append(self.parse_jsx_element())
                continue
            if self.at("{"):
                self.advance()
                if self.at("}"):
                    self.advance()
                    continue
                if self.at("/") and self.peek().kind == "punct" and self.peek().text == "*":
                    self.skip_jsx_comment()
                    continue
                if self.current.kind == "punct" and self.current.text == "...":
                    self.reject("spread JSX child")
                expression = self.parse_expression(allow_call=True)
                self.validate_value_expression(expression, allow_call=True)
                self.expect("}")
                children.append(expression)
                continue
            self.advance()

    def skip_jsx_comment(self) -> None:
        self.advance()
        self.advance()
        while not (self.at("*") and self.peek().kind == "punct" and self.peek().text == "/"):
            if self.current.kind == "eof":
                self.reject("unterminated JSX comment")
            self.advance()
        self.advance()
        self.expect("}")

    # -- closed value-expression grammar ---------------------------------

    def validate_value_expression(
        self,
        expression: ast.AST,
        *,
        allow_call: bool,
        call_target: bool = False,
    ) -> None:
        line = getattr(expression, "lineno", self.current.line)
        if isinstance(expression, (Name, Constant)):
            return
        if isinstance(expression, List):
            for item in expression.elts:
                self.validate_value_expression(item, allow_call=allow_call)
            return
        if isinstance(expression, Dict):
            for item in (*expression.keys, *expression.values):
                self.validate_value_expression(item, allow_call=allow_call)
            return
        if isinstance(expression, Attribute) and call_target:
            self.validate_value_expression(
                expression.value, allow_call=allow_call, call_target=True
            )
            return
        if isinstance(expression, Call) and allow_call:
            if not isinstance(expression.func, (Name, Attribute, Call)):
                _grammar(self.relative_path, line, "unsupported call target")
            self.validate_value_expression(expression.func, allow_call=True, call_target=True)
            for argument in expression.args:
                self.validate_value_expression(argument, allow_call=True)
            return
        if isinstance(expression, JsxElement):
            for attribute in expression.attributes:
                if attribute.value is not None:
                    self.validate_value_expression(attribute.value, allow_call=True)
            for child in expression.children:
                self.validate_value_expression(child, allow_call=True)
            return
        _grammar(
            self.relative_path,
            line,
            f"{type(expression).__name__} is outside the closed expression grammar",
        )

    # -- module resolution ----------------------------------------------

    def resolve_specifier(self, spec: str, line: int) -> str:
        if not (spec.startswith("./") or spec.startswith("../")):
            return spec
        base = os.path.dirname(self.relative_path)
        joined = os.path.normpath(os.path.join(base, spec))
        if joined.startswith("..") or os.path.isabs(joined):
            _block("SOURCE_ROOT_ESCAPE", f"{self.relative_path}:{line}: {spec}")
        candidates = []
        for suffix in ("", ".ts", ".tsx", "/index.ts", "/index.tsx"):
            candidate = joined + suffix
            if candidate not in candidates and (self.source_root / candidate).is_file():
                candidates.append(candidate)
        if len(candidates) > 1:
            _block(
                "SOURCE_IMPORT_AMBIGUOUS",
                f"{self.relative_path}:{line}: {spec}: {candidates}",
            )
        return candidates[0] if candidates else spec


def _string_value(text: str) -> str:
    if text.startswith(("'", '"')):
        body = text[1:-1]
        return body.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
    return text[1:-1]


def _literal_value(token: _Token) -> object:
    if token.kind == "number":
        text = token.text.replace("_", "")
        try:
            if text.lower().startswith(("0x", "0b", "0o")):
                return int(text, 0)
            return int(text) if "." not in text and "e" not in text.lower() else float(text)
        except ValueError:
            _block("SOURCE_PARSE_FAILED", f"malformed numeric literal {text!r}")
    if token.kind in ("string", "template"):
        return _string_value(token.text)
    return token.text


def parse_typescript_module(
    path: Path,
    relative_path: str,
    snapshot: bytes,
    *,
    tsx: bool,
    source_root: Path | None = None,
) -> d85.ModuleIndex:
    if source_root is None:
        source_root = path
        for _ in Path(relative_path).parts:
            source_root = source_root.parent
    try:
        source = snapshot.decode("utf-8")
    except UnicodeDecodeError as exc:
        _block("SOURCE_PARSE_FAILED", f"{path}: {exc}")
    tokens = _tokenize(source, relative_path)
    parser = _Parser(tokens, relative_path, source_root, tsx)
    parser.parse_module()
    symbols = dict(d85._index_symbols(parser.module_body))
    for alias, target in parser.export_aliases.items():
        node = parser.module_functions.get(target)
        if node is None:
            _block("SOURCE_PARSE_FAILED", f"{relative_path}: export alias {alias!r}")
        symbols[alias] = node
    return d85.ModuleIndex(
        relative_path=relative_path,
        symbols=symbols,
        imports=parser.imports,
        language=LANGUAGE,
    )
