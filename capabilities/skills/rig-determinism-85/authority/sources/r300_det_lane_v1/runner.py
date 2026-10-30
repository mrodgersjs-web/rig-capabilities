#!/usr/bin/env python3
"""r300 runner: executes one routines-300 spec (deterministic lane) and writes an
artifact. Spec ops are read-only against external systems; artifacts land in
~/.rig/live/routines-300-out/<ID>/. Exit 1 when any step raises a finding.

Usage: runner.py specs/N107.json [--nowrite]
"""
import json, os, re, sqlite3, subprocess, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
OUT = HOME / ".rig/live/routines-300-out"
SPEC_DIR = Path(__file__).parent / "specs"
LOG = OUT / "ledger.jsonl"


def sh(argv, timeout=60):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def key(name):
    """Resolve a secret by name (case-insensitive); never returns it into artifacts."""
    cands = {name, name.upper(), name.lower()}
    for n in list(cands):
        try:
            rc, out, _ = sh([str(HOME/".local/bin/rig-keychain-api-key"), "get", n], timeout=15)
            if rc == 0 and out.strip():
                return out.strip()
        except Exception:
            pass
    for n in list(cands):
        for svc in (f"com.rig.env.{n.upper()}", f"rig-api-key:{n.upper()}"):
            try:
                rc, out, _ = sh(["security", "find-generic-password", "-s", svc, "-w"], timeout=15)
                if rc == 0 and out.strip():
                    return out.strip()
            except Exception:
                pass
    for env in os.environ:
        if env.upper() == name.upper() and os.environ[env]:
            return os.environ[env].strip()
    for f in sorted((HOME/".rig/secrets").glob("*.env")) + [HOME/".hermes/.env", HOME/".fcc/.env"]:
        try:
            for line in f.read_text().splitlines():
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:]
                if "=" in line and line.split("=", 1)[0].strip().upper() == name.upper():
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if v:
                        return v
        except Exception:
            continue
    return None


TOK = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")


def expand(s):
    """Substitute $NAME tokens with resolved secrets; unknown tokens stay literal."""
    def sub(m):
        v = key(m.group(1))
        return v if v else m.group(0)
    return TOK.sub(sub, s)


def op_http_get(step):
    findings, rows = [], []
    for url in step["urls"]:
        req = urllib.request.Request(url, headers={"User-Agent": "r300-runner/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=step.get("timeout", 20)) as r:
                rows.append({"url": url, "status": r.status})
                if r.status >= 400:
                    findings.append(f"HTTP {r.status} for {url}")
        except urllib.error.HTTPError as e:
            rows.append({"url": url, "status": e.code})
            if e.code >= 400:
                findings.append(f"HTTP {e.code} for {url}")
        except Exception as e:
            rows.append({"url": url, "status": "ERR"})
            findings.append(f"unreachable {url}: {e}")
    return rows, findings


def op_airtable(step):
    pat = key("AIRTABLE_CC_PAT")
    if not pat:
        return [], ["missing credential AIRTABLE_CC_PAT"]
    url = f"https://api.airtable.com/v0/{step['app']}/{step['table']}?maxRecords={step.get('max_records', 20)}"
    if step.get("filter"):
        url += "&filterByFormula=" + urllib.request.quote(step["filter"])
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {pat}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        recs = data.get("records", [])
        return [{"count": len(recs), "sample": [x.get("fields", {}) for x in recs[:5]]}], []
    except Exception as e:
        return [], [f"airtable {step['table']}: {e}"]


def op_sqlite(step):
    con = sqlite3.connect(f"file:{step['db']}?mode=ro", uri=True)
    rows = [dict(zip([c[0] for c in con.execute(step['sql']).description], r))
            for r in con.execute(step["sql"]).fetchall()]
    con.close()
    return rows[:20], ([f"{step['label']}: {step.get('alert', 'row count')} = {len(rows)}"]
                       if step.get("alert") == "nonempty" and rows else [])


def op_shell(step):
    argv = [expand(a) for a in step["argv"]]
    rc, out, err = sh(argv, timeout=step.get("timeout", 120))
    rows = [{"rc": rc, "out": out[-800:], "err": err[-400:]}]
    findings = []
    if step.get("expect_rc", 0) is not None and rc != step.get("expect_rc", 0):
        findings.append(f"{step['argv'][0]} rc={rc} (expected {step.get('expect_rc', 0)})")
    if step.get("expect_out_regex") and not re.search(step["expect_out_regex"], out):
        findings.append(f"{step['label']}: output failed /{step['expect_out_regex']}/ (got {out[:80]!r})")
    if step.get("alert") == "nonempty" and out.strip():
        findings.append(f"{step['label']}: findings present")
    return rows, findings


def op_regex_scan(step):
    rx = re.compile(step["pattern"])
    hits, findings = [], []
    for root in step["roots"]:
        root = Path(root).expanduser()
        if not root.exists():
            continue
        for p in root.rglob(step.get("glob", "*")):
            if not p.is_file() or p.stat().st_size > 2_000_000:
                continue
            if any(s in str(p) for s in step.get("exclude", ["/node_modules/", "/.git/", "/state.db"])):
                continue
            try:
                for i, line in enumerate(p.read_text(errors="ignore").splitlines()):
                    if rx.search(line):
                        hits.append({"file": str(p), "line": i + 1})
                        if len(hits) >= step.get("max_hits", 20):
                            return hits, ([f"{len(hits)}+ pattern hits (scan truncated)"] if step.get("alert") == "nonempty" else [])
            except Exception:
                continue
    if hits and step.get("alert") == "nonempty":
        findings.append(f"{len(hits)} pattern hits")
    return hits, findings


def op_git_repos(step):
    rows, findings = [], []
    for root in step["roots"]:
        root = Path(root).expanduser()
        if not root.exists():
            continue
        for p in sorted(root.iterdir()):
            if not (p/".git").exists():
                continue
            rc1, st, _ = sh(["git", "-C", str(p), "status", "--porcelain"])
            rc2, un, _ = sh(["git", "-C", str(p), "log", "--branches", "--not", "--remotes", "--oneline"])
            rows.append({"repo": p.name, "dirty_files": len(st.splitlines()), "unpushed": len(un.splitlines())})
            if st.strip():
                findings.append(f"{p.name}: {len(st.splitlines())} dirty files")
            if un.strip():
                findings.append(f"{p.name}: {len(un.splitlines())} unpushed commits")
    return rows, findings


def op_plist_audit(step):
    written = {p.stem for p in (HOME/"Library/LaunchAgents").glob("*.plist")}
    rc, out, _ = sh(["launchctl", "list"])
    loaded = {line.split("\t")[-1] for line in out.splitlines() if line.strip()}
    missing = sorted(written - loaded)
    rows = [{"written": len(written), "loaded": len(written & loaded), "not_loaded": missing[:20]}]
    return rows, ([f"{len(missing)} plists written but not loaded"] if missing else [])


def op_disk(step):
    rows, findings = [], []
    for host in step.get("hosts", ["localhost"]):
        rc, out, err = sh(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", host,
                           "df -k | awk 'NR>1 {print $5, $NF}'"], timeout=25)
        if rc != 0:
            rows.append({"host": host, "status": "ssh failed", "err": err[-200:]})
            findings.append(f"{host}: ssh failed")
            continue
        for line in out.splitlines():
            fields = line.split()
            pct_s = next((f for f in fields if re.fullmatch(r"\d{1,3}%", f)), None)
            if not pct_s or len(fields) < 2:
                continue
            pct = int(pct_s.rstrip("%"))
            mount = fields[-1]
            if not mount.startswith("/") or mount == "/dev" or mount.startswith((
                    "/System/Volumes/Update", "/System/Volumes/Preboot", "/System/Volumes/xarts",
                    "/System/Volumes/Hardware", "/System/Volumes/iSCPreboot",
                    "/Library/Developer/CoreSimulator", "/private/var/folders")):
                continue  # devfs and disk-image mounts always read full; not headroom
            rows.append({"host": host, "mount": mount, "used_pct": pct})
            if pct >= step.get("warn_pct", 85):
                findings.append(f"{host}:{mount} at {pct}%")
    return rows, findings


def op_jwt_expiry(step):
    rows, findings = [], []
    for name in step["names"]:
        v = key(name)
        if not v:
            rows.append({"name": name, "status": "absent"})
            continue
        m = re.match(r"^[A-Za-z0-9_-]+\.([A-Za-z0-9_-]+)\.", v)
        exp = None
        if m:
            import base64
            try:
                payload = json.loads(base64.urlsafe_b64decode(m.group(1) + "=" * (-len(m.group(1)) % 4)))
                exp = payload.get("exp")
            except Exception:
                pass
        rows.append({"name": name, "status": "present", "exp": exp})
        if exp:
            left = exp - datetime.now(timezone.utc).timestamp()
            if left < 0:
                findings.append(f"{name}: EXPIRED {int(-left/86400)}d ago")
            elif left < step.get("warn_days", 30) * 86400:
                findings.append(f"{name}: expires within {step.get('warn_days', 30)}d")
        if exp is None and step.get("require_exp"):
            findings.append(f"{name}: no expiry data")
    return rows, findings


def op_env_presence(step):
    rows, findings = [], []
    for name in step["names"]:
        present = key(name) is not None
        rows.append({"name": name, "present": present})
        if not present and step.get("require_all", True):
            findings.append(f"missing credential: {name}")
    return rows, findings


OPS = {"http_get": op_http_get, "airtable": op_airtable, "sqlite": op_sqlite,
       "shell": op_shell, "regex_scan": op_regex_scan, "git_repos": op_git_repos,
       "plist_audit": op_plist_audit, "disk": op_disk, "jwt_expiry": op_jwt_expiry,
       "env_presence": op_env_presence}


def run(spec_path, write=True):
    spec = json.loads(Path(spec_path).read_text())
    now = datetime.now(timezone.utc)
    steps_out, findings = [], []
    for step in spec["steps"]:
        try:
            rows, f = OPS[step["op"]](step)
        except Exception as e:
            rows, f = [], [f"{step['op']} crashed: {e}"]
        steps_out.append({"op": step["op"], "rows": rows, "findings": f})
        findings += f
    result = {"id": spec["id"], "name": spec["name"], "at": now.isoformat(),
              "verdict": "FINDINGS" if findings else "CLEAN", "findings": findings, "steps": steps_out}
    if write:
        d = OUT / spec["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{now.strftime('%Y%m%dT%H%M%SZ')}.json").write_text(json.dumps(result, indent=1, default=str))
        lines = [f"# {spec['id']} {spec['name']}", f"at: {now.isoformat()}", f"verdict: {result['verdict']}"]
        lines += [f"- {f}" for f in findings] or ["- clean"]
        lines += ["", "## steps"] + [f"- {s['op']}: {len(s['rows'])} rows, {len(s['findings'])} findings" for s in steps_out]
        (d / "latest.md").write_text("\n".join(lines) + "\n")
        with open(LOG, "a") as fh:
            fh.write(json.dumps({"id": spec["id"], "at": result["at"], "verdict": result["verdict"],
                                 "findings": findings}) + "\n")
    return result


if __name__ == "__main__":
    spec = sys.argv[1] if len(sys.argv) > 1 else None
    if not spec:
        print(__doc__)
        sys.exit(2)
    if not Path(spec).exists():
        spec = str(SPEC_DIR / spec)
    r = run(spec, write="--nowrite" not in sys.argv)
    print(json.dumps({k: r[k] for k in ("id", "name", "verdict", "findings")}, indent=1))
    sys.exit(1 if r["verdict"] == "FINDINGS" else 0)
