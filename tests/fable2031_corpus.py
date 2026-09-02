"""P2 corpus tests: manifest-first selection, dedup, structural truncation, refusal seam.

Fixture arithmetic for tests/fixtures/fable2031/corpus/ (kept explicit, never implied):

    raw files            22
    unique card keys     20   = 22 - 1 duplicate copy - 1 contradiction copy
    classified           19
    unclassified          1   -> unclassified_rate = 1 / 20 = 0.05  (halt 0.10)
    truncated             1   -> the fuel-budget card, unterminated table at `| App |`
    duplicates            1   -> "rig weekly convergence scorecard", byte-equal, two names
    contradiction variants 1  -> "20-scrutineering-loop-notes", same key, divergent body

The denominator is the unique cards actually scanned — never "~453 Build Cards".

`TruncationLedgerTests` is the cross-check the plan's P2 migration clause demands: P1's
`docs/TRUNCATED-SOURCES.md` and P2's `data/fable2031/source_inventory.json` must agree about all
three truncations in both directions, and the anchors they agree on must be what the
`detect_truncation` rule itself returns. Repo files only — `~/Downloads` is never opened.
"""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
FIX = REPO_ROOT / "tests" / "fixtures" / "fable2031"

from rig_capabilities.corpus import (  # noqa: E402
    CORPUS_ROOTS, SOURCE_MANIFEST, UNCLASSIFIED_HALT_RATE, CorpusRefusal,
    assert_scorable, card_key, classify, corpus_report, detect_truncation,
    gate_corpus_refusal, load_rules, normalize_title, scan_corpus)

CORPUS = FIX / "corpus"
GATE_FIXTURE = FIX / "corpus-manifest.json"

# the nine real cards, by their verbatim frontmatter titles — asserted against the
# committed rules so a rule edit that drops a card fails here, without reading ~/Downloads
NINE_TITLES = {
    "PROMPT PACK — Full-Corpus Scrape → Grok Extraction → Fable 5.1 Capability Map (2031 Design Chain)":
        ("navigation", "Strategy", "workflow"),
    "Claude Fable 5.1 — RIG Fleet Install, Routing Policy & Breaking-Change Audit (shipped Sept 1, 2026)":
        ("powertrain", "App", "doctrine"),
    "BUILD CARD — RIG Realign Loop v1: Weekly Strategy → Research → Design → Execution → Learnings with Convergence Scoring":
        ("transmission", "Strategy", "harness"),
    "RIG CAPABILITY CRITERIA & 2031 ROADMAP — The M0–M5 Ladder, Register Schema, Weight Tiers & Phase Gates (v1)":
        ("scrutineering", "Strategy", "doctrine"),
    "RIG 1000x CAR v2 — The Forward-Deployed Chassis: Every Subsystem Turned Outward + Scrutineering as the Commercial Object":
        ("chassis", "CompanyOSFactory", "offer"),
    "RIG GAP REGISTER v1 — Every Missing Capability, Ranked by Blast Radius × Revenue Proximity (Worst-Harness-First Fix Order)":
        ("shocks", "GTM", "dataset"),
    "PROMPT — Grok Dispatcher System Prompt (Anti-Fabrication, Worktree-Leased, Canary-Gated) v1":
        ("seatbelts", "App", "workflow"),
    "RIG ANTI-FABRICATION HARNESS — Grok Dispatcher Protocol: Worktree Leases, Canary Lie-Detection & Reproducibility-as-Truth (v1)":
        ("seatbelts", "App", "harness"),
    "RIG Known Expert OS — 12-Phase Master Prompt for a Forward-Deployed AI Strategist & Engineer":
        ("steering", "GTM", "harness"),
}


class _Repo:
    """Stand-in for catalog.Repo — the gate only ever wants `.root`."""

    def __init__(self, root: Path) -> None:
        self.root = root


def _copy_corpus(root: Path) -> Path:
    dst = root / "corpus"
    shutil.copytree(CORPUS, dst)
    return dst


def _unclassify(card_path: Path, title: str) -> None:
    """Overwrite a copied card so no rule can reach it — title and tags both neutral."""
    card_path.write_text(f'---\ntitle: {title}\ntags:\n  - "Build Cards"\n'
                         f'  - "personal/baking"\n---\n\n## Note\nNothing here resembles '
                         f'a RIG subsystem, studio, or artifact type.\n', encoding="utf-8")


class CorpusTests(unittest.TestCase):
    maxDiff = None

    # ------------------------------------------------------------- the fixture scan

    def test_scan_numbers_are_the_stated_arithmetic(self):
        scan = scan_corpus(roots=CORPUS)
        self.assertEqual(22, scan["raw"])
        self.assertEqual(20, scan["unique"])
        self.assertEqual(1, len(scan["duplicates"]))
        self.assertEqual(1, len(scan["contradiction_variants"]))
        # the identity that makes the counts reviewable
        self.assertEqual(scan["raw"],
                         scan["unique"] + len(scan["duplicates"])
                         + len(scan["contradiction_variants"]))
        self.assertEqual(20, len(scan["cards"]))
        self.assertEqual(1, sum(1 for c in scan["cards"] if c["truncated"]))
        for card in scan["cards"]:
            for field in ("key", "path", "sha256", "bytes", "truncated", "in_manifest"):
                self.assertIn(field, card)

    def test_card_keys_are_unique_after_collapsing(self):
        scan = scan_corpus(roots=CORPUS)
        keys = [c["key"] for c in scan["cards"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_duplicate_pair_collapses_to_one_card(self):
        scan = scan_corpus(roots=CORPUS)
        dup = scan["duplicates"][0]
        self.assertEqual("rig weekly convergence scorecard", dup["key"])
        self.assertEqual(64, len(dup["sha256"]))
        # both filenames exist, one card comes out, and the bytes were identical
        paths = sorted(p.name for p in CORPUS.glob("*convergence-scorecard*"))
        self.assertEqual(2, len(paths))
        kept = Path(dup["kept"])
        self.assertEqual(Path(dup["path"]).read_bytes(), kept.read_bytes())
        cards = {c["key"]: c for c in scan["cards"]}
        self.assertEqual(kept.name, Path(cards[dup["key"]]["path"]).name)

    def test_contradiction_variant_is_reported_separately_from_duplicates(self):
        scan = scan_corpus(roots=CORPUS)
        conflict = scan["contradiction_variants"][0]
        self.assertEqual("20-scrutineering-loop-notes", conflict["key"])
        self.assertNotEqual(conflict["sha256"], conflict["kept_sha256"])
        self.assertNotIn(conflict["path"], [d["path"] for d in scan["duplicates"]])
        # the surviving card is the longer body, and the variant count is not folded in
        cards = {c["key"]: c for c in scan["cards"]}
        self.assertEqual(20, len(cards))
        self.assertEqual(2, len(cards["20-scrutineering-loop-notes"]["variants"]))
        # a byte-equal key has one body hash, a contradicting key has two
        self.assertEqual(1, len(cards["rig weekly convergence scorecard"]["variants"]))
        kept = Path(cards["20-scrutineering-loop-notes"]["path"])
        self.assertGreater(kept.stat().st_size, Path(conflict["path"]).stat().st_size)

    def test_primary_selection_prefers_longest_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body_short = ("## Note\nShorter statement of the same intent.\n")
            body_long = ("## Note\nLonger statement of the same intent, with the second\n"
                         "sentence carrying the detail that makes it the body to keep.\n")
            front = '---\ntitle: Kept Body Probe\ntags:\n  - "Build Cards"\n---\n\n'
            (root / "a-short.md").write_text(front + body_short, encoding="utf-8")
            (root / "b-long.md").write_text(front + body_long, encoding="utf-8")
            scan = scan_corpus(roots=root, manifest=None)
            self.assertEqual(2, scan["raw"])
            self.assertEqual(1, scan["unique"])
            self.assertEqual("b-long.md", Path(scan["cards"][0]["path"]).name)
            self.assertEqual("kept body probe", scan["cards"][0]["key"])

    def test_unclassified_rate_is_five_percent_and_ok(self):
        report = corpus_report(roots=CORPUS)
        self.assertEqual(22, report["raw"])
        self.assertEqual(20, report["unique"])
        self.assertEqual(19, report["classified"])
        self.assertEqual(1, report["unclassified"])
        self.assertEqual(0.05, report["unclassified_rate"])
        self.assertLessEqual(report["unclassified_rate"], UNCLASSIFIED_HALT_RATE)
        self.assertTrue(report["ok"])
        self.assertEqual(1, report["truncated"])
        self.assertIs(assert_scorable(report), report)

    def test_the_single_unclassifiable_card_is_honest_about_why(self):
        scan = scan_corpus(roots=CORPUS)
        verdicts = {c["key"]: classify(c) for c in scan["cards"]}
        loose = [k for k, v in verdicts.items() if v["unclassified"]]
        self.assertEqual(["sourdough hydration log"], loose)
        self.assertEqual("no_rule_matched", verdicts["sourdough hydration log"]["reason"])
        self.assertIsNone(verdicts["sourdough hydration log"]["subsystem"])
        for key, verdict in verdicts.items():
            if key == "sourdough hydration log":
                continue
            self.assertFalse(verdict["unclassified"], key)
            self.assertIn(verdict["studio"], {"Design", "App", "GTM", "LinkedIn",
                                              "Strategy", "CompanyOSFactory"})

    # ------------------------------------------------------------------ classification

    def test_all_nine_real_card_titles_classify(self):
        rules = load_rules()
        self.assertTrue(rules)
        for title, want in NINE_TITLES.items():
            got = classify({"title": title}, rules=rules)
            self.assertFalse(got["unclassified"], title)
            self.assertEqual(want, (got["subsystem"], got["studio"], got["type"]), title)

    def test_rules_json_uses_only_the_register_vocabularies(self):
        data = json.loads((REPO_ROOT / "data" / "fable2031" / "classify_rules.json")
                          .read_text(encoding="utf-8"))
        vocab = data["vocabularies"]
        for rule in data["rules"]:
            self.assertIn(rule["subsystem"], vocab["subsystems"], rule["id"])
            self.assertIn(rule["studio"], vocab["studios"], rule["id"])
            self.assertIn(rule["type"], vocab["types"], rule["id"])
            self.assertIn(rule["match"]["field"], ("title", "tags", "body"), rule["id"])
            self.assertTrue(rule["match"]["contains"], rule["id"])

    def test_source_inventory_lists_nine_cards_with_honest_anchors(self):
        data = json.loads((REPO_ROOT / SOURCE_MANIFEST).read_text(encoding="utf-8"))
        cards = data["cards"]
        self.assertEqual(9, len(cards))
        self.assertEqual(CORPUS_ROOTS, ("~/Downloads", "~/mnt/RIGLake"))
        truncated = [c for c in cards if c["status"] == "truncated_at_source"]
        self.assertEqual(3, len(truncated))
        for card in cards:
            self.assertEqual(64, len(card["sha256"]))
            self.assertGreater(card["bytes"], 0)
            self.assertIn(card["status"], ("complete", "truncated_at_source"))
            if card["status"] == "complete":
                self.assertIsNone(card["end_anchor"], card["id"])
            else:
                self.assertTrue(card["end_anchor"], card["id"])
        anchors = {c["id"]: c["end_anchor"] for c in truncated}
        self.assertEqual("| QNA |", anchors["prompt-pack-2031-chain"])
        self.assertIn("No capability register.", anchors["rig-gap-register-v1"])
        self.assertIn("Z", anchors["rig-gap-register-v1"])
        # the marker heading proves the cut; the bullet surviving under it is not the anchor
        self.assertEqual("## Sources", anchors["rig-known-expert-os-v1"])

    # --------------------------------------------------------------------- selection

    def test_manifest_membership_wins_over_tags(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # the tag trap: three of the nine cards carry no `Build Cards` tag
            untagged = root / "untagged-card.md"
            untagged.write_text('---\ntitle: Untagged Truncated Card\ntags: []\n---\n\n'
                                '## Source systems\n| System | Content |\n| --- | --- |\n'
                                '| QNA |\n', encoding="utf-8")
            tagged = root / "tagged-card.md"
            tagged.write_text('---\ntitle: Tagged Card\ntags:\n  - "Build Cards"\n---\n\n'
                              'Body that ends on a full sentence.\n', encoding="utf-8")
            tag_only = scan_corpus(roots=root, manifest=None)
            self.assertEqual(1, tag_only["raw"])
            self.assertEqual(["tagged card"], [c["key"] for c in tag_only["cards"]])

            inventory = root / "inventory.json"
            inventory.write_text(json.dumps(
                {"cards": [{"id": "u1", "path": str(untagged), "sha256": "0" * 64,
                            "bytes": untagged.stat().st_size,
                            "status": "truncated_at_source", "end_anchor": "| QNA |"}]}),
                encoding="utf-8")
            picked = scan_corpus(roots=root, manifest=inventory)
            self.assertEqual(2, picked["raw"])
            by_key = {c["key"]: c for c in picked["cards"]}
            self.assertTrue(by_key["untagged truncated card"]["in_manifest"])
            self.assertTrue(by_key["untagged truncated card"]["truncated"])
            self.assertFalse(by_key["tagged card"]["in_manifest"])

    def test_card_key_prefers_title_and_strips_copy_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            titled = Path(tmp) / "whatever.md"
            titled.write_text('---\ntitle: RIG Alpha   Card (v2)\n---\n\nBody.\n',
                              encoding="utf-8")
            self.assertEqual("rig alpha card (v2)", card_key(titled))
            copy = Path(tmp) / "RIG Beta Card (1).md"
            copy.write_text("Body with no frontmatter at all.\n", encoding="utf-8")
            self.assertEqual("rig beta card", card_key(copy))
            self.assertEqual("a - b -> c", normalize_title("A  —\tB → C"))

    # -------------------------------------------------------------------- truncation

    def test_detect_truncation_on_the_fixture_card(self):
        text = (CORPUS / "17-fuel-budget-sweep.md").read_text(encoding="utf-8")
        truncated, anchor = detect_truncation(text)
        self.assertTrue(truncated)
        self.assertEqual("| App |", anchor)

    def test_detect_truncation_covers_the_three_real_shapes(self):
        table = ("## Source systems to sweep\n| System | Content |\n| --- | --- |\n"
                 "| QNA |\n\n\n")
        self.assertEqual((True, "| QNA |"), detect_truncation(table))
        item = ("## Tier 1\n**1. First gap.**Body.\n\n**3. No capability register.**Z\n\n\n")
        truncated, anchor = detect_truncation(item)
        self.assertTrue(truncated)
        self.assertEqual("**3. No capability register.**Z", anchor)
        phase = ("# Phase 11 — Offering\n\n## Objective\nTranslate the validated "
                 "expertise into a bounded offer.\n\n\n## Sources\n- [website](x)\n")
        truncated, anchor = detect_truncation(phase)
        self.assertTrue(truncated)
        # a structural marker immediately after a mid-document cut IS the anchor
        self.assertEqual("## Sources", anchor)
        self.assertNotIn("website", anchor)

    def test_detect_truncation_does_not_invent_truncation(self):
        whole = ("## Purpose\nA finished card.\n\n## Kill criteria\n"
                 "- Nothing left to cut\n\n## Sources\n- [website](https://x.example/y)\n")
        self.assertEqual((False, ""), detect_truncation(""))
        self.assertEqual((False, "- [website](https://x.example/y)"),
                         detect_truncation(whole))
        # a table that closes properly is not a truncation
        closed = ("## Grid\n| A | B |\n| --- | --- |\n| 1 | 2 |\n\n## End\nDone.\n")
        self.assertFalse(detect_truncation(closed)[0])

    def test_only_one_fixture_card_is_truncated(self):
        scan = scan_corpus(roots=CORPUS)
        truncated = [c for c in scan["cards"] if c["truncated"]]
        self.assertEqual(["rig fuel budget sweep"], [c["key"] for c in truncated])
        self.assertEqual("| App |", truncated[0]["end_anchor"])
        for card in scan["cards"]:
            if not card["truncated"]:
                self.assertIsNone(card["end_anchor"], card["key"])

    # -------------------------------------------------------------------- refusal seam

    def test_empty_corpus_reports_a_reason_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "empty").mkdir()
            report = corpus_report(roots=Path(tmp) / "empty")
            self.assertEqual(0, report["unique"])
            self.assertFalse(report["ok"])
            self.assertEqual("empty_corpus", report["reason"])
            self.assertEqual(0.0, report["unclassified_rate"])
            with self.assertRaises(CorpusRefusal):
                assert_scorable(report)

    def test_missing_root_is_reported_and_never_deflates_the_rate(self):
        single = corpus_report(roots=CORPUS)
        report = corpus_report(roots=[CORPUS, "~/mnt/RIGLake-does-not-exist-2031"])
        self.assertEqual(2, len(report["roots"]))
        self.assertEqual({"root": str(CORPUS), "present": True, "cards": 22},
                         report["roots"][0])
        missing = [r for r in report["roots"] if not r["present"]]
        self.assertEqual(1, len(missing))
        self.assertEqual(0, missing[0]["cards"])
        # the absent root changes nothing about the arithmetic
        for field in ("raw", "unique", "classified", "unclassified",
                      "unclassified_rate", "truncated", "ok"):
            self.assertEqual(single[field], report[field], field)

    def test_planted_three_of_twenty_unclassified_turns_the_report_red(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = _copy_corpus(root)
            # 1 honest unclassifiable card + 2 planted = 3/20 = 0.15 > 0.10
            _unclassify(corpus / "11-harness-design-primer.md", "Zither Practice Notes")
            _unclassify(corpus / "13-rig-brand-signal-card.md", "Ferry Timetable Draft")
            report = corpus_report(roots=corpus)
            self.assertEqual(20, report["unique"])
            self.assertEqual(3, report["unclassified"])
            self.assertAlmostEqual(0.15, report["unclassified_rate"], places=6)
            self.assertFalse(report["ok"])
            self.assertEqual("unclassified_rate_exceeded", report["reason"])
            with self.assertRaises(CorpusRefusal):
                assert_scorable(report)
            # and the committed fixture is untouched by the plant
            self.assertTrue((CORPUS / "11-harness-design-primer.md").exists())
            self.assertIn("Harness Design",
                          (CORPUS / "11-harness-design-primer.md").read_text("utf-8"))

    # ------------------------------------------------------------------ hermetic gate

    def test_gate_green_on_the_committed_manifest(self):
        ok, detail = gate_corpus_refusal(_Repo(REPO_ROOT))
        self.assertTrue(ok)
        self.assertIn("rate=0.0500", detail)
        self.assertIn("1/20", detail)
        committed = json.loads(GATE_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(20, len(committed["cards"]))
        self.assertEqual(1, sum(1 for c in committed["cards"] if not c["classified"]))
        for entry in committed["cards"]:
            self.assertIsInstance(entry["classified"], bool)
        # the snapshot agrees with what a real scan of the same cards decides
        scan = scan_corpus(roots=CORPUS)
        verdicts = {c["key"]: not classify(c)["unclassified"] for c in scan["cards"]}
        self.assertEqual({c["key"]: c["classified"] for c in committed["cards"]}, verdicts)

    def test_gate_red_on_a_planted_manifest_without_mutating_the_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dst = root / "tests" / "fixtures" / "fable2031"
            dst.mkdir(parents=True)
            data = json.loads(GATE_FIXTURE.read_text(encoding="utf-8"))
            flips = 0
            for entry in data["cards"]:
                if entry["classified"] and flips < 2:
                    entry["classified"] = False
                    flips += 1
            (dst / "corpus-manifest.json").write_text(json.dumps(data), encoding="utf-8")
            ok, detail = gate_corpus_refusal(_Repo(root))
            self.assertFalse(ok)
            self.assertIn("rate=0.1500", detail)
            self.assertIn("3/20", detail)
            self.assertTrue(gate_corpus_refusal(_Repo(REPO_ROOT))[0],
                            "the committed fixture must stay green")

    def test_gate_accepts_repo_shaped_str_and_path_and_never_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for repo in (_Repo(root), str(root), root):
                ok, detail = gate_corpus_refusal(repo)
                self.assertFalse(ok)
                self.assertIn("corpus_manifest_missing", detail)
            dst = root / "tests" / "fixtures" / "fable2031"
            dst.mkdir(parents=True)
            (dst / "corpus-manifest.json").write_text('{"cards": []}', encoding="utf-8")
            self.assertEqual((False, "corpus_manifest_empty"),
                             gate_corpus_refusal(_Repo(root)))
            (dst / "corpus-manifest.json").write_text("{not json", encoding="utf-8")
            ok, detail = gate_corpus_refusal(_Repo(root))
            self.assertFalse(ok)
            self.assertIn("corpus_manifest_unreadable", detail)


# ------------------------------------------------------------------ truncation ledger
#
# P1's human ledger and P2's machine manifest must describe the SAME three cuts. The
# check below is bidirectional — a row in one and not the other fails — and reads two
# repo files plus inline transcriptions of the tails those files record. `~/Downloads`
# is never opened here (Law L1); the real-card check runs as a CLI command, not in the
# suite (Law L3).

INVENTORY = REPO_ROOT / SOURCE_MANIFEST
LEDGER_DOC = REPO_ROOT / "docs" / "TRUNCATED-SOURCES.md"

#: the plan's three pinned anchors — the acceptance values for `detect_truncation`
EXPECTED_ANCHOR = {
    "prompt-pack-2031-chain": "| QNA |",
    "rig-gap-register-v1": "**3. No capability register.**Z",
    "rig-known-expert-os-v1": "## Sources",
}

#: the fragments the GAP REGISTER ledger row names; the manifest anchor must carry both
GAP_FRAGMENTS = ("No capability register.", "Z")

#: one tail per truncated card, transcribed from `docs/TRUNCATED-SOURCES.md` →
#: "Observed tails", so each recorded anchor is derived from the rule rather than typed
#: in by hand. Card 9's tail keeps the surviving Sources bullet precisely so the test can
#: prove the rule reports the heading and not the bullet.
SHAPE_TAIL = {
    "prompt-pack-2031-chain": ("## Source systems to sweep\n| System | Content |\n"
                              "| --- | --- |\n| QNA |\n\n\n\n"),
    "rig-gap-register-v1": ("## Tier 1 — Structural. Blocks all monetization. (w = 5)\n"
                            "**1. First gap.**Body.\n\n**2. Second gap.**Body.\n\n"
                            "**3. No capability register.**Z\n\n\n\n"),
    "rig-known-expert-os-v1": ("# Phase 11 — Turn the system into the RIG offering\n\n"
                               "## Objective\nTranslate the validated expertise into a "
                               "bounded offer.\n\n\n## Sources\n- [website]"
                               "(https://www.youtube.com/watch?v=vl6GDCbMi4I)\n"),
}

_CELL_SPLIT = re.compile(r"(?<!\\)\|")
_BACKTICK = re.compile(r"`([^`]+)`")


def _span(cell: str) -> str:
    """The first backticked span of a ledger cell, else the cell itself."""
    found = _BACKTICK.search(cell)
    return found.group(1) if found else cell.strip()


def _path_of(cards: list[dict], card_id: str) -> str:
    """The ledger key (a card's source path) for one manifest id."""
    return next(c["path"] for c in cards if c["id"] == card_id)


def _ledger_rows(text: str) -> list[dict]:
    """The ledger table as [{column: cell}], honouring `\\|` escapes inside a cell."""
    rows: list[dict] = []
    header: list[str] | None = None
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in _CELL_SPLIT.split(stripped)][1:-1]
        if header is None:
            if "source_path" in cells:
                header = cells
            continue
        if cells and all(set(c) <= set("-:") for c in cells):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


class TruncationLedgerTests(unittest.TestCase):
    """The P1 ledger and the P2 manifest must name the same three cuts, both ways."""

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        cls.doc = LEDGER_DOC.read_text(encoding="utf-8")
        cls.rows = _ledger_rows(cls.doc)
        cls.truncated = [c for c in cls.inventory["cards"]
                         if c["status"] == "truncated_at_source"]
        cls.ledged = {_span(r["source_path"]): r for r in cls.rows}

    # ----------------------------------------------------------------- both directions

    def test_exactly_three_truncations_are_recorded_each_way(self):
        self.assertEqual(3, len(self.truncated), "the manifest records three truncations")
        self.assertEqual(3, len(self.rows), "the ledger records three truncations")
        self.assertEqual(6, sum(1 for c in self.inventory["cards"]
                                if c["status"] == "complete"))

    def test_every_manifest_truncation_has_a_ledger_row(self):
        for card in self.truncated:
            self.assertIn(card["path"], self.ledged,
                          f"{card['id']}: truncated in the manifest, missing from the ledger")

    def test_every_ledger_row_is_a_manifest_truncation(self):
        booked = {c["path"] for c in self.truncated}
        for path in self.ledged:
            self.assertIn(path, booked,
                          "the ledger claims a truncation the manifest does not carry")
        # a complete card must never show up in the ledger
        for card in self.inventory["cards"]:
            if card["status"] == "complete":
                self.assertNotIn(card["path"], self.ledged, card["id"])

    # ---------------------------------------------------------------- anchor agreement

    def test_end_anchor_cells_agree_with_the_manifest(self):
        self.assertEqual({c["path"] for c in self.truncated}, set(self.ledged))
        for card in self.truncated:
            self.assertEqual(card["end_anchor"], _span(self.ledged[card["path"]]["end_anchor"]),
                             f"{card['id']}: ledger anchor disagrees with the manifest")

    def test_gap_register_row_carries_both_pinned_fragments(self):
        row = self.ledged[_path_of(self.truncated, "rig-gap-register-v1")]
        for fragment in GAP_FRAGMENTS:
            self.assertIn(fragment, _span(row["end_anchor"]),
                          f"the manifest anchor must name {fragment!r}")
            self.assertIn(fragment, row["end_anchor"],
                          f"the ledger row must name {fragment!r}")

    def test_known_expert_os_row_pins_the_marker_not_the_bullet(self):
        row = self.ledged[_path_of(self.truncated, "rig-known-expert-os-v1")]
        self.assertEqual("## Sources", _span(row["end_anchor"]))
        self.assertNotIn("youtube", row["end_anchor"].lower(),
                         "the surviving Sources bullet is not the anchor")
        for promised in ("Phase 11 body", "Phase 12 in full", "Gates 11 and 12"):
            self.assertIn(promised, row["missing_content"], promised)

    def test_the_rule_itself_produces_every_recorded_anchor(self):
        for card in self.truncated:
            truncated, anchor = detect_truncation(SHAPE_TAIL[card["id"]])
            self.assertTrue(truncated, card["id"])
            self.assertEqual(card["end_anchor"], anchor,
                             f"{card['id']}: manifest anchor is not what the rule returns")
            self.assertEqual(EXPECTED_ANCHOR[card["id"]], anchor, card["id"])

    # -------------------------------------------------------------------- byte agreement

    def test_bytes_cells_equal_the_manifest_bytes(self):
        for card in self.truncated:
            self.assertEqual(card["bytes"], int(self.ledged[card["path"]]["bytes"]), card["id"])

    # ------------------------------------------------------------------ QNA promotion ban

    def test_the_ledger_never_promotes_qna_and_says_so(self):
        self.assertNotIn("QNAP", self.doc,
                         "the token on disk is QNA; the promoted spelling may not appear")
        self.assertIn("`| QNA |`", self.doc, "the surviving anchor must be quoted verbatim")
        self.assertIn("## Synthesis prohibition", self.doc)
        for phrase in ("never \"corrected\" or promoted", "may ever be synthesised"):
            self.assertIn(phrase, self.doc, f"prohibition text missing: {phrase}")


if __name__ == "__main__":
    unittest.main()
