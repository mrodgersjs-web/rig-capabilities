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

try:  # pytest is optional: plain `python -m unittest` still runs every test
    import pytest

    # Needs the operator's live estate (external corpus roots, local Postgres).
    # CI deselects these with `-m "not live_estate"`; they run on the RIG host.
    live_estate = pytest.mark.live_estate
except ImportError:  # pragma: no cover
    def live_estate(fn):
        return fn


# Gitignored caches and local state that must never leak into a test: an index
# or graph built under another $HOME (or by an older checkout) is not evidence.
_LOCAL_STATE = (".git", ".venv*", ".venvs", "*.egg-info", "__pycache__", ".pytest_cache",
                ".ruff_cache", ".apodex", ".context", ".index.json", ".graph.json",
                ".concepts.json", ".embeddings.json", ".last_seen.json", ".lanes.json",
                ".signing.key", ".serve.token", ".public-catalog.json", "tree", "tree.new",
                "tree.old", "*.tmp", ".env", "*.env", ".codex-tmp")


def hermetic_repo(test: unittest.TestCase) -> Path:
    """Copy of this checkout in a temp dir: no cached index/state, and no
    external roots (nothing under $HOME is scanned). Every index the test sees
    is built fresh from the copied `capabilities/` tree."""
    import shutil
    tmp = Path(tempfile.mkdtemp(prefix="cap-hermetic-"))
    test.addCleanup(shutil.rmtree, tmp, True)
    root = tmp / "repo"
    shutil.copytree(REPO_ROOT, root, symlinks=True,
                    ignore=shutil.ignore_patterns(*_LOCAL_STATE))
    cfg_path = root / "config.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg["defaults"] = False
    cfg["external_roots"] = []
    cfg_path.write_text(json.dumps(cfg, indent=2))
    assert not (root / ".index.json").exists()
    return root


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
        baks = list((self.tmp / "claude" / "hooks" / ".rig-backups").glob("guard.sh.bak-*"))
        self.assertEqual(1, len(baks))
        # never a sibling backup: a `<name>.bak-*` inside a skills/hooks root is loaded as a duplicate
        self.assertEqual([], list((self.tmp / "claude" / "hooks").glob("guard.sh.bak-*")))

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
        res = lookup_concept(self.repo, "threat")
        self.assertIn("threat-model", res["ids"])
        self.assertIn("threat-model", res["tiers"]["idf"])
        self.assertEqual([], res["tiers"]["llm"])  # no LLM overlay in fixture

    def test_concepts_llm_tier(self):
        import json as _json
        from rig_capabilities.fabric import build_concepts, lookup_concept
        build_concepts(self.repo)
        (Path(self._tmp.name) / "repo" / ".concepts.llm.json").write_text(
            _json.dumps({"security-threat-model|skill|canonical":
                         ["risk-modeling", "threat"]}))
        res = lookup_concept(self.repo, "risk-modeling")
        self.assertIn("security-threat-model", res["tiers"]["llm"])
        self.assertEqual([], res["tiers"]["idf"])
        self.assertIn("security-threat-model", res["ids"])

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


class IntelRootTests(unittest.TestCase):
    def test_intel_markdown_indexed_recursively(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = make_fixture(Path(tmp.name))
        intel = Path(tmp.name) / "intel" / "frontier"
        intel.mkdir(parents=True, exist_ok=True)
        (intel / "2026-08-31-topic.md").write_text(
            "---\nname: research-topic\ndescription: a frontier research note\n---\n"
            "# Research\nbody long enough to index\n")
        cfg = json.loads(repo.config_path.read_text())
        cfg["external_roots"].append({"label": "intel", "kind": "skill",
                                      "path": str(Path(tmp.name) / "intel"),
                                      "pattern": "**/*.md"})
        repo.config_path.write_text(json.dumps(cfg))
        doc = repo.build_index()
        hits = [a for a in doc["assets"] if a["id"] == "2026-08-31-topic.md"]
        self.assertEqual(1, len(hits))
        self.assertEqual("intel", hits[0]["source"])


class GreatExamplesTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)
        great = self.repo.root / "examples" / "great" / "revenue-gtm"
        great.mkdir(parents=True, exist_ok=True)
        (great / "cold-ex.md").write_text(
            "---\nname: great-cold\nlane: revenue-gtm\nsource: curated\n---\n"
            "# Reference\ncold outreach exemplar body long enough\n")
        cfg = json.loads(self.repo.config_path.read_text())
        cfg["external_roots"].append({"label": "great", "kind": "skill",
                                      "path": str(self.repo.root / "examples" / "great"),
                                      "pattern": "*/*.md"})
        self.repo.config_path.write_text(json.dumps(cfg))
        # a gtm skill so the lane routes to revenue-gtm
        d = self.repo.cap_root / "skills" / "cold-outreach-sequence"
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text("---\nname: cold-outreach-sequence\n"
                                    "description: multi-touch cold email outreach for outbound pipeline\n"
                                    "---\n# cold\nbody\n")
        self.repo.build_index()

    def tearDown(self):
        self._tmp.cleanup()

    def test_great_trust_is_high(self):
        a = [x for x in self.repo.load_index()["assets"]
             if x["source"] == "great"][0]
        self.assertEqual(0.8, a["okf"]["trust"])

    def test_pack_injects_reference(self):
        from rig_capabilities.fabric import context_pack
        rep = context_pack(self.repo, "cold email outreach to prospects",
                           budget_tokens=800, max_nodes=5)
        tiers = [n["tier"] for n in rep["nodes"]]
        self.assertIn("reference", tiers)
        self.assertIn("# Reference implementation", rep["markdown"])


class LaneOverlayTests(unittest.TestCase):
    def test_classify_prefers_overlay_lane(self):
        from rig_capabilities.taxonomy import classify
        # an asset that keyword-classifies as misc
        a = {"id": "zzz-unknown-thing", "kind": "skill", "description": "opaque"}
        self.assertEqual("misc", classify(a))
        a["lane"] = "revenue-gtm"
        self.assertEqual("revenue-gtm", classify(a))

    def test_overlay_stamped_at_index(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = make_fixture(Path(tmp.name))
        (repo.root / ".lanes.json").write_text(json.dumps({"demo-skill": "revenue-gtm"}))
        doc = repo.build_index()
        a = [x for x in doc["assets"] if x["id"] == "demo-skill" and x["source"] == "canonical"][0]
        self.assertEqual("revenue-gtm", a.get("lane"))
        from rig_capabilities.taxonomy import classify
        self.assertEqual("revenue-gtm", classify(a))

    def test_cosine_and_centroid_math(self):
        from rig_capabilities.lanes import _cos
        self.assertAlmostEqual(1.0, _cos([1, 0], [2, 0]), places=6)
        self.assertAlmostEqual(0.0, _cos([1, 0], [0, 1]), places=6)
        self.assertEqual(0.0, _cos([0, 0], [1, 1]))


class CoverageTests(unittest.TestCase):
    def test_roster_has_verticals_and_agents(self):
        roster = json.loads((REPO_ROOT / "agents" / "roster.json").read_text())
        self.assertEqual(8, len(roster["verticals"]))
        self.assertIn("healthcare", roster["verticals"])
        self.assertGreaterEqual(len(roster["agents"]), 20)

    def test_every_agent_has_pack(self):
        roster = json.loads((REPO_ROOT / "agents" / "roster.json").read_text())
        for agent in roster["agents"]:
            p = REPO_ROOT / "agents" / agent / "pack.json"
            self.assertTrue(p.exists(), f"missing pack for {agent}")
            d = json.loads(p.read_text())
            self.assertEqual(agent, d["agent"])
            self.assertTrue(d["lanes"])


class BootPackAndHookTests(unittest.TestCase):
    def test_script_quality_in_comments(self):
        from rig_capabilities.catalog import _quality_block
        script = ("#!/bin/bash\n# outcome: agent-engineering: x\n"
                  "# done_when: file:a || cmd:true\n# quality_floor: 0.6\n"
                  "echo hi\n")
        q = _quality_block(script)
        self.assertEqual("agent-engineering: x", q["outcome"])
        self.assertEqual(["file:a", "cmd:true"], q["done_when"])
        self.assertEqual("0.6", q["quality_floor"])

    def test_migrate_script_keeps_shebang_first(self):
        from rig_capabilities.quality import migrate_frontmatter
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p = Path(tmp.name) / "h.sh"
        p.write_text("#!/bin/bash\necho hi\n")
        migrate_frontmatter(p, {"outcome": "agent-engineering: y",
                                "done_when": ["cmd:true"], "quality_floor": 0.6})
        lines = p.read_text().splitlines()
        self.assertTrue(lines[0].startswith("#!"))
        self.assertIn("# outcome: agent-engineering: y", lines)

    def test_canonical_hooks_shebang_first(self):
        for f in (REPO_ROOT / "capabilities" / "hooks").glob("*.sh"):
            first = f.read_text().splitlines()[0]
            self.assertTrue(first.startswith("#!"), f"{f.name} shebang not first")

    def test_boot_pack_writes_artifact(self):
        import subprocess
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = make_fixture(Path(tmp.name))
        env = dict(os.environ, RIG_CAP_REPO=str(repo.root), HARNESS_NAME="tester")
        subprocess.run([sys.executable, str(REPO_ROOT / "bin" / "rig-boot-pack")],
                       env=env, timeout=30, check=True)
        out = repo.root / ".context" / "last-boot-pack.json"
        self.assertTrue(out.exists())
        self.assertEqual("tester", json.loads(out.read_text())["harness"])


class SyncTests(unittest.TestCase):
    def test_asset_rows_lane_from_overlay(self):
        from rig_capabilities.sync import asset_rows
        doc = {"assets": [{"id": "x", "kind": "skill", "source": "canonical",
                           "sha": "s", "description": "d", "tags": [],
                           "okf": {}, "quality": {}}]}
        rows = asset_rows(doc, {"x": "security-review"})
        self.assertEqual("security-review", rows[0][8])

    def test_pack_and_rating_rows(self):
        from rig_capabilities.sync import pack_rows, rating_rows
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = make_fixture(Path(tmp.name))
        ctx = repo.root / ".context"
        ctx.mkdir(exist_ok=True)
        (ctx / "pack-z.json").write_text(json.dumps(
            {"id": "pack-z", "requester": "jake", "intent": "i", "nodes": []}))
        (ctx / "ratings.jsonl").write_text(json.dumps(
            {"pack": "pack-z", "verdict": "useful", "ids": ["demo-skill"]}) + "\n")
        self.assertEqual(1, len(pack_rows(repo)))
        rows = rating_rows(repo)
        self.assertEqual("pack-z", rows[0][0])
        self.assertEqual("useful", rows[0][1])

    def test_discover_dsn_env_override(self):
        from rig_capabilities.sync import discover_dsn
        old = os.environ.get("RIG_CAP_DSN")
        os.environ["RIG_CAP_DSN"] = "postgresql://u:p@h:1/db"
        try:
            self.assertEqual("postgresql://u:p@h:1/db", discover_dsn())
        finally:
            if old is None:
                del os.environ["RIG_CAP_DSN"]
            else:
                os.environ["RIG_CAP_DSN"] = old

    @live_estate
    def test_live_roundtrip(self):
        import socket
        try:
            import psycopg2  # noqa: F401
        except ImportError:
            self.skipTest("psycopg2 missing")
        s = socket.socket()
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", 5433))
        except OSError:
            self.skipTest("rig-dev-db not reachable")
        finally:
            s.close()
        from rig_capabilities.sync import discover_dsn, sync
        dsn = discover_dsn()
        if not dsn:
            self.skipTest("no DSN discoverable")
        repo = Repo(REPO_ROOT)
        rep = sync(repo, dsn=dsn)
        self.assertGreater(rep["assets"], 4000)
        conn = psycopg2.connect(dsn, connect_timeout=5)
        try:
            with conn.cursor() as cur:
                cur.execute("select count(*) from capabilities.assets")
                self.assertEqual(rep["assets"], cur.fetchone()[0])
        finally:
            conn.close()


class DoneTests(unittest.TestCase):
    def _asset(self, td, sid, done_when_yaml):
        d = Path(td) / "repo" / "capabilities" / "skills" / sid
        return d, done_when_yaml

    def _repo_with(self, td, sid, entries):
        repo = make_fixture(Path(td))
        d = repo.cap_root / "skills" / sid
        d.mkdir(parents=True, exist_ok=True)
        dw = "".join(f"  - {e}\n" for e in entries)
        (d / "SKILL.md").write_text(
            f"---\nname: {sid}\ndescription: a capability for checks\n"
            f"done_when:\n{dw}---\n# {sid}\nneedle text here\n")
        repo.build_index()
        return repo

    def test_four_forms_pass_and_fail(self):
        from rig_capabilities.done_tests import run_asset
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = self._repo_with(tmp.name, "ok-skill", [
            "cmd:true", "file:capabilities/skills/ok-skill/SKILL.md",
            "grep:capabilities/skills/ok-skill/SKILL.md:needle",
            "not-a-form"])
        r = run_asset(repo, "ok-skill")
        self.assertTrue(r["pass"])
        self.assertEqual(1, sum(1 for x in r["results"] if x["ok"] is None))
        bad = self._repo_with(tmp.name, "bad-skill", ["cmd:false", "file:nope"])
        r2 = run_asset(bad, "bad-skill")
        self.assertFalse(r2["pass"])

    def test_quality_run_writes_artifact(self):
        from rig_capabilities.done_tests import quality_run
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = self._repo_with(tmp.name, "q-skill", ["cmd:true"])
        rep = quality_run(repo)
        self.assertEqual(1, rep["ran"])
        out = list((repo.root / ".context" / "quality-runs").glob("*.json"))
        self.assertEqual(1, len(out))

    def test_canonical_skills_pass(self):
        from rig_capabilities.done_tests import run_asset
        repo = Repo(hermetic_repo(self))
        for sid in ("semgrep", "codeql", "sarif-parsing", "skill-upgrades"):
            self.assertTrue(run_asset(repo, sid, "canonical")["pass"], sid)


class RoundTests(unittest.TestCase):
    def _repo(self, td, prose_only=True):
        repo = make_fixture(Path(td))
        d = repo.cap_root / "skills" / "weak-skill"
        d.mkdir(parents=True, exist_ok=True)
        dw = ("  - the outcome is achieved\n" if prose_only
              else "  - file:capabilities/skills/weak-skill/SKILL.md\n")
        (d / "SKILL.md").write_text(
            "---\nname: weak-skill\ndescription: weak\noutcome: misc: weak\n"
            f"done_when:\n{dw}great_example: examples/great/misc/weak-skill.md\n"
            "quality_floor: 0.6\n---\n# weak\nbody\n")
        repo.build_index()
        return repo

    def test_dry_writes_nothing(self):
        from rig_capabilities.rounds import run_round
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = self._repo(tmp.name)
        before = (repo.cap_root / "skills" / "weak-skill" / "SKILL.md").read_text()
        rep = run_round(repo, "agent-engineering", n=5, dry=True)
        self.assertEqual(before,
                         (repo.cap_root / "skills" / "weak-skill" / "SKILL.md").read_text())
        self.assertTrue(any(a["action"] == "would-apply" for a in rep["actions"]))

    def test_graduation_only_on_green(self):
        from rig_capabilities.rounds import run_round
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = self._repo(tmp.name)
        rep = run_round(repo, "agent-engineering", n=5)
        wk = next(a for a in rep["actions"] if a["id"] == "weak-skill")
        self.assertEqual("applied", wk["action"])
        self.assertTrue(wk["graduated"])
        text = (repo.cap_root / "skills" / "weak-skill" / "SKILL.md").read_text()
        self.assertIn("file:capabilities/skills/weak-skill/SKILL.md", text)
        # second round: nothing left to apply
        rep2 = run_round(repo, "agent-engineering", n=5)
        wk2 = next(a for a in rep2["actions"] if a["id"] == "weak-skill")
        self.assertEqual("no-op", wk2["action"])

    def test_live_round_is_clean(self):
        from rig_capabilities.rounds import pick_candidates, run_round
        repo = Repo(hermetic_repo(self))
        cands = pick_candidates(repo, "agent-engineering", 3)
        self.assertTrue(cands)
        run_round(repo, "misc", n=2, dry=True)
        self.assertTrue((repo.root / ".context" / "rounds").exists())


class CorpusRootTests(unittest.TestCase):
    def test_mtime_verified_on(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = make_fixture(Path(tmp.name))
        corpus = Path(tmp.name) / "corpus"
        (corpus / "sub").mkdir(parents=True)
        f = corpus / "sub" / "note.md"
        f.write_text("# scraped note\nno frontmatter, just corpus text\n")
        cfg = json.loads(repo.config_path.read_text())
        cfg.setdefault("external_roots", []).append(
            {"label": "corpus", "kind": "skill", "path": str(corpus),
             "pattern": "**/*.md", "mtime_verified": True})
        repo.config_path.write_text(json.dumps(cfg))
        assets = repo.scan()
        a = next(x for x in assets if x["source"] == "corpus")
        import time
        want = time.strftime("%Y-%m-%d", time.localtime(f.stat().st_mtime))
        self.assertEqual(want, (a.get("quality") or {}).get("verified_on"))

    @live_estate
    def test_live_corpus_root_indexed(self):
        rows = [a for a in Repo(REPO_ROOT).load_index()["assets"]
                if a["source"] == "intel-corpus"]
        self.assertGreater(len(rows), 50)
        self.assertTrue(all((a.get("quality") or {}).get("verified_on")
                            for a in rows))


class FederationLiveTests(unittest.TestCase):
    def _serve(self, repo, token):
        import threading
        from rig_capabilities.serve import make_server
        httpd = make_server(repo, "127.0.0.1", 0, token=token)
        th = threading.Thread(target=httpd.serve_forever, daemon=True)
        th.start()
        self.addCleanup(lambda: (httpd.shutdown(), th.join(5),
                                 httpd.server_close()))
        return f"http://127.0.0.1:{httpd.server_address[1]}"

    def _repos(self, tmp):
        peer = make_fixture(Path(tmp) / "peer")
        peer.build_index()
        main = make_fixture(Path(tmp) / "main")
        return peer, main

    def _federate(self, main, entry):
        cfg = json.loads(main.config_path.read_text())
        cfg["federates"] = [entry]
        main.config_path.write_text(json.dumps(cfg))

    def test_token_file_pulls_fed_assets(self):
        from rig_capabilities.federation import federated_assets
        tmp = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, tmp, True)
        peer, main = self._repos(tmp)
        base = self._serve(peer, "PEERTOK")
        tf = Path(tmp) / "main" / "repo" / ".context" / "fed"
        tf.mkdir(parents=True, exist_ok=True)
        (tf / "peer.token").write_text("PEERTOK\n")
        self._federate(main, {"label": "peer", "url": base,
                              "token_file": ".context/fed/peer.token"})
        fed = federated_assets(main)
        self.assertTrue(fed)
        self.assertTrue(all(a["source"] == "fed:peer" for a in fed))

    def test_missing_or_wrong_token_yields_no_assets(self):
        from rig_capabilities.federation import federated_assets
        tmp = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, tmp, True)
        peer, main = self._repos(tmp)
        base = self._serve(peer, "PEERTOK")
        import urllib.error
        import urllib.request
        for hdrs in ({}, {"Authorization": "Bearer WRONG"}):
            req = urllib.request.Request(base + "/index.json", headers=hdrs)
            try:
                urllib.request.urlopen(req, timeout=5)
                self.fail("protected path served without a valid token")
            except urllib.error.HTTPError as e:
                self.assertEqual(401, e.code)
        # federation side: public fallback only (hooks/commands), never skills
        self._federate(main, {"label": "peer", "url": base})
        fed = federated_assets(main)
        self.assertTrue(all(a.get("kind") in ("hook", "command") for a in fed))
        self.assertFalse(any(a.get("kind") == "skill" for a in fed))
        tf = Path(tmp) / "main" / "repo" / ".context" / "fed"
        tf.mkdir(parents=True, exist_ok=True)
        (tf / "peer.token").write_text("WRONG\n")
        self._federate(main, {"label": "peer", "url": base,
                              "token_file": ".context/fed/peer.token"})
        fed = federated_assets(main)
        self.assertFalse(any(a.get("kind") == "skill" for a in fed))


class VerifiedRequesterTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_fixture(Path(self._tmp.name))
        self.repo.build_index()

    def _token(self, agent="jake", ttl=3600):
        from rig_capabilities.idp import issue_token
        return issue_token(self.repo, agent, ttl=ttl, mint_key=True)

    def test_valid_token_verified_and_traced(self):
        from rig_capabilities.fabric import context_pack
        iss = self._token()
        self.assertTrue(iss["ok"])
        art = context_pack(self.repo, "threat model", token=iss["token"],
                           requester="unverified-sue")
        self.assertEqual("jake", art["verified_requester"])
        self.assertEqual("jake", art["requester"])  # token > --requester
        line = json.loads((Path(self.repo.root) / ".context" / "agents"
                           / "jake" / "log.jsonl").read_text().splitlines()[-1])
        self.assertEqual("jake", line["verified_requester"])

    def test_bad_or_expired_token_rejected(self):
        from rig_capabilities.fabric import context_pack
        with self.assertRaises(ValueError):
            context_pack(self.repo, "x", token="v1.bogus.999.deadbeef")
        iss = self._token(ttl=60)
        with self.assertRaises(ValueError):
            context_pack(self.repo, "x", token=iss["token"].replace(
                f".{iss['exp']}.", f".{iss['exp'] - 120}."))  # tampered exp


class StatsDashboardTests(unittest.TestCase):
    def setUp(self):
        import threading
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_fixture(Path(self._tmp.name))
        self.repo.build_index()
        from rig_capabilities.serve import make_server
        self.httpd = make_server(self.repo, "127.0.0.1", 0, token="TOK")
        th = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        th.start()
        self.addCleanup(lambda: (self.httpd.shutdown(), th.join(5),
                                 self.httpd.server_close()))
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def _get(self, p, tok=None):
        import urllib.request
        hdrs = {"Authorization": f"Bearer {tok}"} if tok else {}
        with urllib.request.urlopen(
                urllib.request.Request(self.base + p, headers=hdrs),
                timeout=5) as r:
            return r.status, r.read()

    def test_stats_public_and_shaped(self):
        code, body = self._get("/stats.json")
        d = json.loads(body)
        self.assertEqual(200, code)
        for k in ("version", "assets", "by_source", "by_kind", "quality_runs",
                  "rounds", "concepts_llm", "federates", "federated_assets",
                  "traces", "public_assets", "gate_d_cases"):
            self.assertIn(k, d)
        self.assertGreater(d["assets"], 0)

    def test_dashboard_html_no_asset_data(self):
        code, body = self._get("/dashboard")
        text = body.decode()
        self.assertEqual(200, code)
        self.assertIn("<!doctype html>", text.lower())
        self.assertIn("/stats.json", text)
        # aggregates-only: no asset ids leak into the shell
        self.assertNotIn("demo-skill", text)


class CertifyTests(unittest.TestCase):
    """V22: gates that cannot go RED are theater — prove they fire on a copy."""

    def _tmp_repo(self):
        return hermetic_repo(self)

    def test_acl_gate_green_then_planted_red(self):
        from rig_capabilities.certify import _plant, run_gates
        root = self._tmp_repo()
        green = run_gates(Repo(root), only=["acl_jake"])["acl_jake"]["ok"]
        _plant("acl_jake", root)
        red = run_gates(Repo(root), only=["acl_jake"])["acl_jake"]["ok"]
        self.assertTrue(green)
        self.assertFalse(red)

    def test_index_gate_planted_red(self):
        from rig_capabilities.certify import _plant, run_gates
        root = self._tmp_repo()
        green = run_gates(Repo(root), only=["index_fresh"])["index_fresh"]["ok"]
        _plant("index_fresh", root)
        red = run_gates(Repo(root), only=["index_fresh"])["index_fresh"]["ok"]
        self.assertTrue(green)
        self.assertFalse(red)


class PackTests(unittest.TestCase):
    """V23: agent packs resolve against the index and lead agent-shaped packs."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)
        d = self.repo.root / "agents" / "demo"
        d.mkdir(parents=True, exist_ok=True)
        (d / "pack.json").write_text(json.dumps({
            "agent": "demo", "lanes": ["data-analytics"],
            "skills": [{"id": "demo-skill", "kind": "skill", "trust": 0.9},
                       {"id": "ghost-skill", "kind": "skill", "trust": 0.8}]}))

    def tearDown(self):
        self._tmp.cleanup()

    def test_resolve_pack_resolves_and_flags_ghost(self):
        from rig_capabilities.packs import resolve_pack
        rp = resolve_pack(self.repo, "demo")
        self.assertTrue(rp["ok"])
        self.assertEqual(rp["unresolved"], ["ghost-skill"])
        by = {e["id"]: e for e in rp["entries"]}
        self.assertTrue(by["demo-skill"]["resolved"])
        self.assertEqual(by["demo-skill"]["source"], "canonical")

    def test_match_agent_ranks_and_rejects(self):
        from rig_capabilities.packs import match_agent
        hits = match_agent(self.repo, "wire demo up to run the thing")
        self.assertEqual(hits[0]["agent"], "demo")
        self.assertEqual(match_agent(self.repo, "rotate the api signing key"), [])

    def test_boot_pack_attests_readiness(self):
        from rig_capabilities.packs import boot_pack
        bp = boot_pack(self.repo, "demo")
        self.assertEqual(bp["total"], 2)
        by = {e["id"]: e for e in bp["entries"]}
        self.assertIn("live", by["demo-skill"])
        self.assertEqual(by["ghost-skill"]["live"]["state"], "unresolved")
        self.assertLessEqual(bp["ready"], bp["total"])

    def test_context_pack_leads_with_agent_pack(self):
        from rig_capabilities.fabric import context_pack
        rep = context_pack(self.repo, "wire demo to run the demo flow",
                           sign=False)
        self.assertEqual(rep["pack_for"], "demo")
        self.assertIn("# Agent pack", rep["markdown"])


class CommandCanonicalTests(unittest.TestCase):
    """V24: six canonical commands, contracts intact, delivered by the installer."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "capwire", REPO_ROOT / "wire" / "wire.py")
        self.wire = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.wire)

    def test_all_commands_carry_full_contract(self):
        srcs = list((REPO_ROOT / "capabilities" / "commands").glob("*.md"))
        self.assertEqual(len(srcs), 7, sorted(f.name for f in srcs))
        for f in srcs:
            text = f.read_text()
            for key in ("outcome:", "done_when:", "great_example:", "quality_floor:"):
                self.assertIn(key, text, f"{f.name} missing {key}")
            for line in text.splitlines():
                if line.startswith("great_example:"):
                    ref = line.split(":", 1)[1].strip()
                    self.assertTrue((REPO_ROOT / ref).exists(),
                                    f"{f.name} great_example absent: {ref}")

    def test_sync_commands_dry_then_apply_then_repairs(self):
        import shutil
        tmp = Path(tempfile.mkdtemp(prefix="cap-cmd-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        r1, r2 = tmp / "claude", tmp / "codex"
        self.wire.COMMAND_ROOTS = (r1, r2)
        acts: list = []
        self.wire.sync_commands(False, acts)
        self.assertTrue(all("plan" in a for a in acts))
        self.assertFalse((r1 / "capabilities-round.md").exists())
        acts = []
        self.wire.sync_commands(True, acts)
        n = len(self.wire.command_sources())
        self.assertEqual(len([a for a in acts if "wired" in a]), 2 * n)
        self.assertTrue((r1 / "capabilities-round.md").exists())
        self.assertTrue((r2 / "skill-upgrades.md").exists())
        acts = []
        self.wire.sync_commands(True, acts)
        self.assertEqual(len([a for a in acts if "current" in a]), 2 * n)
        (r1 / "capabilities-round.md").write_text("tampered")
        self.wire.sync_commands(True, acts)
        self.assertIn("# capabilities-round",
                      (r1 / "capabilities-round.md").read_text())

    def test_command_roots_include_omp_prime(self):
        self.assertGreaterEqual(len(self.wire.COMMAND_ROOTS), 6)
        names = [str(p) for p in self.wire.COMMAND_ROOTS]
        self.assertTrue(any("hermes" in n for n in names))
        self.assertTrue(any("omp" in n for n in names))
        self.assertTrue(any("prime" in n for n in names))

    def test_server_tools_registered(self):
        from rig_capabilities.server import TOOLS
        names = {t["name"] for t in TOOLS}
        self.assertIn("capabilities_certify", names)
        self.assertIn("capabilities_agent_pack", names)
        for n in ("capabilities_gaps", "capabilities_overlay_status",
                  "capabilities_proofchain", "capabilities_release"):
            self.assertIn(n, names)

    def test_command_done_when_never_mutates(self):
        banned = ("mcp:capabilities_certify", "mcp:capabilities_round",
                  "mcp:capabilities_db_sync", "mcp:capabilities_reindex",
                  "mcp:capabilities_issue_token")
        for f in (REPO_ROOT / "capabilities" / "commands").glob("*.md"):
            text = f.read_text()
            for b in banned:
                self.assertNotIn(b, text, f"{f.name} invokes mutating {b}")

    def test_quality_run_skips_mutating_mcp(self):
        from rig_capabilities.done_tests import MCP_MUTATING, parse_form
        self.assertIn("capabilities_certify", MCP_MUTATING)
        form, arg = parse_form("mcp:capabilities_certify")
        self.assertEqual((form, arg), ("mcp", "capabilities_certify"))

    def test_quality_run_reentrancy_guard(self):
        from rig_capabilities import done_tests as dt
        dt._IN_QUALITY_RUN = True
        try:
            from rig_capabilities.catalog import Repo
            rep = dt.quality_run(Repo(hermetic_repo(self)))
            self.assertTrue(rep.get("reentrant"))
            self.assertIsNone(rep["pass_rate"])
        finally:
            dt._IN_QUALITY_RUN = False



class HookGapTests(unittest.TestCase):
    """V25: OMP + Prime join the hook install surface."""

    def test_default_hook_roots_include_omp_prime(self):
        from rig_capabilities.catalog import DEFAULT_INSTALL_ROOTS
        h = DEFAULT_INSTALL_ROOTS["hook"]
        self.assertIn("omp", h)
        self.assertIn("prime-agent", h)

    def test_hook_live_when_file_in_omp_root(self):
        import shutil
        tmp = Path(tempfile.mkdtemp(prefix="cap-hook-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        repo = make_fixture(tmp)
        omp = tmp / "omp" / "hooks"
        omp.mkdir(parents=True)
        shutil.copy(repo.cap_root / "hooks" / "guard.sh", omp / "guard.sh")
        cfg = json.loads(repo.config_path.read_text())
        cfg["install_roots"]["hook"] = {"omp": str(omp)}
        repo.config_path.write_text(json.dumps(cfg))
        from rig_capabilities import live as live_mod
        fake = tmp / "settings.json"
        fake.write_text("{}")
        orig = live_mod._CLAUDE_SETTINGS
        live_mod._CLAUDE_SETTINGS = fake
        try:
            st = live_mod.live_status(repo, id="guard.sh", services=False)
        finally:
            live_mod._CLAUDE_SETTINGS = orig
        self.assertTrue(st["summary"]["live"])
        self.assertIn("omp", st["summary"]["roots"])
        self.assertFalse(st["summary"]["claude_registered"])

    def test_sync_hooks_dry_then_apply(self):
        import importlib.util
        import shutil
        spec = importlib.util.spec_from_file_location(
            "capwire_hooks", REPO_ROOT / "wire" / "wire.py")
        wire = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wire)
        tmp = Path(tempfile.mkdtemp(prefix="cap-hooksync-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        r1, r2 = tmp / "omp", tmp / "prime"
        wire.HOOK_ROOTS = (r1, r2)
        acts: list = []
        wire.sync_hooks(False, acts)
        self.assertTrue(all("plan" in a for a in acts))
        acts = []
        wire.sync_hooks(True, acts)
        n = len(wire.hook_sources())
        self.assertEqual(len([a for a in acts if "wired" in a]), 2 * n)
        self.assertTrue((r1 / "guard-secret-write.sh").exists())
        self.assertTrue((r2 / "goal-loop-startup.sh").exists())


class GapHarnessTests(unittest.TestCase):
    """V26: requests.jsonl cells become draft harnesses that can go RED."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_fixture(self.tmp)
        ctx = self.repo.root / ".context"
        ctx.mkdir(parents=True, exist_ok=True)
        (ctx / "requests.jsonl").write_text(
            json.dumps({"type": "capability_request", "vertical": "healthcare",
                        "lane": "security-review", "have": 0, "need": 3}) + "\n"
            + json.dumps({"type": "capability_request", "vertical": "healthcare",
                          "lane": "security-review", "have": 1, "need": 3}) + "\n"
            + json.dumps({"type": "capability_request", "vertical": "dental",
                          "lane": "revenue-gtm", "have": 0, "need": 3}) + "\n"
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_rank_gaps_last_row_wins_and_prefers_lane(self):
        from rig_capabilities.gaps import load_requests, rank_gaps
        ranked = rank_gaps(load_requests(self.repo), n=8)
        by = {r["vertical"]: r for r in ranked}
        self.assertEqual(by["healthcare"]["have"], 1)
        self.assertEqual(by["healthcare"]["lane"], "security-review")
        self.assertEqual(by["dental"]["lane"], "revenue-gtm")

    def test_dry_does_not_write(self):
        from rig_capabilities.gaps import write_gap_harnesses
        dest = self.repo.root / "capabilities" / "harnesses"
        before = set(dest.glob("gap-*.yaml")) if dest.exists() else set()
        write_gap_harnesses(self.repo, n=8, apply=False)
        after = set(dest.glob("gap-*.yaml")) if dest.exists() else set()
        self.assertEqual(before, after)

    def test_apply_writes_grepable_stake(self):
        from rig_capabilities.gaps import write_gap_harnesses
        rep = write_gap_harnesses(self.repo, n=8, apply=True)
        self.assertGreaterEqual(rep["count"], 2)
        pth = self.repo.root / "capabilities" / "harnesses" / "gap-healthcare-security-review.yaml"
        text = pth.read_text()
        self.assertIn("PHI", text)
        self.assertIn("file:capabilities/harnesses/gap-healthcare-security-review.yaml", text)


class TracesPanelTests(unittest.TestCase):
    """V27: traces on the public panel are aggregates — no payloads."""

    def test_compute_traces_hide_payloads(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        repo = make_fixture(Path(self._tmp.name))
        from rig_capabilities.observe import trace
        from rig_capabilities.stats import compute
        trace(repo, "context_pack",
              input={"intent": "secret-query-xyz"},
              output={"pack": "pack-secret"})
        d = compute(repo)
        self.assertGreaterEqual(d["traces"]["count"], 1)
        self.assertEqual(d["traces"]["by_name"].get("context_pack"), 1)
        blob = json.dumps(d["traces"])
        self.assertNotIn("secret-query-xyz", blob)
        self.assertNotIn("pack-secret", blob)
        for ev in d["traces"]["recent"]:
            self.assertNotIn("input", ev)
            self.assertNotIn("output", ev)


class PublicZipTests(unittest.TestCase):
    """V28: public zip is catalog-only, dormant, and secret-free."""

    def test_zip_is_dormant_catalog_only(self):
        import zipfile
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        repo = make_fixture(Path(self._tmp.name))
        from rig_capabilities.release import build_public_zip, GATE_D_RUN
        dry = build_public_zip(repo, apply=False)
        self.assertFalse(dry["armed"])
        self.assertEqual(dry["gate_d_run_id"] if "gate_d_run_id" in dry else dry["manifest"]["gate_d_run_id"], GATE_D_RUN)
        self.assertFalse(Path(dry["path"]).exists())
        live = build_public_zip(repo, apply=True)
        self.assertFalse(live["armed"])
        z = zipfile.ZipFile(live["path"])
        names = set(z.namelist())
        self.assertEqual(names, {".public-catalog.json", "MANIFEST.json"})
        self.assertTrue(all(".signing" not in n and ".token" not in n for n in names))
        man = json.loads(z.read("MANIFEST.json"))
        self.assertFalse(man["armed"])
        cat = json.loads(z.read(".public-catalog.json"))
        self.assertEqual(cat["count"], man["count"])


class WholeRepoCertifyTests(unittest.TestCase):
    """V29: Layer-Isolated — certify gates minus suite, locked on the live tree."""

    def test_non_suite_gates_green(self):
        from rig_capabilities.certify import GATES, run_gates
        only = [k for k in GATES if k != "suite"]
        self.assertEqual(sorted(only),
                         ["acl_jake", "done_tests", "idp_integrity", "index_fresh"])
        # Fresh copy, fresh index, throwaway signing key: no cached file from the
        # working tree or $HOME can turn a gate green or red.
        old_key = os.environ.get("RIG_CAPABILITIES_SIGNING_KEY")
        os.environ["RIG_CAPABILITIES_SIGNING_KEY"] = os.urandom(32).hex()
        self.addCleanup(lambda: os.environ.__setitem__("RIG_CAPABILITIES_SIGNING_KEY", old_key)
                        if old_key is not None else os.environ.pop("RIG_CAPABILITIES_SIGNING_KEY", None))
        res = run_gates(Repo(hermetic_repo(self)), only=only)
        for name, row in res.items():
            self.assertTrue(row["ok"], f"{name} red: {row.get('detail')}")


class RoadmapTests(unittest.TestCase):
    """V30: the ladder is a file, not a speech."""

    def test_roadmap_lists_1_to_30(self):
        text = (REPO_ROOT / "docs" / "ROADMAP.md").read_text()
        for n in range(1, 41):
            self.assertRegex(text, rf"\| {n} \|")
        self.assertIn("gd_1788227314643", text)
        self.assertIn("ARMED", text)


class GateDLibTests(unittest.TestCase):
    """V31: evaluate() is the source of truth, no SDK required."""

    def test_cases_match_expected(self):
        from rig_capabilities.gate_d import CASES, evaluate
        for tool, payload, want in CASES:
            got, rule = evaluate(tool, payload)
            self.assertEqual(got, want, f"{tool} {payload} -> {got}/{rule}")

    def test_relative_rm_allowed(self):
        from rig_capabilities.gate_d import evaluate
        got, rule = evaluate("Bash", {"command": "rm -rf ./build && npm run build"})
        self.assertEqual(got, "allow")

    def test_sanitize_redacts_akia(self):
        from rig_capabilities.gate_d import sanitize
        out = sanitize({"content": "key: AKIAIOSFODNN7EXAMPLE"})
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", json.dumps(out))
        self.assertIn("REDACTED", json.dumps(out))


class PublicAclTests(unittest.TestCase):
    """V32: canonical commands/hooks default public; skills do not."""

    def test_fixture_command_not_applicable_skill_stays_private(self):
        from rig_capabilities.okf import meta
        skill = meta({"name": "x"}, "canonical", kind="skill")
        self.assertEqual(skill["acl"], [])
        cmd = meta({"name": "x"}, "canonical", kind="command")
        self.assertEqual(cmd["acl"], ["public"])
        hook = meta({"name": "x"}, "canonical", kind="hook")
        self.assertEqual(hook["acl"], ["public"])
        explicit = meta({"acl": "internal"}, "canonical", kind="command")
        self.assertEqual(explicit["acl"], ["internal"])


class OverlayDoctorTests(unittest.TestCase):
    """V34: overlay_status never claims complete on a short file."""

    def test_empty_overlay_is_incomplete(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        repo = make_fixture(Path(self._tmp.name))
        from rig_capabilities.concepts_llm import overlay_status
        st = overlay_status(repo, target=300)
        self.assertEqual(st["tagged"], 0)
        self.assertFalse(st["complete"])
        self.assertIn("concepts-build", st["resume"])

    def test_partial_overlay_ratio_honest(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        repo = make_fixture(Path(self._tmp.name))
        (repo.root / ".concepts.llm.json").write_text(json.dumps({"a|skill|canonical": ["x"]}))
        from rig_capabilities.concepts_llm import overlay_status
        st = overlay_status(repo, target=10)
        self.assertEqual(st["tagged"], 1)
        self.assertEqual(st["ratio"], 0.1)
        self.assertFalse(st["complete"])


class HarnessInstallTests(unittest.TestCase):
    def test_dry_does_not_write(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        repo = make_fixture(Path(self._tmp.name))
        src = repo.root / "out" / "harness-goalspecs"
        src.mkdir(parents=True)
        (src / "hA-01.yaml").write_text("id: GL-HA-01\n")
        dest = Path(self._tmp.name) / "dest"
        from rig_capabilities.harness_install import harness_install
        dry = harness_install(repo, dest=dest, apply=False)
        self.assertEqual(dry["count"], 1)
        self.assertFalse(dest.exists())
        live = harness_install(repo, dest=dest, apply=True)
        self.assertEqual(live["written"], ["hA-01.yaml"])
        self.assertTrue((dest / "hA-01.yaml").exists())


class ProofchainTests(unittest.TestCase):
    def test_missing_prefix_is_reported(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        repo = make_fixture(Path(self._tmp.name))
        docs = repo.root / "docs"
        docs.mkdir(parents=True)
        (docs / "ROADMAP.md").write_text("| V | commit | packet | what |\n| 21 | `abcabcab` | `deadbeef` | x |\nsha256:cafebabe00\n")
        proofs = Path(self._tmp.name) / "proof"
        proofs.mkdir()
        (proofs / "a.json").write_text(json.dumps({"proof_hash": "sha256:cafebabe00ffff"}))
        from rig_capabilities.proofchain import verify_roadmap
        rep = verify_roadmap(repo, proof_dir=proofs)
        self.assertIn("deadbeef", rep["missing"])
        self.assertIn("cafebabe", rep["found"])
        self.assertFalse(rep["ok"])



class McpStdioSmokeTests(unittest.TestCase):
    """The shipped MCP entrypoint answers a real catalog query over stdio."""

    def test_smoke_script_finds_bundled_skill(self):
        r = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "smoke_mcp.py"),
                            "--repo", str(hermetic_repo(self))],
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("SMOKE OK", r.stdout)
        self.assertIn("capabilities_get proof-loop: skill canonical", r.stdout)

    def test_server_version_matches_package(self):
        from rig_capabilities import __version__
        from rig_capabilities.server import VERSION
        self.assertEqual(VERSION, __version__)

if __name__ == "__main__":
    unittest.main()
