"""Stdlib unittests for rig-capabilities: index, search, install, protocol."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities.catalog import Repo  # noqa: E402


def make_fixture(tmp: Path) -> Repo:
    repo = Repo(tmp / "repo")
    hook = repo.cap_root / "hooks" / "guard.sh"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text("#!/bin/sh\n# guard hook: blocks dangerous rm -rf commands\n"
                    "echo block\n")
    skill = repo.cap_root / "skills" / "demo-skill"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo capability\n"
                                    "tags: testing, demo\n---\n# Demo Skill\nbody\n")
    ext_skill = tmp / "extskills" / "ext-thing"
    ext_skill.mkdir(parents=True, exist_ok=True)
    (ext_skill / "SKILL.md").write_text("---\nname: ext-thing\n"
                                        "description: external shadowed skill\n---\n"
                                        "# Ext\n")
    dup = tmp / "extskills" / "demo-skill"
    dup.mkdir(parents=True, exist_ok=True)
    (dup / "SKILL.md").write_text("---\nname: demo-skill\ndescription: external copy\n"
                                  "---\n# dup\n")
    repo.config_path.write_text(json.dumps({
        "defaults": False,
        "external_roots": [
            {"label": "ext", "kind": "skill", "path": str(tmp / "extskills"),
             "pattern": "*/SKILL.md"}],
        "install_roots": {
            "hook": {"claude": str(tmp / "claude" / "hooks")},
            "skill": {"claude": str(tmp / "claude" / "skills")}},
    }))
    repo.build_index()
    return repo


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_index_counts(self):
        doc = self.repo.load_index()
        kinds = {(a["id"], a["source"]) for a in doc["assets"]}
        self.assertIn(("guard.sh", "canonical"), kinds)
        self.assertIn(("demo-skill", "canonical"), kinds)
        self.assertIn(("ext-thing", "ext"), kinds)
        # canonical shadows the external same-id copy: exactly one demo-skill
        self.assertEqual(1, len([a for a in doc["assets"] if a["id"] == "demo-skill"]))

    def test_search_ranks_name_match(self):
        rows = self.repo.search("guard")
        self.assertTrue(rows)
        self.assertEqual("guard.sh", rows[0]["id"])

    def test_search_canonical_bonus_and_kind_filter(self):
        rows = self.repo.search("demo", kind="skill")
        self.assertEqual([("demo-skill", "canonical")],
                         [(r["id"], r["source"]) for r in rows])

    def test_install_and_idempotence(self):
        out = self.repo.install("guard.sh", "claude")
        self.assertEqual("installed", out["status"])
        target = Path(out["target"])
        self.assertTrue(target.exists())
        again = self.repo.install("guard.sh", "claude")
        self.assertEqual("already-installed", again["status"])
        led = self.repo.ledger()
        self.assertEqual(1, len(led["guard.sh"]))

    def test_overwrite_refuses_then_force_backs_up(self):
        self.repo.install("guard.sh", "claude")
        (self.repo.cap_root / "hooks" / "guard.sh").write_text("# changed\n" + "x" * 40)
        self.repo.build_index()
        with self.assertRaises(ValueError):
            self.repo.install("guard.sh", "claude")
        out = self.repo.install("guard.sh", "claude", force=True)
        self.assertEqual("replaced", out["status"])
        baks = list((self.tmp / "claude" / "hooks").glob("guard.sh.bak-*"))
        self.assertEqual(1, len(baks))

    def test_external_requires_canonicalize(self):
        with self.assertRaises(ValueError) as cm:
            self.repo.install("ext-thing", "claude")
        self.assertIn("capability_add", str(cm.exception))

    def test_add_canonicalizes_directory(self):
        out = self.repo.add("ext-thing", "skill", str(self.tmp / "extskills" / "ext-thing"))
        self.assertEqual("added", out["status"])
        self.assertTrue((self.repo.cap_root / "skills" / "ext-thing").is_dir())
        installed = self.repo.install("ext-thing", "claude")
        self.assertEqual("installed", installed["status"])

    def test_add_is_idempotent_when_source_is_canonical(self):
        # Registering a skill whose source path IS the canonical dir must not
        # delete the source (regression: rmtree(dst) destroyed src when
        # src.resolve()==dst.resolve(), then copytree ENOENT'd).
        canon = self.repo.cap_root / "skills" / "demo-skill"
        self.assertTrue(canon.is_dir())
        before = (canon / "SKILL.md").read_text()
        out = self.repo.add("demo-skill", "skill", str(canon), overwrite=True)
        self.assertIn(out["status"], ("added", "replaced", "registered"))
        self.assertTrue((canon / "SKILL.md").is_dir() or canon.is_dir())
        self.assertEqual(before, (canon / "SKILL.md").read_text())
        resolved = self.repo.resolve("demo-skill")
        self.assertIsNotNone(resolved)


class ProtocolTests(unittest.TestCase):
    def test_handshake_and_tool_call(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            repo = make_fixture(tmp)
            env = dict(os.environ, RIG_CAP_REPO=str(repo.root))
            req = ("\n".join([
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                            "params": {"protocolVersion": "2025-06-18"}}),
                json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                            "params": {"name": "capabilities_search",
                                       "arguments": {"query": "guard"}}}),
                json.dumps({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                            "params": {"name": "capability_install",
                                       "arguments": {"id": "guard.sh",
                                                     "harness": "claude"}}}),
                "",
            ])).encode()
            proc = subprocess.run([sys.executable, str(REPO_ROOT / "server.py")],
                                  input=req, capture_output=True, env=env, timeout=30)
            lines = [json.loads(ln) for ln in proc.stdout.decode().splitlines() if ln]
            by_id = {m.get("id"): m for m in lines}
            self.assertEqual("2025-06-18", by_id[1]["result"]["protocolVersion"])
            names = [t["name"] for t in by_id[2]["result"]["tools"]]
            self.assertIn("capabilities_search", names)
            self.assertIn("capability_install", names)
            search_txt = by_id[3]["result"]["content"][0]["text"]
            self.assertIn("guard.sh", search_txt)
            self.assertFalse(by_id[3]["result"]["isError"])
            install_txt = by_id[4]["result"]["content"][0]["text"]
            self.assertIn("installed", install_txt)
            self.assertFalse(by_id[4]["result"]["isError"])






class LiveTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_hook_wired_vs_dormant(self):
        from rig_capabilities.live import hook_live
        asset = {"id": "guard.sh", "kind": "hook", "source": "canonical"}
        wired = hook_live(asset, "bash ~/.claude/hooks/guard.sh --mode x")
        self.assertEqual("wired", wired["state"])
        self.assertTrue(wired["live"])
        self.assertEqual("dormant", hook_live(asset, "echo nothing")["state"])

    def test_installed_in_roots(self):
        from rig_capabilities.live import installed_in
        asset = {"id": "demo-skill", "kind": "skill"}
        roots = {"skill": {"claude": str(self.tmp / "claude" / "skills")}}
        self.assertEqual("dormant", installed_in(asset, roots)["state"])
        d = self.tmp / "claude" / "skills" / "demo-skill"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: demo-skill\n---\nbody here\n")
        st = installed_in(asset, roots)
        self.assertEqual("wired", st["state"])
        self.assertEqual(["claude"], st["roots"])

    def test_cli_presence(self):
        from rig_capabilities.live import cli_live
        self.assertEqual("wired", cli_live({"id": "sh"})["state"])
        self.assertEqual("dormant", cli_live({"id": "rig-nope-xyzzy-9977"})["state"])

    def test_service_down_then_wired(self):
        import socket
        from rig_capabilities.live import service_state
        svc = {"id": "fake", "ports": [49717], "owner_regex": r"python|node",
               "finger": None}
        self.assertEqual("down", service_state(svc)["state"])
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        try:
            svc2 = dict(svc, ports=[port])
            st = service_state(svc2)
            self.assertIn(st["state"], ("wired", "hijacked"))
            self.assertEqual("fake", st["id"])
        finally:
            srv.close()
    def test_live_status_aggregates_canonical(self):
        from rig_capabilities.live import live_status
        rep = live_status(self.repo, services=False)
        canon = [a for a in self.repo.load_index()["assets"]
                 if a["source"] == "canonical"]
        self.assertEqual(len(canon), rep["canonical_probed"])
        self.assertTrue(rep["assets"])
        for r in rep["assets"]:
            self.assertIn(r["state"], ("wired", "dormant", "absent"))
        one = live_status(self.repo, id="guard.sh", services=False)
        self.assertEqual("guard.sh", one["summary"]["id"])


class TaxonomyTests(unittest.TestCase):
    def _a(self, id_, kind="skill", desc=""):
        return {"id": id_, "kind": kind, "source": "canonical", "abs_path": "/",
                "name": id_, "description": desc}

    def test_precedence_order(self):
        from rig_capabilities.taxonomy import classify
        self.assertEqual("security-review", classify(self._a("semgrep-rule-creator")))
        # 'email' must not outrank outreach tokens
        self.assertEqual("revenue-gtm", classify(self._a("darius-cold-email")))
        # code-review-session: code beats the agent 'session' token
        self.assertEqual("code-engineering", classify(self._a("code-review-session")))
        self.assertEqual("media-production", classify(self._a("hyperframes-cli")))
        self.assertEqual("docs-knowledge", classify(self._a("rig-office-docs")))
        # kind fallbacks + misc never crash
        self.assertEqual("agent-engineering", classify(self._a("x", kind="hook")))
        self.assertEqual("misc", classify(self._a("zzz-nomatch-xyz")))

    def test_tree_build_idempotent_and_complete(self):
        from rig_capabilities.taxonomy import build_tree, dedupe
        with tempfile.TemporaryDirectory() as td:
            repo = make_fixture(Path(td))
            out = Path(td) / "view"
            rep = build_tree(repo, out)
            n = len(dedupe(repo.load_index()["assets"]))
            self.assertEqual(n, rep["assets"])
            links = list(out.rglob("*"))
            self.assertTrue((out / "AGENT-INDEX.md").exists())
            self.assertTrue(any(p.is_symlink() for p in links))
            rep2 = build_tree(repo, out)  # rebuild via swap, no leftovers
            self.assertEqual(rep["assets"], rep2["assets"])
            self.assertFalse((Path(td) / "view.old").exists())
            self.assertFalse((Path(td) / "view.new").exists())
            for p in links:
                if p.is_symlink() and not (Path(td) / "view.old").exists():
                    self.assertTrue(p.resolve().exists() or p.exists(),
                                    f"dangling link {p}")

    def test_route_ranks_lane_first(self):
        from rig_capabilities.taxonomy import route
        rep = route(self.repo, "cold email outreach sequence")
        self.assertEqual("revenue-gtm", rep["lanes"][0]["outcome"])
        self.assertIn("cold-outreach-sequence",
                      [c["id"] for c in rep["lanes"][0]["capabilities"]])

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        td = Path(self._tmp.name)
        self.repo = make_fixture(td)
        s = self.repo.cap_root / "skills" / "cold-outreach-sequence"
        s.mkdir(parents=True, exist_ok=True)
        (s / "SKILL.md").write_text(
            "---\nname: cold-outreach-sequence\ndescription: multi-touch cold "
            "email outreach sequences for outbound pipeline\n"
            "tags: gtm\n---\n# cold\n")
        self.repo.build_index()

    def tearDown(self):
        self._tmp.cleanup()


class FabricTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        td = Path(self._tmp.name)
        self.repo = make_fixture(td)
        c = self.repo.cap_root / "skills"
        for sid, fm in (
            ("threat-model", "description: threat modeling for APIs\n"
                             "status: Stable\nowner: rig\ndomain: Security\n"
                             "verified_on: 2026-08-01\n"),
            ("dead-skill", "description: old withdrawn guidance on threat apis\n"
                           "status: Deprecated\n"),
            ("graph-a", "description: alpha node thing\nrelates_to: graph-b\n"),
            ("graph-b", "description: beta node thing\n"),
        ):
            d = c / sid
            d.mkdir(parents=True, exist_ok=True)
            (d / "SKILL.md").write_text(f"---\nname: {sid}\n{fm}---\n# {sid}\n"
                                        "body text long enough to pass the scanner\n")
        self.repo.build_index()

    def tearDown(self):
        self._tmp.cleanup()

    def test_okf_trust_formula(self):
        from datetime import date, timedelta
        from rig_capabilities.okf import trust, freshness
        today = date(2026, 8, 30)
        fresh = date(2026, 8, 1)
        self.assertEqual(1.0, trust("canonical", "Stable", fresh, today))
        self.assertEqual(0.2, trust("canonical", "Deprecated", fresh, today))
        self.assertEqual(0.3, trust("external", "Draft", None, today))
        old = today - timedelta(days=400)
        self.assertEqual(0.8, trust("canonical", "Stable", old, today))
        self.assertEqual("Stale", freshness("Stable", old, today))
        self.assertEqual("Deprecated", freshness("Deprecated", fresh, today))

    def test_frontmatter_okf_fields_indexed(self):
        a = [x for x in self.repo.load_index()["assets"]
             if x["id"] == "threat-model"][0]
        self.assertEqual("Stable", a["okf"]["status"])
        self.assertEqual("Security", a["okf"]["domain"])
        self.assertGreaterEqual(a["okf"]["trust"], 0.9)

    def test_bm25_ranks_specific_first(self):
        from rig_capabilities.fabric import Corpus
        assets = self.repo.load_index()["assets"]
        hits = Corpus(assets).bm25("threat modeling apis")
        self.assertEqual("threat-model", hits[0][0]["id"])

    def test_graph_declared_edge_symmetric_and_expand(self):
        from rig_capabilities.fabric import build_graph, expand
        stats = build_graph(self.repo)
        self.assertGreaterEqual(stats["edges"], 1)
        out = expand(self.repo, ["graph-a"], depth=1)
        self.assertIn("graph-b", out.get("graph-a", []))
        self.assertIn("graph-a", out.get("graph-b", []))

    def test_pack_filters_deprecated_and_persists(self):
        from rig_capabilities.fabric import context_pack
        rep = context_pack(self.repo, "threat model this api",
                           budget_tokens=400, max_nodes=5)
        ids = [n["id"] for n in rep["nodes"]]
        self.assertNotIn("dead-skill", ids)
        self.assertIn("threat-model", ids)
        self.assertFalse(rep["tiers"]["dense_ollama"])   # no cache => honest False
        self.assertTrue(Path(rep["artifact"]).exists())
        art = json.loads(Path(rep["artifact"]).read_text())
        self.assertLessEqual(art["estimated_tokens"], 400)
        for n in art["nodes"]:
            self.assertIn("sha", n)

    def test_rate_appends(self):
        from rig_capabilities.fabric import context_pack, rate
        rep = context_pack(self.repo, "threat model api")
        rec = rate(self.repo, rep["id"], "useful")
        self.assertEqual("useful", rec["verdict"])
        lines = (Path(self.repo.root) / ".context" / "ratings.jsonl"
                 ).read_text().splitlines()
        self.assertEqual(1, len(lines))
        with self.assertRaises(ValueError):
            rate(self.repo, "pack-nope", "useful")

    def test_concepts_lookup(self):
        from rig_capabilities.fabric import build_concepts, lookup_concept
        build_concepts(self.repo)
        self.assertIn("threat-model", lookup_concept(self.repo, "threat"))

    def test_registry_status_handles_missing(self):
        from rig_capabilities.registry import status as reg_status
        rep = reg_status(repo_filter="nonexistent-repo-xyz",
                         path=str(Path(self._tmp.name) / "no-such-registry.json"))
        self.assertEqual(0, rep["count"])


class VersionLadderTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_v3_drift_then_refresh(self):
        from rig_capabilities.refresh import auto_refresh, drift_report, mark_seen
        mark_seen(self.repo)
        r1 = drift_report(self.repo)
        self.assertFalse(r1["stale"])
        ext = Path(self.tmp / "extskills" / "ext-thing" / "SKILL.md")
        ext.write_text(ext.read_text() + "\n# touched\n")
        later = ext.stat().st_mtime + 5
        os.utime(ext, (later, later))
        r2 = drift_report(self.repo)
        self.assertTrue(r2["stale"])
        self.assertIn("ext", r2["drifted"])
        r3 = auto_refresh(self.repo)
        self.assertTrue(r3["refreshed"])
        self.assertFalse(drift_report(self.repo)["stale"])

    def test_v3_decay_unseen_is_one(self):
        from datetime import datetime, timedelta, timezone
        from rig_capabilities.policy import decay_multiplier
        self.assertEqual(1.0, decay_multiplier(None))
        now = datetime(2026, 8, 30, tzinfo=timezone.utc)
        recent = (now - timedelta(days=10)).isoformat()
        self.assertEqual(1.0, decay_multiplier(recent, now))
        old = (now - timedelta(days=180)).isoformat()
        self.assertLess(decay_multiplier(old, now), 1.0)
        self.assertGreaterEqual(decay_multiplier(old, now), 0.85)

    def test_v3_acl_enforced_for_requester(self):
        from rig_capabilities.fabric import context_pack
        (self.repo.root / "acl_policy.json").write_text(json.dumps({
            "agents": {"locked": ["secret-scope"], "jake": ["*"],
                       "default": ["public"]}}))
        d = self.repo.cap_root / "skills" / "secret-thing"
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(
            "---\nname: secret-thing\ndescription: classified threat notes\n"
            "status: Stable\nacl: [secret-scope]\n---\n# secret\nbody long enough\n")
        self.repo.build_index()
        locked = context_pack(self.repo, "classified threat notes",
                              max_nodes=8, requester="locked")
        open_ = context_pack(self.repo, "classified threat notes",
                             max_nodes=8, requester="jake")
        ids_locked = [n["id"] for n in locked["nodes"]]
        ids_jake = [n["id"] for n in open_["nodes"]]
        self.assertIn("secret-thing", ids_jake)
        self.assertTrue(locked["tiers"]["acl_enforced"])
        self.assertTrue(open_["tiers"]["acl_enforced"])  # policy applied; * permits
        self.assertIn("secret-thing", ids_locked)
        denied = context_pack(self.repo, "classified threat notes",
                              max_nodes=8, requester="stranger")
        self.assertNotIn("secret-thing", [n["id"] for n in denied["nodes"]])

    def test_v4_ratings_shift_trust(self):
        from rig_capabilities.fabric import context_pack, rate
        from rig_capabilities.policy import ratings_delta
        rep = context_pack(self.repo, "demo capability")
        rate(self.repo, rep["id"], "useful")
        rate(self.repo, rep["id"], "useful")
        d = ratings_delta(self.repo)
        for n in json.loads(Path(rep["artifact"]).read_text())["nodes"]:
            self.assertGreaterEqual(d.get(n["id"], 0), 0.05)

    def test_v4_federation_prefixes_source(self):
        peer = Repo(self.tmp / "peer")
        sk = peer.cap_root / "skills" / "peer-only"
        sk.mkdir(parents=True, exist_ok=True)
        (sk / "SKILL.md").write_text(
            "---\nname: peer-only\ndescription: unique peer asset\n---\n# peer\nbody\n")
        peer.config_path.write_text(json.dumps({"defaults": False,
                                                "external_roots": []}))
        peer.build_index()
        cfg = json.loads(self.repo.config_path.read_text())
        cfg["federates"] = [{"label": "peer", "path": str(peer.root)}]
        self.repo.config_path.write_text(json.dumps(cfg))
        doc = self.repo.build_index()
        hits = [a for a in doc["assets"] if a["id"] == "peer-only"]
        self.assertEqual(1, len(hits))
        self.assertEqual("fed:peer", hits[0]["source"])
        self.assertFalse(hits[0]["installable"])

    def test_v4_workspace_log(self):
        from rig_capabilities.fabric import context_pack
        context_pack(self.repo, "demo capability", requester="jake")
        log = self.repo.root / ".context" / "agents" / "jake" / "log.jsonl"
        self.assertTrue(log.exists())
        rec = json.loads(log.read_text().splitlines()[0])
        self.assertEqual("demo capability", rec["intent"])

    def test_v5_sign_verify_roundtrip(self):
        from rig_capabilities.fabric import context_pack
        from rig_capabilities.surface import generate_key, load_key, verify_artifact
        generate_key(self.repo)
        rep = context_pack(self.repo, "demo capability")
        self.assertTrue(rep["tiers"]["signed"])
        art = json.loads(Path(rep["artifact"]).read_text())
        self.assertTrue(verify_artifact(art, load_key(self.repo)))

    def test_v5_public_catalog_opt_in(self):
        from rig_capabilities.surface import public_assets, write_public_catalog
        d = self.repo.cap_root / "skills" / "open-thing"
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(
            "---\nname: open-thing\ndescription: public surface asset\n"
            "acl: [public]\n---\n# open\nbody long enough\n")
        self.repo.build_index()
        ids = [a["id"] for a in public_assets(self.repo)]
        self.assertIn("open-thing", ids)
        self.assertNotIn("demo-skill", ids)
        w = write_public_catalog(self.repo)
        self.assertGreaterEqual(w["count"], 1)
        self.assertTrue(Path(w["path"]).exists())

    def test_v5_analytics_counts(self):
        from rig_capabilities.fabric import context_pack, rate
        from rig_capabilities.surface import collect_analytics
        rep = context_pack(self.repo, "demo capability")
        rate(self.repo, rep["id"], "useful")
        a = collect_analytics(self.repo)
        self.assertGreaterEqual(a["packs"], 1)
        self.assertTrue(any(v.get("useful", 0) >= 1 for v in a["per_asset"].values()))



    def test_registry_status_one_round_trip(self):
        path = Path(self._tmp.name) / "reg.json"
        path.write_text(json.dumps({"repositories": [{
            "id": "demo", "github": "octocat/Hello-World",
            "local_path": "/nonexistent/path",
            "expected_origin": "https://github.com/octocat/Hello-World.git",
            "disposition": "TEST"}]}))
        from rig_capabilities.registry import load_registry, status_one
        rows = load_registry(path)
        self.assertEqual(1, len(rows))
        rec = status_one(rows[0], fetch=False)
        self.assertEqual("demo", rec["id"])
        self.assertFalse(rec["live"])


class RestGapTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_sqlite_connector_ingests_rows(self):
        import sqlite3
        db = self.tmp / "kb.sqlite"
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE docs (id TEXT, name TEXT, description TEXT, tags TEXT)")
        con.execute("INSERT INTO docs VALUES ('sql-doc','SQL Doc','from sqlite','kb')")
        con.commit(); con.close()
        cfg = json.loads(self.repo.config_path.read_text())
        cfg["connectors"] = [{"label": "kb", "type": "sqlite", "path": str(db),
                              "query": "SELECT id, name, description, tags FROM docs",
                              "kind": "skill"}]
        self.repo.config_path.write_text(json.dumps(cfg))
        doc = self.repo.build_index()
        hits = [a for a in doc["assets"] if a["id"] == "sql-doc"]
        self.assertEqual(1, len(hits))
        self.assertEqual("sql:kb", hits[0]["source"])
        self.assertFalse(hits[0]["installable"])

    def test_sqlite_missing_records_error(self):
        from rig_capabilities.connectors import ingest_sqlite, connector_status
        ingest_sqlite(self.repo, {"label": "gone", "type": "sqlite",
                                  "path": str(self.tmp / "nope.sqlite")})
        st = connector_status(self.repo)
        self.assertEqual("gone", st["last_error"]["label"])

    def test_http_serve_and_url_federation(self):
        import threading
        from rig_capabilities.serve import make_server
        peer = Repo(self.tmp / "peer")
        sk = peer.cap_root / "skills" / "net-peer"
        sk.mkdir(parents=True, exist_ok=True)
        (sk / "SKILL.md").write_text(
            "---\nname: net-peer\ndescription: served over http\n"
            "acl: [public]\n---\n# net\nbody\n")
        peer.config_path.write_text(json.dumps({"defaults": False, "external_roots": []}))
        peer.build_index()
        httpd = make_server(peer, "127.0.0.1", 0)
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            cfg = json.loads(self.repo.config_path.read_text())
            cfg["federates"] = [{"label": "net", "url": f"http://127.0.0.1:{port}"}]
            self.repo.config_path.write_text(json.dumps(cfg))
            doc = self.repo.build_index()
            hits = [a for a in doc["assets"] if a["id"] == "net-peer"]
            self.assertEqual(1, len(hits))
            self.assertEqual("fed:net", hits[0]["source"])
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_http_connector_reads_json_list(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        payload = json.dumps([{"id": "api-item", "name": "API Item",
                               "description": "from http api"}]).encode()

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                return

            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        srv = HTTPServer(("127.0.0.1", 0), H)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            cfg = json.loads(self.repo.config_path.read_text())
            cfg["connectors"] = [{"label": "docs", "type": "http",
                                  "url": f"http://127.0.0.1:{port}/",
                                  "kind": "skill"}]
            self.repo.config_path.write_text(json.dumps(cfg))
            doc = self.repo.build_index()
            hits = [a for a in doc["assets"] if a["id"] == "api-item"]
            self.assertEqual(1, len(hits))
            self.assertEqual("api:docs", hits[0]["source"])
        finally:
            srv.shutdown()
            srv.server_close()

    def test_observe_local_traces_langfuse_false(self):
        from rig_capabilities.fabric import context_pack
        from rig_capabilities.observe import status as obs_status
        context_pack(self.repo, "demo capability")
        st = obs_status(self.repo)
        self.assertFalse(st["langfuse_configured"])
        self.assertGreaterEqual(st["local_traces"], 1)
        traces = (self.repo.root / ".context" / "traces.jsonl").read_text()
        self.assertIn("context_pack", traces)

    def test_sql_trust_prefix(self):
        from rig_capabilities.okf import trust
        self.assertEqual(0.55, trust("sql:kb", "", None))
        self.assertEqual(0.5, trust("fed:net", "", None))
        self.assertEqual(0.9, trust("canonical", "", None))


class IdpServeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)
        from rig_capabilities.surface import generate_key
        generate_key(self.repo)

    def tearDown(self):
        self._tmp.cleanup()

    def test_token_roundtrip(self):
        from rig_capabilities.idp import issue_token, verify_token
        t = issue_token(self.repo, "jake", ttl=3600)
        self.assertTrue(t["ok"])
        res = verify_token(self.repo, t["token"])
        self.assertTrue(res["ok"])
        self.assertEqual("jake", res["agent"])

    def test_token_expired(self):
        import time
        from rig_capabilities.idp import issue_token, verify_token
        t = issue_token(self.repo, "jake", ttl=60)
        res = verify_token(self.repo, t["token"], now=int(time.time()) + 120)
        self.assertFalse(res["ok"])
        self.assertEqual("expired", res["error"])

    def test_token_bad_sig(self):
        from rig_capabilities.idp import issue_token, verify_token
        t = issue_token(self.repo, "jake")
        tampered = t["token"][:-4] + ("aaaa" if not t["token"].endswith("aaaa") else "bbbb")
        res = verify_token(self.repo, tampered)
        self.assertFalse(res["ok"])

    def test_token_malformed(self):
        from rig_capabilities.idp import verify_token
        self.assertFalse(verify_token(self.repo, "garbage")["ok"])

    def test_pack_token_precedence(self):
        from rig_capabilities.fabric import context_pack
        from rig_capabilities.idp import issue_token
        t = issue_token(self.repo, "jake")["token"]
        rep = context_pack(self.repo, "demo capability", token=t, requester="someone-else")
        self.assertEqual("jake", rep["verified_requester"])
        self.assertEqual("jake", rep["requester"])

    def test_pack_bad_token_rejected(self):
        from rig_capabilities.fabric import context_pack
        with self.assertRaises(ValueError):
            context_pack(self.repo, "demo capability", token="v1.bad.0.bad")

    def test_serve_bearer_protects_index(self):
        import threading
        import urllib.request
        import urllib.error
        from rig_capabilities.serve import make_server
        httpd = make_server(self.repo, "127.0.0.1", 0, token="secret-tok")
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            # no header -> 401
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/index.json", timeout=5)
            self.assertEqual(401, cm.exception.code)
            # good header -> 200
            req = urllib.request.Request(f"http://127.0.0.1:{port}/index.json",
                                         headers={"Authorization": "Bearer secret-tok"})
            with urllib.request.urlopen(req, timeout=5) as r:
                self.assertEqual(200, r.status)
            # health is public
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as r:
                self.assertEqual(200, r.status)
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_federation_sends_bearer(self):
        import threading
        import json as _json
        from http.server import BaseHTTPRequestHandler, HTTPServer
        seen = {}
        payload = _json.dumps({"assets": [{"id": "peer-x", "kind": "skill",
                                           "name": "Peer X", "description": "peer",
                                           "sha": "abc", "tags": []}]}).encode()

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                return

            def do_GET(self):
                seen["auth"] = self.headers.get("Authorization")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        srv = HTTPServer(("127.0.0.1", 0), H)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            cfg = json.loads(self.repo.config_path.read_text())
            cfg["federates"] = [{"label": "net", "url": f"http://127.0.0.1:{port}",
                                 "token": "fed-secret"}]
            self.repo.config_path.write_text(json.dumps(cfg))
            self.repo.build_index()
            self.assertEqual("Bearer fed-secret", seen.get("auth"))
        finally:
            srv.shutdown()
            srv.server_close()


class QualityTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_check_asset_scores(self):
        from rig_capabilities.quality import check_asset
        full = {"id": "x", "kind": "skill", "quality": {
            "outcome": "do a thing", "done_when": ["cmd:true"],
            "great_example": "examples/great/x.md", "quality_floor": 0.6}}
        r = check_asset(full)
        self.assertEqual(100, r["score"])
        self.assertTrue(r["has_done_test"])
        bare = {"id": "y", "kind": "skill", "quality": {}}
        rb = check_asset(bare)
        self.assertEqual(0, rb["score"])
        self.assertEqual(set(("outcome", "done_when", "great_example", "quality_floor")),
                         set(rb["missing"]))

    def test_migrate_frontmatter_adds_block_list(self):
        from rig_capabilities.quality import migrate_frontmatter
        p = self.repo.cap_root / "skills" / "demo-skill" / "SKILL.md"
        changed = migrate_frontmatter(p, {"outcome": "demo out",
                                          "done_when": ["file:x", "cmd:true"],
                                          "quality_floor": 0.6})
        self.assertTrue(changed)
        text = p.read_text()
        self.assertIn("outcome: demo out", text)
        self.assertIn("  - file:x", text)
        # idempotent: second run makes no change
        self.assertFalse(migrate_frontmatter(p, {"outcome": "other"}))
        self.assertIn("outcome: demo out", p.read_text())

    def test_index_carries_quality_block(self):
        from rig_capabilities.quality import migrate_frontmatter
        p = self.repo.cap_root / "skills" / "demo-skill" / "SKILL.md"
        migrate_frontmatter(p, {"outcome": "o", "done_when": ["cmd:true"],
                                "great_example": "e.md", "quality_floor": 0.6})
        self.repo.build_index()
        a = [x for x in self.repo.load_index()["assets"]
             if x["id"] == "demo-skill" and x["source"] == "canonical"][0]
        self.assertEqual("o", a["quality"]["outcome"])
        self.assertEqual(["cmd:true"], a["quality"]["done_when"])

    def test_migrate_canonical_fills_all(self):
        from rig_capabilities.quality import migrate_canonical, quality_report
        migrate_canonical(self.repo)
        rep = quality_report(self.repo)
        self.assertEqual(rep["total"], rep["fully_specified"])


class SkillUpgradesCommandTests(unittest.TestCase):
    def test_command_install_roots_cover_five(self):
        from rig_capabilities.catalog import DEFAULT_INSTALL_ROOTS
        cmd = DEFAULT_INSTALL_ROOTS["command"]
        for h in ("claude", "codex", "hermes", "omp", "agents"):
            self.assertIn(h, cmd)

    def test_install_kind_disambiguates(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = make_fixture(Path(tmp.name))
        # two canonical assets, same id, different kind
        skdir = repo.cap_root / "skills" / "dual"
        skdir.mkdir(parents=True, exist_ok=True)
        (skdir / "SKILL.md").write_text("---\nname: dual\ndescription: the skill\n---\n# dual\nbody\n")
        cmddir = repo.cap_root / "commands"
        cmddir.mkdir(parents=True, exist_ok=True)
        (cmddir / "dual.md").write_text("---\nname: dual\ndescription: the command\n---\n# dual cmd\nbody\n")
        cfg = json.loads(repo.config_path.read_text())
        cfg.setdefault("install_roots", {})["command"] = {"claude": str(Path(tmp.name) / "cc")}
        cfg["install_roots"]["skill"] = {"claude": str(Path(tmp.name) / "cs")}
        repo.config_path.write_text(json.dumps(cfg))
        repo.build_index()
        res = repo.install("dual.md", "claude", kind="command")
        self.assertEqual("command", res["kind"])
        self.assertTrue(res["target"].endswith("dual.md"))


if __name__ == "__main__":
    unittest.main()
