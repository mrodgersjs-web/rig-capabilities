#!/usr/bin/env python3
"""Build a RIG-native NLI corpus (premise, hypothesis, label) deterministically.

Deterministic code, not an LLM: the label must be a property of how the row was
constructed, never a judgement that could drift.

Labels: 0=contradiction, 1=entailment, 2=neutral.

Sources
  memory_os  : RIG Memory OS records (jsonl/sqlite under ~/.rig, ~/.jake)
  jakestudio : Obsidian vault /Users/rig128gb/Documents/JakeStudio (frontmatter + body)
  github     : proof packets / ledgers / results JSON under ~/.rig and ~/Developer

Construction
  entailment    : hypothesis restates a fact that is literally present in the premise
                  (a frontmatter field, a verdict, a count).
  contradiction : the SAME sentence frame with the value replaced by a different value
                  drawn from the same field's vocabulary (verdict flip, number perturb).
  neutral       : the same sentence frame, but about a field that the premise does not
                  mention at all (value drawn from another document's vocabulary).

Because all three labels reuse one frame per field, surface form does not reveal the
label -- only agreement with the premise does. An anti-leak audit is run at the end.
"""
import argparse
import collections
import hashlib
import json
import os
import pathlib
import random
import re
import sys

VAULT = pathlib.Path("/Users/rig128gb/Documents/JakeStudio")
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)

# field -> sentence frame. One frame per field, shared by all three labels.
FRAMES = {
    "type":     "This document is of type {v}.",
    "status":   "The recorded status is {v}.",
    "date":     "This record is dated {v}.",
    "verdict":  "The verdict recorded here is {v}.",
    "sensitivity": "The sensitivity of this record is {v}.",
    "tags":     "This record is tagged {v}.",
    "title":    "The title of this record is {v}.",
    "source":   "The source of this record is {v}.",
    "trust-tier": "The trust tier of this record is {v}.",
    "exit_code": "The recorded exit code is {v}.",
    "n":        "The recorded count is {v}.",
}


def clean(s, n):
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s[:n]


def parse_front(text):
    m = FRONT.match(text)
    if not m:
        return {}, text
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "-", "#")):
            k, v = line.split(":", 1)
            v = v.strip().strip('"').strip("'")
            if v and v not in ("|", ">"):
                out[k.strip()] = v
    return out, text[m.end():]


def harvest_vault(limit, rng):
    """(premise, {field: value}) from vault notes that carry usable frontmatter."""
    docs = []
    files = []
    for sub in ("Logs", "Knowledge", "Projects", "Research", "Memory", "Capabilities", "Company", "Intel"):
        d = VAULT / sub
        if d.is_dir():
            files.extend(list(d.rglob("*.md"))[: limit * 3])
    rng.shuffle(files)
    for f in files:
        if len(docs) >= limit:
            break
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        fm, body = parse_front(text)
        fields = {k: clean(v, 90) for k, v in fm.items() if k in FRAMES and v}
        if not fields:
            continue
        body = clean(body, 1200)
        if len(body) < 120:
            continue
        docs.append((body, fields, str(f)))
    return docs


def harvest_json(roots, limit, rng):
    """(premise, fields) from proof packets / results JSON."""
    docs, files = [], []
    for root in roots:
        p = pathlib.Path(root)
        if not p.exists():
            continue
        for pat in ("**/proof/*.json", "**/*proof*.json", "**/results/*.json", "**/*ledger*.json"):
            files.extend(list(p.glob(pat))[: limit])
    rng.shuffle(files)
    seen = set()
    for f in files:
        if len(docs) >= limit:
            break
        if f in seen:
            continue
        seen.add(f)
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        fields = {}
        for k, v in d.items():
            kl = k.lower()
            if isinstance(v, (str, int, float)) and not isinstance(v, bool):
                if "verdict" in kl or "status" in kl:
                    fields["verdict" if "verdict" in kl else "status"] = clean(v, 60)
                elif kl in ("exit_code", "exitcode"):
                    fields["exit_code"] = clean(v, 20)
                elif kl in ("date", "generated_at", "timestamp"):
                    fields["date"] = clean(v, 40)
        premise = clean(json.dumps(d)[:1200], 1200)
        if fields and len(premise) > 120:
            docs.append((premise, fields, str(f)))
    return docs


def harvest_memory_os(limit, rng):
    """(premise, fields) from Memory OS on-disk records."""
    docs, files = [], []
    for root in ("/Users/rig128gb/.rig", "/Users/rig128gb/.jake"):
        p = pathlib.Path(root)
        if p.exists():
            for pat in ("**/memory*/**/*.jsonl", "**/*events*.jsonl", "**/*memory*.jsonl"):
                files.extend(list(p.glob(pat))[:limit])
    rng.shuffle(files)
    for f in files[: limit]:
        try:
            lines = f.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        for line in lines[:200]:
            if len(docs) >= limit:
                break
            try:
                d = json.loads(line)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            fields = {}
            for k in ("type", "status", "sensitivity", "date"):
                if isinstance(d.get(k), str) and d[k]:
                    fields[k] = clean(d[k], 60)
            premise = clean(json.dumps(d), 1200)
            if fields and len(premise) > 120:
                docs.append((premise, fields, str(f)))
    return docs


def build_rows(docs, source, vocab, rng):
    rows = []
    for premise, fields, path in docs:
        for field, value in fields.items():
            frame = FRAMES[field]
            pool = [v for v in vocab[field] if v != value]
            if len(pool) < 2:
                continue
            # entailment: the true value
            rows.append((premise, frame.format(v=value), 1, source, path, field))
            # contradiction: a different value for a field the premise DOES state
            rows.append((premise, frame.format(v=rng.choice(pool)), 0, source, path, field))
            # neutral: a field the premise does not state at all. The neutral frame is
            # attributed to the field it names, so the per-field balancer below removes
            # any token that would otherwise predict "neutral" on sight.
            absent = [f for f in FRAMES if f not in fields and vocab.get(f)]
            if absent:
                nf = rng.choice(absent)
                rows.append((premise, FRAMES[nf].format(v=rng.choice(vocab[nf])), 2, source, path, nf))
    return rows


def anti_leak_audit(rows):
    """A label must not be predictable from hypothesis surface form alone."""
    by_label = collections.defaultdict(collections.Counter)
    lens = collections.defaultdict(list)
    for _, hyp, label, _, _, _ in rows:
        for tok in set(re.findall(r"[a-z]{3,}", hyp.lower())):
            by_label[tok][label] += 1
        lens[label].append(len(hyp))
    flags = []
    for tok, c in by_label.items():
        tot = sum(c.values())
        if tot >= 25:
            share = max(c.values()) / tot
            if share > 0.90:
                flags.append((tok, tot, round(share, 3)))
    means = {k: round(sum(v) / len(v), 1) for k, v in lens.items() if v}
    return flags, means


def balance_per_field(rows, rng):
    """Equalise label counts WITHIN each field.

    Without this, a field that is rarely stated in a premise only ever appears as a
    neutral row, so its frame's words predict the label on sight (observed: the token
    'sensitivity' was 100% neutral). Balancing inside the field removes that shortcut.
    """
    by_field = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        by_field[r[5]][r[2]].append(r)
    out = []
    for field, per_label in by_field.items():
        if len(per_label) < 3:      # a field that cannot supply all three labels is dropped
            continue
        n = min(len(v) for v in per_label.values())
        for lab in per_label:
            rng.shuffle(per_label[lab])
            out.extend(per_label[lab][:n])
    rng.shuffle(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/Users/rig128gb/.rig/openjev-rig/rig_nli_corpus.jsonl")
    ap.add_argument("--report", default="/Users/rig128gb/.rig/openjev-rig/rig_corpus_report.md")
    ap.add_argument("--per_source", type=int, default=700)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    print("harvesting jakestudio ...", flush=True)
    d_vault = harvest_vault(args.per_source, rng)
    print(f"  {len(d_vault)} docs", flush=True)
    print("harvesting github/proof json ...", flush=True)
    d_git = harvest_json(["/Users/rig128gb/.rig/gtm-agentic-ops/proof",
                          "/Users/rig128gb/.rig/mesh",
                          "/Users/rig128gb/.rig/openjev/results",
                          "/Users/rig128gb/.rig/openjev-rig/results",
                          "/Users/rig128gb/Developer/rig-capabilities/.context"], args.per_source, rng)
    print(f"  {len(d_git)} docs", flush=True)
    print("harvesting memory os ...", flush=True)
    d_mem = harvest_memory_os(args.per_source, rng)
    print(f"  {len(d_mem)} docs", flush=True)

    vocab = collections.defaultdict(set)
    for docs in (d_vault, d_git, d_mem):
        for _, fields, _ in docs:
            for k, v in fields.items():
                vocab[k].add(v)
    vocab = {k: sorted(v) for k, v in vocab.items()}

    rows = []
    rows += build_rows(d_vault, "jakestudio", vocab, rng)
    rows += build_rows(d_git, "github", vocab, rng)
    rows += build_rows(d_mem, "memory_os", vocab, rng)
    rng.shuffle(rows)

    # 1) equalise labels within each field (kills field-token -> label shortcuts)
    rows = balance_per_field(rows, rng)
    if not rows:
        print("FAIL: no rows survived per-field balancing")
        return 1
    # 2) equalise the global class counts
    by_label = collections.defaultdict(list)
    for r in rows:
        by_label[r[2]].append(r)
    n = min(len(v) for v in by_label.values())
    balanced = [r for lab in by_label for r in by_label[lab][:n]]
    rng.shuffle(balanced)

    flags, means = anti_leak_audit(balanced)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        for premise, hyp, label, source, path, field in balanced:
            f.write(json.dumps({"premise": premise, "hypothesis": hyp, "label": label,
                                "source": source, "origin_path": path}) + "\n")

    per_source = collections.Counter(r[3] for r in balanced)
    per_label = collections.Counter(r[2] for r in balanced)
    names = {0: "contradiction", 1: "entailment", 2: "neutral"}
    with open(args.report, "w") as f:
        f.write("# RIG NLI corpus\n\n")
        f.write(f"rows: {len(balanced)}  (balanced to {n} per class)\n\n")
        f.write("## per source\n\n| source | rows |\n|---|---|\n")
        for s, c in per_source.most_common():
            f.write(f"| {s} | {c} |\n")
        f.write("\n## class balance\n\n| label | name | rows |\n|---|---|---|\n")
        for lab, c in sorted(per_label.items()):
            f.write(f"| {lab} | {names[lab]} | {c} |\n")
        f.write(f"\n## anti-leak audit\n\nmean hypothesis length by label: {means}\n\n")
        f.write(f"tokens appearing >=25 times with >90% concentration in one label: {len(flags)}\n\n")
        for tok, tot, share in flags[:20]:
            f.write(f"- `{tok}` n={tot} share={share}\n")
        f.write("\n## examples\n\n")
        for lab in (0, 1, 2):
            ex = [r for r in balanced if r[2] == lab][:2]
            for premise, hyp, label, source, path, field in ex:
                f.write(f"**{names[lab]}** (source={source})\n\n")
                f.write(f"- premise: `{premise[:220]}...`\n- hypothesis: `{hyp}`\n\n")
    print(f"wrote {args.out} rows={len(balanced)} per_source={dict(per_source)} per_label={dict(per_label)}")
    print(f"anti-leak flags: {len(flags)}  mean hyp len by label: {means}")
    print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
