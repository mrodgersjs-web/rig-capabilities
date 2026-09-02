"""Surface tools: the verdict machinery behind the MCP surface, callable by name.

`paired_runs`, `skill_contract`, `acceptance_identity`, `lifecycle`, `topology` and
the two estate scanners (`scripts/exemplar_resolution.py`,
`scripts/frontmatter_visibility.py`) all compute real verdicts — and until now an
agent could reach none of them from the one surface it is supposed to pull from.
It could read an asset's `done_when` but not ask "does this plan dispatch a cycle",
"which of my `great_example` paths dangle", or "did this paired-run ledger actually
isolate the variable". The finding stayed in the repo and out of the loop.

Design rules, each because of a failure seen in this repo:

* **Read-only.** No writes, no network, no model. `read_only: True` in every
  result, per the house convention for the five fable-2031 tools.
* **Same code path as the CLI.** Verdicts come from the modules' own `main()` (or
  the committed script's `main()`), stdout captured, so the surface cannot
  disagree with `./bin/rig-capabilities`. A second implementation of a check is how
  `40.0.0` ended up nine rungs out of date.
* **`ran` is not `clean`.** These scanners exit 1 to report debt (dangling
  exemplars, contract findings) and 2 to refuse (unreadable input, planted
  nonsense). Collapsing the two is how "0 of 19 done-tests ran" once read as
  `pass: true`. So every result carries `ran`, `clean` and `exit_code`, and an
  empty scan on a run that claimed success is reported as `surface_empty`.
* **Refusal by name, and repo-rooted paths only.** Every argv token naming an
  existing file must resolve inside the repo; otherwise the tool refuses without
  reading it. A read-only tool that will read `/etc/passwd` is not read-only in
  the sense that matters.
"""
from __future__ import annotations

import contextlib
import importlib.util
import inspect
import io
import json
import os
import re
from pathlib import Path

CHECKS = ("paired_runs", "skill_contract", "acceptance_identity", "lifecycle",
          "topology")
# display name -> committed script under scripts/
SCANNERS = (("exemplars", "exemplar_resolution"),
            ("frontmatter", "frontmatter_visibility"))
SUMMARY_RE = re.compile(r"HEAD_BYTES=\d+\s+clean=\d+\s+other_unloaded=\d+\s+"
                        r"truncation_hidden=\d+")
# Tail kept for the two summary parsers. 4 KB so a long debt list cannot push
# the scanner's own summary line out of reach; if it ever does, the counts come
# back None and `counts_unreadable` fires instead of a quiet zero.

TAIL_CHARS = 4000
RAN_MAX = 1

CONTRACT_RE = re.compile(
    r"skill_contract:\s*(?P<findings>\d+)\s+finding\(s\) across\s+(?P<files>\d+)\s+file\(s\)"
    r"\s*\[(?P<verdicts>[^\]]*)\]")


def _parse_contract(res: dict) -> dict:
    """Fold the scanner's own summary line into `data`, or refuse."""
    m = CONTRACT_RE.search(res.get("text", ""))
    if not m:
        if res.get("ran"):
            res["ran"] = False
            res["clean"] = False
            res["reason"] = "counts_unreadable:skill_contract"
        return res
    tally = dict(re.findall(r"([A-Z_]+)=(\d+)", m.group("verdicts")))
    res["data"] = {"findings": int(m.group("findings")),
                   "scanned": int(m.group("files")),
                   "by_verdict": {k: int(v) for k, v in tally.items()}}
    return res


class Guard(Exception):
    """A refusal the caller must see as a named reason, never as data."""


def _repo_root(repo) -> Path:
    return Path(getattr(repo, "root", None) or repo).resolve()


def _inside(root: Path, token: str) -> bool:
    p = Path(os.path.expanduser(str(token)))
    p = p if p.is_absolute() else root / p
    try:
        p.resolve().relative_to(root)
    except ValueError:
        return False
    return True


def _guard_argv(root: Path, argv: list) -> None:
    """Refuse before anything outside the repo is read."""
    for tok in argv:
        s = str(tok)
        if s.startswith("-") or s == "-":
            continue
        cand = Path(os.path.expanduser(s))
        if not (cand.is_absolute() or (root / cand).exists()):
            continue                                # a word, a date, a mutation
        if not _inside(root, s):
            raise Guard(f"path_outside_repo:{s}")


def _capture(fn, argv: list) -> dict:
    """Run a committed `main(argv)` in-process and keep its exit code.

    stdout and stderr are kept apart because exit 2 means two opposite things
    here. `lifecycle` printing `assets_unreadable:<path>: <why>` on stderr with
    an empty stdout is a refusal; `--plant revocation` printing the violated rule
    on stdout and exiting 2 is the guard FIRING, which is exactly what the
    assets' own `done_when` asserts (`rc=$?; test $rc -eq 2`). The exit code
    alone cannot tell those apart. A verdict on stdout can.
    """
    so, se = io.StringIO(), io.StringIO()
    zero_arg = not list(inspect.signature(fn).parameters)
    with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
        try:
            rc = fn() if zero_arg else fn(argv)
        except SystemExit as exc:                    # argparse / sys.exit(n)
            rc = exc.code if isinstance(exc.code, int) else 1
        except Exception as exc:                     # noqa: BLE001 — report, never raise
            return {"ran": False, "clean": False, "exit_code": 2,
                    "reason": f"{type(exc).__name__}:{exc}",
                    "stderr": se.getvalue()[-TAIL_CHARS:]}
    out_s, err_s = so.getvalue(), se.getvalue()
    try:
        rc = int(rc or 0)
    except (TypeError, ValueError):                  # a main() that returns None/True
        rc = 1 if out_s.strip() else 2
    out: dict = {"ran": rc <= RAN_MAX or bool(out_s.strip()),
                 "clean": rc == 0, "exit_code": rc}
    payload = None
    start = out_s.find("{")
    if start >= 0:
        try:
            payload, _ = json.JSONDecoder().raw_decode(out_s[start:])
        except Exception:                            # noqa: BLE001
            payload = None
    if isinstance(payload, (dict, list)):
        out["data"] = payload
    out["text"] = out_s.strip()[-TAIL_CHARS:]
    if err_s.strip():
        out["stderr"] = err_s.strip()[-TAIL_CHARS:]
    return out


def _load_script(root: Path, name: str):
    """Exec a committed scanner out of scripts/ so the surface runs ITS code."""
    path = root / "scripts" / f"{name}.py"
    if not path.is_file():
        raise Guard(f"script_missing:scripts/{name}.py")
    spec = importlib.util.spec_from_file_location(f"_rig_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                     # committed repo code, read-only
    return mod


def _require_ran(res: dict, label: str) -> dict:
    """A run that produced NOTHING is a refusal, not a pass.

    Only total silence counts — both streams, since verdicts land on stdout for
    some modules (`topology`: "OK … acyclic on dispatch") and stderr for others
    (`paired_runs` reports a defective ledger on stderr and exits 1). Demanding
    JSON specifically would turn a text verdict into a fake red, which is the
    same error pointed the other way.
    """
    if (res.get("ran") and "data" not in res and not res.get("text", "").strip()
            and not res.get("stderr", "").strip()):
        res["ran"] = False
        res["clean"] = False
        res["reason"] = f"surface_empty:{label}"
    return res


def _module_main(check: str, argv: list) -> dict:
    if check == "paired_runs":
        from . import paired_runs
        return _capture(paired_runs.main, ["check", *argv])
    if check == "skill_contract":
        from . import skill_contract
        # No `--json`: that mode streams one JSON object per finding and has no
        # summary at all, so a caller that `raw_decode`s it gets the FIRST
        # finding and reports it as the whole verdict. The text mode's last line
        # is the scanner's own aggregate; parsing that keeps one implementation.
        return _parse_contract(_capture(skill_contract.main, list(argv)))
    if check == "lifecycle":
        from . import lifecycle
        return _capture(lifecycle.main, argv)
    if check == "topology":
        from . import topology
        return _capture(topology.main, argv)
    raise Guard(f"unknown_check:{check}")


# --------------------------------------------------------------------------
def verdict(repo, args: dict) -> dict:
    """One verdict from one module, through the module's own CLI path.

    args: {"check": one of CHECKS, "argv": [tokens that module expects]}
    """
    root = _repo_root(repo)
    check = str(args.get("check") or "")
    argv = [str(a) for a in (args.get("argv") or [])]
    if check not in CHECKS:
        return {"read_only": True, "ran": False, "clean": False, "root": str(root),
                "reason": f"unknown_check:{check or '(missing)'}",
                "checks": list(CHECKS)}
    try:
        _guard_argv(root, argv)
    except Guard as g:
        return {"read_only": True, "ran": False, "clean": False, "root": str(root),
                "reason": str(g), "check": check}
    if check == "acceptance_identity":
        if not argv:
            return {"read_only": True, "ran": False, "clean": False, "root": str(root),
                    "reason": "record_missing", "check": check}
        p = Path(os.path.expanduser(argv[0]))
        p = p if p.is_absolute() else root / p
        if not p.is_file():
            return {"read_only": True, "ran": False, "clean": False, "root": str(root),
                    "reason": f"record_missing:{argv[0]}", "check": check}
        raw = p.read_bytes()
        from .acceptance_identity import evaluate
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            return {"read_only": True, "ran": False, "clean": False, "root": str(root),
                    "check": check, "exit_code": 2,
                    "reason": f"record_unreadable:{exc.msg}"}
        res = {"ran": True, "clean": True, "exit_code": 0,
               "data": evaluate(record, raw)}
    else:
        # Relative tokens are repo-relative, NOT process-relative: the handlers
        # run in-process, so leaving `examples/…` alone would resolve it against
        # whatever cwd the agent process happens to have and report
        # "No such file or directory" for a file that is right there.
        resolved = []
        for a in argv:
            cand = Path(os.path.expanduser(a))
            resolved.append(str(root / a) if (cand.exists() or (root / cand).exists())
                            and not cand.is_absolute() else a)
        res = _module_main(check, resolved)
    res = _require_ran(res, check)
    res.update({"read_only": True, "check": check, "root": str(root), "argv": argv})
    if not res["ran"] and "reason" not in res:
        # Name the refusal with what the module actually said (`assets_unreadable:
        # …`, argparse's `usage: …`), not just a bare exit code.
        first = (res.get("stderr") or "").strip().splitlines()
        res["reason"] = (first[0].strip() if first
                         else f"exit_code_{res.get('exit_code')}")
    return res


def asset_hygiene(repo, args: dict) -> dict:
    """What the estate cannot see about itself: dangling exemplars, frontmatter
    invisible to the 4096-byte read, skill slots never declared.

    `ran` means every scanner reported. `clean` means none of them found debt.
    Debt is reported in `debt`, never folded into a refusal.
    """
    root = _repo_root(repo)
    out = {"read_only": True, "root": str(root), "surfaces": {}}
    s = out["surfaces"]

    for name, script in SCANNERS:
        argv = ["--root", str(root), "--json"] if script == "exemplar_resolution" else []
        try:
            mod = _load_script(root, script)
            s[name] = _capture(mod.main, argv)
        except Guard as g:
            s[name] = {"ran": False, "clean": False, "exit_code": 2, "reason": str(g)}
        except Exception as exc:                     # noqa: BLE001
            s[name] = {"ran": False, "clean": False, "exit_code": 2,
                       "reason": f"{type(exc).__name__}:{exc}"}
    # Scope is the canonical estate, not the whole tree: `skill_contract .` walks
    # `.index.json`, `out/`, `examples/` and `.context/` too and reported 1,875
    # files / 12,901 findings — a number that looks like an estate verdict and is
    # instead an accident of the argument. Default `capabilities`, and say the
    # scope out loud so no caller mistakes one for the other.
    scope = str(args.get("scope") or "capabilities")
    out["scope"] = scope
    if not _inside(root, scope) or not (root / scope).is_dir():
        s["contract"] = {"ran": False, "clean": False, "exit_code": 2,
                         "reason": f"scope_unusable:{scope}"}
    else:
        s["contract"] = _require_ran(_module_main("skill_contract", [str(root / scope)]),
                                     "contract")

    counts: dict = {}
    ex = s["exemplars"]
    if isinstance(ex.get("data"), dict):
        counts["declared_great_example"] = ex["data"].get("declared")
        counts["resolved_great_example"] = ex["data"].get("resolved")
        miss = ex["data"].get("missing")
        counts["dangling_great_example"] = len(miss) if isinstance(miss, list) else None
    fm = SUMMARY_RE.search(s["frontmatter"].get("text", ""))
    if fm:
        counts.update({f"frontmatter_{k}": int(v)
                       for k, v in re.findall(r"(\w+)=(\d+)", fm.group(0))})
    sc = s["contract"]
    if isinstance(sc.get("data"), dict):
        counts["contract_files_scanned"] = sc["data"].get("scanned")
        counts["contract_findings"] = sc["data"].get("findings")
    s["counts"] = counts

    debt = {k: v for k, v in (("dangling_great_example", counts.get("dangling_great_example")),
                             ("frontmatter_truncation_hidden",
                              counts.get("frontmatter_truncation_hidden")),
                             ("contract_findings", counts.get("contract_findings")))
            if v}
    out["ran"] = all(s[k].get("ran") for k in ("exemplars", "frontmatter", "contract"))
    # Anti-false-clean: every count this tool publishes must actually have been
    # read. A key that came back None means a scanner's shape moved, and `debt`
    # built from Nones reads as zero debt — the silently-empty answer that this
    # whole increment exists to eliminate.
    unreadable = [k for k in ("declared_great_example", "dangling_great_example",
                              "contract_files_scanned", "contract_findings",
                              "frontmatter_truncation_hidden")
                  if counts.get(k) is None]
    if unreadable:
        out["ran"] = False
        out["reason"] = "counts_unreadable:" + ",".join(unreadable)
    elif not out["ran"]:
        out["reason"] = "|".join(
            f"{k}:{s[k].get('reason') or 'exit_code_' + str(s[k].get('exit_code'))}"
            for k in ("exemplars", "frontmatter", "contract") if not s[k].get("ran"))
    out["clean"] = bool(out["ran"]) and not debt
    out["debt"] = debt
    return out
