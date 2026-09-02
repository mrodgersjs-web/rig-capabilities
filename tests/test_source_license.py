"""Licence enforcement for scraped corpora.

Three claims, all checkable without network or a model:

1. No creator-owned text (transcripts, captions, uploader metadata) is TRACKED by git.
   Checked against the index rather than .gitignore, because the index is what a clone
   receives and ignore files drift out of sync far more often than people notice.
2. The corpus directories are ignored, so a careless `git add .` cannot stage them.
3. The provenance and licence documents the scraper's docstring points at actually
   exist, so that reference cannot rot into a lie.

Plant-failure regression (see module bottom): staging a transcript under a corpus path
must turn this file red; unstaging must turn it green again.
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Anything whose words belong to a creator, not to RIG.
BAD_TRACKED = re.compile(
    r"(?:^|/)\.context/.*(?:transcripts?|raw|descriptions?)/"
    r"|\.(?:vtt|srt)$"
    r"|\.info\.json$"
)

DOCS = ("docs/CORPUS-DISCOVER-AI.md", "docs/SOURCE-LICENSE.md")


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True).stdout


class SourceLicenceTests(unittest.TestCase):
    def test_no_creator_text_is_tracked(self):
        tracked = _git("ls-files").splitlines()
        bad = [p for p in tracked if BAD_TRACKED.search(p)]
        self.assertEqual(
            bad, [],
            "creator-owned caption/transcript text is in git; keep it under "
            ".context/ (untracked) per docs/SOURCE-LICENSE.md")

    def test_corpus_dirs_are_ignored(self):
        probe = ".context/discover-ai/transcripts/probe.txt"
        rc = subprocess.run(["git", "-C", str(REPO), "check-ignore", "-q", probe],
                            capture_output=True).returncode
        self.assertEqual(rc, 0, f"{probe} is not gitignored — `git add .` would "
                                "capture a creator's transcript")

    def test_referenced_docs_exist(self):
        for d in DOCS:
            self.assertTrue((REPO / d).is_file(), f"{d} missing; the scraper docstring "
                                                  "and this suite both point at it")

    def test_docs_state_the_two_rules_that_matter(self):
        lic = (REPO / "docs/SOURCE-LICENSE.md").read_text(encoding="utf-8")
        self.assertIn("no_captions", lic)          # the string the tool really reports
        self.assertIn("members_only", lic)         # membership content is named, not hedged
        self.assertTrue("no code path" in lic.lower() or "no attempt" in lic.lower(),
                        "the paywall rule must be an explicit refusal, not a suggestion")
        self.assertIn("licence", lic.lower(),
                      "third-party code needs its licence named before any vendoring")
        prov = (REPO / "docs/CORPUS-DISCOVER-AI.md").read_text(encoding="utf-8")
        self.assertRegex(prov, r"27 of 27|27/27|27 ids|27 arXiv",
                         "the arXiv verification count must be stated")
        self.assertIn("YuqiChen4188", prov,
                      "the fabricated repo must stay named in the record")

    def test_scraper_docstring_reference_is_true(self):
        src = (REPO / "scripts/scrape_channel_corpus.py").read_text(encoding="utf-8")
        head = src[: src.find('"""', 3)]
        for ref in re.findall(r"docs/[A-Z0-9-]+\.md", head):
            self.assertTrue((REPO / ref).is_file(),
                            f"docstring points at {ref}, which does not exist")


if __name__ == "__main__":
    unittest.main()
