#!/usr/bin/env python3
"""Probe this machine for agentic-framework setup and print one JSON receipt.

What it answers (stage E1 of agentic-systems-setup):
  - which toolchains exist (python3.12/3.13, uv, node, pnpm, npx, docker, java, colima, temporal)
    and their versions, searching PATH plus ~/.local/bin, ~/.homebrew/bin, /usr/local/bin, /opt/homebrew/bin
    because the Aside sandbox PATH omits them (lesson AS-03)
  - whether the Docker daemon answers (AS-04) and whether a Java runtime exists (AS-05)
  - whether PYTHONHOME/PYTHONPATH are exported into this shell (AS-02)
  - which OpenAI-compatible model endpoints answer GET /v1/models right now (AS-08)
  - the route each workload class can take: aside-sandbox, host-shell (Orca terminal), docker,
    each with BLOCKED reasons instead of guesses
  - library_validation (AS-11): whether this process tree refuses to load freshly written native
    code. Network-free: copy the interpreter's own stdlib extension (_json) into a temp dir (the
    sandbox stamps new files com.apple.quarantine), load the ORIGINAL (GREEN control) and the
    COPY. PRESENT = the copy failed with "library load disallowed by system policy" while the
    original loaded; LIKELY = the copy is quarantined and its load did not return within
    --libval-timeout (denials took 10 s once and over 100 s later on 2026-09-28); ABSENT = the
    copy loaded; UNKNOWN = the control failed or nothing ran.
  - listeners (AS-12): every TCP listener with pid, command, and bind address, flagging known
    framework ports and all-interface binds, so a stray server is reported, not reused

Usage:
  env -u PYTHONHOME -u PYTHONPATH python3 env_probe.py [--out receipt.json] [--endpoint URL ...]
                                                      [--no-lan] [--timeout 4] [--no-libval]
  env_probe.py --selftest-libval     classifier fixtures: RED message -> LIBRARY_VALIDATION,
                                     plain import errors -> OTHER; exit 0 correct, 2 wrong
  env_probe.py --libval-only [--libval-plant]
                                     run only the library-validation probe; the plant loads the
                                     original twice (no quarantined copy) and must report ABSENT
Exit: 0 probe completed (BLOCKED routes are data, not errors); 1 usage error.
Stdlib only. Read-only outside a temp dir it deletes: --version style commands, HTTP GETs, lsof.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

HOME = Path.home()
EXTRA_PATH = [str(HOME / ".local/bin"), str(HOME / ".homebrew/bin"), "/usr/local/bin", "/opt/homebrew/bin"]  # Mike's Homebrew prefix is ~/.homebrew
TOOLS = {
    "python3.12": ["--version"], "python3.13": ["--version"], "uv": ["--version"],
    "node": ["--version"], "pnpm": ["--version"], "npx": ["--version"],
    "docker": ["--version"], "colima": ["version"], "java": ["-version"],
    "temporal": ["--version"], "n8n": ["--version"], "limactl": ["--version"], "ollama": ["--version"],
}
LOOPBACK = [
    ("pair-router", "http://127.0.0.1:8771/v1"),
    ("mac-studio-tunnel", "http://127.0.0.1:8657/v1"),
    ("personal-ai-router", "http://127.0.0.1:11435/v1"),
    ("omniroute", "http://127.0.0.1:20128/v1"),
]
LAN = [
    ("blackwell-flash", "http://192.168.68.90:8011/v1"),
    ("blackwell-uncensored", "http://192.168.68.90:8111/v1"),
]


def run(argv: list[str], timeout: float = 20) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONHOME", "PYTHONPATH")}
    env["PATH"] = os.pathsep.join(EXTRA_PATH + [env.get("PATH", "")])
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, f"{type(e).__name__}: {e}"


def find(tool: str) -> str | None:
    return shutil.which(tool, path=os.pathsep.join(EXTRA_PATH + [os.environ.get("PATH", "")]))


def probe_tools() -> dict:
    out = {}
    for tool, args in TOOLS.items():
        path = find(tool)
        if not path:
            out[tool] = {"present": False}
            continue
        rc, text = run([path, *args])
        line = next((ln for ln in text.splitlines() if ln.strip() and "WARNING" not in ln), "")
        out[tool] = {"present": True, "path": path, "rc": rc, "version": line[:120],
                     "on_sandbox_path": shutil.which(tool) is not None}
    return out


def probe_endpoint(name: str, base: str, timeout: float) -> dict:
    url = base.rstrip("/") + "/models"
    t0 = time.time()
    try:
        with urllib.request.urlopen(urllib.request.Request(url), timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8", "ignore") or "{}")
            ids = [m.get("id") for m in body.get("data", [])][:8]
            return {"name": name, "base_url": base, "state": "ANSWERED", "http": r.status,
                    "models": ids, "ms": int((time.time() - t0) * 1000)}
    except urllib.error.HTTPError as e:
        state = "KEYED" if e.code in (401, 403) else "HTTP_ERROR"
        return {"name": name, "base_url": base, "state": state, "http": e.code, "ms": int((time.time() - t0) * 1000)}
    except Exception as e:  # noqa: BLE001 - every failure class is data here
        msg = str(getattr(e, "reason", e))
        state = "TIMEOUT" if "timed out" in msg.lower() else "UNREACHABLE"
        return {"name": name, "base_url": base, "state": state, "error": msg[:120], "ms": int((time.time() - t0) * 1000)}


LIBVAL_MARKERS = ("library load disallowed by system policy", "not valid for use in process")
LIBVAL_FIXTURES = [
    ("dlopen(/x/_cffi_backend.cpython-312-darwin.so, 0x0002): tried: '/x/_cffi_backend.cpython-312-darwin.so' "
     "(code signature in <9B6B5FCA> '/x/_cffi_backend.cpython-312-darwin.so' not valid for use in process: "
     "library load disallowed by system policy)", "LIBRARY_VALIDATION"),
    ("No module named 'tiktoken'", "OTHER"),
    ("dynamic module does not define module export function (PyInit_x)", "OTHER"),
    ("", "OK"),
]
# Runs inside the framework interpreter (python3.12/3.13), not in this probe's own process.
# Prints one JSON line per stage and flushes, so a timeout still leaves the earlier stages.
LIBVAL_CHILD = r'''
import atexit, glob, importlib.util, json, os, shutil, subprocess, sys, sysconfig, tempfile, time
plant = sys.argv[1] == "plant"
src = sorted(glob.glob(os.path.join(sysconfig.get_path("platstdlib"), "lib-dynload", "_json*.so")))[0]
d = tempfile.mkdtemp(prefix="rig-libval-")
atexit.register(shutil.rmtree, d, True)
dst = src if plant else os.path.join(d, os.path.basename(src))
if not plant:
    with open(src, "rb") as a, open(dst, "wb") as b:
        b.write(a.read())
xa = lambda p: subprocess.run(["xattr", p], capture_output=True, text=True).stdout.split()
def emit(**k):
    print(json.dumps(k), flush=True)
def load(path):
    t = time.time()
    try:
        spec = importlib.util.spec_from_file_location("_json", path)
        spec.loader.exec_module(importlib.util.module_from_spec(spec))
        return "", round(time.time() - t, 2)
    except ImportError as e:
        return str(e), round(time.time() - t, 2)
emit(stage="setup", interpreter=sys.executable, version=sys.version.split()[0], original=src,
     original_xattr=xa(src), copy_xattr=xa(dst), plant=plant)
e, s = load(src); emit(stage="original", error=e, s=s)
e, s = load(dst); emit(stage="copy", error=e, s=s)
'''
KNOWN_PORTS = {80: "dify web", 3000: "dagster/flowise", 4111: "mastra", 4200: "prefect", 4400: "n8n (lab)",
               5001: "dify api", 5678: "n8n", 5679: "n8n task broker", 7233: "temporal", 7860: "langflow", 8080: "kestra/airflow",
               8233: "temporal ui", 8288: "inngest dev", 11434: "ollama"}


def classify_import_error(msg: str) -> str:
    if not msg:
        return "OK"
    return "LIBRARY_VALIDATION" if any(k in msg for k in LIBVAL_MARKERS) else "OTHER"


def probe_library_validation(plant: bool = False, timeout: float = 15.0) -> dict:
    py = find("python3.12") or find("python3.13")
    if not py:
        return {"state": "UNKNOWN", "reason": "no python3.12/3.13 found"}
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONHOME", "PYTHONPATH")}
    t0, timed_out = time.time(), False
    try:
        r = subprocess.run([py, "-c", LIBVAL_CHILD, "plant" if plant else "live"],
                           capture_output=True, timeout=timeout, env=env)
        raw = r.stdout
    except subprocess.TimeoutExpired as e:
        raw, timed_out = e.stdout or b"", True
    stages = {}
    for ln in raw.decode("utf-8", "ignore").splitlines():
        try:
            row = json.loads(ln)
            stages[row["stage"]] = row
        except (ValueError, KeyError):
            continue
    setup, orig_row, copy_row = stages.get("setup"), stages.get("original"), stages.get("copy")
    if not setup:
        return {"state": "UNKNOWN", "reason": "probe child produced no setup line", "timed_out": timed_out}
    quarantined = "com.apple.quarantine" in setup.get("copy_xattr", [])
    orig = classify_import_error(orig_row["error"]) if orig_row else "NOT_RUN"
    copy = classify_import_error(copy_row["error"]) if copy_row else ("TIMEOUT" if timed_out else "NOT_RUN")
    if orig != "OK":
        state = "UNKNOWN"
    elif copy == "LIBRARY_VALIDATION":
        state = "PRESENT"
    elif copy == "OK":
        state = "ABSENT"
    elif copy == "TIMEOUT" and quarantined:
        state = "LIKELY"
    else:
        state = "UNKNOWN"
    return {"state": state, "original": orig, "copy": copy, "copy_quarantined": quarantined,
            "timed_out": timed_out, "cap_s": timeout, "seconds": round(time.time() - t0, 1),
            "interpreter": setup.get("interpreter"), "python": setup.get("version"), "plant": setup.get("plant"),
            "detail": ((copy_row or {}).get("error") or (orig_row or {}).get("error") or "")[-160:]}


def probe_listeners() -> list[dict]:
    rc, text = run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], timeout=20)
    seen, out = set(), []
    for ln in text.splitlines()[1:]:
        parts = ln.split()
        if len(parts) < 9 or ":" not in parts[8]:
            continue
        addr, _, port = parts[8].rpartition(":")
        if not port.isdigit() or (parts[1], port) in seen:
            continue
        seen.add((parts[1], port))
        p = int(port)
        out.append({"port": p, "pid": int(parts[1]), "command": parts[0], "bind": addr,
                    "all_interfaces": addr in ("*", "0.0.0.0", "[::]"), "framework": KNOWN_PORTS.get(p)})
    return sorted(out, key=lambda x: x["port"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--endpoint", action="append", default=[], help="extra base URL ending in /v1")
    ap.add_argument("--no-lan", action="store_true")
    ap.add_argument("--timeout", type=float, default=4.0)
    ap.add_argument("--no-libval", action="store_true")
    ap.add_argument("--libval-only", action="store_true")
    ap.add_argument("--libval-plant", action="store_true")
    ap.add_argument("--libval-timeout", type=float, default=15.0)
    ap.add_argument("--selftest-libval", action="store_true")
    a = ap.parse_args()

    if a.selftest_libval:
        bad = [(m[:50], want, classify_import_error(m)) for m, want in LIBVAL_FIXTURES if classify_import_error(m) != want]
        print(json.dumps({"selftest_libval": "PASS" if not bad else "FAIL", "cases": len(LIBVAL_FIXTURES), "wrong": bad}))
        return 0 if not bad else 2
    if a.libval_only:
        r = probe_library_validation(plant=a.libval_plant, timeout=a.libval_timeout)
        print(json.dumps(r))
        return 0

    tools = probe_tools()
    docker = {"cli": tools["docker"].get("present", False)}
    if docker["cli"]:
        rc, text = run([tools["docker"]["path"], "info", "--format", "{{.ServerVersion}}"], timeout=15)
        docker.update({"daemon": rc == 0 and bool(text) and "Cannot connect" not in text,
                       "detail": text.splitlines()[-1][:200] if text else ""})
    java_ok = tools["java"].get("present") and tools["java"].get("rc") == 0
    # The macOS /usr/bin/java stub fails without a registered JDK; Homebrew JDKs are keg-only.
    jdks = []
    for jb in sorted(HOME.glob(".homebrew/opt/openjdk*/bin/java")) + sorted(Path("/opt/homebrew/opt").glob("openjdk*/bin/java")):
        rc, text = run([str(jb), "-version"], timeout=20)
        if rc == 0:
            jdks.append({"java": str(jb), "version": text.splitlines()[0][:80]})
    java_ok = bool(java_ok or jdks)
    colima = find("colima")
    if colima:
        rc, text = run([colima, "status"], timeout=20)
        docker["colima"] = {"path": colima, "status_rc": rc, "status": (text.splitlines() or [""])[-1][:160]}

    eps = LOOPBACK + ([] if a.no_lan else LAN) + [(f"extra-{i}", u) for i, u in enumerate(a.endpoint)]
    endpoints = [probe_endpoint(n, u, a.timeout) for n, u in eps]

    blocked = []
    if not docker.get("daemon"):
        blocked.append({"route": "docker", "reason": docker.get("detail") or "docker CLI absent", "check": "docker info"})
    if not java_ok:
        blocked.append({"route": "jvm", "reason": tools["java"].get("version") or "java absent", "check": "java -version and ~/.homebrew/opt/openjdk*/bin/java -version"})
    if not any(e["state"] == "ANSWERED" for e in endpoints):
        blocked.append({"route": "local-model", "reason": "no endpoint answered /v1/models", "check": "GET /v1/models"})
    libval = {"state": "SKIPPED"} if a.no_libval else probe_library_validation(timeout=a.libval_timeout)
    if libval.get("state") in ("PRESENT", "LIKELY"):
        blocked.append({"route": "python-native-fresh", "reason": "library validation refuses freshly written native .so (quarantined copy blocked, original loads)",
                        "check": "env_probe.py --libval-only"})
    listeners = probe_listeners()
    strays = [x for x in listeners if x["framework"]]

    receipt = {
        "probe": "agentic-env-probe", "version": 1,
        "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "host": os.uname().nodename, "cwd": os.getcwd(),
        "sandbox_hints": {
            "pythonhome_exported": "PYTHONHOME" in os.environ,
            "pythonpath_exported": "PYTHONPATH" in os.environ,
            "local_bin_on_path": str(HOME / ".local/bin") in os.environ.get("PATH", "").split(os.pathsep),
            "usr_local_bin_on_path": "/usr/local/bin" in os.environ.get("PATH", "").split(os.pathsep),
        },
        "tools": tools, "docker": docker, "java_runtime": bool(java_ok), "jdks": jdks, "endpoints": endpoints,
        "library_validation": libval,
        "listeners_on_framework_ports": strays,
        "listeners_all_interfaces": [x for x in listeners if x["all_interfaces"]],
        "routes": {
            "python": "aside-sandbox via uv venv" if tools["uv"].get("present") else "host-shell (uv absent here)",
            "python_native": ("host-shell (Orca terminal), or pure-Python fallback / pin / stub in the sandbox: freshly written native .so are refused here"
                              if libval.get("state") in ("PRESENT", "LIKELY") else "aside-sandbox" if libval.get("state") == "ABSENT" else "UNKNOWN: run --libval-only"),
            "node": "aside-sandbox for pure-JS deps; host-shell for native .node addons" if tools["node"].get("present") else "BLOCKED: node absent",
            "docker": "docker" if docker.get("daemon") else "BLOCKED",
            "jvm": (f"JAVA_HOME from {jdks[-1]['java']}" if jdks else "system java") if java_ok else "BLOCKED",
            "local_model": next((e["base_url"] for e in endpoints if e["state"] == "ANSWERED"), "BLOCKED"),
        },
        "blocked": blocked,
    }
    text = json.dumps(receipt, indent=1)
    if a.out:
        Path(a.out).write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
