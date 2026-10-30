#!/usr/bin/env python3
"""Render a sanitized DOCX into actual PNG pages for human and Jev review."""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from resume_quality import render_document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True, help="Hash of the exact working or reviewed final Markdown used to create the DOCX")
    args = parser.parse_args()
    source = args.docx.resolve()
    if source.suffix.lower() != ".docx" or not source.is_file():
        parser.error("A readable final DOCX is required")
    if len(args.source_sha256) != 64 or any(c not in "0123456789abcdef" for c in args.source_sha256):
        parser.error("--source-sha256 must be the actual lowercase SHA-256 of the source Markdown")
    output = args.output.resolve()
    if output.exists():
        parser.error("Use a new output directory to prevent stale-page reuse")
    evidence = render_document(source, output, source_sha256=args.source_sha256)
    (output / "render-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
