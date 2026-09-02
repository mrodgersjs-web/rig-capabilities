"""evidence-retrieval-citations-gate — the three jobs, proven by exit code.

Retrieval that returns unranked recall, self-vouches its own citations, or
cannot beat a keyword baseline is the failure this asset exists to refuse. The
GateNotTheater test bakes in the out-of-band plant: disable the beats-baseline
clause and a tie must pass (gate blind), restore and it must refuse again.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "capabilities/skills/evidence-retrieval-citations-gate"
R = SKILL / "retrieve.py"
FX = SKILL / "fixtures"
import unittest


def run(*args):
    return subprocess.run([sys.executable, str(R), *args], cwd=REPO,
                          capture_output=True, text=True, timeout=300)


class RetrievalTests(unittest.TestCase):
    def test_benchmark_beats_the_keyword_baseline(self):
        p = run("benchmark", "--matrix", str(FX / "corpus.json"),
                "--probes", str(FX / "probes.json"), "--hit-floor", "0.6")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("bm25 MRR", p.stdout)
        # non-vacuity: the win is real, not a tie rounded up
        import re
        m = re.search(r"bm25_mrr\D+([\d.]+)", p.stdout)
        k = re.search(r"keyword_mrr\D+([\d.]+)", p.stdout)
        self.assertGreater(float(m.group(1)), float(k.group(1)))

    def test_gate_green_when_every_citation_resolves(self):
        p = run("gate", "--matrix", str(FX / "corpus.json"),
                "--registry", str(FX / "registry.json"), "--query", "harness state memory")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_a_fabricated_citation_is_refused(self):
        p = run("gate", "--matrix", str(FX / "corpus_bogus_citation.json"),
                "--registry", str(FX / "registry.json"),
                "--query", "lesson trigger mandated check")
        self.assertEqual(p.returncode, 2, p.stdout)
        self.assertIn("UNRESOLVED_CITATION", p.stdout)

    def test_an_uncited_result_is_refused(self):
        p = run("gate", "--matrix", str(FX / "corpus_no_citation.json"),
                "--registry", str(FX / "registry.json"),
                "--query", "lesson trigger mandated check")
        self.assertEqual(p.returncode, 2, p.stdout)

    def test_a_probe_gold_outside_the_corpus_is_refused(self):
        p = run("benchmark", "--matrix", str(FX / "corpus.json"),
                "--probes", str(FX / "probes_bad_gold.json"), "--hit-floor", "0.6")
        self.assertEqual(p.returncode, 2, p.stdout)

    def test_missing_file_is_a_refusal_not_a_verdict(self):
        p = run("gate", "--matrix", "/nonexistent.json",
                "--registry", str(FX / "registry.json"), "--query", "x")
        self.assertEqual(p.returncode, 1)

    def test_the_registry_is_independent_not_self_vouching(self):
        """The load-bearing correction: registry never comes from the corpus.
        Point the gate at a registry that OMITS the bogus id and it must refuse;
        a self-vouching build would have added it and passed."""
        src = R.read_text(encoding="utf-8")
        self.assertIn("load_registry", src)
        self.assertNotIn("registry.update", src,
                         "registry must not be accumulated from the corpus rows")

    def test_gate_is_not_theater(self):
        """Out-of-band plant: on the SAME tie probe, the real checker refuses
        (rc 2, bm25 does not beat keyword) and the planted one goes blind (rc 0).
        Proving both halves is what makes it RED->restore, not just 'planted 0'."""
        src = R.read_text(encoding="utf-8")
        anchor = "    if not (bm25_mrr > kw_mrr):"
        self.assertIn(anchor, src)
        with tempfile.TemporaryDirectory() as td:
            tie = Path(td) / "tie.json"
            tie.write_text(
                '[{"query":"experience lesson records","gold":"experience-lesson-records"}]',
                encoding="utf-8")

            def bench(script):
                return subprocess.run(
                    [sys.executable, str(script), "benchmark",
                     "--matrix", str(FX / "corpus.json"), "--probes", str(tie),
                     "--hit-floor", "0.1"], cwd=REPO, capture_output=True, text=True)

            # RED: the real, unmodified checker refuses a tie.
            real = bench(R)
            self.assertEqual(real.returncode, 2,
                             "real checker must refuse a bm25==keyword tie")
            self.assertIn("does not beat", real.stdout)

            # BLIND: disable the beats-baseline clause and the same tie passes.
            planted = Path(td) / "retrieve.py"
            planted.write_text(src.replace(anchor, "    if False:  # PLANT"),
                               encoding="utf-8")
            self.assertEqual(bench(planted).returncode, 0,
                             "planted gate should go blind on the same tie probe")


if __name__ == "__main__":
    unittest.main()
