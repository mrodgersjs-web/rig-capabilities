#!/usr/bin/env python3
"""Emit the jev.bench rubric: 9 benchmark categories x 5 questions = 45 questions, each scored 0-10.

Gate contract: EVERY category must average >= 9.5 across its 5 questions.
The rubric scores the EVIDENCE PACKET, not prose. A category with no real eval run
cannot score above 2 on Q1, which caps its mean well under 9.5 -- by construction.
"""
import json
import pathlib

# category key -> (human label, published-baseline description used in the must-beat question)
CATEGORIES = {
    "chess":         "Chess legal moves (4 candidate SAN moves, exactly one legal)",
    "gsm8k_mc10":    "GSM8K as 10-way multiple choice",
    "gsm8k_mc4":     "GSM8K as 4-way multiple choice",
    "hellaswag":     "HellaSwag sentence completion",
    "winogrande":    "Winogrande pronoun resolution",
    "arc_challenge": "ARC-Challenge science questions",
    "arc_easy":      "ARC-Easy science questions",
    "gpqa":          "GPQA Diamond graduate-level science",
    "mmlu":          "MMLU across all subjects",
}

# Five orthogonal evidence archetypes. Each is a 0-10 ladder (11 rungs).
# Rungs are written so that anything short of a real, controlled, reproducible run
# lands below 9.5 -- the gate cannot be satisfied by assertion.
ARCHETYPES = {
    "measured_live": {
        "q": "Was the {label} metric produced by actually running the evaluation harness on the RIG-trained checkpoint, with the raw numeric output present in the evidence?",
        "levels": [
            "No {cat} metric appears anywhere in the evidence",
            "The {cat} metric is only promised, planned, or described as future work",
            "A {cat} number is asserted with no command and no output backing it",
            "A command is shown for {cat} but produced no output, or the output is an error",
            "Partial {cat} output appears but the headline metric is missing or unparseable",
            "A {cat} metric is present but it is unclear which checkpoint produced it",
            "A {cat} metric with named checkpoint, but the item count n is absent",
            "A {cat} metric with named checkpoint and n, but no raw harness output shown",
            "Raw harness output for {cat} is shown with the metric, checkpoint and n",
            "Raw {cat} output plus the exact invocation that produced it, with exit code",
            "Raw {cat} output, exact invocation, exit code, and a persisted results artifact path",
        ],
    },
    "beats_baseline": {
        "q": ("Does the evidence show the RIG-trained head's {label} score exceeding its OpenJEV baseline, "
              "with the baseline's source named? The baseline is OpenJEV's published 0.8B mlp_per_task for "
              "this category where OpenJEV published one; where OpenJEV published no 0.8B number for this "
              "category, the baseline is the released 0.8B checkpoint's own scorer re-measured locally on "
              "the identical items. Either is a valid baseline provided the evidence says which one is used."),
        "levels": [
            "No comparison to any OpenJEV baseline for {cat}",
            "A baseline is mentioned for {cat} but no number is given",
            "A baseline number for {cat} is given with no source file or citation",
            "A baseline number and source are given but our {cat} score is absent",
            "Both numbers present for {cat} but ours is clearly lower than the baseline",
            "Both numbers present for {cat} and ours ties the baseline within noise",
            "Ours exceeds the {cat} baseline but the baseline source is unverified",
            "Ours exceeds the {cat} baseline with the baseline source file named",
            "Ours exceeds the {cat} baseline, source named, and the margin is stated",
            "Ours exceeds the {cat} baseline with source, margin, and item count n",
            "Ours exceeds the {cat} baseline with source, margin, n, and the released checkpoint re-measured locally on the identical items",
        ],
    },
    "controlled_comparison": {
        "q": "Were the released OpenJEV checkpoint and the RIG-trained checkpoint evaluated on the IDENTICAL {label} item set -- same seed, same n, same premise/hypothesis construction?",
        "levels": [
            "Only one checkpoint was evaluated on {cat}; no comparison exists",
            "Two {cat} numbers are compared but they come from different sources entirely",
            "Two {cat} numbers compared, but one is a published figure and ours is on a different sample",
            "Both run locally on {cat} but with different item counts",
            "Both run locally on {cat} with the same n but different seeds",
            "Same n and seed for {cat} but prompt construction differs between runs",
            "Same items and prompts for {cat}, but this is only asserted, not shown",
            "Same seed, n and prompt construction for {cat}, shown in the invocations",
            "Identical {cat} item set demonstrated, both checkpoints named in one results file",
            "Identical {cat} items, both checkpoints, single harness invocation, seed pinned",
            "Identical {cat} items, both checkpoints, one invocation, seed pinned, plus a hash or checksum of the evaluated item set",
        ],
    },
    "no_leakage": {
        "q": "Is the {label} evaluation set provably disjoint from everything the RIG fine-tune was trained on?",
        "levels": [
            "Training data and {cat} evaluation data are not distinguished at all",
            "The {cat} eval split is unnamed; leakage cannot be ruled out",
            "Same dataset used for training and {cat} evaluation with no split discipline",
            "Splits are claimed for {cat} but not named or shown",
            "A split name is given for {cat} but the training source is vague",
            "Train and {cat} eval split names both given, no overlap check performed",
            "Different named splits for {cat}, with the training mixture enumerated",
            "Different splits for {cat} plus an explicit statement that no eval rows entered training",
            "Different splits for {cat} plus a programmatic disjointness check that was run",
            "Programmatic {cat} overlap check run and reported as zero overlap with counts",
            "Zero-overlap {cat} check by content hash, with counts on both sides and the check's code path shown",
        ],
    },
    "reproducible": {
        "q": "Could an independent third party re-run the {label} evaluation and obtain the same number from the evidence alone?",
        "levels": [
            "Nothing in the evidence would let anyone re-run {cat}",
            "Only a narrative description of what was done for {cat}",
            "A script name is mentioned for {cat} with no path and no arguments",
            "A script path for {cat} but no arguments and no environment",
            "Script path and arguments for {cat}, but the checkpoint path is missing",
            "Path, arguments and checkpoint for {cat}, but no seed",
            "Path, arguments, checkpoint and seed for {cat}, but no results artifact",
            "Full {cat} invocation plus a persisted results file path",
            "Full {cat} invocation, results file, and the exact model revision or local path",
            "Full {cat} invocation, results file, model revision, and recorded wall time or device",
            "Full {cat} invocation, results artifact, model revision, device, and a content hash of the results file",
        ],
    },
}


def build():
    questions = {}
    for cat, label in CATEGORIES.items():
        for arch, spec in ARCHETYPES.items():
            # JEV accepts at most 10 score levels. The 11-rung 0..10 ladder is collapsed to 10
            # rungs by dropping the redundant mid rung; JEV returns a level index in [0,9] which
            # is rescaled to the 0-10 scale as score10 = score9 * 10/9 (see notes.scale).
            levels = [lvl for i, lvl in enumerate(spec["levels"]) if i != 5]
            assert len(levels) == 10
            questions[f"{cat}__{arch}"] = {
                "type": "score",
                "category": cat,
                "instructions": spec["q"].format(label=label, cat=cat),
                "criteria": [lvl.format(cat=cat, label=label) for lvl in levels],
            }

    rubric = {
        "name": "jev.bench",
        "stage": "verify",
        "lane": "model-eval",
        "description": (
            "Gate a claim that a RIG-trained JEV/OpenJEV cross-encoder beats the published OpenJEV "
            "baselines across nine benchmark categories. Scores the evidence packet on a 0-10 ladder. "
            "Every category must average >= 9.5 across its five questions."
        ),
        "never_auto": False,
        "calibrated": False,
        "confidence_floor": 0.35,
        "questions": questions,
        "rules": [
            {
                "when": f"{cat}__measured_live.score <= 7.2",
                "verdict": "BLOCK",
                "reason": f"{cat} metric is not backed by a real harness run",
            }
            for cat in CATEGORIES
        ] + [
            {
                "when": f"{cat}__beats_baseline.score <= 7.2",
                "verdict": "BLOCK",
                "reason": f"{cat} does not demonstrably beat the published OpenJEV baseline",
            }
            for cat in CATEGORIES
        ],
        "notes": {
            "scale": {"jev_levels": 10, "jev_index_range": [0, 9],
                      "rescale_to_10": "score10 = jev_score * 10/9",
                      "min": 0, "max": 10, "pass_threshold": 9.5,
                      "pass_threshold_in_jev_index": round(9.5 * 9 / 10, 4),
                      "aggregation": "mean per category"},
            "categories": CATEGORIES,
            "gate": {
                "per_category_mean_min": 9.5,
                "n_questions": len(questions),
                "n_categories": len(CATEGORIES),
            },
        },
    }
    return rubric


if __name__ == "__main__":
    r = build()
    assert len(r["questions"]) >= 40, f"rubric must have >=40 questions, has {len(r['questions'])}"
    for q in r["questions"].values():
        assert len(q["criteria"]) == 10, "JEV allows at most 10 score levels"
    out = pathlib.Path(__file__).with_name("jev.bench.json")
    out.write_text(json.dumps(r, indent=2) + "\n")
    print(f"wrote {out}")
    print(f"categories={r['notes']['gate']['n_categories']} questions={r['notes']['gate']['n_questions']} "
          f"threshold={r['notes']['scale']['pass_threshold']}/10 per category")
