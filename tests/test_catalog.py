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

    def test_registry_status_one_round_trip(self):
        import json
        from rig_capabilities.registry import (load_registry, status_one)
        path = Path(self._tmp.name) / "reg.json"
        path.write_text(json.dumps({"repositories": [{
            "id": "demo", "github": "octocat/Hello-World",
            "local_path": "/nonexistent/path",
            "expected_origin": "https://github.com/octocat/Hello-World.git",
            "disposition": "TEST"}]}))
        rows = load_registry(path)
        self.assertEqual(1, len(rows))
        rec = status_one(rows[0], fetch=False)
        self.assertEqual("demo", rec["id"])
        self.assertEqual("octocat/Hello-World", rec["github"])
        self.assertIsNone(rec.get("local_path"))
        self.assertFalse(rec["live"])

if __name__ == "__main__":
    unittest.main()
