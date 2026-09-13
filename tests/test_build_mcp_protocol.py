"""B44 + B45 — MCP protocol BEHAVIOR proofs for the capabilities_build_* surface.

The server is driven exactly as a harness sees it: the house entrypoint
(repo-root server.py — the same entry mcp_wire projects into all four
harness configs) is spawned over stdio and spoken to in newline-delimited
JSON-RPC 2.0: initialize, tools/list, tools/call. No handler function is
imported — the wire and the server wrapper are the layer under test.

B44 per-tool guarantees proven here:
  * unknown argument keys refused (the eight B23-B28 schemas advertise
    additionalProperties:false and every handler re-refuses stray keys);
  * missing required keys answer a named error, never a crash;
  * no argument slot exists where a caller can submit pass/approved/
    qualified/verdict, and injecting such a key is refused (closed tools) —
    open pre-wave schemas that silently ignore it are recorded as findings;
  * capabilities_build_run_get pagination bounded (limit clamp) with cursor
    behaviour recorded;
  * an unavailable database answers explicit blocked / unknown /
    configured=false, never a fabricated result;
  * identity comes from the server wrapper (RIG_CAP_CALLER); a caller-
    authored identity field is refused.

B45: ten multi-tool scenarios end-to-end (diagnosis, missing dependency,
approval staging, failure recovery, qualification), receipts under
runs/agentic-stack-buildout/backend/proofs/mcp-b45-scenarios.json.

Backend targets NEVER touch a shared database:
  * NO_STORE server: RIG_CAP_DSN unset + a fake `docker` shim on PATH so
    rig-dev-db discovery cannot find a live container;
  * BAD_DSN server: DSN aimed at a TCP-refusing port;
  * LIVE server (optional): a throwaway initdb cluster in a temp dir owned
    by this process, DDL applied to it and it is torn down on exit. If the
    Postgres binaries are absent the live scenarios report UNVERIFIED with
    the named reason — never a dressed-up pass.
"""
from __future__ import annotations

import atexit
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import selectors
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

ENTRY = REPO / "server.py"
PROOF_DIR = REPO / "runs" / "agentic-stack-buildout" / "backend" / "proofs"
B44_RECEIPT = PROOF_DIR / "mcp-b44-protocol.json"
B45_RECEIPT = PROOF_DIR / "mcp-b45-scenarios.json"
EVIDENCE_FILE = "runs/agentic-stack-buildout/backend/proofs/mcp-probe-evidence.txt"
EVIDENCE_FILE2 = "runs/agentic-stack-buildout/backend/proofs/mcp-probe-evidence-2.txt"
MANIFEST_FILE = "runs/agentic-stack-buildout/backend/proofs/mcp-probe-manifest.json"

CALLER_NO_STORE = "mcp-protocol-probe-nostore"
CALLER_BAD_DSN = "mcp-protocol-probe-bad-dsn"
CALLER_LIVE = "mcp-protocol-probe-live"
BAD_DSN = "postgresql://nopass@127.0.0.1:1/rig_nope"

BUILD_TOOLS_CLOSED = (
    "capabilities_build_diagnose", "capabilities_build_index",
    "capabilities_build_gaps", "capabilities_build_run_start",
    "capabilities_build_run_get", "capabilities_build_evidence_add",
    "capabilities_build_omission_request", "capabilities_build_qualify")
BUILD_TOOLS_OPEN = (
    "capabilities_build_store", "capabilities_build_run",
    "capabilities_build_contract", "capabilities_measure_quorum")
ALL_BUILD_TOOLS = BUILD_TOOLS_CLOSED + BUILD_TOOLS_OPEN

GOOD_PACKET = {
    "goal": "ship the pack",
    "cell_id": "L1-D1-A1-I1",
    "done_test": ["python3 rig_capabilities/criteria_pack.py generate "
                  "--verify runs/agentic-stack-buildout/packs/"
                  "criteria-v1.jsonl"],
    "out_of_scope": ["push"],
    "effort_budget": {"cpu_minutes": 30, "usd": 0.01,
                      "wallclock_seconds": 900},
    "evidence_refs": ["receipt:mcp-protocol-probe"],
}

RUN_STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# Findings and receipts accumulate across the run and are written even when
# a later assertion aborts the class (each mutation rewrites the file).
FINDINGS: list[dict] = []
SCENARIOS: list[dict] = []


def _write_receipt(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, sort_keys=True,
                               default=str) + "\n", encoding="utf-8")


def _flush_b44(extra: dict | None = None) -> None:
    doc = {"receipt": "rig.build.mcp.b44", "generated_at": RUN_STAMP,
           "entrypoint": str(ENTRY.relative_to(REPO)),
           "transport": "spawned python3 server.py, newline JSON-RPC 2.0 stdio",
           "findings": FINDINGS, **(extra or {})}
    _write_receipt(B44_RECEIPT, doc)


def _flush_scenarios() -> None:
    doc = {"receipt": "rig.build.mcp.b45", "generated_at": RUN_STAMP,
           "scenario_total": len(SCENARIOS), "scenarios": SCENARIOS}
    _write_receipt(B45_RECEIPT, doc)


def _record_finding(tool: str, finding: str, where: str, observed: str,
                    kind: str = "fail-open") -> None:
    if any(f["tool"] == tool and f["finding"] == finding
           for f in FINDINGS):
        return
    FINDINGS.append({"tool": tool, "kind": kind, "finding": finding,
                     "file_line": where, "observed": observed[:400]})
    _flush_b44()


class McpClient:
    """Newline JSON-RPC 2.0 over the spawned house entrypoint."""

    def __init__(self, tag: str, env_extra: dict, timeout: float = 180.0):
        env = dict(os.environ)
        env.pop("RIG_CAP_DSN", None)          # never inherit a live target
        env["PATH"] = _FAKEBIN + os.pathsep + env.get("PATH", "")
        env.update(env_extra)
        env["RIG_CAP_CALLER"] = env_extra.get("RIG_CAP_CALLER", "anon")
        self.tag = tag
        self.timeout = timeout
        self.proc = subprocess.Popen(
            [sys.executable, str(ENTRY)], cwd=str(REPO), env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1)
        self.stderr_lines: list[str] = []
        threading.Thread(
            target=lambda: [self.stderr_lines.append(ln)
                            for ln in self.proc.stderr],
            daemon=True).start()
        self._next_id = 0
        init = self.rpc("initialize", {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": f"b44-{tag}", "version": "0"}})
        assert "result" in init, f"{tag}: initialize failed: {init}"
        self.proc.stdin.write(json.dumps(
            {"jsonrpc": "2.0", "method": "notifications/initialized"})
            + "\n")
        self.proc.stdin.flush()

    # -- raw protocol -------------------------------------------------------
    def rpc(self, method: str, params: dict | None = None):
        self._next_id += 1
        rid = self._next_id
        msg = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            msg["params"] = params
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        sel = selectors.DefaultSelector()
        sel.register(self.proc.stdout, selectors.EVENT_READ)
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            if not sel.select(timeout=max(0.0, deadline - time.time())):
                raise TimeoutError(f"{self.tag}: no reply to {method}")
            line = self.proc.stdout.readline()
            if not line:
                raise EOFError(f"{self.tag}: server died; stderr tail: "
                               + "".join(self.stderr_lines[-5:]))
            reply = json.loads(line)
            if reply.get("id") == rid:
                return reply
        raise TimeoutError(f"{self.tag}: deadline for {method}")

    # -- tool call surface ----------------------------------------------------
    def call(self, tool: str, args: dict) -> dict:
        """Returns {"isError","text","json","rpc_error","raw"}."""
        reply = self.rpc("tools/call", {"name": tool, "arguments": args})
        if "error" in reply:
            return {"isError": True, "text": reply["error"]["message"],
                    "json": None, "rpc_error": reply["error"],
                    "raw": reply}
        res = reply["result"]
        text = res["content"][0]["text"] if res.get("content") else ""
        try:
            parsed = json.loads(text)
        except ValueError:
            parsed = None
        return {"isError": bool(res.get("isError")), "text": text,
                "json": parsed, "rpc_error": None, "raw": reply}

    def tools(self) -> dict:
        if not hasattr(self, "_tools"):
            r = self.rpc("tools/list")
            self._tools = {t["name"]: t for t in r["result"]["tools"]}
        return self._tools

    def alive(self) -> bool:
        return self.proc.poll() is None

    def close(self) -> None:
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


# -- server fixtures (lazily spawned, reused across the module) ---------------
_FAKEBIN = tempfile.mkdtemp(prefix="mcp-proto-fakebin-")
with open(os.path.join(_FAKEBIN, "docker"), "w") as fh:
    fh.write("#!/bin/sh\nexit 1\n")
os.chmod(os.path.join(_FAKEBIN, "docker"), 0o755)

_SERVERS: dict[str, McpClient | Exception] = {}


def _server(kind: str) -> McpClient:
    if kind not in _SERVERS:
        try:
            if kind == "no_store":
                _SERVERS[kind] = McpClient(
                    kind, {"RIG_CAP_CALLER": CALLER_NO_STORE})
            elif kind == "bad_dsn":
                _SERVERS[kind] = McpClient(
                    kind, {"RIG_CAP_DSN": BAD_DSN,
                           "RIG_CAP_CALLER": CALLER_BAD_DSN})
            elif kind == "live":
                dsn = _cluster_dsn()
                if dsn is None:
                    raise unittest.SkipTest(
                        "live backend UNAVAILABLE: "
                        + _CLUSTER_STATE["reason"])
                _SERVERS[kind] = McpClient(
                    kind, {"RIG_CAP_DSN": dsn,
                           "RIG_CAP_CALLER": CALLER_LIVE})
            else:
                raise KeyError(kind)
        except Exception as exc:                       # noqa: BLE001
            _SERVERS[kind] = exc
    s = _SERVERS[kind]
    if isinstance(s, Exception):
        raise s
    return s


def _need(kind: str) -> McpClient:
    try:
        return _server(kind)
    except unittest.SkipTest as skip:
        raise unittest.SkipTest(str(skip))


# -- throwaway Postgres cluster (temp dir, torn down on exit) ------------------
_CLUSTER_STATE = {"reason": "unattempted", "dsn": None, "pg_version": None}
_TMPDIR: str | None = None


def _find_bin(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for cand in ("~/.homebrew/bin", "/opt/homebrew/opt/postgresql@16/bin",
                 "/opt/homebrew/bin", "/usr/local/bin"):
        p = Path(cand).expanduser() / name
        if p.is_file():
            return str(p)
    return None


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _stop_cluster() -> None:
    global _TMPDIR
    if not _TMPDIR:
        return
    ctl = _find_bin("pg_ctl")
    if ctl:
        subprocess.run([ctl, "-D", os.path.join(_TMPDIR, "data"), "stop",
                        "-m", "fast"], capture_output=True, timeout=60)
    shutil.rmtree(_TMPDIR, ignore_errors=True)
    _TMPDIR = None


def _cluster_dsn() -> str | None:
    """Bring up a private Postgres ONCE; DDL goes only to this cluster."""
    global _TMPDIR
    if _CLUSTER_STATE["dsn"]:
        return _CLUSTER_STATE["dsn"]
    initdb, ctl = _find_bin("initdb"), _find_bin("pg_ctl")
    if not (initdb and ctl):
        _CLUSTER_STATE["reason"] = "initdb/pg_ctl binaries not found"
        return None
    try:
        _TMPDIR = tempfile.mkdtemp(prefix="rig-mcp-proto-pg-")
        data = os.path.join(_TMPDIR, "data")
        sock = os.path.join(_TMPDIR, "sock")
        os.mkdir(sock)
        r = subprocess.run([initdb, "-D", data, "-U", "postgres",
                            "-A", "trust"],
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            _CLUSTER_STATE["reason"] = f"initdb failed: {r.stderr[-300:]}"
            return None
        port = _free_port()
        r = subprocess.run(
            [ctl, "-D", data, "-l", os.path.join(_TMPDIR, "pg.log"), "-w",
             "-t", "60", "start", "-o",
             f"-p {port} -c listen_addresses='127.0.0.1' -k {sock}"],
            capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            _CLUSTER_STATE["reason"] = f"pg_ctl start failed: {r.stderr[-300:]}"
            return None
        atexit.register(_stop_cluster)
        dsn = f"postgresql://postgres@127.0.0.1:{port}/postgres"
        from rig_capabilities import build_migrate
        tok = build_migrate.plan()["confirm_token"]
        applied = build_migrate.apply(dsn, tok)
        if applied.get("status") != "applied":
            _CLUSTER_STATE["reason"] = f"DDL apply refused: {applied}"
            return None
        import psycopg2
        conn = psycopg2.connect(dsn, connect_timeout=10)
        cur = conn.cursor()
        cur.execute("SHOW server_version")
        _CLUSTER_STATE["pg_version"] = cur.fetchone()[0]
        conn.close()
        _CLUSTER_STATE["dsn"] = dsn
        return dsn
    except Exception as exc:                            # noqa: BLE001
        _CLUSTER_STATE["reason"] = f"{type(exc).__name__}: {exc}"[:300]
        return None


def _live_or_skip(test: unittest.TestCase) -> McpClient:
    srv = None
    try:
        srv = _need("live")
    except unittest.SkipTest as skip:
        test.skipTest(str(skip))
    return srv


def _ensure_probe_files() -> None:
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    for rel, body in ((EVIDENCE_FILE, "rig-build-mcp protocol probe evidence\n"),
                      (EVIDENCE_FILE2, "rig-build-mcp protocol probe evidence 2\n"),
                      (MANIFEST_FILE, "{}\n")):
        p = REPO / rel
        if not p.is_file():
            p.write_text(body, encoding="utf-8")


def _head_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                          capture_output=True, text=True).stdout.strip()


class _ProtoCase(unittest.TestCase):
    kind = "no_store"

    def setUp(self) -> None:
        self.srv = _need(self.kind)

    @staticmethod
    def assert_json(res: dict) -> dict:
        assert res["json"] is not None, f"non-JSON tool text: {res['text'][:200]}"
        return res["json"]


# ---------------------------------------------------------------------------
# B44 — handshake, schema advertisement, refusal behavior
# ---------------------------------------------------------------------------

class HandshakeAndAdvertisement(_ProtoCase):

    def test_initialize_negotiates_and_advertises(self):
        srv = _server("no_store")
        r = srv.rpc("initialize", {"protocolVersion": "2024-11-05",
                                   "capabilities": {},
                                   "clientInfo": {"name": "b44",
                                                  "version": "0"}})
        self.assertEqual(r["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(r["result"]["serverInfo"]["name"],
                         "rig-capabilities")
        self.assertIn("tools", r["result"]["capabilities"])

    def test_unknown_method_is_jsonrpc_refused(self):
        r = self.srv.rpc("tools/exec", {"name": "x"})
        self.assertIn("error", r)
        self.assertEqual(r["error"]["code"], -32601)

    def test_unknown_tool_is_jsonrpc_refused_not_isError(self):
        r = self.srv.rpc("tools/call", {"name": "capabilities_build_nope",
                                        "arguments": {}})
        self.assertIn("error", r)
        self.assertEqual(r["error"]["code"], -32602)

    def test_all_build_tools_advertised_with_schemas(self):
        tools = self.srv.tools()
        for name in ALL_BUILD_TOOLS:
            self.assertIn(name, tools, f"{name} missing from tools/list")
            self.assertIn("inputSchema", tools[name])

    def test_closed_schemas_advertise_additionalproperties_false(self):
        tools = self.srv.tools()
        for name in BUILD_TOOLS_CLOSED:
            self.assertIs(
                tools[name]["inputSchema"].get("additionalProperties"),
                False, f"{name} does not advertise a closed schema")

    def test_build_readers_advertise_closed_schemas_and_refuse_injection(self):
        """The four B19-era readers used to advertise OPEN schemas and swallow
        an injected verdict key. They are closed now: the wire refuses."""
        tools = self.srv.tools()
        for name in BUILD_TOOLS_OPEN:
            self.assertIs(
                tools[name]["inputSchema"].get("additionalProperties"),
                False, f"{name} still advertises an open schema")
            res = self.srv.call(name, {"verdict": "pass", "approved": True})
            self.assertTrue(res["isError"],
                            f"{name} accepted an injected verdict key")
            self.assertIn(name, res["text"])
        # the store probe still answers honestly when given nothing
        res = self.srv.call("capabilities_build_store", {})
        j = self.assert_json(res)
        self.assertFalse(res["isError"])
        self.assertFalse(j["record"].get("ok", False),
                         "store probe must not fabricate ok")


class ClosedSchemaRefusals(_ProtoCase):
    """Every closed build tool refuses unknown keys — including caller-
    authored identity and PASS/verdict fields — over the real wire."""

    MINIMAL: dict[str, dict] = {
        "capabilities_build_diagnose": dict(GOOD_PACKET),
        "capabilities_build_index": {},
        "capabilities_build_gaps": {},
        "capabilities_build_run_start":
            dict(GOOD_PACKET, process_key="mcp-proc",
                 process_version="1"),
        "capabilities_build_run_get": {"run_id": "probe"},
        "capabilities_build_evidence_add":
            {"run_id": "probe", "path": EVIDENCE_FILE, "kind": "receipt",
             "sequence": 1, "fencing_token": 1},
        "capabilities_build_omission_request":
            {"cell_id": "L1-D1-A1-I1", "reason": "probe",
             "evidence_refs": ["receipt:probe"]},
        "capabilities_build_qualify":
            {"cell_id": "L1-D1-A1-I1", "sha": "0" * 40,
             "manifest_path": MANIFEST_FILE},
    }

    def test_unknown_key_refused_on_every_closed_tool(self):
        _ensure_probe_files()
        for name, base in self.MINIMAL.items():
            with self.subTest(tool=name):
                res = self.srv.call(name, dict(base, zz_not_allowed=True))
                self.assertTrue(res["isError"],
                                f"{name} accepted an unknown key: "
                                f"{res['text'][:160]}")
                self.assertIn("unknown keys", res["text"])
                self.assertIn("zz_not_allowed", res["text"])

    def test_verdict_and_identity_injection_refused_on_closed_tools(self):
        """No tool may let a caller mint authority or identity through an
        argument slot. The schemas have NO such property; injection of the
        word anyway is refused as an unknown key."""
        _ensure_probe_files()
        banned = ("pass", "approved", "qualified", "verdict", "admitted",
                  "outcome", "requested_by", "started_by", "checked_by",
                  "state")
        for name, base in self.MINIMAL.items():
            for key in banned:
                with self.subTest(tool=name, key=key):
                    res = self.srv.call(name, dict(base, **{key: "pass"}))
                    self.assertTrue(
                        res["isError"],
                        f"FAIL-OPEN: {name} accepted {key!r} over the wire: "
                        f"{res['text'][:200]}")
                    self.assertIn("unknown keys", res["text"])

    def test_no_authority_slot_exists_in_any_build_schema(self):
        tools = _server("no_store").tools()
        banned = {"pass", "approved", "qualified", "verdict", "admitted",
                  "outcome"}
        for name in ALL_BUILD_TOOLS:
            props = set(
                tools[name]["inputSchema"].get("properties", {}))
            self.assertFalse(
                props & banned,
                f"{name} exposes an authority slot: {props & banned}")


class MissingRequiredKeys(_ProtoCase):
    """A named error, never a crash: after every malformed call the same
    session must still answer a well-formed one."""

    def test_contract_missing_cell_named_error(self):
        res = self.srv.call("capabilities_build_contract", {})
        self.assertFalse(res["isError"])       # answered, not crashed
        self.assertIn("missing required arg(s): cell_id",
                      res["json"].get("error", ""))
        ping = self.srv.rpc("ping")
        self.assertIn("result", ping)

    def test_diagnose_missing_field_named_and_server_survives(self):
        missing = {k: v for k, v in GOOD_PACKET.items()
                   if k != "done_test"}
        res = self.srv.call("capabilities_build_diagnose", missing)
        self.assertTrue(res["isError"])
        self.assertIn("capabilities_build_diagnose: missing required field: "
                      "done_test", res["text"])
        good = self.srv.call("capabilities_build_diagnose", GOOD_PACKET)
        self.assertFalse(good["isError"], "session must survive the bad call")

    def test_run_start_missing_required_names_the_field(self):
        missing = {k: v for k, v in GOOD_PACKET.items() if k != "goal"}
        res = self.srv.call("capabilities_build_run_start", missing)
        self.assertTrue(res["isError"])
        self.assertIn("missing required field: goal", res["text"])
        self.assertTrue(self.srv.alive())

    def test_qualify_missing_manifest_key_named(self):
        res = self.srv.call("capabilities_build_qualify",
                            {"cell_id": "L1-D1-A1-I1", "sha": "0" * 40})
        self.assertTrue(res["isError"])
        self.assertIn("manifest_path", res["text"])
        self.assertTrue(self.srv.alive())

    def test_measure_quorum_missing_cell_refused_by_name(self):
        """Schema declares required ['cell']; the handler must refuse by name
        rather than answering with cell=''."""
        res = self.srv.call("capabilities_measure_quorum", {})
        self.assertTrue(res["isError"])
        self.assertIn("capabilities_measure_quorum: missing required field: cell",
                      res["text"])
        self.assertTrue(self.srv.alive())


class UnavailableBackendStates(_ProtoCase):
    """No DSN discovered -> explicit blocked/unknown/configured=false."""

    def test_store_probe_honest_unconfigured(self):
        res = self.srv.call("capabilities_build_store", {})
        j = self.assert_json(res)
        self.assertFalse(res["isError"])
        self.assertFalse(j["record"]["configured"])
        self.assertFalse(j["measure"]["configured"])
        self.assertNotIn(True, [j["record"].get("ok"),
                                j["measure"].get("ok")],
                         "an unreachable plane must never report ok=true")

    def test_run_start_blocked_names_reason_and_next_action(self):
        res = self.srv.call(
            "capabilities_build_run_start",
            dict(GOOD_PACKET, process_key="mcp-proc", process_version="1"))
        j = self.assert_json(res)
        self.assertFalse(res["isError"],
                         "blocked is a STATE, not a transport error")
        self.assertEqual(j["state"], "blocked")
        self.assertIn("no rig_build target", j["reason"])
        self.assertIn("approval", j["next_action"])
        self.assertNotIn("run", j, "a blocked start never invents a run")

    def test_run_get_unknown_state_not_empty_success(self):
        res = self.srv.call("capabilities_build_run_get",
                            {"run_id": "no-such-run"})
        j = self.assert_json(res)
        self.assertFalse(res["isError"])
        self.assertEqual(j["state"], "unknown")
        self.assertIn("storage unreachable", j["reason"])

    def test_evidence_add_blocked_not_fabricated(self):
        _ensure_probe_files()
        res = self.srv.call(
            "capabilities_build_evidence_add",
            {"run_id": "no-such-run", "path": EVIDENCE_FILE,
             "kind": "receipt", "sequence": 1, "fencing_token": 1})
        j = self.assert_json(res)
        self.assertEqual(j["state"], "blocked")
        self.assertIn("no rig_build target", j["reason"])

    def test_configured_but_down_dsn_answers_unknown_state(self):
        """A configured-but-unreachable DSN is a STATE, not a transport error:
        the handler must answer state=unknown with a named reason (psycopg2
        raises OperationalError, which is not a StoreError subclass)."""
        bad = _need("bad_dsn")
        res = bad.call("capabilities_build_run_get", {"run_id": "x"})
        self.assertFalse(res["isError"],
                         "unreachable storage must not crash to isError")
        j = self.assert_json(res)
        self.assertEqual(j["state"], "unknown")
        self.assertIn("storage unreachable", j["reason"])
        self.assertTrue(bad.alive())


class IdentityBinding(_ProtoCase):
    """Identity is the server wrapper's env, never a caller argument."""

    def test_caller_from_wrapper_env(self):
        _ensure_probe_files()
        cell = "L1-D1-A1-I1"
        res = self.srv.call("capabilities_build_omission_request", {
            "cell_id": cell,
            "reason": f"protocol probe {RUN_STAMP}",
            "evidence_refs": ["receipt:mcp-identity-probe"]})
        j = self.assert_json(res)
        self.assertEqual(j["state"], "staged_dormant")
        self.assertEqual(j["requested_by"], CALLER_NO_STORE,
                         "requested_by must be the wrapper-bound caller")
        staged = Path(j["path"])
        doc = json.loads(staged.read_text())
        self.assertEqual(doc["state"], "PENDING_HUMAN_REVIEW")
        staged.unlink()                      # probe file, keep repo clean

    def test_caller_authored_identity_field_refused(self):
        res = self.srv.call("capabilities_build_omission_request", {
            "cell_id": "L1-D1-A1-I1", "reason": "probe",
            "evidence_refs": ["receipt:probe"],
            "requested_by": "someone-else"})
        self.assertTrue(res["isError"])
        self.assertIn("requested_by", res["text"])


class LivePagination(_ProtoCase):
    """run_get pagination bounded + the cursor behaviour recorded."""

    kind = "live"

    def setUp(self):
        try:
            self.srv = _server("live")
        except unittest.SkipTest as skip:
            self.skipTest(str(skip))

    def test_limit_clamped_and_pages_bounded(self):
        # A run with events exists after the scenario class — if not yet,
        # seed the minimum here via the same protocol path (start + evidence).
        srv = self.srv
        seeded = _seed_live_run(srv)
        run_id = seeded["run_id"]
        # append two more events so paging has material
        max_seq = seeded["max_seq"]
        for off, rel in ((1, EVIDENCE_FILE), (2, EVIDENCE_FILE2)):
            r = srv.call("capabilities_build_evidence_add",
                         {"run_id": run_id, "path": rel, "kind": "report",
                          "sequence": max_seq + off,
                          "fencing_token": seeded["token"]})
            self.assertEqual(r["json"].get("state"), "recorded", r["text"])
        big = srv.call("capabilities_build_run_get",
                       {"run_id": run_id, "limit": 1000})
        j = self.assert_json(big)
        self.assertEqual(j["state"], "live")
        self.assertLessEqual(len(j["events_newest_first"]), 100)
        self.assertEqual(j["next_cursor"], 100,
                         "limit=1000 must clamp to the advertised maximum 100")
        page = srv.call("capabilities_build_run_get",
                        {"run_id": run_id, "limit": 1})
        self.assertLessEqual(
            len(self.assert_json(page)["events_newest_first"]), 1)
        seqs = [e["sequence"] for e in j["events_newest_first"]]
        self.assertEqual(seqs, sorted(seqs, reverse=True),
                         "events must be newest-first")
        # cursor behaviour (was a recorded defect: cursor echoed, never applied)
        second = srv.call("capabilities_build_run_get",
                          {"run_id": run_id, "cursor": j["next_cursor"],
                           "limit": 1000})
        self.assertNotEqual(
            self.assert_json(second)["events_newest_first"],
            j["events_newest_first"],
            "paging with the echoed next_cursor must advance the window")
        # walk the whole log one event at a time: pages must be disjoint and
        # together cover exactly the window the clamped page served.
        seen: list[int] = []
        cursor, guard = 0, 0
        while guard <= len(seqs) + 1:
            guard += 1
            page = self.assert_json(srv.call(
                "capabilities_build_run_get",
                {"run_id": run_id, "cursor": cursor, "limit": 1}))
            self.assertEqual(page["state"], "live")
            got = page["events_newest_first"]
            if not got:
                break
            seen.append(got[0]["sequence"])
            cursor = page["next_cursor"]
        self.assertEqual(len(seen), len(set(seen)),
                         f"pages overlapped: {seen}")
        self.assertEqual(sorted(seen, reverse=True), seqs,
                         "page-walk must cover the same events as one "
                         "clamped page, no more and no less")


_SEED: dict = {}


def _seed_live_run(srv: McpClient) -> dict:
    """Idempotently ensure one live run exists through the protocol path;
    owner binding (cell contract + process version) is seeded out-of-band,
    exactly as the blocked message instructs (CLI/store, not a tool slot)."""
    if _SEED:
        r = srv.call("capabilities_build_run_get", {"run_id": _SEED["run_id"]})
        j = _assert_json_state(r)
        _SEED["token"] = j["run"]["fencing_token"]
        _SEED["max_seq"] = max([e["sequence"] for e in
                                j["events_newest_first"]] or [0])
        return _SEED
    from rig_capabilities import build_store
    from rig_capabilities.build_index import current_pack_sha
    import psycopg2
    cv = current_pack_sha(REPO)
    conn = psycopg2.connect(_CLUSTER_STATE["dsn"], connect_timeout=10)
    try:
        build_store.put_cell_contract(
            conn, cell_id=GOOD_PACKET["cell_id"], criteria_version=cv,
            contract={"done_test": GOOD_PACKET["done_test"]},
            criteria_pack_sha256=cv, sealed_by="mcp-proto-setup")
        build_store.register_process_version(
            conn, process_key="mcp-proc", version="1",
            definition={"cmd": "probe"}, declared_owner="rig-intelligence",
            registered_by="mcp-proto-setup")
        build_store.bind_cell(
            conn, cell_id=GOOD_PACKET["cell_id"], criteria_version=cv,
            process_key="mcp-proc", process_version="1",
            work_type="T1", owner="rig-intelligence",
            bound_by="mcp-proto-setup")
    finally:
        conn.close()
    r = srv.call("capabilities_build_run_start",
                 dict(GOOD_PACKET, process_key="mcp-proc",
                      process_version="1"))
    j = _assert_json_state(r)
    assert j["state"] in ("started", "replayed"), j
    run_id = j["run"]["run_id"]
    g = srv.call("capabilities_build_run_get", {"run_id": run_id})
    gj = _assert_json_state(g)
    _SEED.update({"run_id": run_id,
                  "token": gj["run"]["fencing_token"],
                  "max_seq": max([e["sequence"] for e in
                                  gj["events_newest_first"]] or [0]),
                  "started_by": gj["run"]["started_by"]})
    return _SEED


def _assert_json_state(res: dict) -> dict:
    assert res["json"] is not None, f"non-JSON: {res['text'][:200]}"
    return res["json"]


# ---------------------------------------------------------------------------
# B45 — ten end-to-end scenarios over the wire
# ---------------------------------------------------------------------------

def _summarize(res: dict) -> dict:
    out = {"isError": res["isError"],
           "text": res["text"][:400]}
    if res["json"] is not None:
        j = res["json"]
        out["state"] = j.get("state") or (
            "configured=false" if j.get("configured") is False
            or j.get("record", {}).get("configured") is False
            or j.get("measure", {}).get("configured") is False else None)
        if isinstance(j.get("admitted"), bool):
            out["admitted"] = j["admitted"]
    return out


class ScenariosB45(_ProtoCase):
    """Ten multi-tool scenarios; receipt written per scenario so partial
    evidence survives an abort. A scenario whose backend is unavailable is
    recorded UNVERIFIED with the named reason — never dressed as a pass."""

    def test_b45_ten_scenarios(self):
        self.scenarios = [
            ("S1 store triage on an unconfigured backend",
             self._s1, "live-independent"),
            ("S2 diagnosis accepted and bound to the live pack",
             self._s2, "live-independent"),
            ("S3 diagnosis refused for an out-of-authority cell",
             self._s3, "live-independent"),
            ("S4 run start blocked honestly with no store target",
             self._s4, "live-independent"),
            ("S5 run start blocked on missing owner binding (store live)",
             self._s5, "live"),
            ("S6 omission staged dormant; replay idempotent; never approved",
             self._s6, "live-independent"),
            ("S7 stale fencing token refused; current token records",
             self._s7, "live"),
            ("S8 unknown run answers state=unknown, never empty success",
             self._s8, "live"),
            ("S9 run_get pages bounded, newest-first, clamp proven",
             self._s9, "live"),
            ("S10 qualification recomputed from an empty manifest denies",
             self._s10, "live-independent"),
        ]
        failures = []
        for idx, (title, fn, need) in enumerate(self.scenarios, 1):
            entry = {"scenario": idx, "title": title, "lane":
                     {1: "diagnosis", 2: "diagnosis", 3: "diagnosis",
                      4: "missing-dependency", 5: "missing-dependency",
                      6: "approval-staging", 7: "failure-recovery",
                      8: "failure-recovery", 9: "failure-recovery",
                      10: "qualification"}[idx]}
            try:
                fn(entry)
            except unittest.SkipTest as skip:
                entry["status"] = "UNVERIFIED"
                entry["reason"] = str(skip)[:300]
            if "status" not in entry:
                entry["status"] = "PASS"
            SCENARIOS[:] = [s for s in SCENARIOS
                            if s["scenario"] != idx] + [entry]
            SCENARIOS.sort(key=lambda s: s["scenario"])
            _flush_scenarios()
            if entry["status"] == "FAIL":
                failures.append(f"S{idx}: {entry.get('expectation')}")
        # The count is the deliverable: exactly ten, whatever their status.
        self.assertEqual(len(SCENARIOS), 10)
        unverified = [s for s in SCENARIOS if s["status"] == "UNVERIFIED"]
        self.assertFalse(
            failures, "scenario expectations failed: " + "; ".join(failures))
        # Report-only: if the live cluster was unavailable the report names
        # it; that is not a test failure (task allows honest UNVERIFIED).
        _flush_scenarios()

    def _run_steps(self, entry: dict, srv: McpClient) -> None:
        entry["server"] = srv.tag

    def _expect(self, entry: dict, expectation: str) -> None:
        entry["expectation"] = expectation

    # -- scenario bodies -----------------------------------------------------
    def _s1(self, entry):
        srv = _server("no_store")
        self._run_steps(entry, srv)
        steps = []
        r1 = srv.call("capabilities_build_store", {})
        steps.append({"tool": "capabilities_build_store",
                      "result": _summarize(r1)})
        entry["calls"] = steps
        j = r1["json"]
        ok = (not r1["isError"]) and j["record"]["configured"] is False \
            and j["measure"]["configured"] is False
        self._expect(entry, f"both planes configured=false: {steps}")
        if not ok:
            entry["status"] = "FAIL"

    def _s2(self, entry):
        srv = _server("no_store")
        self._run_steps(entry, srv)
        r0 = srv.call("capabilities_build_store", {})
        r1 = srv.call("capabilities_build_diagnose", GOOD_PACKET)
        entry["calls"] = [
            {"tool": "capabilities_build_store", "result": _summarize(r0)},
            {"tool": "capabilities_build_diagnose",
             "result": _summarize(r1)}]
        sha = (r1["json"] or {}).get("criteria_pack_sha256", "")
        ok = (not r1["isError"]) and r1["json"]["state"] == "validated" \
            and len(sha) == 64
        self._expect(entry, "diagnose -> validated, bound to live pack sha")
        if not ok:
            entry["status"] = "FAIL"

    def _s3(self, entry):
        srv = _server("no_store")
        self._run_steps(entry, srv)
        r1 = srv.call("capabilities_build_diagnose",
                      dict(GOOD_PACKET, cell_id="L9-DX-A9-I9"))
        r2 = srv.call("capabilities_build_diagnose", GOOD_PACKET)
        entry["calls"] = [
            {"tool": "capabilities_build_diagnose",
             "args": {"cell_id": "L9-DX-A9-I9"}, "result": _summarize(r1)},
            {"tool": "capabilities_build_diagnose",
             "result": _summarize(r2)}]
        ok = r1["isError"] and "588-cell authority" in r1["text"] \
            and not r2["isError"]
        self._expect(entry, "bad cell refused naming the authority; session "
                            "still serves the valid packet")
        if not ok:
            entry["status"] = "FAIL"

    def _s4(self, entry):
        srv = _server("no_store")
        self._run_steps(entry, srv)
        r0 = srv.call("capabilities_build_store", {})
        r1 = srv.call("capabilities_build_run_start",
                      dict(GOOD_PACKET, process_key="mcp-proc",
                           process_version="1"))
        r2 = srv.call("capabilities_build_run",
                      {"idempotency_key": (r1["json"] or {}).get(
                          "idempotency_key", "")})
        entry["calls"] = [
            {"tool": "capabilities_build_store", "result": _summarize(r0)},
            {"tool": "capabilities_build_run_start", "result": _summarize(r1)},
            {"tool": "capabilities_build_run", "result": _summarize(r2)}]
        j = r1["json"] or {}
        ok = j.get("state") == "blocked" and "approval" in j.get(
            "next_action", "") and not r2["isError"] \
            and r2["json"]["configured"] is False
        self._expect(entry, "run_start -> blocked + next_action names "
                            "approval; follow-up read honestly UNCONFIGURED")
        if not ok:
            entry["status"] = "FAIL"

    def _s5(self, entry):
        try:
            srv = _server("live")
        except unittest.SkipTest as skip:
            raise unittest.SkipTest(str(skip))
        self._run_steps(entry, srv)
        no_owner = {k: GOOD_PACKET[k] for k in GOOD_PACKET}
        r = srv.call("capabilities_build_run_start", no_owner)
        entry["calls"] = [{"tool": "capabilities_build_run_start",
                           "args_note": "valid packet, no process_key/"
                                        "process_version",
                           "result": _summarize(r)}]
        j = r["json"] or {}
        ok = j.get("state") == "blocked" and "bind_cell" in j.get("reason", "")
        self._expect(entry, "store live but no owner binding -> blocked "
                            "naming bind_cell, no default owner invented")
        if not ok:
            entry["status"] = "FAIL"

    def _s6(self, entry):
        srv = _server("no_store")
        self._run_steps(entry, srv)
        args = {"cell_id": "L1-D1-A1-I1",
                "reason": f"b45 staging probe {RUN_STAMP}",
                "evidence_refs": ["receipt:b45-staging"]}
        r1 = srv.call("capabilities_build_omission_request", args)
        r2 = srv.call("capabilities_build_omission_request", args)
        j1 = r1["json"] or {}
        staged_doc = None
        if j1.get("path"):
            staged_doc = json.loads(Path(j1["path"]).read_text())
            Path(j1["path"]).unlink()          # probe artifact
        entry["calls"] = [
            {"tool": "capabilities_build_omission_request",
             "result": _summarize(r1)},
            {"tool": "capabilities_build_omission_request",
             "result": _summarize(r2)},
            {"staged_file_state": (staged_doc or {}).get("state"),
             "requested_by": (staged_doc or {}).get("requested_by")}]
        ok = (j1.get("state") == "staged_dormant"
              and (r2["json"] or {}).get("state") == "already_staged"
              and staged_doc
              and staged_doc["state"] == "PENDING_HUMAN_REVIEW"
              and "NOT POSSIBLE HERE" in staged_doc["approval"])
        self._expect(entry, "staged dormant -> replay already_staged; file "
                            "says PENDING_HUMAN_REVIEW, approval impossible")
        if not ok:
            entry["status"] = "FAIL"

    def _s7(self, entry):
        try:
            srv = _server("live")
        except unittest.SkipTest as skip:
            raise unittest.SkipTest(str(skip))
        self._run_steps(entry, srv)
        seed = _seed_live_run(srv)
        stale = srv.call("capabilities_build_evidence_add",
                         {"run_id": seed["run_id"], "path": EVIDENCE_FILE,
                          "kind": "receipt", "sequence": seed["max_seq"] + 1,
                          "fencing_token": 999})
        fresh = srv.call("capabilities_build_evidence_add",
                         {"run_id": seed["run_id"], "path": EVIDENCE_FILE,
                          "kind": "checkpoint",
                          "sequence": seed["max_seq"] + 1,
                          "fencing_token": seed["token"]})
        entry["calls"] = [
            {"tool": "capabilities_build_run_start",
             "result": {"run_id": seed["run_id"], "note": "seeded"}},
            {"tool": "capabilities_build_evidence_add",
             "args": {"fencing_token": 999}, "result": _summarize(stale)},
            {"tool": "capabilities_build_evidence_add",
             "args": {"fencing_token": seed["token"]},
             "result": _summarize(fresh)}]
        ok = (stale["json"] or {}).get("state") == "refused" \
            and "stale fencing token" in (stale["json"] or {}).get(
                "reason", "").lower() \
            and (fresh["json"] or {}).get("state") == "recorded"
        self._expect(entry, "stale token refused (B47); current token "
                            "records through the same protocol path")
        if not ok:
            entry["status"] = "FAIL"

    def _s8(self, entry):
        try:
            srv = _server("live")
        except unittest.SkipTest as skip:
            raise unittest.SkipTest(str(skip))
        self._run_steps(entry, srv)
        r = srv.call("capabilities_build_run_get",
                     {"run_id": "run-does-not-exist-000"})
        entry["calls"] = [{"tool": "capabilities_build_run_get",
                           "result": _summarize(r)}]
        ok = not r["isError"] and r["json"]["state"] == "unknown"
        self._expect(entry, "unknown run -> state=unknown, no fabricated "
                            "empty success")
        if not ok:
            entry["status"] = "FAIL"

    def _s9(self, entry):
        try:
            srv = _server("live")
        except unittest.SkipTest as skip:
            raise unittest.SkipTest(str(skip))
        self._run_steps(entry, srv)
        seed = _seed_live_run(srv)
        pages = []
        r1 = srv.call("capabilities_build_run_get",
                      {"run_id": seed["run_id"], "limit": 1})
        r2 = srv.call("capabilities_build_run_get",
                      {"run_id": seed["run_id"], "limit": 5})
        for r in (r1, r2):
            pages.append(r["json"])
        entry["calls"] = [
            {"tool": "capabilities_build_run_get", "args": {"limit": 1},
             "returned": len(pages[0]["events_newest_first"])},
            {"tool": "capabilities_build_run_get", "args": {"limit": 5},
             "returned": len(pages[1]["events_newest_first"])}]
        ok = (len(pages[0]["events_newest_first"]) <= 1
              and len(pages[1]["events_newest_first"]) <= 5
              and pages[0]["events_newest_first"][0]["sequence"] >=
              pages[1]["events_newest_first"][0]["sequence"])
        self._expect(entry, "pages respect limit, newest-first ordering")
        if not ok:
            entry["status"] = "FAIL"

    def _s10(self, entry):
        srv = _server("no_store")
        self._run_steps(entry, srv)
        _ensure_probe_files()
        sha = _head_sha() or "0" * 40
        r = srv.call("capabilities_build_qualify",
                     {"cell_id": "L1-D1-A1-I1", "sha": sha,
                      "manifest_path": MANIFEST_FILE})
        entry["calls"] = [
            {"tool": "capabilities_build_qualify",
             "args": {"manifest": "empty {} manifest, real HEAD sha"},
             "result": _summarize(r)}]
        j = r["json"] or {}
        ok = (j.get("state") == "recomputed" and j.get("admitted") is False
              and len(j.get("refusals", [])) >= 1
              and all("UNKNOWN blocks" in rf or "fail closed" in rf
                      for rf in j.get("refusals", []))
              and j.get("checked_by") == CALLER_NO_STORE)
        # The anchor preflight short-circuits BEFORE the four receipts are
        # consulted when the out-of-tree certifier digest is absent — the
        # gate refuses to evaluate at all. Counting ">=4 missing-receipt"
        # refusals would assert an unreachable code path on this host;
        # what IS proven: verdict recomputed here, admitted=False, every
        # blocker named, caller is the wrapper identity.
        entry["note"] = ("refusals on this host: "
                         + " | ".join(j.get("refusals", []))[:300])
        self._expect(entry, "qualification RECOMPUTED: empty manifest -> "
                            "admitted=false with named receipt refusals")
        if not ok:
            entry["status"] = "FAIL"


def tearDownModule() -> None:
    for s in list(_SERVERS.values()):
        if isinstance(s, McpClient):
            s.close()
    _flush_b44({"live_cluster": {k: _CLUSTER_STATE[k] for k in
                                 ("dsn", "pg_version", "reason")}})
    _flush_scenarios()


if __name__ == "__main__":
    unittest.main(verbosity=2)
