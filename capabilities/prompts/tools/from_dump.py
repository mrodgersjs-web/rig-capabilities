#!/usr/bin/env python3
"""from_dump.py — extract an AutoPrompt run's best prompt + full score history.

Run with the AutoPrompt venv (outside the Aside sandbox):
    ~/Developer/AutoPrompt/.venv/bin/python from_dump.py <dump_dir> [out.json]

Reads <dump_dir>/history.pkl (pickle written by optimization_pipeline.save_state)
and writes JSON: { best: {prompt, score, step}, steps, history: [...] }.
"""
import json
import pathlib
import pickle
import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: from_dump.py <dump_dir> [out.json]", file=sys.stderr)
        sys.exit(2)
    dump_dir = pathlib.Path(sys.argv[1])
    out_path = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else dump_dir / "history.json"
    state = pickle.load(open(dump_dir / "history.pkl", "rb"))
    history = state.get("history", [])
    entries = [
        {"step": i, "score": h.get("score"), "prompt": h.get("prompt")}
        for i, h in enumerate(history)
    ]
    if not entries:
        print("BLOCKED: empty history in", dump_dir / "history.pkl", file=sys.stderr)
        sys.exit(1)
    best = max(entries, key=lambda e: e["score"])
    result = {"best": best, "steps": len(entries), "history": entries}
    out_path.write_text(json.dumps(result, indent=2))
    print(f"best score {best['score']} at step {best['step']} -> {out_path}")


if __name__ == "__main__":
    main()
