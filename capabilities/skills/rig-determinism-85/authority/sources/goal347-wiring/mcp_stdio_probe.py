#!/usr/bin/env python3
"""MCP stdio real-call probe (goal 347).

Spawn a registered MCP server exactly as the harness would (command + args),
drive initialize -> tools/list -> one tools/call, exit 0 only if all three
succeed. Usage:
  mcp_stdio_probe.py <expect-tool-name> <command> [args...]
"""
import json
import os
import subprocess
import sys


def send(p, msg):
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()


def recv(p, want_id, timeout=None):
    import select
    deadline = timeout if timeout is not None else int(os.environ.get("MCP_PROBE_TIMEOUT", "30"))
    while True:
        r, _, _ = select.select([p.stdout], [], [], deadline)
        if not r:
            raise TimeoutError("no response from server")
        line = p.stdout.readline()
        if not line:
            raise EOFError("server closed stdout")
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if m.get("id") == want_id:
            return m


def main() -> int:
    import tempfile
    expect_tool, cmd = sys.argv[1], sys.argv[2]
    errfile = tempfile.NamedTemporaryFile("w+", prefix="mcp-probe-", suffix=".err",
                                          delete=False)
    rc, proc = 1, None
    proc = subprocess.Popen([cmd] + sys.argv[3:], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=errfile,
                            text=True, bufsize=1)
    try:
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2025-03-26",
                               "capabilities": {},
                               "clientInfo": {"name": "goal347-probe",
                                              "version": "1"}}})
        init = recv(proc, 1)
        if "result" not in init or not (init["result"].get("serverInfo") or {}).get("name"):
            print(f"initialize failed (no serverInfo.name): {init}",
                  file=sys.stderr)
            return 1
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = recv(proc, 2)
        names = [t.get("name") for t in tools.get("result", {}).get("tools", [])]
        if expect_tool not in names:
            print(f"{expect_tool} not in tools/list ({len(names)} tools)",
                  file=sys.stderr)
            return 1
        send(proc, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": expect_tool, "arguments": {}}})
        call = recv(proc, 3, timeout=90)
        if "result" not in call or call["result"].get("isError"):
            print(f"tools/call {expect_tool} failed: "
                  f"{json.dumps(call)[:300]}", file=sys.stderr)
            return 1
        payload = call["result"]
        content = payload.get("content") or []
        useful = any(
            isinstance(c, dict) and (c.get("text") or "").strip()
            for c in content
        ) or bool(payload.get("structuredContent"))
        if not useful:
            print(f"tools/call {expect_tool} returned no useful output: "
                  f"{json.dumps(call)[:300]}", file=sys.stderr)
            return 1
        print(f"OK {expect_tool}: {len(names)} tools listed, call returned "
              f"result")
        rc = 0
    except Exception as e:
        print(f"probe error: {e}", file=sys.stderr)
    finally:
        if proc:
            proc.kill()
        errfile.flush()
        if rc:
            with open(errfile.name) as fh:
                tail = fh.read()[-500:].strip()
            if tail:
                print(f"server stderr tail: {tail}", file=sys.stderr)
        os.unlink(errfile.name)
    return rc


if __name__ == "__main__":
    sys.exit(main())
