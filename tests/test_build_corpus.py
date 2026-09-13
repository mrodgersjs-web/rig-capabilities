"""Corpus-freeze tests (A33–A37). The suite itself performs no network call
and fetches nothing; it proves the golden bytes, the distribution, the
PENDING-only discipline, and the absence of any rewrite/add verb."""
import copy
import json
import shutil
import tempfile
import unittest

from rig_capabilities import build_corpus


class CorpusFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.man = build_corpus.manifest_path("v1")
        cls.doc = json.loads(cls.man.read_bytes())
        cls.raw = cls.man.read_bytes()

    def test_frozen_manifest_is_golden(self):
        errs, info = build_corpus.verify("v1")
        self.assertEqual(errs, [])
        self.assertEqual(info["items"], 30)

    def test_distribution_is_exact(self):
        self.assertEqual(self.doc["distribution"], build_corpus.DISTRIBUTION)
        self.assertEqual(sum(build_corpus.DISTRIBUTION.values()), 30)

    def test_thirty_unique_pending_sources(self):
        urls = [row["url"] for row in self.doc["items"]]
        self.assertEqual(len(urls), 30)
        self.assertEqual(len(set(urls)), 30)
        counts: dict[str, int] = {}
        for row in self.doc["items"]:
            counts[row["provider"]] = counts.get(row["provider"], 0) + 1
        self.assertEqual(counts, build_corpus.DISTRIBUTION)
        self.assertEqual({r["retrieval_status"] for r in self.doc["items"]},
                         {"PENDING"})

    def test_a37_discipline_is_on_every_row(self):
        for row in self.doc["items"]:
            self.assertEqual(row["claim_class"], "PENDING")
            self.assertEqual(row["policy_effect"], "NONE")
        for rule in ("rule_a37", "rule_a34", "rule_a36"):
            self.assertIn(rule, self.doc["policy"])
        self.assertIn("policy", self.doc["policy"]["rule_a37"].lower())
        self.assertIn("TRANSCRIPT_HYPOTHESIS",
                      self.doc["policy"]["claim_classes"])
    def test_a36_gaps_are_mechanism_keyed_not_popularity(self):
        gaps = self.doc["mechanism_gaps"]
        self.assertGreaterEqual(len(gaps), 4)
        for g in gaps:
            self.assertTrue(g["mechanism"].strip())
            self.assertTrue(g["candidate_source_author"].strip())
            self.assertEqual(g["selection_status"], "KEYED_PENDING_SOURCE")
            self.assertNotIn("url", g)  # no invented practitioner URLs

    def test_retrieval_is_an_open_named_step(self):
        item = self.doc["open_items"][0]
        self.assertIn("OPEN", item["status"])
        self.assertIn("build_store.put_source_document",
                      item["command_when_approved"])
        # and the freeze itself fetched nothing — no transcript payload on
        # any row, only the discipline text at the policy layer:
        self.assertNotIn("transcript",
                         json.dumps(self.doc["items"]).lower())

    def test_no_verb_rewrites_a_frozen_manifest(self):
        with self.assertRaises(build_corpus.CorpusFreezeError):
            build_corpus.freeze("v1")          # frozen: refuses
        with self.assertRaises(build_corpus.CorpusFreezeError):
            build_corpus.freeze("v2")          # no auto-copy re-freeze

    def test_verify_goes_red_on_planted_tamper_then_green(self):
        # plant-failure doctrine: the golden check must catch a smuggled
        # non-PENDING status, and pass again untouched.
        tampered = copy.deepcopy(self.doc)
        tampered["items"][0]["retrieval_status"] = "FETCHED"
        tampered["items"][0]["claim_class"] = "VERIFIED_PROCEDURE"
        tmp = tempfile.mkdtemp()
        try:
            fake = __import__("pathlib").Path(tmp) / "corpus"
            fake.mkdir()
            payload = json.dumps(tampered, indent=1, sort_keys=True) + "\n"
            (fake / "manifest-v1.json").write_text(payload)
            sha = __import__("hashlib").sha256(payload.encode()).hexdigest()
            (fake / "manifest-v1.sha256").write_text(
                f"{sha}  manifest-v1.json  items=30\n")
            errs, _ = _verify_against(fake, "v1")
            self.assertTrue(any("PENDING" in e for e in errs), errs)
        finally:
            shutil.rmtree(tmp)
        # untouched tree still green (the planted case never leaked):
        errs, _ = build_corpus.verify("v1")
        self.assertEqual(errs, [])

    def test_sidecar_binding_follows_golden_pattern(self):
        line = self.man.with_suffix(".sha256").read_text().strip()
        m = build_corpus.MANIFEST_RX.match(line)
        self.assertIsNotNone(m)
        import hashlib
        self.assertEqual(m.group(1), hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(m.group(2), "manifest-v1.json")
        self.assertEqual(m.group(3), "30")


def _verify_against(corpus_dir, version):
    """Run the golden check with the corpus root redirected (tamper sandbox)."""
    real = build_corpus.CORPUS_DIR
    build_corpus.CORPUS_DIR = corpus_dir
    try:
        return build_corpus.verify(version)
    finally:
        build_corpus.CORPUS_DIR = real


if __name__ == "__main__":
    unittest.main()
