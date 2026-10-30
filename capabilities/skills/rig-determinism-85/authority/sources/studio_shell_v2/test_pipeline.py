"""Self-check for the pipeline runner + proof-manifest module. Run: python3 test_pipeline.py"""
import json
import tempfile
from pathlib import Path

import pipeline


def demo():
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "artifacts"
        src.mkdir()
        (src / "a.txt").write_text("alpha")
        (src / "b.txt").write_text("beta")
        out = Path(td) / "manifest.json"
        spec = Path(td) / "spec.json"
        spec.write_text(json.dumps({
            "name": "proof-manifest-test",
            "nodes": [
                {"id": "scan", "fn": "scan_files", "args": {"root": str(src)}, "retries": 2},
                {"id": "hash", "fn": "hash_files", "args": {"out": str(out)}, "retries": 2},
                {"id": "emit", "fn": "write_manifest", "args": {}, "retries": 1},
            ]}))
        res = pipeline.run_pipeline(spec)
        assert res["ok"], res
        m = json.loads(out.read_text())
        assert m["count"] == 2, m
        assert {e["path"] for e in m["entries"]} == {str(src / "a.txt"), str(src / "b.txt")}
        hashes = {e["sha256"] for e in m["entries"]}
        assert len(hashes) == 2 and all(len(h) == 64 for h in hashes), hashes
        hist = pipeline.run_history()
        assert any(r.get("run_id") == res["run_id"] and r["event"] == "run_ok" for r in hist), hist[-3:]
        # failure path: missing root must land as run_fail, not silence
        spec.write_text(json.dumps({
            "name": "proof-manifest-fail",
            "nodes": [{"id": "scan", "fn": "scan_files", "args": {"root": "/nonexistent-zz"}, "retries": 1}]}))
        bad = pipeline.run_pipeline(spec)
        assert not bad["ok"] and "error" in bad, bad
        print("self-check PASS:", res["run_id"], "manifest count", m["count"], "| fail path:", bad["error"])


if __name__ == "__main__":
    demo()
