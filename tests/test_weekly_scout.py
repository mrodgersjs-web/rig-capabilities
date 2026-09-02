"""Tests for the weekly capability scout's deterministic half.

No network, no gh, no model: the fetcher and the gh runner are injected, and the
scrape subprocess is bypassed with skip_scrape. These tests exist because the stage
step is the only thing standing between a transcript and a citation, and a citation
stage that silently accepts a dead paper number is worse than no stage at all — it
launders an unverified claim into a "verified sources" list.
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "weekly_capability_scout", REPO / "scripts" / "weekly_capability_scout.py")
wc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wc)

ARXIV_OK = ("<?xml version='1.0'?><feed>"
            "<entry><id>https://arxiv.org/abs/2608.29596v1</id>"
            "<title>Towards a Systems Foundation for Agentic Skills</title></entry>"
            "<entry><id>https://arxiv.org/abs/2608.26263v2</id>"
            "<title>SKILL.state: Scalable Long-Horizon Agent Skills</title></entry>"
            "</feed>")


class _Proc:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


class ArxivVerifier(unittest.TestCase):
    def test_https_id_elements_still_resolve(self):
        """Regression: the id pattern once required http:// and resolved nothing.

        An empty verified-set reads exactly like "this week cited no papers", so
        the bug hid as a quiet, plausible week.
        """
        out = wc.verify_arxiv(["2608.29596", "2608.26263"], fetcher=lambda u: ARXIV_OK)
        self.assertTrue(out["2608.29596"]["resolved"])
        self.assertEqual(out["2608.26263"]["title"],
                         "SKILL.state: Scalable Long-Horizon Agent Skills")

    def test_unreturned_id_is_a_rejection_not_a_silence(self):
        out = wc.verify_arxiv(["2608.29596", "2699.00001"], fetcher=lambda u: ARXIV_OK)
        self.assertFalse(out["2699.00001"]["resolved"])
        self.assertEqual(out["2699.00001"]["reason"], "not_returned_by_arxiv")

    def test_unreachable_api_reports_reason_not_crash(self):
        def boom(_u):
            raise TimeoutError("export.arxiv.org timed out")
        out = wc.verify_arxiv(["2608.29596"], fetcher=boom)
        self.assertIn("api_unreachable:TimeoutError", out["2608.29596"]["reason"])

    def test_no_ids_makes_no_request(self):
        called = []
        self.assertEqual(wc.verify_arxiv([], fetcher=called.append), {})
        self.assertEqual(called, [])


class RepoVerifier(unittest.TestCase):
    def test_live_and_dead_repos_split(self):
        def runner(args):
            if "dead" in " ".join(args):
                return _Proc(1, "", "gh: Not Found (HTTP 404)")
            return _Proc(0, "HKUDS/HELIX\t31\tMIT\t2026-08-17\n", "")
        out = wc.verify_repos(["HKUDS/HELIX", "dead/dead"], runner=runner)
        self.assertTrue(out["HKUDS/HELIX"]["verified"])
        self.assertEqual(out["HKUDS/HELIX"]["stars"], 31)
        self.assertFalse(out["dead/dead"]["verified"])
        self.assertEqual(out["dead/dead"]["reason"], "not_found")

    def test_markdown_bold_contamination_is_stripped(self):
        """Dossiers write `**org/repo**`; that slug must not 404 for punctuation."""
        seen = []
        wc.verify_repos(["HKUDS/HELIX**"], runner=lambda a: (seen.append(a), _Proc(0, "x\t1\tMIT\t2026-08-01\n"))[1])
        self.assertIn("repos/HKUDS/HELIX", seen[0])

    def test_missing_gh_is_unverified_not_absent(self):
        real = wc.shutil.which
        wc.shutil.which = lambda name: None
        try:
            out = wc.verify_repos(["some/one"])
        finally:
            wc.shutil.which = real
        self.assertEqual(out["some/one"]["reason"], "gh_unavailable")


class Harvest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "transcripts").mkdir()
        (self.tmp / "descriptions").mkdir()
        (self.tmp / "transcripts" / "a.txt").write_text(
            "see arXiv:2608.29596 and https://arxiv.org/abs/2608.26263 "
            "code at https://github.com/HKUDS/HELIX README.md at "
            "https://github.com/foo/bar/blob/main/NOTES.md")
        (self.tmp / "descriptions" / "a.md").write_text(
            "Paper https://arxiv.org/abs/2608.13951. Repo https://github.com/a/b**.")

    def test_ids_urls_and_repos(self):
        urls, ids, repos = wc.harvest(self.tmp)
        self.assertIn("2608.29596", ids)          # bare mention form
        self.assertIn("2608.13951", ids)          # from the description
        self.assertIn("HKUDS/HELIX", repos)
        self.assertIn("a/b", repos)               # bold marker stripped by verifier
        self.assertTrue(all(not r.endswith(".md") for r in repos), repos)
        self.assertTrue(all(u.startswith("http") for u in urls))

    def test_missing_dirs_do_not_raise(self):
        self.assertEqual(wc.harvest(self.tmp / "nope"), ([], [], set()))


class Stage(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.week = self.tmp / "2026-W36"
        corpus = self.week / "code4ai"
        (corpus / "transcripts").mkdir(parents=True)
        (corpus / "transcripts" / "Kbxg-_CXs78.txt").write_text("hello arXiv:2608.29596")
        (corpus / "manifest.json").write_text(json.dumps({
            "targets": 2, "transcribed": 1, "total_words": 100,
            "videos": [{"id": "Kbxg-_CXs78", "title": "Agentic Skills",
                        "published": "2026-09-02", "words": 100},
                       {"id": "dead0000000", "title": "Members only", "words": 0}],
            "failed": [{"id": "OrpXpMd8mEY", "error": "members_only"}]}))
        self._load = wc.load_sources
        wc.load_sources = lambda *a, **k: [{"slug": "code4ai", "label": "Discover AI",
                                            "channel": "https://youtube.com/@code4AI"}]
        self._ax, self._gh = wc.verify_arxiv, wc.verify_repos
        wc.verify_arxiv = lambda ids: {i: {"resolved": i == "2608.29596"} for i in ids}
        wc.verify_repos = lambda rs: {r: {"verified": True, "stars": 1} for r in rs}

    def tearDown(self):
        wc.load_sources, wc.verify_arxiv, wc.verify_repos = self._load, self._ax, self._gh

    def test_writes_the_three_artifacts(self):
        res = wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        self.assertEqual(res["verdict"], "OK")
        for name in ("week.json", "queue.json", "brief.md"):
            self.assertTrue((self.week / name).exists(), name)

    def test_only_videos_with_words_are_queued(self):
        wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        q = json.loads((self.week / "queue.json").read_text())
        self.assertEqual([v["video"] for v in q["videos"]], ["Kbxg-_CXs78"])
        self.assertTrue(Path(q["videos"][0]["transcript"]).exists())

    def test_exclusions_are_carried_into_the_report(self):
        wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        doc = json.loads((self.week / "week.json").read_text())
        self.assertEqual(doc["sources"][0]["excluded"], ["members_only"])

    def test_writes_stay_inside_the_week_dir(self):
        before = {p for p in self.tmp.rglob("*")}
        wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        stray = [str(p) for p in Path(REPO).rglob("*")
                 if p.name == "week.json" and REPO / ".context" not in p.parents
                 and "capability-scout" not in str(p)]
        self.assertEqual(stray, [])
        self.assertTrue(len(set(self.tmp.rglob("*"))) > len(before))

    def test_rejections_are_kept_not_dropped(self):
        wc.verify_arxiv = lambda ids: {i: {"resolved": False, "reason": "nope"}
                                       for i in ids}
        wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        doc = json.loads((self.week / "week.json").read_text())
        self.assertEqual(doc["arxiv_verified"], {})
        self.assertIn("2608.29596", doc["arxiv_rejected"])

    def test_analyst_candidates_get_the_same_machine_check(self):
        """The creator links one paper and names three out loud without a URL."""
        seen = []

        def spy(ids):
            seen.append(sorted(ids))
            return {i: {"resolved": i in ("2608.29596", "2608.13951")} for i in ids}
        wc.verify_arxiv = spy
        (self.week / "candidates.json").write_text(json.dumps(
            {"arxiv": ["2608.13951", "2699.00001"], "repos": ["HKUDS/HELIX"]}))
        wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        doc = json.loads((self.week / "week.json").read_text())
        self.assertIn("2608.13951", seen[0])          # candidate reached the verifier
        self.assertIn("2608.13951", doc["arxiv_verified"])
        self.assertIn("2699.00001", doc["arxiv_rejected"])
        self.assertEqual(doc["candidates"]["arxiv"], 2)

    def test_malformed_candidates_is_recorded_not_fatal(self):
        (self.week / "candidates.json").write_text("{not json")
        res = wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        self.assertEqual(res["verdict"], "OK")
        doc = json.loads((self.week / "week.json").read_text())
        self.assertIn("error", doc["candidates"])

    def test_skip_scrape_cannot_look_like_a_fresh_scrape(self):
        wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        doc = json.loads((self.week / "week.json").read_text())
        self.assertFalse(doc["scraped"])
        self.assertEqual(doc["sources"][0]["rc"], -1)

    def test_empty_registry_refuses(self):
        wc.load_sources = lambda *a, **k: []
        res = wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        self.assertEqual(res["verdict"], "NO_SOURCES")
        self.assertFalse((self.week / "week.json").exists())

    def test_brief_names_the_verified_set_and_the_draft_rule(self):
        wc.stage("2026-W36", 9, self.tmp, skip_scrape=True)
        b = (self.week / "brief.md").read_text()
        self.assertIn("arXiv 2608.29596", b)
        self.assertIn("DRAFT", b)
        self.assertIn("fabrication", b)


class Registry(unittest.TestCase):
    """The tracked files are the contract the cron reads; they must parse and stay dormant."""

    def test_sources_registry_has_an_enabled_channel(self):
        srcs = wc.load_sources()
        self.assertTrue(srcs)
        for s in srcs:
            self.assertTrue(s["channel"].startswith("https://"))
            self.assertTrue(s["slug"])

    def test_cron_spec_is_dormant_and_gate_d(self):
        doc = json.loads((REPO / "data" / "capability-scout-weekly-cron.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(doc["state"], "DORMANT")
        self.assertFalse(doc["enabled"])
        self.assertTrue(doc["gate_d_required"])
        self.assertTrue(doc["dry_by_default"])
        self.assertIn("--disabled", doc["orca_command"])
        self.assertIn("install", " ".join(doc["never"]))

    def test_contract_json_has_no_duplicate_keys(self):
        """json.loads keeps the LAST duplicate, so a stale value silently wins.

        This happened for real: a patched orca_command was inserted while the
        original survived further down, and the dormancy assertion then read the
        stale command and passed. Duplicate keys in a contract file are a bug the
        parser will never report.
        """
        def no_dups(pairs):
            counts = {}
            for k, _v in pairs:
                counts[k] = counts.get(k, 0) + 1
            dupes = sorted(k for k, n in counts.items() if n > 1)
            self.assertEqual(dupes, [], f"duplicate keys in {name}")
            return dict(pairs)
        for name in ("capability-scout-weekly-cron.json",
                     "capability-scout-sources.json"):
            with self.subTest(name=name):
                json.loads((REPO / "data" / name).read_text(encoding="utf-8"),
                           object_pairs_hook=no_dups)

    def test_prompt_forbids_install_and_publish(self):
        p = (REPO / "data" / "capability-scout-prompt.txt").read_text(encoding="utf-8").lower()
        for word in ("do not install", "do not publish", "verbatim",
                     "membership-only"):
            self.assertIn(word, p)

if __name__ == "__main__":
    unittest.main(verbosity=2)
